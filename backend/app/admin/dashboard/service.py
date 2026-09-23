import asyncio
import calendar
import logging
from collections import Counter
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from app.tenants.hospitales.models import Tenant, TenantModule
from app.auth.models import User
from app.sigarh.mantenimiento.models import UsuarioSigarh
from app.admin.auditoria.models import AuditLog
from app.core.tenant_db import get_tenant_sessionmaker
from app.core.concurrency import gather_limitado

logger = logging.getLogger(__name__)

# Misma zona fija que auditoria/service.py y reportes/service.py (Peru no
# tiene horario de verano). "Hospitales por mes" y "Actividad por hora" se
# mostraban agrupados por el dia/hora en UTC de created_at -- un evento de
# las 8pm en Lima ya es la 1am UTC del dia siguiente, asi que aparecia una
# hora antes de la real y, cerca de fin de mes, hasta en el mes equivocado.
_ZONA_LIMA = timezone(timedelta(hours=-5))


def _a_lima(momento_utc_naive: datetime) -> datetime:
    return momento_utc_naive.replace(tzinfo=timezone.utc).astimezone(_ZONA_LIMA)


async def _usuarios_hospital(tenant: Tenant) -> tuple[dict, int, int, bool]:
    """(por_panel, total_sigarh, activos_sigarh, disponible) para UN hospital
    con base fisica propia. `por_panel` es {panel: (total, activos)} sobre
    la tabla User de esa base -- User.panel admite "app" Y "portal" (ver
    auth/models.py), no solo "app". Antes esta funcion sumaba TODA la tabla
    User como si fuera panel="app", así que una cuenta "portal" se contaba
    dos veces mal: inflaba el total de "app" y el desglose users_by_panel
    nunca mostraba "portal" aunque existiera. Las cuentas SIGARH de estos
    hospitales viven solo en su propia base (ver create_tenant), no en la
    central -- sin esto, total_users/active_users del dashboard solo
    contaban cuentas centrales (admins y hospitales sin base propia)."""
    if not tenant.database_name:
        return {}, 0, 0, True
    try:
        TenantSession = get_tenant_sessionmaker(tenant.database_name)
        async with TenantSession() as tdb:
            panel_rows = (await tdb.execute(
                select(
                    User.panel,
                    func.count(User.id),
                    func.sum(case((User.is_active.is_(True), 1), else_=0)),
                ).group_by(User.panel)
            )).all()
            por_panel = {panel: (total, activos or 0) for panel, total, activos in panel_rows}
            total_sigarh = await tdb.scalar(select(func.count(UsuarioSigarh.id))) or 0
            activos_sigarh = await tdb.scalar(
                select(func.count(UsuarioSigarh.id)).where(UsuarioSigarh.is_active == True)
            ) or 0
            return por_panel, total_sigarh, activos_sigarh, True
    except Exception:
        logger.exception("No se pudo consultar usuarios del hospital %s para el dashboard", tenant.name)
        return {}, 0, 0, False


async def _usuarios_recientes_hospital(tenant: Tenant, limite: int = 6) -> list[dict]:
    """Ultimas cuentas (panel app + SIGARH) creadas en la base fisica de UN
    hospital, para el widget "Usuarios recientes" del dashboard -- igual que
    total_users, estas cuentas no viven en la BD central."""
    if not tenant.database_name:
        return []
    try:
        TenantSession = get_tenant_sessionmaker(tenant.database_name)
        async with TenantSession() as tdb:
            usuarios = (await tdb.scalars(
                select(User).order_by(User.created_at.desc()).limit(limite)
            )).all()
            sigarh = (await tdb.scalars(
                select(UsuarioSigarh).order_by(UsuarioSigarh.created_at.desc()).limit(limite)
            )).all()
            return [
                {"name": u.name, "email": u.email, "panel": u.panel,
                 "tenant_name": tenant.name, "created_at": u.created_at}
                for u in usuarios
            ] + [
                {"name": u.username, "email": u.email, "panel": "sigarh",
                 "tenant_name": tenant.name, "created_at": u.created_at}
                for u in sigarh
            ]
    except Exception:
        logger.exception("No se pudo consultar usuarios recientes del hospital %s", tenant.name)
        return []


