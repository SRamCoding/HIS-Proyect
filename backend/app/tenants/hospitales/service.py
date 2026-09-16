import asyncio
import json
import logging
import re
import uuid

import bcrypt
from fastapi import HTTPException
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.admin.modulos.models import ModuleDependency
from app.admin.niveles_hospitalarios.models import HospitalLevel
from app.auth.models import User
from app.core.tenancy import invalidate_tenant_cache
from app.sigarh.mantenimiento.models import PerfilUsuario, RolSistema, UsuarioSigarh
from app.tenants.hospitales.models import Tenant, TenantModule
from app.tenants.hospitales.schemas import TenantCreate
from app.tenants.modulos.models import Module


def generate_schema_name(domain: str) -> str:
    """Nombre legado conservado mientras exista la columna schema_name."""
    return f"tenant_{re.sub(r'[^a-z0-9_]', '_', domain.lower())}"


async def _validate_modules(db: AsyncSession, module_codes: list[str]) -> set[str]:
    requested = set(module_codes)
    valid = set((await db.scalars(select(Module.code).where(
        Module.code.in_(requested), Module.is_active.is_(True),
    ))).all()) if requested else set()
    invalid = sorted(requested - valid)
    if invalid:
        raise HTTPException(422, f"Módulos inexistentes o inactivos: {', '.join(invalid)}")
    dependencies = (await db.execute(select(
        ModuleDependency.module_code, ModuleDependency.depends_on_code,
    ).where(
        ModuleDependency.module_code.in_(requested),
        ModuleDependency.is_required.is_(True),
    ))).all() if requested else []
    missing = sorted({required for _, required in dependencies if required not in requested})
    if missing:
        raise HTTPException(422, f"Faltan módulos requeridos: {', '.join(missing)}")
    return requested


async def crear_tenant_rapido(db: AsyncSession, data: TenantCreate) -> Tenant:
    """Parte RAPIDA de crear un hospital: valida y registra el Tenant (y sus
    modulos) en estado 'pendiente'. Responde al instante -- el trabajo
    pesado (crear la BD fisica, migrarla, sembrar catalogos, crear los
    usuarios iniciales) se encola aparte (ver workers/tasks.py) en vez de
    correr atado a esta misma peticion HTTP. Antes todo eso pasaba aqui
    mismo: si el admin perdia la conexion a mitad de camino, el servidor
    seguia trabajando a ciegas y nadie sabia si el hospital habia quedado
    creado, a medias, o nunca aplico."""
    from app.core.tenant_db import _slugify_db_name

    database_name = _slugify_db_name(data.domain.split(".")[0])
    level = await db.scalar(select(HospitalLevel).where(
        HospitalLevel.code == data.hospital_level,
        HospitalLevel.is_active.is_(True),
    ))
    if not level:
        raise HTTPException(422, "El nivel hospitalario no existe o está inactivo")
    await _validate_modules(db, data.active_modules)
    if await db.scalar(select(Tenant.id).where(Tenant.database_name == database_name)):
        raise HTTPException(400, "El subdominio genera un nombre de base ya registrado")

    tenant = Tenant(
        name=data.name, domain=data.domain,
        schema_name=generate_schema_name(data.domain), database_name=database_name,
        ruc=data.ruc, address=data.address, phone=data.phone, email=data.email,
        hospital_level=data.hospital_level, mission=data.mission, vision=data.vision,
        values=data.values, schedule=data.schedule, social_media=data.social_media,
        provisioning_status="pendiente",
    )
    db.add(tenant)
    await db.flush()
    db.add_all([
        TenantModule(tenant_id=tenant.id, module_code=code, is_active=True)
        for code in data.active_modules
    ])
    await db.commit()
    try:
        await db.refresh(tenant, attribute_names=["modules"])
    except Exception:
        logging.getLogger(__name__).exception(
            "Hospital %s registrado, pero no se pudo refrescar tenant.modules", tenant.id
        )
    return tenant


