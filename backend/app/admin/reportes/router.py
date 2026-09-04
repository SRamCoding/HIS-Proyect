from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.reportes.schemas import HospitalModuleReportItem
from app.admin.reportes.service import get_hospitals_modules_report

router = APIRouter()


@router.get("/reportes/hospitales-modulos", response_model=list[HospitalModuleReportItem], summary="Reporte hospitales y módulos")
async def reporte_hospitales_modulos(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_hospitals_modules_report(db)
