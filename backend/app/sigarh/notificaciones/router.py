# backend/app/sigarh/notificaciones/router.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.sigarh.notificaciones.schemas import NotificacionSigarhResponse
from app.sigarh.notificaciones.service import (
    listar_notificaciones, contar_no_leidas, marcar_leida, marcar_todas_leidas,
)

router = APIRouter()


@router.get("/notificaciones", summary="Listar notificaciones SIGARH")
async def listar(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    items, total = await listar_notificaciones(db, limit, offset)
    return {"items": [NotificacionSigarhResponse.model_validate(i) for i in items], "total": total}


@router.get("/notificaciones/no-leidas", summary="Cantidad de notificaciones sin leer")
async def no_leidas(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return {"count": await contar_no_leidas(db)}


@router.patch("/notificaciones/{notif_id}/leer", summary="Marcar una notificación como leída")
async def leer(
    notif_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    notif = await marcar_leida(db, notif_id)
    if not notif:
        raise HTTPException(404, "Notificación no encontrada")
    return {"ok": True}


@router.patch("/notificaciones/leer-todas", summary="Marcar todas como leídas")
async def leer_todas(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    await marcar_todas_leidas(db)
    return {"ok": True}
