import asyncio
import json
import logging
import re
import uuid

import bcrypt
from fastapi import HTTPException
from redis.asyncio import Redis
from sqlalchemy import select, text
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


async def create_tenant(db: AsyncSession, data: TenantCreate) -> Tenant:
    from app.core.tenant_db import (
        _slugify_db_name, _tenant_engines, create_tenant_database,
        drop_tenant_database, get_tenant_sessionmaker, run_tenant_migrations,
    )

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
    )
    db.add(tenant)
    await db.flush()
    tenant.modules = [
        TenantModule(tenant_id=tenant.id, module_code=code, is_active=True)
        for code in data.active_modules
    ]

    database_created = False
    try:
        await create_tenant_database(database_name)
        database_created = True
        await asyncio.to_thread(run_tenant_migrations, database_name)
        TenantSession = get_tenant_sessionmaker(database_name)
        async with TenantSession() as tenant_db:
            from app.sigarh.rrhh.service import asegurar_oferta_especialidades
            await asegurar_oferta_especialidades(tenant_db, tenant.id, data.hospital_level)
            from app.sigarh.mantenimiento.service import asegurar_estructura_asistencial
            await asegurar_estructura_asistencial(tenant_db, tenant.id, data.hospital_level)
            from app.sigarh.mantenimiento.profesiones_catalogo import asegurar_catalogo_personal
            await asegurar_catalogo_personal(tenant_db, tenant.id)
            from app.sigarh.mantenimiento.escalas_catalogo import asegurar_escalas
            await asegurar_escalas(tenant_db, tenant.id)
            from app.sigarh.mantenimiento.departamentos_catalogo import asegurar_departamentos
            await asegurar_departamentos(tenant_db, tenant.id, data.hospital_level)
            from app.sigarh.mantenimiento.guardias_catalogo import asegurar_guardias
            await asegurar_guardias(tenant_db, tenant.id, data.hospital_level)
            from app.sigarh.mantenimiento.actividades_catalogo import asegurar_actividades
            await asegurar_actividades(tenant_db, tenant.id, data.hospital_level)
            tenant_db.add(User(
                name=data.admin_name, email=data.admin_email,
                password=bcrypt.hashpw(data.admin_password.encode(), bcrypt.gensalt()).decode(),
                role="administrador", panel="app", tenant_id=None, is_active=True,
            ))
            role = RolSistema(
                tenant_id=tenant.id, nombre="Administrador SIGARH", panel="sigarh",
                modulos_permitidos=json.dumps(data.active_modules),
                # El rol Administrador SIGARH debe poder gestionar Mantenimiento,
                # Seguridad (usuarios/perfiles/roles) y aprobar roles de turno
                # desde el primer momento; sin esto, la propia cuenta que crea
                # el hospital queda sin acceso a Mantenimiento → Roles del Sistema.
                permisos_accion=json.dumps([
                    "administrar_mantenimiento", "administrar_seguridad", "aprobar_roles_turno",
                ]),
                alcance_global=True,
                is_active=True,
            )
            tenant_db.add(role)
            await tenant_db.flush()
            profile = PerfilUsuario(
                tenant_id=tenant.id, nombre=data.sigarh_name,
                rol_sistema_id=role.id, modulos_acceso=json.dumps(data.active_modules),
                is_active=True,
            )
            tenant_db.add(profile)
            await tenant_db.flush()
            tenant_db.add(UsuarioSigarh(
                tenant_id=tenant.id, perfil_id=profile.id,
                name=data.sigarh_name,
                username=data.sigarh_email.split("@")[0], email=data.sigarh_email,
                password=bcrypt.hashpw(data.sigarh_password.encode(), bcrypt.gensalt()).decode(),
                is_active=True,
            ))
            await tenant_db.commit()
        from app.sigarh.rrhh.service import asegurar_oferta_especialidades
        await asegurar_oferta_especialidades(db, tenant.id, data.hospital_level)
        from app.sigarh.mantenimiento.service import asegurar_estructura_asistencial
        await asegurar_estructura_asistencial(db, tenant.id, data.hospital_level)
        from app.sigarh.mantenimiento.profesiones_catalogo import asegurar_catalogo_personal
        await asegurar_catalogo_personal(db, tenant.id)
        from app.sigarh.mantenimiento.escalas_catalogo import asegurar_escalas
        await asegurar_escalas(db, tenant.id)
        from app.sigarh.mantenimiento.departamentos_catalogo import asegurar_departamentos
        await asegurar_departamentos(db, tenant.id, data.hospital_level)
        from app.sigarh.mantenimiento.guardias_catalogo import asegurar_guardias
        await asegurar_guardias(db, tenant.id, data.hospital_level)
        from app.sigarh.mantenimiento.actividades_catalogo import asegurar_actividades
        await asegurar_actividades(db, tenant.id, data.hospital_level)
        await db.commit()
        await db.refresh(tenant, attribute_names=["modules"])
        return tenant
    except Exception:
        await db.rollback()
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
        raise


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
    await db.execute(
        text("DELETE FROM tenant_modules WHERE tenant_id = :tid"),
        {"tid": str(tenant_id)},
    )
    db.add_all([
        TenantModule(tenant_id=tenant_id, module_code=code, is_active=True)
        for code in sorted(requested)
    ])
    await db.commit()
    await invalidate_tenant_cache(tenant.domain, redis)
