# backend/app/admin/notificaciones/router.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.notificaciones.schemas import NotificacionResponse
from app.admin.notificaciones.service import (
    listar_notificaciones, contar_no_leidas, marcar_leida, marcar_todas_leidas,
)

router = APIRouter()

# Marcar notificaciones como leidas se deja con get_admin_user (no
# get_admin_user_escritura) a proposito: es un ajuste de lectura personal
# de la bandeja, no una operacion sobre el sistema (no crea/modifica/borra
# ningun hospital, usuario, modulo, etc.) -- bloquearlo tambien a una
# cuenta de solo lectura (ej. un Auditor monitoreando notificaciones)
# seria una restriccion sin beneficio real de seguridad.


@router.get("/notificaciones", summary="Listar notificaciones")
async def listar(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    items, total = await listar_notificaciones(db, limit, offset)
    return {"items": [NotificacionResponse.model_validate(i) for i in items], "total": total}


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
