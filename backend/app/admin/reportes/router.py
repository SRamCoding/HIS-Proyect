# backend/app/admin/reportes/router.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.reportes.schemas import HospitalModuleReportItem, MonthlyReportResponse
from app.admin.reportes.service import get_hospitals_modules_report, get_monthly_report

router = APIRouter()


@router.get("/reportes/hospitales-modulos", response_model=list[HospitalModuleReportItem], summary="Reporte hospitales y módulos")
async def reporte_hospitales_modulos(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_hospitals_modules_report(db)


@router.get("/reportes/mensuales", response_model=MonthlyReportResponse, summary="Reporte mensual del sistema")
async def reporte_mensual(
    month: str,
    tenant_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    try:
        return await get_monthly_report(db, month, tenant_id)
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc