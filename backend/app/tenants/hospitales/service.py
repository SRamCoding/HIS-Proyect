import asyncio
import json
import logging
import re
import uuid
from datetime import datetime, timedelta

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
        logo_url=data.logo_url,
        hospital_level=data.hospital_level, mission=data.mission, vision=data.vision,
        values=data.values, schedule=data.schedule, social_media=data.social_media,
        provisioning_status="pendiente",
        provisioning_started_at=datetime.utcnow(),
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


async def _sigue_siendo_el_intento_vigente(tenant_id: uuid.UUID, attempt_token: str) -> bool:
    """Confirma que `attempt_token` (el provisioning_started_at con el que
    arranco ESTA ejecucion) sigue siendo el intento actual del hospital.

    Sin esto: revisar_aprovisionamientos_atascados puede marcar "error" a
    un hospital cuya tarea en realidad sigue corriendo de verdad (el tiempo
    transcurrido no PRUEBA que el worker murio, solo lo hace probable), y
    un admin puede reintentarlo mientras tanto. Quedarian dos ejecuciones
    de aprovisionar_hospital_async escribiendo sobre el mismo hospital sin
    que ninguna supiera de la otra. Cada ejecucion revisa esto antes de
    hacer algo irreversible (borrar la base fisica) o de escribir el
    resultado final (listo/error): si ya no es el intento vigente, se
    retira en silencio -- el intento mas nuevo es el que manda."""
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        tenant = await db.get(Tenant, tenant_id)
        if not tenant or not tenant.provisioning_started_at:
            return False
        return tenant.provisioning_started_at.isoformat() == attempt_token


async def aprovisionar_hospital_async(
    tenant_id: uuid.UUID,
    database_name: str,
    hospital_level: str,
    active_modules: list[str],
    admin_name: str, admin_email: str, admin_password_hash: str,
    sigarh_name: str, sigarh_email: str, sigarh_password_hash: str,
    attempt_token: str,
) -> None:
    """Trabajo pesado de aprovisionar un hospital -- lo llama la tarea de
    Celery (workers/tasks.py), NUNCA una peticion HTTP directamente. Al
    terminar deja `provisioning_status` en 'listo' o 'error' (con el detalle
    en `provisioning_error`) y notifica al panel Admin.

    Recibe los HASHES de las contraseñas, no las contraseñas en claro: estos
    argumentos viajan serializados como JSON dentro del mensaje de la cola
    (RabbitMQ) y quedan un rato en el broker/backend de resultados -- ya
    llegan hasheados desde crear_hospital() para no exponer credenciales en
    claro en ese trayecto."""
    from app.core.database import AsyncSessionLocal, engine as central_engine
    from app.core.tenant_db import (
        _tenant_engines, create_tenant_database,
        drop_tenant_database, get_tenant_sessionmaker, run_tenant_migrations,
    )
    from app.admin.notificaciones.service import crear_notificacion

    database_created = False
    try:
        try:
            # database_created SOLO es True si ESTA llamada creo la base de
            # verdad -- si ya existia (un reintento sobre una base de un
            # intento anterior), un fallo mas adelante en ESTE intento NUNCA
            # debe poder borrarla: podria ser una base ya completamente
            # funcional (si lo unico que fallo antes fue marcar el estado
            # final "listo"), no un residuo a mitad de camino.
            database_created = await create_tenant_database(database_name)
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
                    password=admin_password_hash,
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
                    password=sigarh_password_hash,
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
            tenant_engine = _tenant_engines.pop(database_name, None)
            if tenant_engine is not None:
                await tenant_engine.dispose()

            if not await _sigue_siendo_el_intento_vigente(tenant_id, attempt_token):
                # Un intento mas nuevo (un reintento manual, o el propio
                # detector de atascados que ya lo marco "error" mientras
                # ESTE seguia corriendo) ya tomo el control del hospital.
                # Tocar la base fisica o el estado ahora pisaria ese
                # trabajo mas nuevo -- esta ejecucion se retira sin hacer
                # nada mas, solo deja registro de lo que paso.
                logging.getLogger(__name__).warning(
                    "Aprovisionamiento de %s: intento superado, no se toca la base ni el estado", tenant_id
                )
                raise
            if database_created:
                try:
                    await drop_tenant_database(database_name)
                except Exception:
                    logging.getLogger(__name__).exception(
                        "No se pudo limpiar la base hospitalaria %s", database_name
                    )
            mensaje_error = str(exc)[:1900]
            if not database_created:
                # La base ya existia ANTES de este intento (probablemente un
                # reintento) y no se borro -- puede tener trabajo valido de
                # un intento anterior. Se deja explicito para que quien
                # revise sepa que la base sigue ahi y por que no se limpio sola.
                mensaje_error += " [La base de datos ya existía antes de este intento; no se eliminó automáticamente.]"
            async with AsyncSessionLocal() as db:
                tenant = await db.get(Tenant, tenant_id)
                if tenant:
                    tenant.provisioning_status = "error"
                    tenant.provisioning_error = mensaje_error
                    nombre_hospital = tenant.name
                    await db.commit()
                else:
                    nombre_hospital = str(tenant_id)
            await crear_notificacion(
                f"Error al aprovisionar: {nombre_hospital}",
                str(exc)[:500],
                nivel="error",
            )
            # Antes esta rama terminaba en `return`: la tarea de Celery
            # quedaba en estado SUCCESS aunque el hospital hubiera quedado
            # en "error". Relanzar la excepcion hace que Celery marque la
            # tarea como FAILED de verdad -- necesario para que cualquier
            # monitoreo/alerta sobre el worker detecte el fallo real.
            raise

        if not await _sigue_siendo_el_intento_vigente(tenant_id, attempt_token):
            # El trabajo termino bien, pero ya no es el intento vigente (uno
            # mas nuevo tomo el control mientras este corria). Escribir
            # "listo" aca pisaria a ese intento mas nuevo -- que puede seguir
            # corriendo, o ya haber terminado con otro resultado. Se retira
            # sin tocar el estado.
            logging.getLogger(__name__).warning(
                "Aprovisionamiento de %s termino, pero ya no es el intento vigente; no se marca 'listo'", tenant_id
            )
            return
        try:
            async with AsyncSessionLocal() as db:
                tenant = await db.get(Tenant, tenant_id)
                if tenant:
                    tenant.provisioning_status = "listo"
                    tenant.provisioning_error = None
                    # Ya no hacen falta para precargar un reintento -- las
                    # cuentas reales ya existen en la BD fisica del hospital.
                    tenant.admin_name = tenant.admin_email = None
                    tenant.sigarh_name = tenant.sigarh_email = None
                    nombre_hospital, dominio, nivel = tenant.name, tenant.domain, tenant.hospital_level
                    await db.commit()
                else:
                    nombre_hospital, dominio, nivel = str(tenant_id), "", ""
        except Exception:
            # El hospital SI quedo funcionalmente listo (BD fisica, catalogos
            # y usuarios ya se crearon arriba) -- este commit final solo pone
            # la bandera en "listo". Si este paso puntual falla, el hospital
            # quedaria en "pendiente" para siempre, sin error visible y sin
            # que nadie se entere de que en realidad ya se puede usar. Se
            # notifica explicitamente en vez de dejarlo como un pendiente
            # fantasma indistinguible de uno que sigue en curso.
            logging.getLogger(__name__).exception(
                "El hospital %s se aprovisiono correctamente pero no se pudo marcar como 'listo'", tenant_id
            )
            await crear_notificacion(
                f"Revisar hospital {tenant_id}",
                "El aprovisionamiento terminó bien, pero no se pudo actualizar su estado a 'listo'. Verificar manualmente.",
                nivel="alerta",
            )
            raise
        await crear_notificacion(
            f"Hospital creado: {nombre_hospital}",
            f"Dominio {dominio} · nivel {nivel}",
            nivel="exito",
            link=f"/admin/hospitales/{tenant_id}",
        )
    finally:
        # Los engines de asyncpg quedan atados al event loop en el que se
        # crearon. El worker de Celery corre cada tarea con un asyncio.run()
        # nuevo (un event loop nuevo por tarea): si el engine central o el
        # del hospital sobreviven en el cache del proceso, la SIGUIENTE
        # tarea intenta reusar conexiones de un loop que ya se cerro.
        # Disponerlos aqui, todavia dentro del mismo loop que los abrio,
        # fuerza a que la proxima tarea arme un engine/pool nuevo desde cero.
        await central_engine.dispose()
        tenant_engine = _tenant_engines.pop(database_name, None)
        if tenant_engine is not None:
            await tenant_engine.dispose()


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
    #
    # Importante: solo se borra lo que YA NO esta seleccionado y solo se
    # inserta lo NUEVO. Borrar todo y volver a insertar todo lo seleccionado
    # (como antes) rompe con IntegrityError en uq_tenant_module cuando un
    # modulo se conserva: dentro del mismo flush, SQLAlchemy puede emitir el
    # INSERT de la fila nueva antes que el DELETE de la vieja, y ambas
    # comparten (tenant_id, module_code).
    existentes = (await db.scalars(
        select(TenantModule).where(TenantModule.tenant_id == tenant_id)
    )).all()
    existentes_por_code = {tm.module_code: tm for tm in existentes}
    for code, tm in existentes_por_code.items():
        if code not in requested:
            await db.delete(tm)
    nuevos = requested - existentes_por_code.keys()
    db.add_all([
        TenantModule(tenant_id=tenant_id, module_code=code, is_active=True)
        for code in sorted(nuevos)
    ])
    await db.commit()
    await invalidate_tenant_cache(tenant.domain, redis)


