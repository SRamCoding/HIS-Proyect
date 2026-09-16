# backend/app/admin/auditoria/service.py
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, cast, String

from app.admin.auditoria.models import AuditLog

# Zona horaria fija de Peru (sin horario de verano, UTC-5 todo el ano) --
# "eventos de hoy" debe representar el dia calendario de Lima, no el de UTC
# (created_at se guarda en UTC): un evento a las 7pm en Lima ya es
# medianoche en UTC y antes se contaba como "de mañana", no "de hoy".
_ZONA_LIMA = timezone(timedelta(hours=-5))

LIMIT_MAXIMO = 200


def _scope(query, tenant_id, only_global):
    if only_global:
        return query.where(AuditLog.tenant_id.is_(None))
    if tenant_id:
        return query.where(AuditLog.tenant_id == tenant_id)
    return query


async def get_audit_logs(
    db: AsyncSession,
    tenant_id: uuid.UUID | None = None,
    only_global: bool = False,
    limit: int = 100,
    offset: int = 0,
    q: str | None = None,
    action: str | None = None,
) -> tuple[list[AuditLog], int]:
    """Antes traia hasta `limit` filas SIEMPRE desde el principio y toda la
    busqueda/paginacion pasaba en el navegador sobre ese lote descargado --
    el historial real (mas alla de esas primeras filas) era invisible.
    Ahora offset/busqueda/filtro de accion se resuelven en la consulta, y se
    devuelve el total real para que la paginacion en pantalla sea honesta.

    `limit`/`offset` se acotan aca (no solo confiar en el tipo `int` del
    parametro del router): sin esto, cualquiera podia pedir limit=999999999
    o un offset negativo."""
    limit = max(1, min(limit, LIMIT_MAXIMO))
    offset = max(0, offset)

    base = select(AuditLog)
    base = _scope(base, tenant_id, only_global)
    if action and action != "all":
        base = base.where(AuditLog.action == action)
    if q:
        like = f"%{q}%"
        base = base.where(or_(
            AuditLog.user_name.ilike(like),
            AuditLog.action.ilike(like),
            AuditLog.description.ilike(like),
            AuditLog.model.ilike(like),
        ))

    total = await db.scalar(select(func.count()).select_from(base.subquery())) or 0

    query = base.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_audit_summary(
    db: AsyncSession,
    tenant_id: uuid.UUID | None = None,
    only_global: bool = False,
) -> dict:
    """Agregados (eventos de hoy, usuarios unicos, accion mas frecuente) para
    el mismo alcance (global o un hospital), calculados en el servidor --
    antes salian de sumar el lote de hasta 1000 filas ya descargado, asi que
    quedaban mal apenas el historial real superaba eso."""
    # "Hoy" se calcula en hora de Lima, no UTC (created_at se guarda en
    # UTC): un evento de las 7pm en Lima ya es medianoche UTC del dia
    # siguiente, y antes se contaba como "de mañana" en vez de "de hoy".
    ahora_lima = datetime.now(_ZONA_LIMA)
    hoy_inicio_lima = ahora_lima.replace(hour=0, minute=0, second=0, microsecond=0)
    hoy_inicio_utc = hoy_inicio_lima.astimezone(timezone.utc).replace(tzinfo=None)

    base = _scope(select(AuditLog.id), tenant_id, only_global)
    total = await db.scalar(select(func.count()).select_from(base.subquery())) or 0

    hoy_query = _scope(select(func.count(AuditLog.id)), tenant_id, only_global).where(
        AuditLog.created_at >= hoy_inicio_utc
    )
    eventos_hoy = await db.scalar(hoy_query) or 0

    # Por id cuando existe (identifica a la persona sin ambiguedad); solo
    # cae al nombre para los eventos que no traen user_id (login_failed de
    # un correo que no existe, por ejemplo). Contar por nombre para TODOS
    # los eventos fundia a dos personas distintas con el mismo nombre en
    # una sola "cuenta unica".
    identificador = func.coalesce(cast(AuditLog.user_id, String), AuditLog.user_name)
    usuarios_query = _scope(
        select(func.count(func.distinct(identificador))), tenant_id, only_global,
    ).where(identificador.is_not(None))
    usuarios_unicos = await db.scalar(usuarios_query) or 0

    acciones_query = _scope(
        select(AuditLog.action, func.count(AuditLog.id)), tenant_id, only_global,
    ).group_by(AuditLog.action).order_by(func.count(AuditLog.id).desc())
    filas_accion = (await db.execute(acciones_query)).all()
    por_accion = {accion: cuenta for accion, cuenta in filas_accion}

    return {
        "total": total,
        "eventos_hoy": eventos_hoy,
        "usuarios_unicos": usuarios_unicos,
        "accion_mas_frecuente": filas_accion[0][0] if filas_accion else None,
        "por_accion": por_accion,
    }


