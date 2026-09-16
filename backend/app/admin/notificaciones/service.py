# backend/app/admin/notificaciones/service.py
import uuid
import logging
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.notificaciones.models import Notificacion

logger = logging.getLogger(__name__)


async def crear_notificacion(titulo: str, cuerpo: str | None = None, nivel: str = "info", link: str | None = None) -> None:
    """Se llama desde cualquier flujo de negocio (crear hospital, crear admin,
    etc.), con su propia sesion central -- nunca debe tumbar la operacion
    real si falla, asi que cualquier error solo se registra."""
    try:
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            db.add(Notificacion(titulo=titulo, cuerpo=cuerpo, nivel=nivel, link=link))
            await db.commit()
    except Exception:
        logger.exception("No se pudo crear la notificacion: %s", titulo)


async def listar_notificaciones(db: AsyncSession, limit: int = 20) -> list[Notificacion]:
    result = await db.execute(
        select(Notificacion).order_by(Notificacion.created_at.desc()).limit(limit)
    )
    return result.scalars().all()


async def contar_no_leidas(db: AsyncSession) -> int:
    return await db.scalar(
        select(func.count()).select_from(Notificacion).where(Notificacion.is_read.is_(False))
    ) or 0


async def marcar_leida(db: AsyncSession, notif_id: uuid.UUID) -> Notificacion | None:
    notif = await db.get(Notificacion, notif_id)
    if not notif:
        return None
    notif.is_read = True
    await db.commit()
    return notif


async def marcar_todas_leidas(db: AsyncSession) -> None:
    await db.execute(
        update(Notificacion).where(Notificacion.is_read.is_(False)).values(is_read=True)
    )
    await db.commit()
