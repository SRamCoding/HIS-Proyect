import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.hospital.dashboard import service, medico_service
from app.hospital.dashboard.schemas import DashboardResponse, DashboardMedicoResponse

router = APIRouter()


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/resumen", response_model=DashboardResponse)
async def resumen(db=Depends(get_db), user=Depends(get_current_user)):
    """Escritorio hospitalario: KPIs y serie de 7 días de los módulos activos del usuario."""
    return await service.get_dashboard(db, tid(user), user.get("active_modules") or [])


@router.get("/medico", response_model=DashboardMedicoResponse)
async def medico(db=Depends(get_db), user=Depends(get_current_user)):
    """Escritorio personal del médico: solo sus propias citas y programación."""
    if user.get("role") != "medico" or not user.get("empleado_id"):
        raise HTTPException(403, detail="Este escritorio es exclusivo de cuentas médicas")
    return await medico_service.get_dashboard_medico(db, tid(user), uuid.UUID(user["empleado_id"]))
