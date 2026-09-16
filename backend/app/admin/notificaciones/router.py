# backend/app/admin/notificaciones/router.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.notificaciones.schemas import NotificacionResponse
from app.admin.notificaciones.service import (
    listar_notificaciones, contar_no_leidas, marcar_leida, marcar_todas_leidas,
)

router = APIRouter()


@router.get("/notificaciones", response_model=list[NotificacionResponse], summary="Listar notificaciones")
async def listar(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await listar_notificaciones(db, limit)


@router.get("/notificaciones/no-leidas", summary="Cantidad de notificaciones sin leer")
async def no_leidas(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return {"count": await contar_no_leidas(db)}


@router.patch("/notificaciones/{notif_id}/leer", summary="Marcar una notificación como leída")
async def leer(
    notif_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    notif = await marcar_leida(db, notif_id)
    if not notif:
        raise HTTPException(404, "Notificación no encontrada")
    return {"ok": True}


@router.patch("/notificaciones/leer-todas", summary="Marcar todas como leídas")
async def leer_todas(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    await marcar_todas_leidas(db)
    return {"ok": True}
