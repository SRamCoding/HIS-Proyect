# backend/app/admin/notificaciones/service.py
import uuid
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.notificaciones.models import Notificacion

logger = logging.getLogger(__name__)

# Cuanto tiempo se conserva una notificacion YA LEIDA antes de poder
# purgarla. Las no leidas nunca se purgan, sin importar su antiguedad --
# nada que nadie haya visto todavia debe poder desaparecer solo.
RETENCION_LEIDAS = timedelta(days=90)


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


async def listar_notificaciones(db: AsyncSession, limit: int = 20, offset: int = 0) -> tuple[list[Notificacion], int]:
    """Antes solo aceptaba `limit`, sin `offset`: no habia forma de ver
    nada mas viejo que las ultimas `limit` notificaciones. Devuelve tambien
    el total real para poder mostrar "cargar mas" quedo o no."""
    total = await db.scalar(select(func.count()).select_from(Notificacion)) or 0
    result = await db.execute(
        select(Notificacion).order_by(Notificacion.created_at.desc()).limit(limit).offset(offset)
    )
    return result.scalars().all(), total


async def purgar_notificaciones_antiguas(retencion: timedelta = RETENCION_LEIDAS) -> int:
    """La tabla no tenia NINGUN mecanismo de purga -- crecia para siempre.
    Solo borra notificaciones YA LEIDAS y mas viejas que `retencion`; una
    no leida se conserva sin importar su antiguedad, aunque tenga años."""
    from app.core.database import AsyncSessionLocal

    limite = datetime.utcnow() - retencion
    async with AsyncSessionLocal() as db:
        resultado = await db.execute(
            delete(Notificacion).where(
                Notificacion.is_read.is_(True),
                Notificacion.created_at < limite,
            )
        )
        await db.commit()
        return resultado.rowcount or 0


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