async def get_dashboard_stats(db: AsyncSession) -> dict:
    total_hospitals = await db.scalar(select(func.count(Tenant.id)))
    active_hospitals = await db.scalar(
        select(func.count(Tenant.id)).where(Tenant.is_active == True)
    )
    total_users_centrales = await db.scalar(select(func.count(User.id))) or 0
    active_users_centrales = await db.scalar(
        select(func.count(User.id)).where(User.is_active == True)
    ) or 0

    # Los hospitales con base fisica propia guardan ahi sus cuentas (panel
    # "app" o "portal") y SIGARH (ver create_tenant); hay que sumarlas aparte,
    # igual que ya hace el reporte mensual (reportes/service.py::_stats_hospital).
    # Sin filtrar por Tenant.is_active: un hospital desactivado en el panel
    # admin no deja de tener una base fisica con cuentas reales -- filtrar
    # por activos aca hacia que "Cuentas Totales" no fuera realmente el total
    # del sistema, solo el de los hospitales actualmente activos.
    tenants_con_bd = (await db.scalars(
        select(Tenant).where(Tenant.database_name.is_not(None))
    )).all()
    resultados_hospitales = await gather_limitado([_usuarios_hospital(t) for t in tenants_con_bd])
    total_sigarh_hosp = sum(r[1] for r in resultados_hospitales)
    activos_sigarh_hosp = sum(r[2] for r in resultados_hospitales)
    hospitales_no_disponibles = sum(1 for r in resultados_hospitales if not r[3])

    panel_hosp_totales: Counter = Counter()
    panel_hosp_activos: Counter = Counter()
    for por_panel, _, _, _ in resultados_hospitales:
        for panel, (total, activos) in por_panel.items():
            panel_hosp_totales[panel] += total
            panel_hosp_activos[panel] += activos
    total_hosp = sum(panel_hosp_totales.values())
    activos_hosp = sum(panel_hosp_activos.values())

    total_users = total_users_centrales + total_hosp + total_sigarh_hosp
    active_users = active_users_centrales + activos_hosp + activos_sigarh_hosp

    active_module_assignments = await db.scalar(
        select(func.count(TenantModule.id)).where(TenantModule.is_active == True)
    )

    # Salud del sistema: hospitales atascados en aprovisionamiento y eventos
    # de auditoria que no se pudieron escribir (ver auditoria/router.py::
    # auditoria_fallback_estado). El dashboard antes no avisaba de esto -- un
    # admin solo se enteraba entrando a Hospitales o a Auditoria por su cuenta.
    hospitales_con_error = await db.scalar(
        select(func.count(Tenant.id)).where(Tenant.provisioning_status == "error")
    ) or 0
    hospitales_pendientes = await db.scalar(
        select(func.count(Tenant.id)).where(Tenant.provisioning_status == "pendiente")
    ) or 0
    from app.admin.auditoria.models import AuditLogFallback
    auditoria_fallback_pendientes = await db.scalar(
        select(func.count()).select_from(AuditLogFallback)
    ) or 0

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
    ahora_lima = _a_lima(now)
    month_keys = []
    year, month = ahora_lima.year, ahora_lima.month
    for _ in range(6):
        month_keys.append((year, month))
        month = 12 if month == 1 else month - 1
        year = year - 1 if month == 12 else year
    month_keys.reverse()
    monthly_counts = Counter((_a_lima(item).year, _a_lima(item).month) for item in recent_tenants)
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
    for panel, total in panel_hosp_totales.items():
        users_by_panel[panel] = users_by_panel.get(panel, 0) + total
    users_by_panel["sigarh"] = users_by_panel.get("sigarh", 0) + total_sigarh_hosp

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
    audit_hours = Counter((_a_lima(item[0]).hour // 3) * 3 for item in audit_logs)
    audit_events_by_hour = [
        {"label": f"{hour:02d}:00", "value": audit_hours[hour]}
        for hour in range(0, 24, 3)
    ]
    audit_actions = dict(Counter(item[1] for item in audit_logs))

    # Usuarios recientes: mezcla cuentas centrales (con su hospital, si tiene)
    # y las ultimas de cada hospital con base fisica propia, ordenadas por
    # fecha real de creacion -- no solo "ultimos 5 de la central" como si
    # fuera todo el sistema.
    central_recientes_rows = (await db.execute(
        select(User, Tenant.name.label("tenant_name"))
        .outerjoin(Tenant, User.tenant_id == Tenant.id)
        .where(User.is_superadmin.is_(False))
        .order_by(User.created_at.desc())
        .limit(6)
    )).all()
    usuarios_recientes = [
        {"name": u.name, "email": u.email, "panel": u.panel,
         "tenant_name": tenant_name or "Central", "created_at": u.created_at}
        for u, tenant_name in central_recientes_rows
    ]
    recientes_por_hospital = await gather_limitado([_usuarios_recientes_hospital(t) for t in tenants_con_bd])
    for lista in recientes_por_hospital:
        usuarios_recientes.extend(lista)
    usuarios_recientes.sort(key=lambda u: u["created_at"], reverse=True)
    usuarios_recientes = [
        {**u, "created_at": u["created_at"].isoformat()}
        for u in usuarios_recientes[:6]
    ]

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
        # Cobertura del conteo de usuarios: cuantos hospitales con base fisica
        # propia se pudieron consultar. Si uno no responde, total_users/
        # active_users igual reflejan el resto -- pero es_parcial avisa que
        # la cifra no es exacta, en vez de mostrar un numero completo falso.
        "usuarios_hospitales_consultados": len(tenants_con_bd) - hospitales_no_disponibles,
        "usuarios_hospitales_totales": len(tenants_con_bd),
        "usuarios_es_parcial": hospitales_no_disponibles > 0,
        "actualizado_en": now.isoformat(),
        "hospitales_con_error": hospitales_con_error,
        "hospitales_pendientes": hospitales_pendientes,
        "auditoria_fallback_pendientes": auditoria_fallback_pendientes,
        "usuarios_recientes": usuarios_recientes,
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


async def _verificar_redis() -> bool:
    from app.core.redis import redis_client
    try:
        return bool(await asyncio.wait_for(redis_client.ping(), timeout=2))
    except Exception:
        logger.exception("Redis no respondio al chequeo de salud del dashboard")
        return False


async def _verificar_celery() -> tuple[bool, int]:
    """control.ping() es sincrono/bloqueante (usa kombu por debajo) -- se
    corre en un thread aparte para no trabar el event loop mientras espera
    la respuesta de los workers."""
    from workers.celery_app import celery_app
    try:
        respuestas = await asyncio.wait_for(
            asyncio.to_thread(celery_app.control.ping, timeout=1.5),
            timeout=2.5,
        )
        return len(respuestas) > 0, len(respuestas)
    except Exception:
        logger.exception("Celery no respondio al chequeo de salud del dashboard")
        return False, 0


async def obtener_salud_sistema() -> dict:
    """Chequeo real de Redis y de los workers de Celery, con timeout corto
    para cada uno -- si alguno no responde a tiempo se reporta como caido
    en vez de colgar la carga del dashboard (mismo criterio que
    usuarios_es_parcial: mejor mostrar 'no se pudo verificar' que bloquear
    toda la pagina)."""
    redis_ok, (celery_ok, workers_activos) = await asyncio.gather(
        _verificar_redis(), _verificar_celery()
    )
    return {
        "redis_ok": redis_ok,
        "celery_ok": celery_ok,
        "celery_workers_activos": workers_activos,
        "verificado_en": datetime.now(timezone.utc).isoformat(),
    }
