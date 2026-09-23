# backend/app/sigarh/notificaciones/service.py
import uuid
import logging
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.sigarh.notificaciones.models import NotificacionSigarh

logger = logging.getLogger(__name__)


async def crear_notificacion_sigarh(
    db: AsyncSession, titulo: str, cuerpo: str | None = None, nivel: str = "info", link: str | None = None,
) -> None:
    """A diferencia de admin (crear_notificacion en app/admin/notificaciones/
    service.py), que abre su PROPIA sesion central nueva, aca se reusa la
    sesion `db` que ya trae el llamador -- esa sesion YA esta resuelta a la
    BD FISICA del hospital correcto (ver get_db()/_bd_fisica_sigarh), y no
    hay forma de reabrir "la sesion de este hospital" desde un sessionmaker
    fijo como si fuera la central. Solo se hace flush (no commit): el
    commit final lo hace get_db() al terminar la request, junto con el
    resto de la operacion -- una notificacion nunca debe forzar un commit
    parcial de un cambio de negocio que todavia no termino de validarse."""
    try:
        db.add(NotificacionSigarh(titulo=titulo, cuerpo=cuerpo, nivel=nivel, link=link))
        await db.flush()
    except Exception:
        logger.exception("No se pudo crear la notificacion SIGARH: %s", titulo)


async def listar_notificaciones(db: AsyncSession, limit: int = 20, offset: int = 0) -> tuple[list[NotificacionSigarh], int]:
    total = await db.scalar(select(func.count()).select_from(NotificacionSigarh)) or 0
    result = await db.execute(
        select(NotificacionSigarh).order_by(NotificacionSigarh.created_at.desc()).limit(limit).offset(offset)
    )
    return result.scalars().all(), total


async def contar_no_leidas(db: AsyncSession) -> int:
    return await db.scalar(
        select(func.count()).select_from(NotificacionSigarh).where(NotificacionSigarh.is_read.is_(False))
    ) or 0


async def marcar_leida(db: AsyncSession, notif_id: uuid.UUID) -> NotificacionSigarh | None:
    notif = await db.get(NotificacionSigarh, notif_id)
    if not notif:
        return None
    notif.is_read = True
    await db.commit()
    return notif


async def marcar_todas_leidas(db: AsyncSession) -> None:
    await db.execute(
        update(NotificacionSigarh).where(NotificacionSigarh.is_read.is_(False)).values(is_read=True)
    )
    await db.commit()