UMBRAL_APROVISIONAMIENTO_ATASCADO = timedelta(minutes=20)


async def revisar_aprovisionamientos_atascados() -> list[str]:
    """Detecta hospitales en 'pendiente' cuyo intento actual (provisioning_started_at)
    lleva mas del umbral corriendo -- eso significa que la tarea de Celery
    nunca se encolo de verdad (el proceso murio entre confirmar 'pendiente'
    y publicar el mensaje) o que el worker que la tomo murio a mitad de
    camino sin poder avisar. Sin este chequeo, ese hospital quedaba
    'pendiente' para siempre: sin tarea corriendo, sin error visible, y
    el endpoint de reintento solo acepta hospitales en estado 'error'.

    Lo pasa a 'error' con un mensaje claro para que SI se pueda reintentar.
    El UPDATE es atomico por fila (WHERE exige que siga en 'pendiente' con
    ese mismo intento vencido), asi que es seguro llamarlo mas de una vez
    o desde mas de un proceso a la vez -- cada hospital atascado se marca
    una sola vez."""
    from app.admin.notificaciones.service import crear_notificacion

    limite = datetime.utcnow() - UMBRAL_APROVISIONAMIENTO_ATASCADO
    from app.core.database import AsyncSessionLocal
    marcados: list[str] = []
    async with AsyncSessionLocal() as db:
        pendientes = (await db.scalars(
            select(Tenant).where(
                Tenant.provisioning_status == "pendiente",
                Tenant.provisioning_started_at.is_not(None),
                Tenant.provisioning_started_at < limite,
            )
        )).all()
        for tenant in pendientes:
            resultado = await db.execute(
                select(Tenant.id).where(
                    Tenant.id == tenant.id,
                    Tenant.provisioning_status == "pendiente",
                    Tenant.provisioning_started_at < limite,
                ).with_for_update(skip_locked=True)
            )
            if resultado.scalar_one_or_none() is None:
                continue  # otro proceso ya lo tomo, o una tarea real lo termino justo ahora
            tenant.provisioning_status = "error"
            tenant.provisioning_error = (
                "El aprovisionamiento no terminó en el tiempo esperado. "
                "Es probable que la tarea nunca se haya encolado o que el worker se haya interrumpido. "
                "Puedes reintentarlo desde esta pantalla."
            )
            await db.commit()
            marcados.append(tenant.name)
            await crear_notificacion(
                f"Aprovisionamiento atascado: {tenant.name}",
                "Quedó en 'pendiente' sin avanzar; se marcó como error para poder reintentarlo.",
                nivel="alerta",
                link=f"/admin/hospitales/{tenant.id}/reintentar",
            )
    return marcados
