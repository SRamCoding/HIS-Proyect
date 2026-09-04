import calendar
from collections import Counter
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.tenants.hospitales.models import Tenant, TenantModule
from app.auth.models import User
from app.admin.auditoria.models import AuditLog


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
