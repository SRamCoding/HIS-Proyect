"""Agregación del dashboard hospitalario (Escritorio).

Un único punto de entrada -`get_dashboard`- que arma el resumen del día y la
serie de los últimos 7 días que consume DashboardGeneral.vue, calculando solo
las secciones de los módulos que el usuario tiene activos (mismo criterio que
ya usa el front en `active_modules`, firmado en el JWT por contexto_hospital).
"""
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.sigarh.infraestructura_hosp.models import Cama
from app.hospital.admision.models import Patient
from app.hospital.consulta_externa.models import (
    Hospitalizacion, Cita, ProgramacionMedica, OrdenLaboratorio, Receta,
)
from app.hospital.emergencia.models import AdmisionEmergencia
from app.admin.auditoria.models import AuditLog
from app.tenants.modulos.submodulos import permiso_incluye

DIAS_SEMANA = 7


def _dias_rango(hoy: date, cantidad: int) -> list[date]:
    return [hoy - timedelta(days=i) for i in range(cantidad - 1, -1, -1)]


async def _count(db: AsyncSession, stmt) -> int:
    return (await db.scalar(stmt)) or 0


async def get_dashboard(db: AsyncSession, tid: uuid.UUID, active_modules: list[str]) -> dict:
    hoy = date.today()
    dias = _dias_rango(hoy, DIAS_SEMANA)
    desde = dias[0]

    tiene_hosp = permiso_incluye(active_modules, "hospitalizacion")
    tiene_consulta = permiso_incluye(active_modules, "consulta_externa")
    tiene_emergencia = permiso_incluye(active_modules, "emergencia")
    tiene_lab = permiso_incluye(active_modules, "laboratorio")
    tiene_farmacia = permiso_incluye(active_modules, "farmacia")
    tiene_auditoria = permiso_incluye(active_modules, "auditoria")
    tiene_admision = permiso_incluye(active_modules, "admision")

    kpis = {
        "camas_total": 0, "camas_ocupadas": 0,
        "citas_hoy_total": 0, "citas_hoy_pendientes": 0, "citas_hoy_atendidas": 0,
        "emergencias_en_atencion": 0,
        "lab_pendientes": 0,
        "recetas_pendientes": 0,
    }
    serie = {d: {"label": d.strftime("%d/%m"), "ingresos": 0, "altas": 0, "citas": 0, "emergencias": 0} for d in dias}

    if tiene_hosp:
        kpis["camas_total"] = await _count(db, select(func.count()).where(
            Cama.tenant_id == tid, Cama.is_active.is_(True)))
        kpis["camas_ocupadas"] = await _count(db, select(func.count()).where(
            Hospitalizacion.tenant_id == tid, Hospitalizacion.fecha_alta.is_(None)))

        desde_dt = datetime.combine(desde, datetime.min.time())
        rows = (await db.execute(select(Hospitalizacion.fecha_ingreso, Hospitalizacion.fecha_alta).where(
            Hospitalizacion.tenant_id == tid,
            or_(Hospitalizacion.fecha_ingreso >= desde_dt, Hospitalizacion.fecha_alta >= desde_dt),
        ))).all()
        for fecha_ingreso, fecha_alta in rows:
            d_ingreso = fecha_ingreso.date()
            if d_ingreso in serie:
                serie[d_ingreso]["ingresos"] += 1
            if fecha_alta:
                d_alta = fecha_alta.date()
                if d_alta in serie:
                    serie[d_alta]["altas"] += 1

    if tiene_consulta:
        rows = (await db.execute(
            select(ProgramacionMedica.fecha, Cita.estado)
            .join(ProgramacionMedica, ProgramacionMedica.id == Cita.programacion_medica_id)
            .where(Cita.tenant_id == tid, ProgramacionMedica.fecha >= desde, ProgramacionMedica.fecha <= hoy)
        )).all()
        for fecha, estado in rows:
            if fecha in serie:
                serie[fecha]["citas"] += 1
            if fecha == hoy:
                kpis["citas_hoy_total"] += 1
                if estado == "atendida":
                    kpis["citas_hoy_atendidas"] += 1
        # "Pendientes" = todo lo que hoy no está atendida todavía (separada,
        # confirmada, cancelada, no_asistio incluidas): así el total siempre
        # cuadra con citas_hoy_total, sin inventar una tercera categoría.
        kpis["citas_hoy_pendientes"] = kpis["citas_hoy_total"] - kpis["citas_hoy_atendidas"]

    if tiene_lab:
        kpis["lab_pendientes"] = await _count(db, select(func.count()).where(
            OrdenLaboratorio.tenant_id == tid, OrdenLaboratorio.estado == "pendiente"))

    if tiene_farmacia:
        kpis["recetas_pendientes"] = await _count(db, select(func.count()).where(
            Receta.tenant_id == tid, Receta.estado == "pendiente"))

    if tiene_emergencia:
        desde_dt = datetime.combine(desde, datetime.min.time())
        rows = (await db.execute(select(AdmisionEmergencia.created_at).where(
            AdmisionEmergencia.tenant_id == tid, AdmisionEmergencia.created_at >= desde_dt,
        ))).all()
        for (creado,) in rows:
            d = creado.date()
            if d in serie:
                serie[d]["emergencias"] += 1
        kpis["emergencias_en_atencion"] = await _count(db, select(func.count()).where(
            AdmisionEmergencia.tenant_id == tid, AdmisionEmergencia.estado == "en_atencion"))

    # Actividad por hora (últimas 24h, bloques de 3h) -- mismo criterio que
    # admin/dashboard/service.py::get_dashboard_stats, aplicado al tenant.
    actividad_por_hora = [{"label": f"{h:02d}:00", "valor": 0} for h in range(0, 24, 3)]
    if tiene_auditoria:
        desde_24h = datetime.utcnow() - timedelta(hours=24)
        horas = (await db.execute(select(AuditLog.created_at).where(
            AuditLog.tenant_id == tid, AuditLog.created_at >= desde_24h,
        ))).scalars().all()
        bloques = Counter((h.hour // 3) * 3 for h in horas)
        actividad_por_hora = [{"label": f"{h:02d}:00", "valor": bloques[h]} for h in range(0, 24, 3)]

    pacientes_recientes = []
    if tiene_admision:
        recientes = (await db.scalars(
            select(Patient).where(Patient.tenant_id == tid)
            .order_by(Patient.created_at.desc()).limit(6)
        )).all()
        pacientes_recientes = [
            {
                "id": p.id, "nombre": p.full_name, "dni": p.dni, "edad": p.age,
                "created_at": p.created_at,
            }
            for p in recientes
        ]

    return {
        "fecha": str(hoy),
        "kpis": kpis,
        "serie_semana": [serie[d] for d in dias],
        "actividad_por_hora": actividad_por_hora,
        "pacientes_recientes": pacientes_recientes,
    }
