import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.dependencies import get_admin_user
from app.tenants.schemas import TenantCreate, TenantResponse
from app.tenants.service import create_tenant, get_tenant_by_domain, update_tenant_modules
from app.admin.schemas import (
    DashboardStats, HospitalListItem, ModuleToggle,
    SystemRoleCreate, SystemRoleResponse,
    HospitalLevelCreate, HospitalLevelResponse,
    ModuleDependencyCreate, ModuleDependencyResponse,
    UserListItem, UserCreate,
    AuditLogResponse, HospitalModuleReportItem,
)
from app.admin.service import (
    get_dashboard_stats, get_all_hospitals, toggle_tenant_active,
    get_hospitals_registered_by_day,
    get_all_users, get_users_by_tenant, create_user,
    get_all_hospital_levels, create_hospital_level,
    get_module_dependencies, create_module_dependency,
    get_all_system_roles, create_system_role,
    get_audit_logs, get_hospitals_modules_report,
)

router = APIRouter()


# ─── Dashboard ────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardStats, summary="Estadísticas globales")
async def dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_dashboard_stats(db)


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


# ─── Hospitales ───────────────────────────────────────────────────────────────

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


# ─── Usuarios ─────────────────────────────────────────────────────────────────

@router.get("/usuarios", response_model=list[UserListItem], summary="Listar todos los usuarios")
async def listar_usuarios(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_all_users(db)


@router.get("/usuarios/hospital/{tenant_id}", response_model=list[UserListItem], summary="Usuarios por hospital")
async def usuarios_por_hospital(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_users_by_tenant(db, tenant_id)


@router.post("/usuarios", response_model=UserListItem, status_code=201, summary="Crear usuario")
async def crear_usuario(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await create_user(db, data)


# ─── Niveles Hospitalarios ────────────────────────────────────────────────────

@router.get("/niveles-hospitalarios", response_model=list[HospitalLevelResponse], summary="Niveles MINSA")
async def listar_niveles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_all_hospital_levels(db)


@router.post("/niveles-hospitalarios", response_model=HospitalLevelResponse, status_code=201)
async def crear_nivel(
    data: HospitalLevelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await create_hospital_level(db, data)


# ─── Dependencias de Módulos ──────────────────────────────────────────────────

@router.get("/modulos/dependencias", response_model=list[ModuleDependencyResponse])
async def listar_dependencias(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_module_dependencies(db)


@router.post("/modulos/dependencias", response_model=ModuleDependencyResponse, status_code=201)
async def crear_dependencia(
    data: ModuleDependencyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await create_module_dependency(db, data)


# ─── System Roles ─────────────────────────────────────────────────────────────

@router.get("/roles", response_model=list[SystemRoleResponse], summary="Listar roles del sistema")
async def listar_roles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_all_system_roles(db)


@router.post("/roles", response_model=SystemRoleResponse, status_code=201)
async def crear_rol(
    data: SystemRoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await create_system_role(db, data)


# ─── Auditoría ────────────────────────────────────────────────────────────────

@router.get("/auditoria", response_model=list[AuditLogResponse], summary="Auditoría del ERP")
async def auditoria_erp(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_audit_logs(db, limit=limit)


@router.get("/auditoria/hospital/{tenant_id}", response_model=list[AuditLogResponse], summary="Auditoría por hospital")
async def auditoria_hospital(
    tenant_id: uuid.UUID,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_audit_logs(db, tenant_id=tenant_id, limit=limit)


# ─── Reportes ─────────────────────────────────────────────────────────────────

@router.get("/reportes/hospitales-modulos", response_model=list[HospitalModuleReportItem], summary="Reporte hospitales y módulos")
async def reporte_hospitales_modulos(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_hospitals_modules_report(db)

# ─── Niveles — módulos por defecto ────────────────────────────────────────────

@router.get("/niveles-hospitalarios/{code}/modulos", summary="Módulos por defecto de un nivel")
async def modulos_por_nivel(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    """
    Dado un código de nivel (II-2, III-1, etc.), retorna los módulos
    que se activarán automáticamente — equivalente al wizard de Laravel.
    """
    from sqlalchemy import select
    from app.admin.models import HospitalLevel
    result = await db.execute(
        select(HospitalLevel).where(HospitalLevel.code == code)
    )
    level = result.scalar_one_or_none()
    if not level:
        raise HTTPException(404, detail=f"Nivel '{code}' no encontrado")

    return {
        "code": level.code,
        "name": level.name,
        "color": level.color,
        "default_modules": level.default_modules or {"app": [], "sigarh": []},
    }

@router.get("/modulos/catalogo", summary="Catalogo de modulos")
async def catalogo_modulos(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    from sqlalchemy import select
    from app.tenants.models import Module
    result = await db.execute(select(Module).order_by(Module.category, Module.name))
    return [
        {"id": str(m.id), "code": m.code, "name": m.name, "category": m.category, "is_active": m.is_active}
        for m in result.scalars().all()
    ]

@router.get("/usuarios/con-hospital", summary="Usuarios con datos de hospital")
async def usuarios_con_hospital(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    from sqlalchemy import select
    from app.auth.models import User
    from app.tenants.models import Tenant

    result = await db.execute(
        select(User, Tenant.name.label("tenant_name"))
        .outerjoin(Tenant, User.tenant_id == Tenant.id)
        .where(User.email != "admin@erp.local")  # excluir super admin
        .order_by(User.created_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": str(u.id),
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "panel": u.panel,
            "is_active": u.is_active,
            "tenant_name": tenant_name or "—",
            "tenant_id": str(u.tenant_id) if u.tenant_id else None,
            "created_at": u.created_at.strftime("%d/%m/%Y"),
        }
        for u, tenant_name in rows
    ]

@router.get("/hospitales/{tenant_id}", summary="Obtener hospital por ID")
async def obtener_hospital(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.tenants.models import Tenant

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
    from sqlalchemy import select
    from app.tenants.models import Tenant

    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(404, detail="Hospital no encontrado")
    for field, value in data.items():
        if hasattr(tenant, field):
            setattr(tenant, field, value)
    await db.commit()
    return {"ok": True}

@router.get("/niveles-hospitalarios/{nivel_id}", summary="Obtener nivel por ID")
async def obtener_nivel(
    nivel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    from sqlalchemy import select
    from app.admin.models import HospitalLevel
    result = await db.execute(select(HospitalLevel).where(HospitalLevel.id == nivel_id))
    nivel = result.scalar_one_or_none()
    if not nivel:
        raise HTTPException(404, detail="Nivel no encontrado")
    return {
        "id": str(nivel.id),
        "code": nivel.code,
        "name": nivel.name,
        "description": nivel.description,
        "color": nivel.color,
        "sort_order": nivel.sort_order,
        "is_active": nivel.is_active,
        "default_modules": nivel.default_modules or {"app": [], "sigarh": []},
    }


@router.patch("/niveles-hospitalarios/{nivel_id}", summary="Actualizar nivel")
async def actualizar_nivel(
    nivel_id: uuid.UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    from sqlalchemy import select
    from app.admin.models import HospitalLevel
    result = await db.execute(select(HospitalLevel).where(HospitalLevel.id == nivel_id))
    nivel = result.scalar_one_or_none()
    if not nivel:
        raise HTTPException(404, detail="Nivel no encontrado")
    for field, value in data.items():
        if hasattr(nivel, field):
            setattr(nivel, field, value)
    await db.commit()
    return {"ok": True}
