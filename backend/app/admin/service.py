import uuid
import bcrypt
import calendar
from collections import Counter
from datetime import datetime, timedelta
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
    active_users = await db.scalar(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_module_assignments = await db.scalar(
        select(func.count(TenantModule.id)).where(TenantModule.is_active == True)
    )

    now = datetime.utcnow()
    audit_since = now - timedelta(hours=24)
    audit_events_24h = await db.scalar(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= audit_since)
    )

    result = await db.execute(
        select(TenantModule.module_code, func.count(TenantModule.id))
        .where(TenantModule.is_active == True)
        .group_by(TenantModule.module_code)
        .order_by(func.count(TenantModule.id).desc())
    )
    modules_distribution = {row[0]: row[1] for row in result.fetchall()}

    # Se agrupan en Python para conservar el endpoint compatible con SQLite
    # durante pruebas y con PostgreSQL en producción.
    recent_tenants = (await db.execute(
        select(Tenant.created_at).where(Tenant.created_at >= now - timedelta(days=184))
    )).scalars().all()
    month_keys = []
    year, month = now.year, now.month
    for _ in range(6):
        month_keys.append((year, month))
        month = 12 if month == 1 else month - 1
        year = year - 1 if month == 12 else year
    month_keys.reverse()
    monthly_counts = Counter((item.year, item.month) for item in recent_tenants)
    hospitals_by_month = [
        {
            "label": datetime(year, month, 1).strftime("%b"),
            "value": monthly_counts[(year, month)],
        }
        for year, month in month_keys
    ]

    panel_rows = await db.execute(
        select(User.panel, func.count(User.id)).group_by(User.panel)
    )
    users_by_panel = {row[0]: row[1] for row in panel_rows.fetchall()}

    level_rows = await db.execute(
        select(Tenant.hospital_level, func.count(Tenant.id))
        .group_by(Tenant.hospital_level)
        .order_by(func.count(Tenant.id).desc())
    )
    hospitals_by_level = [
        {"code": row[0] or "Sin nivel", "count": row[1]}
        for row in level_rows.fetchall()
    ]

    module_count = func.count(TenantModule.id).label("module_count")
    top_rows = await db.execute(
        select(Tenant.id, Tenant.name, module_count)
        .outerjoin(TenantModule, (TenantModule.tenant_id == Tenant.id) & (TenantModule.is_active == True))
        .group_by(Tenant.id, Tenant.name)
        .order_by(module_count.desc(), Tenant.name)
        .limit(4)
    )
    top_hospitals_by_modules = [
        {"id": str(row[0]), "name": row[1], "modules": row[2]}
        for row in top_rows.fetchall()
    ]

    audit_logs = (await db.execute(
        select(AuditLog.created_at, AuditLog.action).where(AuditLog.created_at >= audit_since)
    )).all()
    # Agrupar en bloques de tres horas, igual que las ocho barras del dashboard.
    audit_hours = Counter((item[0].hour // 3) * 3 for item in audit_logs)
    audit_events_by_hour = [
        {"label": f"{hour:02d}:00", "value": audit_hours[hour]}
        for hour in range(0, 24, 3)
    ]
    audit_actions = dict(Counter(item[1] for item in audit_logs))

    return {
        "total_hospitals": total_hospitals or 0,
        "active_hospitals": active_hospitals or 0,
        "total_users": total_users or 0,
        "active_users": active_users or 0,
        "active_module_assignments": active_module_assignments or 0,
        "audit_events_24h": audit_events_24h or 0,
        "modules_distribution": modules_distribution,
        "hospitals_by_month": hospitals_by_month,
        "users_by_panel": users_by_panel,
        "hospitals_by_level": hospitals_by_level,
        "top_hospitals_by_modules": top_hospitals_by_modules,
        "audit_events_by_hour": audit_events_by_hour,
        "audit_actions": audit_actions,
    }


async def get_hospitals_registered_by_day(db: AsyncSession, month: str) -> dict:
    """Retorna una serie diaria completa para el mes ``YYYY-MM`` indicado."""
    try:
        start = datetime.strptime(month, "%Y-%m")
    except ValueError as exc:
        raise ValueError("El mes debe tener el formato YYYY-MM") from exc

    days_in_month = calendar.monthrange(start.year, start.month)[1]
    end = datetime(
        start.year + 1 if start.month == 12 else start.year,
        1 if start.month == 12 else start.month + 1,
        1,
    )
    registrations = (await db.execute(
        select(Tenant.created_at).where(
            Tenant.created_at >= start,
            Tenant.created_at < end,
        )
    )).scalars().all()
    totals_by_day = Counter(item.day for item in registrations)
    days = [
        {"label": str(day), "value": totals_by_day[day]}
        for day in range(1, days_in_month + 1)
    ]

    return {
        "month": month,
        "total": len(registrations),
        "days": days,
    }


# ─── Hospitales ───────────────────────────────────────────────────────────────

from sqlalchemy.orm import selectinload

async def get_all_hospitals(db: AsyncSession) -> list[Tenant]:
    result = await db.execute(
        select(Tenant)
        .options(selectinload(Tenant.modules))
        .order_by(Tenant.created_at.desc())
    )
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
