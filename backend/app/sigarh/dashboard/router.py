import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.sigarh.dashboard.schemas import DashboardResponse
from app.sigarh.dashboard.service import get_dashboard

router = APIRouter()


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
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
    return await get_dashboard(db, get_tenant_id(current_user, request))
