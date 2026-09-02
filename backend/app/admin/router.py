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