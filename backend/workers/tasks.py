# backend/workers/tasks.py
"""Tareas de Celery. El aprovisionamiento de un hospital es pesado (crea una
BD fisica, la migra, siembra catalogos, crea usuarios) y antes corria atado
a la peticion HTTP de POST /admin/hospitales -- si el cliente se
desconectaba a mitad de camino, el trabajo seguia a ciegas en el worker de
uvicorn. Ahora esa parte se encola aqui y el endpoint responde de inmediato.
"""
import asyncio
import uuid

from workers.celery_app import celery_app


async def _cerrar_engines_compartidos() -> None:
    """El engine central (app/core/database.py) y los engines por hospital
    (app/core/tenant_db.py) son objetos de modulo, creados UNA vez y
    reusados entre tareas -- pero cada tarea de Celery corre en su propio
    asyncio.run(), es decir su propio event loop nuevo. Las conexiones
    asyncpg quedan atadas para siempre al loop en el que se crearon: si una
    tarea reutiliza una conexion abierta por una tarea anterior (loop ya
    cerrado), revienta con "got Future attached to a different loop". Se
    cierran y se descartan TODAS las conexiones cacheadas al final de cada
    tarea, dentro de este mismo loop (dispose() es async y debe correr en
    el loop donde esas conexiones viven), para que la siguiente tarea
    arranque siempre con conexiones frescas en SU propio loop."""
    from app.core.database import engine as engine_central
    from app.core.tenant_db import _tenant_engines

    await engine_central.dispose()
    for engine_tenant in list(_tenant_engines.values()):
        await engine_tenant.dispose()
    _tenant_engines.clear()


def _ejecutar(coro) -> None:
    """asyncio.run(), pero cerrando los engines compartidos SIEMPRE al
    final (exito o fallo) y DENTRO del mismo loop -- ver
    _cerrar_engines_compartidos."""
    async def _con_cierre():
        try:
            return await coro
        finally:
            await _cerrar_engines_compartidos()

    return asyncio.run(_con_cierre())


@celery_app.task(name="workers.tasks.aprovisionar_hospital")
def aprovisionar_hospital(
    tenant_id: str,
    database_name: str,
    hospital_level: str,
    active_modules: list[str],
    admin_name: str, admin_email: str, admin_password_hash: str,
    sigarh_name: str, sigarh_email: str, sigarh_password_hash: str,
    attempt_token: str,
) -> None:
    from app.tenants.hospitales.service import aprovisionar_hospital_async

    _ejecutar(aprovisionar_hospital_async(
        tenant_id=uuid.UUID(tenant_id),
        database_name=database_name,
        hospital_level=hospital_level,
        active_modules=active_modules,
        admin_name=admin_name, admin_email=admin_email, admin_password_hash=admin_password_hash,
        sigarh_name=sigarh_name, sigarh_email=sigarh_email, sigarh_password_hash=sigarh_password_hash,
        attempt_token=attempt_token,
    ))


@celery_app.task(name="workers.tasks.reintentar_auditoria_fallback")
def reintentar_auditoria_fallback() -> dict:
    """Reprocesa los eventos de auditoria que quedaron en el archivo de
    fallback (ver app/core/audit.py) porque AuditLog no los acepto la
    primera vez. Se dispara al instante cuando ocurre un fallo nuevo, y
    ademas corre sola cada cierto tiempo (ver beat_schedule en
    celery_app.py) por si ese primer intento inmediato tambien fallo."""
    from app.core.audit import reintentar_fallback_pendiente

    return _ejecutar(reintentar_fallback_pendiente())


@celery_app.task(name="workers.tasks.revisar_aprovisionamientos_atascados")
def revisar_aprovisionamientos_atascados() -> list[str]:
    """Corre periodicamente (ver beat_schedule en celery_app.py): marca
    como 'error' cualquier hospital que quedo en 'pendiente' mas tiempo del
    razonable, sin ninguna tarea real trabajando en el (el proceso murio
    entre confirmar 'pendiente' y encolar la tarea, o el worker que la
    tomo murio a mitad de camino). Sin esto ese hospital quedaba atascado
    para siempre, sin error visible y sin poder reintentarse."""
    from app.tenants.hospitales.service import revisar_aprovisionamientos_atascados as _revisar

    return _ejecutar(_revisar())


@celery_app.task(name="workers.tasks.purgar_notificaciones_antiguas")
def purgar_notificaciones_antiguas() -> int:
    """Corre una vez al dia (ver beat_schedule en celery_app.py): borra
    notificaciones YA LEIDAS con mas de 90 dias -- la tabla no tenia ningun
    mecanismo de retencion y crecia para siempre. Las no leidas nunca se
    tocan, sin importar su antiguedad."""
    from app.admin.notificaciones.service import purgar_notificaciones_antiguas as _purgar

    return _ejecutar(_purgar())
