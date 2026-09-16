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
from app.tenants.hospitales.schemas import TenantCreate, TenantUpdate, TenantResponse
from app.tenants.hospitales.service import crear_tenant_rapido, get_tenant_by_domain, update_tenant_modules
from app.admin.hospitales.schemas import HospitalListItem, ModuleToggle, ActiveToggle
from app.admin.hospitales.service import get_all_hospitals, toggle_tenant_active
from app.admin.notificaciones.service import crear_notificacion

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
            provisioning_status=t.provisioning_status, provisioning_error=t.provisioning_error,
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
    tenant = await crear_tenant_rapido(db, data)

    from workers.tasks import aprovisionar_hospital
    aprovisionar_hospital.delay(
        tenant_id=str(tenant.id),
        database_name=tenant.database_name,
        hospital_level=data.hospital_level,
        active_modules=data.active_modules,
        admin_name=data.admin_name, admin_email=data.admin_email, admin_password=data.admin_password,
        sigarh_name=data.sigarh_name, sigarh_email=data.sigarh_email, sigarh_password=data.sigarh_password,
    )
    return tenant


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
        "provisioning_status": tenant.provisioning_status,
        "provisioning_error": tenant.provisioning_error,
    }


@router.patch("/hospitales/{tenant_id}", summary="Actualizar hospital")
async def actualizar_hospital(
    tenant_id: uuid.UUID,
    data: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(404, detail="Hospital no encontrado")
    # TenantUpdate es la lista blanca de campos editables (hereda de TenantBase);
    # antes se aceptaba un dict libre y se aplicaba con setattr a cualquier
    # atributo del modelo, incluidos campos internos como schema_name. is_active
    # SI esta en la lista blanca (el formulario de edicion lo envia junto con el
    # resto de la identidad), pero domain/active_modules tienen su propio flujo.
    cambios = data.model_dump(exclude_unset=True, exclude={"active_modules", "domain"})
    for field, value in cambios.items():
        setattr(tenant, field, value)
    await db.commit()
    return {"ok": True}


@router.patch("/hospitales/{tenant_id}/toggle", summary="Activar/desactivar hospital")
async def toggle_hospital(
    tenant_id: uuid.UUID,
    data: ActiveToggle,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    tenant = await toggle_tenant_active(db, tenant_id, data.is_active)
    if not tenant:
        raise HTTPException(404, detail="Hospital no encontrado")
    await crear_notificacion(
        f"Hospital {'activado' if data.is_active else 'desactivado'}: {tenant.name}",
        nivel="alerta" if not data.is_active else "info",
        link=f"/admin/hospitales/{tenant.id}",
    )
    return {"ok": True, "is_active": tenant.is_active}


@router.put("/hospitales/modulos", summary="Actualizar módulos de un hospital")
async def actualizar_modulos(
    data: ModuleToggle,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: dict = Depends(get_admin_user),
):
    tenant = await db.get(Tenant, data.tenant_id)
    await update_tenant_modules(db, redis, data.tenant_id, data.module_codes)
    await crear_notificacion(
        f"Módulos actualizados: {tenant.name if tenant else data.tenant_id}",
        f"{len(data.module_codes)} módulos activos",
        nivel="info",
        link=f"/admin/hospitales/{data.tenant_id}",
    )
    return {"ok": True, "message": "Módulos actualizados correctamente"}
