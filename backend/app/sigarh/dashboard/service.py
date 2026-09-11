"""Lógica de agregación del dashboard SIGARH.

Un único punto de entrada -`get_dashboard`- que arma todo el payload que
consume el escritorio (pages/sigarh/index.vue).
"""
import uuid
from datetime import date, datetime, time, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.sigarh.rrhh.models import Empleado, RegistroAsistencia, Justificacion
from app.sigarh.movimientos.models import CambioTurno, Papeleta
from app.sigarh.infraestructura_hosp.models import Cama

# Vacaciones y licencias no tienen tabla propia en uso: "Tramitar Licencia" y
# "Justificación y Vacaciones" (movimientos) escriben en sigarh_justificaciones
# (rrhh), discriminando por `tipo`. Las clases Vacacion/Licencia de
# movimientos.models existen pero nunca reciben datos — leerlas aquí hacía que
# estos KPIs mostraran siempre 0 aunque hubiera vacaciones/licencias reales.

MESES_ES = ["ene", "feb", "mar", "abr", "may", "jun",
            "jul", "ago", "sep", "oct", "nov", "dic"]

ASISTENCIA_PRESENTE = ("presente", "tardanza", "justificado")


async def _count(db: AsyncSession, stmt) -> int:
    return (await db.scalar(stmt)) or 0


def _rango_meses(hoy: date, cantidad: int) -> list[tuple[date, date]]:
    """Devuelve [(inicio_mes, inicio_mes_siguiente)] para los últimos `cantidad` meses."""
    rangos: list[tuple[date, date]] = []
    anio, mes = hoy.year, hoy.month
    # retroceder hasta el mes más antiguo
    for _ in range(cantidad - 1):
        mes -= 1
        if mes == 0:
            mes, anio = 12, anio - 1
    for _ in range(cantidad):
        inicio = date(anio, mes, 1)
        if mes == 12:
            fin = date(anio + 1, 1, 1)
        else:
            fin = date(anio, mes + 1, 1)
        rangos.append((inicio, fin))
        mes += 1
        if mes == 13:
            mes, anio = 1, anio + 1
    return rangos


def _rango_semanas(hoy: date, cantidad: int) -> list[tuple[date, date]]:
    """Devuelve [(lunes, domingo)] para las últimas `cantidad` semanas (incluida la actual)."""
    lunes_actual = hoy - timedelta(days=hoy.weekday())
    rangos: list[tuple[date, date]] = []
    for i in range(cantidad - 1, -1, -1):
        lunes = lunes_actual - timedelta(weeks=i)
        rangos.append((lunes, lunes + timedelta(days=6)))
    return rangos


