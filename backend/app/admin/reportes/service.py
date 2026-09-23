# backend/app/admin/reportes/service.py
import logging
import uuid
from collections import Counter
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.tenants.hospitales.models import Tenant
from app.tenants.modulos.service import get_all_modules
from app.auth.models import User
from app.hospital.admision.models import Patient
from app.sigarh.mantenimiento.models import UsuarioSigarh
from app.core.tenant_db import get_tenant_sessionmaker
from app.core.concurrency import gather_limitado

logger = logging.getLogger(__name__)

# Mismo criterio que auditoria/service.py: "mes" debe representar el mes
# calendario de Lima, no el de UTC (created_at se guarda en UTC). Sin esto,
# un reporte de "enero" arrancaba/terminaba 5 horas antes de lo esperado
# por un admin en Peru, desalineado con el filtro de Auditoria.
_ZONA_LIMA = timezone(timedelta(hours=-5))


def _limite_mes_a_utc_naive(anio: int, mes: int) -> datetime:
    limite_lima = datetime(anio, mes, 1, tzinfo=_ZONA_LIMA)
    return limite_lima.astimezone(timezone.utc).replace(tzinfo=None)


async def _stats_hospital(tenant: Tenant, start: datetime, end: datetime) -> tuple[int, int, bool]:
    """(pacientes_nuevos, usuarios_count, disponible) para UN hospital,
    consultando su propia BD fisica -- ahi es donde realmente viven sus
    Patient/User, no en la central. usuarios_count suma User (panel app) y
    UsuarioSigarh: antes solo contaba User, subestimando el total real de
    cuentas de cada hospital (todo el personal SIGARH quedaba fuera)."""
    if not tenant.database_name:
        return 0, 0, True  # nunca se aprovisiono base propia: no hay nada que consultar, no es una falla
    try:
        TenantSession = get_tenant_sessionmaker(tenant.database_name)
        async with TenantSession() as tdb:
            pacientes_nuevos = await tdb.scalar(
                select(func.count(Patient.id)).where(
                    Patient.created_at >= start, Patient.created_at < end,
                )
            )
            usuarios_app = await tdb.scalar(select(func.count(User.id))) or 0
            usuarios_sigarh = await tdb.scalar(select(func.count(UsuarioSigarh.id))) or 0
            return pacientes_nuevos or 0, usuarios_app + usuarios_sigarh, True
    except Exception:
        logger.exception("No se pudo consultar la BD del hospital %s para el reporte mensual", tenant.name)
        return 0, 0, False


async def get_hospitals_modules_report(db: AsyncSession) -> list[dict]:
    """Antes devolvia active_modules como codigos crudos (sigarh_infraestructura_hosp,
    fact_config...) -- la pantalla los pintaba tal cual, un muro de ~38 chips
    con el codigo tecnico en vez del nombre visible del modulo. Ahora resuelve
    nombre/categoria desde el catalogo y separa el conteo App/SIGARH, para que
    el frontend pueda mostrar un resumen legible en vez de todos los codigos
    de una sola vez."""
    result = await db.execute(
        select(Tenant)
        .options(selectinload(Tenant.modules))
        .where(Tenant.is_active == True)
        .order_by(Tenant.name)
    )
    tenants = result.scalars().all()

    catalogo = await get_all_modules(db)
    info_por_codigo = {m.code: m for m in catalogo}

    reporte = []
    for t in tenants:
        codigos = t.active_module_codes
        modulos = [
            {
                "code": code,
                "name": info_por_codigo[code].name if code in info_por_codigo else code,
                "category": info_por_codigo[code].category if code in info_por_codigo else "app",
            }
            for code in codigos
        ]
        modulos.sort(key=lambda m: (m["category"], m["name"]))
        reporte.append({
            "hospital_name": t.name,
            "domain": t.domain,
            "hospital_level": t.hospital_level,
            "modules": modulos,
            "total_modules": len(modulos),
            "app_modules": sum(1 for m in modulos if m["category"] == "app"),
            "sigarh_modules": sum(1 for m in modulos if m["category"] == "sigarh"),
        })
    return reporte


