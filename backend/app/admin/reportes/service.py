# backend/app/admin/reportes/service.py
import uuid
from collections import Counter
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.tenants.hospitales.models import Tenant
from app.tenants.modulos.service import get_all_modules
from app.auth.models import User
from app.hospital.admision.models import Patient


async def get_hospitals_modules_report(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Tenant)
        .options(selectinload(Tenant.modules))
        .where(Tenant.is_active == True)
        .order_by(Tenant.name)
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


async def get_monthly_report(
    db: AsyncSession,
    month: str,
    tenant_id: uuid.UUID | None = None,
) -> dict:
    try:
        start = datetime.strptime(month, "%Y-%m")
    except ValueError as exc:
        raise ValueError("El mes debe tener el formato YYYY-MM") from exc

    end = datetime(
        start.year + 1 if start.month == 12 else start.year,
        1 if start.month == 12 else start.month + 1,
        1,
    )

    # Hospitales activos (con sus modulos precargados)
    tenants_query = (
        select(Tenant)
        .options(selectinload(Tenant.modules))
        .where(Tenant.is_active == True)
        .order_by(Tenant.name)
    )
    if tenant_id:
        tenants_query = tenants_query.where(Tenant.id == tenant_id)
    tenants = (await db.execute(tenants_query)).scalars().all()

    # Pacientes nuevos del periodo, agrupados por hospital
    patients_rows = await db.execute(
        select(Patient.tenant_id, func.count(Patient.id))
        .where(Patient.created_at >= start, Patient.created_at < end)
        .group_by(Patient.tenant_id)
    )
    patients_by_tenant = {row[0]: row[1] for row in patients_rows.fetchall()}

    # Usuarios por hospital (total actual, no solo nuevos)
    users_rows = await db.execute(
        select(User.tenant_id, func.count(User.id))
        .where(User.tenant_id.isnot(None))
        .group_by(User.tenant_id)
    )
    users_by_tenant = {row[0]: row[1] for row in users_rows.fetchall()}

    hospitales_summary = []
    module_counter: Counter = Counter()
    for t in tenants:
        active_codes = t.active_module_codes
        for code in active_codes:
            module_counter[code] += 1
        hospitales_summary.append({
            "id": t.id,
            "hospital_name": t.name,
            "domain": t.domain,
            "is_active": t.is_active,
            "pacientes_nuevos": patients_by_tenant.get(t.id, 0),
            "usuarios_count": users_by_tenant.get(t.id, 0),
            "modules_count": len(active_codes),
            "created_at": t.created_at,
        })

    pacientes_nuevos_total = sum(h["pacientes_nuevos"] for h in hospitales_summary)

    # Cobertura de modulos (top 10 mas adoptados)
    modules_catalog = await get_all_modules(db)
    name_by_code = {m.code: m.name for m in modules_catalog}
    total_para_pct = len(hospitales_summary) or 1
    coverage = [
        {
            "code": code,
            "name": name_by_code.get(code, code),
            "hospitals_with_module": count,
            "total_hospitals": total_para_pct,
            "percentage": round(count / total_para_pct * 100, 1),
        }
        for code, count in module_counter.items()
    ]
    coverage.sort(key=lambda x: x["hospitals_with_module"], reverse=True)
    coverage = coverage[:10]

    # Hospitales registrados en el periodo (independiente de is_active)
    registrados_rows = await db.execute(
        select(Tenant)
        .where(Tenant.created_at >= start, Tenant.created_at < end)
        .order_by(Tenant.created_at.desc())
    )
    registrados = registrados_rows.scalars().all()
    hospitales_registrados_periodo = [
        {"name": t.name, "domain": t.domain, "created_at": t.created_at}
        for t in registrados
    ]

    # Usuarios centrales (sin tenant, ej. super-admins) registrados en el periodo
    usuarios_centrales = await db.scalar(
        select(func.count(User.id)).where(
            User.tenant_id.is_(None),
            User.created_at >= start,
            User.created_at < end,
        )
    )

    return {
        "month": month,
        "total_hospitales_activos": len(hospitales_summary),
        "pacientes_nuevos_total": pacientes_nuevos_total,
        "modules_coverage": coverage,
        "hospitales": hospitales_summary,
        "hospitales_registrados_periodo": hospitales_registrados_periodo,
        "usuarios_centrales_registrados": usuarios_centrales or 0,
    }
