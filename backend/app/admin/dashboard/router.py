from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.dashboard.schemas import DashboardStats, SaludSistema
from app.admin.dashboard.service import (
    get_dashboard_stats,
    get_hospitals_registered_by_day,
    obtener_salud_sistema,
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats, summary="Estadísticas globales")
async def dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_dashboard_stats(db)


@router.get("/dashboard/salud", response_model=SaludSistema, summary="Salud de Redis y Celery")
async def salud(
    current_user: dict = Depends(get_admin_user),
):
    return await obtener_salud_sistema()


@router.get("/dashboard/hospitales-por-dia", summary="Hospitales registrados por día")
async def hospitales_por_dia(
    month: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    try:
        return await get_hospitals_registered_by_day(db, month)
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc
