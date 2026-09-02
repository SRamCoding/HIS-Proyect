import uuid
import bcrypt
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from redis.asyncio import Redis

from app.tenants.models import Tenant, TenantModule, Module
from app.auth.models import User
from app.admin.models import SystemRole, HospitalLevel, ModuleDependency, AuditLog
from app.tenants.service import update_tenant_modules


# ─── Dashboard ────────────────────────────────────────────────────────────────

async def get_dashboard_stats(db: AsyncSession) -> dict:
    total_hospitals = await db.scalar(select(func.count(Tenant.id)))
    active_hospitals = await db.scalar(
        select(func.count(Tenant.id)).where(Tenant.is_active == True)
    )
    total_users = await db.scalar(select(func.count(User.id)))

    result = await db.execute(
        select(TenantModule.module_code, func.count(TenantModule.id))
        .where(TenantModule.is_active == True)
        .group_by(TenantModule.module_code)
        .order_by(func.count(TenantModule.id).desc())
    )
    modules_distribution = {row[0]: row[1] for row in result.fetchall()}

    return {
        "total_hospitals": total_hospitals or 0,
        "active_hospitals": active_hospitals or 0,
        "total_users": total_users or 0,
        "modules_distribution": modules_distribution,
    }


# ─── Hospitales ───────────────────────────────────────────────────────────────

async def get_all_hospitals(db: AsyncSession) -> list[Tenant]:
    result = await db.execute(select(Tenant).order_by(Tenant.created_at.desc()))
    return result.scalars().all()


async def toggle_tenant_active(
    db: AsyncSession, tenant_id: uuid.UUID, is_active: bool
) -> Tenant | None:
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        return None
    tenant.is_active = is_active
    await db.commit()
    await db.refresh(tenant)
    return tenant


# ─── Usuarios ─────────────────────────────────────────────────────────────────

async def get_all_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


async def get_users_by_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> list[User]:
    result = await db.execute(
        select(User).where(User.tenant_id == tenant_id).order_by(User.name)
    )
    return result.scalars().all()


async def create_user(db: AsyncSession, data) -> User:
    hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
    user = User(
        name=data.name,
        email=data.email,
        password=hashed,
        role=data.role,
        panel=data.panel,
        tenant_id=data.tenant_id,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ─── Niveles Hospitalarios ────────────────────────────────────────────────────

async def get_all_hospital_levels(db: AsyncSession) -> list[HospitalLevel]:
    result = await db.execute(
        select(HospitalLevel).order_by(HospitalLevel.sort_order)
    )
    return result.scalars().all()


async def create_hospital_level(db: AsyncSession, data) -> HospitalLevel:
    level = HospitalLevel(
        code=data.code,
        name=data.name,
        description=data.description,
        default_modules=data.default_modules,
        default_roles=data.default_roles,
        sort_order=data.sort_order,
    )
    db.add(level)
    await db.commit()
    await db.refresh(level)
    return level


# ─── Dependencias de Módulos ──────────────────────────────────────────────────

async def get_module_dependencies(db: AsyncSession) -> list[ModuleDependency]:
    result = await db.execute(
        select(ModuleDependency).order_by(ModuleDependency.module_code)
    )
    return result.scalars().all()


async def create_module_dependency(db: AsyncSession, data) -> ModuleDependency:
    dep = ModuleDependency(
        module_code=data.module_code,
        depends_on_code=data.depends_on_code,
        is_required=data.is_required,
    )
    db.add(dep)
    await db.commit()
    await db.refresh(dep)
    return dep


# ─── System Roles ─────────────────────────────────────────────────────────────

async def get_all_system_roles(db: AsyncSession) -> list[SystemRole]:
    result = await db.execute(
        select(SystemRole).order_by(SystemRole.panel, SystemRole.sort_order)
    )
    return result.scalars().all()


async def create_system_role(db: AsyncSession, data) -> SystemRole:
    role = SystemRole(
        name=data.name,
        label=data.label,
        panel=data.panel,
        required_module=data.required_module,
        allowed_modules=data.allowed_modules,
        sort_order=data.sort_order,
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


# ─── Auditoría ────────────────────────────────────────────────────────────────

async def get_audit_logs(
    db: AsyncSession,
    tenant_id: uuid.UUID | None = None,
    limit: int = 100,
) -> list[AuditLog]:
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if tenant_id:
        query = query.where(AuditLog.tenant_id == tenant_id)
    result = await db.execute(query)
    return result.scalars().all()


async def create_audit_log(
    db: AsyncSession,
    user_id: uuid.UUID | None,
    user_name: str | None,
    tenant_id: uuid.UUID | None,
    tenant_name: str | None,
    action: str,
    model: str | None = None,
    model_id: str | None = None,
    description: str | None = None,
    old_values: dict | None = None,
    new_values: dict | None = None,
    ip_address: str | None = None,
) -> None:
    log = AuditLog(
        user_id=user_id,
        user_name=user_name,
        tenant_id=tenant_id,
        tenant_name=tenant_name,
        action=action,
        model=model,
        model_id=model_id,
        description=description,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
    )
    db.add(log)
    await db.commit()


# ─── Reportes ─────────────────────────────────────────────────────────────────

async def get_hospitals_modules_report(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Tenant).where(Tenant.is_active == True).order_by(Tenant.name)
    )
    tenants = result.scalars().all()
    return [
        {
            "hospital_name": t.name,
            "domain": t.domain,
            "active_modules": t.active_module_codes,
            "total_modules": len(t.active_module_codes),
        }
        for t in tenants
    ]