async def aprovisionar_hospital_async(
    tenant_id: uuid.UUID,
    database_name: str,
    hospital_level: str,
    active_modules: list[str],
    admin_name: str, admin_email: str, admin_password: str,
    sigarh_name: str, sigarh_email: str, sigarh_password: str,
) -> None:
    """Trabajo pesado de aprovisionar un hospital -- lo llama la tarea de
    Celery (workers/tasks.py), NUNCA una peticion HTTP directamente. Al
    terminar deja `provisioning_status` en 'listo' o 'error' (con el detalle
    en `provisioning_error`) y notifica al panel Admin."""
    from app.core.database import AsyncSessionLocal
    from app.core.tenant_db import (
        _tenant_engines, create_tenant_database,
        drop_tenant_database, get_tenant_sessionmaker, run_tenant_migrations,
    )
    from app.admin.notificaciones.service import crear_notificacion

    database_created = False
    try:
        await create_tenant_database(database_name)
        database_created = True
        await asyncio.to_thread(run_tenant_migrations, database_name)
        TenantSession = get_tenant_sessionmaker(database_name)
        async with TenantSession() as tenant_db:
            from app.sigarh.rrhh.service import asegurar_oferta_especialidades
            await asegurar_oferta_especialidades(tenant_db, tenant_id, hospital_level)
            from app.sigarh.mantenimiento.service import asegurar_estructura_asistencial
            await asegurar_estructura_asistencial(tenant_db, tenant_id, hospital_level)
            from app.sigarh.mantenimiento.profesiones_catalogo import asegurar_catalogo_personal
            await asegurar_catalogo_personal(tenant_db, tenant_id)
            from app.sigarh.mantenimiento.escalas_catalogo import asegurar_escalas
            await asegurar_escalas(tenant_db, tenant_id)
            from app.sigarh.mantenimiento.departamentos_catalogo import asegurar_departamentos
            await asegurar_departamentos(tenant_db, tenant_id, hospital_level)
            from app.sigarh.mantenimiento.guardias_catalogo import asegurar_guardias
            await asegurar_guardias(tenant_db, tenant_id, hospital_level)
            from app.sigarh.mantenimiento.actividades_catalogo import asegurar_actividades
            await asegurar_actividades(tenant_db, tenant_id, hospital_level)
            tenant_db.add(User(
                name=admin_name, email=admin_email,
                password=bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode(),
                role="administrador", panel="app", tenant_id=None, is_active=True,
            ))
            role = RolSistema(
                tenant_id=tenant_id, nombre="Administrador SIGARH", panel="sigarh",
                modulos_permitidos=json.dumps(active_modules),
                permisos_accion=json.dumps([
                    "administrar_mantenimiento", "administrar_seguridad", "aprobar_roles_turno",
                ]),
                alcance_global=True,
                is_active=True,
            )
            tenant_db.add(role)
            await tenant_db.flush()
            profile = PerfilUsuario(
                tenant_id=tenant_id, nombre=sigarh_name,
                rol_sistema_id=role.id, modulos_acceso=json.dumps(active_modules),
                is_active=True,
            )
            tenant_db.add(profile)
            await tenant_db.flush()
            tenant_db.add(UsuarioSigarh(
                tenant_id=tenant_id, perfil_id=profile.id,
                name=sigarh_name,
                username=sigarh_email.split("@")[0], email=sigarh_email,
                password=bcrypt.hashpw(sigarh_password.encode(), bcrypt.gensalt()).decode(),
                is_active=True,
            ))
            await tenant_db.commit()

        async with AsyncSessionLocal() as db:
            from app.sigarh.rrhh.service import asegurar_oferta_especialidades
            await asegurar_oferta_especialidades(db, tenant_id, hospital_level)
            from app.sigarh.mantenimiento.service import asegurar_estructura_asistencial
            await asegurar_estructura_asistencial(db, tenant_id, hospital_level)
            from app.sigarh.mantenimiento.profesiones_catalogo import asegurar_catalogo_personal
            await asegurar_catalogo_personal(db, tenant_id)
            from app.sigarh.mantenimiento.escalas_catalogo import asegurar_escalas
            await asegurar_escalas(db, tenant_id)
            from app.sigarh.mantenimiento.departamentos_catalogo import asegurar_departamentos
            await asegurar_departamentos(db, tenant_id, hospital_level)
            from app.sigarh.mantenimiento.guardias_catalogo import asegurar_guardias
            await asegurar_guardias(db, tenant_id, hospital_level)
            from app.sigarh.mantenimiento.actividades_catalogo import asegurar_actividades
            await asegurar_actividades(db, tenant_id, hospital_level)
            await db.commit()
    except Exception as exc:
        logging.getLogger(__name__).exception("Fallo el aprovisionamiento del hospital %s", tenant_id)
        engine = _tenant_engines.pop(database_name, None)
        if engine is not None:
            await engine.dispose()
        if database_created:
            try:
                await drop_tenant_database(database_name)
            except Exception:
                logging.getLogger(__name__).exception(
                    "No se pudo limpiar la base hospitalaria %s", database_name
                )
        async with AsyncSessionLocal() as db:
            tenant = await db.get(Tenant, tenant_id)
            if tenant:
                tenant.provisioning_status = "error"
                tenant.provisioning_error = str(exc)[:2000]
                nombre_hospital = tenant.name
                await db.commit()
            else:
                nombre_hospital = str(tenant_id)
        await crear_notificacion(
            f"Error al aprovisionar: {nombre_hospital}",
            str(exc)[:500],
            nivel="error",
        )
        return

    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, tenant_id)
        if tenant:
            tenant.provisioning_status = "listo"
            tenant.provisioning_error = None
            nombre_hospital, dominio, nivel = tenant.name, tenant.domain, tenant.hospital_level
            await db.commit()
        else:
            nombre_hospital, dominio, nivel = str(tenant_id), "", ""
    await crear_notificacion(
        f"Hospital creado: {nombre_hospital}",
        f"Dominio {dominio} · nivel {nivel}",
        nivel="exito",
        link=f"/admin/hospitales/{tenant_id}",
    )


async def get_tenant_by_domain(db: AsyncSession, domain: str) -> Tenant | None:
    result = await db.execute(
        select(Tenant).options(selectinload(Tenant.modules)).where(
            Tenant.domain == domain.lower().rstrip(".")
        )
    )
    return result.scalar_one_or_none()


async def update_tenant_modules(
    db: AsyncSession, redis: Redis, tenant_id: uuid.UUID, module_codes: list[str],
) -> None:
    tenant = await db.scalar(select(Tenant).where(Tenant.id == tenant_id))
    if not tenant:
        raise HTTPException(404, "Hospital no encontrado")
    requested = await _validate_modules(db, module_codes)
    # DELETE por SQL directo (antes) no pasa por la sesion ORM, asi que el
    # listener de auditoria automatica (before_flush, engachado a
    # session.deleted) nunca lo veia -- quitarle modulos a un hospital
    # quedaba sin rastro. Borrando cada fila via el ORM si queda registrado.
    existentes = (await db.scalars(
        select(TenantModule).where(TenantModule.tenant_id == tenant_id)
    )).all()
    for tm in existentes:
        await db.delete(tm)
    db.add_all([
        TenantModule(tenant_id=tenant_id, module_code=code, is_active=True)
        for code in sorted(requested)
    ])
    await db.commit()
    await invalidate_tenant_cache(tenant.domain, redis)