async def get_dashboard(db: AsyncSession, tenant_id: uuid.UUID) -> dict:
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)

    def emp(*extra):
        return select(func.count(Empleado.id)).where(Empleado.tenant_id == tenant_id, *extra)

    # ── Empleados ─────────────────────────────────────────────────────────────
    total_empleados = await _count(db, emp())
    empleados_activos = await _count(db, emp(Empleado.is_active.is_(True)))
    empleados_inactivos = total_empleados - empleados_activos

    genero_m = await _count(db, emp(Empleado.sexo == "M"))
    genero_f = await _count(db, emp(Empleado.sexo == "F"))

    # ── Asistencia de hoy ────────────────────────────────────────────────────
    asistencia_hoy = await _count(db, select(func.count(RegistroAsistencia.id)).where(
        RegistroAsistencia.tenant_id == tenant_id,
        RegistroAsistencia.fecha == hoy,
        RegistroAsistencia.estado.in_(ASISTENCIA_PRESENTE),
    ))
    ausentes_hoy = await _count(db, select(func.count(RegistroAsistencia.id)).where(
        RegistroAsistencia.tenant_id == tenant_id,
        RegistroAsistencia.fecha == hoy,
        RegistroAsistencia.estado == "ausente",
    ))
    porcentaje_asistencia = round(asistencia_hoy / empleados_activos * 100, 1) if empleados_activos else 0.0

    def justif(tipo, *extra):
        return select(func.count(Justificacion.id)).where(
            Justificacion.tenant_id == tenant_id, Justificacion.tipo == tipo, *extra)

    # ── Movimientos del mes ─────────────────────────────────────────────────
    mov_mes = {
        "vacaciones": await _count(db, justif("vacacion", Justificacion.fecha_inicio >= inicio_mes)),
        "licencias": await _count(db, justif("licencia", Justificacion.fecha_tramite >= inicio_mes)),
        "papeletas": await _count(db, select(func.count(Papeleta.id)).where(
            Papeleta.tenant_id == tenant_id, Papeleta.fecha_tramite >= inicio_mes)),
        "cambios_turno": await _count(db, select(func.count(CambioTurno.id)).where(
            CambioTurno.tenant_id == tenant_id, CambioTurno.fecha_original >= inicio_mes)),
    }

    # ── Pendientes (alertas) ────────────────────────────────────────────────
    pendientes = {
        "vacaciones": await _count(db, justif("vacacion", Justificacion.estado == "pendiente")),
        "licencias": await _count(db, justif("licencia", Justificacion.estado == "pendiente")),
        "papeletas": await _count(db, select(func.count(Papeleta.id)).where(
            Papeleta.tenant_id == tenant_id, Papeleta.estado == "pendiente")),
        "cambios_turno": await _count(db, select(func.count(CambioTurno.id)).where(
            CambioTurno.tenant_id == tenant_id, CambioTurno.estado == "pendiente")),
    }
    solicitudes_pendientes = sum(pendientes.values())

    justificaciones_pendientes = await _count(db, select(func.count(Justificacion.id)).where(
        Justificacion.tenant_id == tenant_id, Justificacion.estado == "pendiente"))

    # ── Camas ───────────────────────────────────────────────────────────────
    def cama(*extra):
        return select(func.count(Cama.id)).where(Cama.tenant_id == tenant_id, *extra)

    camas_total = await _count(db, cama())
    camas_disp = await _count(db, cama(Cama.estado == "DISPONIBLE"))
    camas_ocup = await _count(db, cama(Cama.estado == "OCUPADA"))
    camas_mant = await _count(db, cama(Cama.estado == "MANTENIMIENTO"))
    camas_res = await _count(db, cama(Cama.estado == "RESERVADA"))

    # ── Empleados por estado (en vacaciones / licencia hoy) ─────────────────
    en_vacaciones = await _count(db, select(func.count(func.distinct(Justificacion.empleado_id))).where(
        Justificacion.tenant_id == tenant_id, Justificacion.tipo == "vacacion",
        Justificacion.estado == "aprobado",
        Justificacion.fecha_inicio <= hoy,
        Justificacion.fecha_fin >= hoy,
    ))
    en_licencia = await _count(db, select(func.count(func.distinct(Justificacion.empleado_id))).where(
        Justificacion.tenant_id == tenant_id, Justificacion.tipo == "licencia",
        Justificacion.estado == "aprobado",
        Justificacion.fecha_inicio <= hoy,
        Justificacion.fecha_fin >= hoy,
    ))

    # ── Serie: empleados dados de alta por mes (últimos 6) ──────────────────
    empleados_por_mes = []
    for inicio, fin in _rango_meses(hoy, 6):
        valor = await _count(db, emp(
            Empleado.created_at >= datetime.combine(inicio, time.min),
            Empleado.created_at < datetime.combine(fin, time.min),
        ))
        empleados_por_mes.append({"label": MESES_ES[inicio.month - 1], "anio": inicio.year, "valor": valor})

    # ── Serie: tendencia de solicitudes por mes (últimos 6) ────────────────
    tendencias_solicitudes = []
    for inicio, fin in _rango_meses(hoy, 6):
        v = await _count(db, justif("vacacion", Justificacion.fecha_inicio >= inicio, Justificacion.fecha_inicio < fin))
        l = await _count(db, justif("licencia", Justificacion.fecha_tramite >= inicio, Justificacion.fecha_tramite < fin))
        p = await _count(db, select(func.count(Papeleta.id)).where(
            Papeleta.tenant_id == tenant_id, Papeleta.fecha_tramite >= inicio, Papeleta.fecha_tramite < fin))
        c = await _count(db, select(func.count(CambioTurno.id)).where(
            CambioTurno.tenant_id == tenant_id, CambioTurno.fecha_original >= inicio, CambioTurno.fecha_original < fin))
        tendencias_solicitudes.append({
            "label": MESES_ES[inicio.month - 1], "anio": inicio.year,
            "vacaciones": v, "licencias": l, "papeletas": p, "cambios_turno": c,
            "total": v + l + p + c,
        })

    # ── Serie: asistencia por semana (últimas 5) ───────────────────────────
    asistencia_semanal = []
    for lunes, domingo in _rango_semanas(hoy, 5):
        presentes = await _count(db, select(func.count(RegistroAsistencia.id)).where(
            RegistroAsistencia.tenant_id == tenant_id,
            RegistroAsistencia.fecha >= lunes, RegistroAsistencia.fecha <= domingo,
            RegistroAsistencia.estado.in_(ASISTENCIA_PRESENTE),
        ))
        ausentes = await _count(db, select(func.count(RegistroAsistencia.id)).where(
            RegistroAsistencia.tenant_id == tenant_id,
            RegistroAsistencia.fecha >= lunes, RegistroAsistencia.fecha <= domingo,
            RegistroAsistencia.estado == "ausente",
        ))
        asistencia_semanal.append({
            "label": lunes.strftime("%d/%m"),
            "presentes": presentes, "ausentes": ausentes, "total": presentes + ausentes,
        })

    # ── Actividad reciente ────────────────────────────────────────────────
    res_vac = await db.execute(
        select(Justificacion, Empleado)
        .join(Empleado, Empleado.id == Justificacion.empleado_id)
        .where(Justificacion.tenant_id == tenant_id, Justificacion.tipo == "vacacion")
        .order_by(Justificacion.created_at.desc()).limit(5)
    )
    ultimas_vacaciones = [
        {
            "id": str(v.id),
            "empleado_nombre": e.nombre_completo,
            "tipo": v.tipo,
            "fecha_inicio": str(v.fecha_inicio),
            "fecha_fin": str(v.fecha_fin),
            "estado": v.estado,
        }
        for v, e in res_vac.all()
    ]

    res_lic = await db.execute(
        select(Justificacion, Empleado)
        .join(Empleado, Empleado.id == Justificacion.empleado_id)
        .where(Justificacion.tenant_id == tenant_id, Justificacion.tipo == "licencia")
        .order_by(Justificacion.created_at.desc()).limit(5)
    )
    ultimas_licencias = [
        {
            "id": str(l.id),
            "empleado_nombre": e.nombre_completo,
            "fecha_tramite": str(l.fecha_tramite),
            "fecha_inicio": str(l.fecha_inicio),
            "fecha_fin": str(l.fecha_fin),
            "estado": l.estado,
        }
        for l, e in res_lic.all()
    ]

    return {
        "fecha": str(hoy),
        "kpis": {
            "total_empleados": total_empleados,
            "empleados_activos": empleados_activos,
            "empleados_inactivos": empleados_inactivos,
            "asistencia_hoy": asistencia_hoy,
            "ausentes_hoy": ausentes_hoy,
            "porcentaje_asistencia": porcentaje_asistencia,
            "solicitudes_pendientes": solicitudes_pendientes,
            "justificaciones_pendientes": justificaciones_pendientes,
        },
        "movimientos_mes": mov_mes,
        "pendientes": pendientes,
        "camas": {
            "total": camas_total,
            "disponibles": camas_disp,
            "ocupadas": camas_ocup,
            "mantenimiento": camas_mant,
            "reservadas": camas_res,
            "porcentaje_ocupacion": round(camas_ocup / camas_total * 100, 1) if camas_total else 0.0,
        },
        "distribucion_genero": {
            "masculino": genero_m,
            "femenino": genero_f,
            "sin_registrar": max(total_empleados - genero_m - genero_f, 0),
        },
        "distribucion_estado": {
            "activos": empleados_activos,
            "inactivos": empleados_inactivos,
            "en_vacaciones": en_vacaciones,
            "en_licencia": en_licencia,
        },
        "empleados_por_mes": empleados_por_mes,
        "asistencia_semanal": asistencia_semanal,
        "tendencias_solicitudes": tendencias_solicitudes,
        "ultimas_vacaciones": ultimas_vacaciones,
        "ultimas_licencias": ultimas_licencias,
    }
