from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.dependencies import get_admin_user
from app.tenants.schemas import TenantCreate, TenantResponse
from app.tenants.service import create_tenant, get_tenant_by_domain

router = APIRouter()


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def crear_hospital(
    data: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    """Registra un nuevo hospital en el sistema. Solo Admin ERP."""
    existing = await get_tenant_by_domain(db, data.domain)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un hospital con el dominio '{data.domain}'"
        )
    tenant = await create_tenant(db, data)
    return tenant


@router.get("/by-domain/{domain}", response_model=TenantResponse)
async def obtener_hospital_por_dominio(
    domain: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    """Obtiene un hospital por su dominio."""
    tenant = await get_tenant_by_domain(db, domain)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hospital no encontrado: {domain}"
        )
    return tenant