async def get_monthly_report(
    db: AsyncSession,
    month: str,
    tenant_id: uuid.UUID | None = None,
) -> dict:
    try:
        mes_solicitado = datetime.strptime(month, "%Y-%m")
    except ValueError as exc:
        raise ValueError("El mes debe tener el formato YYYY-MM") from exc

    start = _limite_mes_a_utc_naive(mes_solicitado.year, mes_solicitado.month)
    end = _limite_mes_a_utc_naive(
        mes_solicitado.year + 1 if mes_solicitado.month == 12 else mes_solicitado.year,
        1 if mes_solicitado.month == 12 else mes_solicitado.month + 1,
    )

    # Se consultan TODOS los hospitales con base fisica propia (activos e
    # inactivos), no solo los activos: pacientes_nuevos_total se calcula
    # sobre este universo completo para que el numero de un mes pasado no
    # cambie solo porque alguien desactivo un hospital despues (ver
    # pacientes_nuevos_total mas abajo). Lo que SI sigue siendo estado
    # ACTUAL (cobertura de modulos, total_hospitales_activos) se filtra por
    # separado a partir de esta misma lista.
    tenants_query = (
        select(Tenant)
        .options(selectinload(Tenant.modules))
        .order_by(Tenant.name)
    )
    if tenant_id:
        tenants_query = tenants_query.where(Tenant.id == tenant_id)
    tenants = (await db.execute(tenants_query)).scalars().all()

    # Pacientes y usuarios por hospital viven en la BD FISICA de cada uno
    # (no en la central), asi que hay que consultar cada base por separado.
    # Antes esto consultaba Patient/User de la BD central: como esas tablas
    # ahi casi siempre estan vacias (los hospitales con base propia guardan
    # sus datos en SU base), el reporte mostraba ~0 para practicamente
    # cualquier hospital, sin importar su actividad real. Se piden en
    # paralelo, y si una base no responde se marca "no disponible" en vez
    # de mostrar 0 (que se confundiria con "sin actividad").
    resultados = await gather_limitado([_stats_hospital(t, start, end) for t in tenants])

    hospitales_summary = []
    module_counter: Counter = Counter()
    hospitales_no_disponibles = 0
    hospitales_activos = 0
    for t, (pacientes_nuevos, usuarios_count, disponible) in zip(tenants, resultados):
        active_codes = t.active_module_codes
        if t.is_active:
            hospitales_activos += 1
            # La cobertura de modulos SI sigue siendo estado actual: un
            # hospital inactivo no aporta a "cuantos hospitales activos
            # tienen tal modulo hoy".
            for code in active_codes:
                module_counter[code] += 1
        if not disponible:
            hospitales_no_disponibles += 1
        hospitales_summary.append({
            "id": t.id,
            "hospital_name": t.name,
            "domain": t.domain,
            "is_active": t.is_active,
            "pacientes_nuevos": pacientes_nuevos,
            "usuarios_count": usuarios_count,
            "modules_count": len(active_codes),
            "created_at": t.created_at,
            "disponible": disponible,
        })

    pacientes_nuevos_total = sum(h["pacientes_nuevos"] for h in hospitales_summary if h["disponible"])

    # Cobertura de modulos (top 10 mas adoptados) -- porcentaje sobre
    # hospitales ACTIVOS unicamente, coherente con module_counter arriba.
    modules_catalog = await get_all_modules(db)
    name_by_code = {m.code: m.name for m in modules_catalog}
    total_para_pct = hospitales_activos or 1
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

    # Hospitales registrados en el periodo (independiente de is_active). Si
    # el reporte esta filtrado a UN hospital puntual, esta lista debe seguir
    # ese mismo filtro -- antes ignoraba `tenant_id` y siempre mostraba los
    # hospitales registrados de TODO el sistema, incluso viendo el reporte
    # de un solo hospital.
    registrados_query = select(Tenant).where(
        Tenant.created_at >= start, Tenant.created_at < end,
    ).order_by(Tenant.created_at.desc())
    if tenant_id:
        registrados_query = registrados_query.where(Tenant.id == tenant_id)
    registrados = (await db.execute(registrados_query)).scalars().all()
    hospitales_registrados_periodo = [
        {"name": t.name, "domain": t.domain, "created_at": t.created_at}
        for t in registrados
    ]

    # Usuarios centrales (sin tenant, ej. super-admins) registrados en el
    # periodo: no pertenecen a ningun hospital, asi que cuando el reporte
    # esta filtrado a un hospital puntual esta cifra no aplica -- antes
    # igual mostraba el total GLOBAL de usuarios centrales aunque se
    # estuviera viendo el reporte de un solo hospital, lo cual no tiene
    # relacion con ese hospital. `None` (no 0) para que el frontend pueda
    # distinguir "no aplica a este filtro" de "de verdad no hubo ninguno".
    if tenant_id:
        usuarios_centrales = None
    else:
        usuarios_centrales = await db.scalar(
            select(func.count(User.id)).where(
                User.tenant_id.is_(None),
                User.created_at >= start,
                User.created_at < end,
            )
        )

    return {
        "month": month,
        "total_hospitales_activos": hospitales_activos,
        "pacientes_nuevos_total": pacientes_nuevos_total,
        "modules_coverage": coverage,
        "hospitales": hospitales_summary,
        "hospitales_registrados_periodo": hospitales_registrados_periodo,
        "usuarios_centrales_registrados": usuarios_centrales if usuarios_centrales is None else usuarios_centrales or 0,
        "hospitales_consultados": len(tenants) - hospitales_no_disponibles,
        "hospitales_totales": len(tenants),
        "es_parcial": hospitales_no_disponibles > 0,
        # "Hospitales Activos" y la cobertura de modulos siguen siendo
        # estado ACTUAL del sistema, no una foto historica de `month` -- ver
        # nota en el frontend (mensuales.vue) que lo aclara en pantalla. No
        # se decidio construir un cierre historico reproducible (exigiria
        # guardar snapshots mensuales, ver discusion en el codigo antes de
        # este cambio): se opto por dejarlo como reporte de estado actual y
        # corregir en cambio pacientes_nuevos_total (ver abajo).
        "es_estado_actual": True,
        # pacientes_nuevos_total ahora suma TODOS los hospitales con base
        # fisica propia, activos e inactivos (antes solo activos): un
        # hospital que tuvo pacientes reales en `month` y se desactivo
        # DESPUES seguia contando en ese momento, asi que ocultarlo hacia
        # que el total de un mes pasado cambiara segun el estado de hoy.
        # Se deja el campo en False (en vez de borrarlo) para no romper al
        # frontend que ya lo consume condicionalmente.
        "pacientes_solo_hospitales_activos": False,
    }
