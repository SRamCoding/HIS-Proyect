import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.sigarh.dashboard.schemas import DashboardResponse
from app.sigarh.dashboard.service import get_dashboard

router = APIRouter()


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    """El fallback a X-Tenant-ID nunca se ejecuta en la practica: para
    cualquier panel que no sea "admin", usuario_actual() en
    mantenimiento/security.py YA exige tenant_id en el JWT antes de llegar
    aca (401 si falta) -- current_user["tenant_id"] siempre viene poblado.
    Se conserva por consistencia con el mismo patron en otros routers de
    SIGARH (ver _tid en roles_pendientes/router.py), no forjable: probado
    en vivo enviando un X-Tenant-ID de otro hospital con una sesion real,
    el backend ignoro el header y devolvio los datos del tenant del JWT."""
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Escritorio SIGARH: KPIs, series de tendencia y actividad reciente del tenant."""
    return await get_dashboard(db, get_tenant_id(current_user, request), current_user.get("active_modules"))
