import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.dependencies import get_admin_user
from app.tenants.hospitales.models import Tenant
from app.tenants.hospitales.schemas import TenantCreate, TenantResponse
from app.tenants.hospitales.service import create_tenant, get_tenant_by_domain, update_tenant_modules
from app.admin.hospitales.schemas import HospitalListItem, ModuleToggle
from app.admin.hospitales.service import get_all_hospitals, toggle_tenant_active

router = APIRouter()


@router.get("/hospitales", response_model=list[HospitalListItem], summary="Listar hospitales")
async def listar_hospitales(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    tenants = await get_all_hospitals(db)
    return [
        HospitalListItem(
            id=t.id, name=t.name, domain=t.domain,
            hospital_level=t.hospital_level, is_active=t.is_active,
            active_modules=t.active_module_codes, created_at=t.created_at,
        )
        for t in tenants
    ]


@router.post("/hospitales", response_model=TenantResponse, status_code=201, summary="Crear hospital")
async def crear_hospital(
    data: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    existing = await get_tenant_by_domain(db, data.domain)
    if existing:
        raise HTTPException(400, detail=f"Ya existe un hospital con el dominio '{data.domain}'")
    return await create_tenant(db, data)


@router.get("/hospitales/{tenant_id}", summary="Obtener hospital por ID")
async def obtener_hospital(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    result = await db.execute(
        select(Tenant)
        .options(selectinload(Tenant.modules))
        .where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(404, detail="Hospital no encontrado")
    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "domain": tenant.domain,
        "hospital_level": tenant.hospital_level,
        "ruc": tenant.ruc,
        "phone": tenant.phone,
        "email": tenant.email,
        "address": tenant.address,
        "mission": tenant.mission,
        "vision": tenant.vision,
        "values": tenant.values,
        "is_active": tenant.is_active,
        "active_modules": tenant.active_module_codes,
        "created_at": tenant.created_at.isoformat(),
    }


@router.patch("/hospitales/{tenant_id}", summary="Actualizar hospital")
async def actualizar_hospital(
    tenant_id: uuid.UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(404, detail="Hospital no encontrado")
    for field, value in data.items():
        if hasattr(tenant, field):
            setattr(tenant, field, value)
    await db.commit()
    return {"ok": True}


@router.patch("/hospitales/{tenant_id}/toggle", summary="Activar/desactivar hospital")
async def toggle_hospital(
    tenant_id: uuid.UUID,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    tenant = await toggle_tenant_active(db, tenant_id, is_active)
    if not tenant:
        raise HTTPException(404, detail="Hospital no encontrado")
    return {"ok": True, "is_active": tenant.is_active}


@router.put("/hospitales/modulos", summary="Actualizar módulos de un hospital")
async def actualizar_modulos(
    data: ModuleToggle,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: dict = Depends(get_admin_user),
):
    await update_tenant_modules(db, redis, data.tenant_id, data.module_codes)
    return {"ok": True, "message": "Módulos actualizados correctamente"}
