"""Agregación del dashboard personal del médico (rol 'medico').

Todo se filtra por su propio `empleado_id` -- exactamente el mismo criterio
que ya usan /consulta-externa/citas y /consulta-externa/programacion-medica
al forzar `medico_id` cuando el usuario logueado es médico.
"""
import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.admision.models import Patient
from app.hospital.consulta_externa.models import Cita, ProgramacionMedica

DIAS_SEMANA = 7


def _dias_rango(hoy: date, cantidad: int) -> list[date]:
    return [hoy - timedelta(days=i) for i in range(cantidad - 1, -1, -1)]


async def get_dashboard_medico(db: AsyncSession, tid: uuid.UUID, empleado_id: uuid.UUID) -> dict:
    hoy = date.today()
    dias = _dias_rango(hoy, DIAS_SEMANA)
    desde = dias[0]
    inicio_mes = hoy.replace(day=1)

    # Citas de hoy (para KPIs y para listar las próximas por atender).
    rows_hoy = (await db.execute(
        select(Cita.id, Cita.hora_inicio, Cita.estado, Cita.patient_id)
        .join(ProgramacionMedica, ProgramacionMedica.id == Cita.programacion_medica_id)
        .where(
            Cita.tenant_id == tid, ProgramacionMedica.medico_id == empleado_id,
            ProgramacionMedica.fecha == hoy,
        )
        .order_by(Cita.hora_inicio)
    )).all()

    pacientes_ids = {r.patient_id for r in rows_hoy}
    nombres = {}
    if pacientes_ids:
        pac_rows = (await db.execute(
            select(Patient.id, Patient.first_name, Patient.last_name_paterno, Patient.last_name_materno)
            .where(Patient.id.in_(pacientes_ids))
        )).all()
        nombres = {p.id: f"{p.first_name} {p.last_name_paterno} {p.last_name_materno}" for p in pac_rows}

    citas_hoy_total = len(rows_hoy)
    citas_hoy_atendidas = sum(1 for r in rows_hoy if r.estado == "atendida")
    citas_hoy_pendientes = citas_hoy_total - citas_hoy_atendidas

    hora_actual = datetime.now().strftime("%H:%M")
    proximas = [
        {"id": r.id, "hora": r.hora_inicio, "paciente": nombres.get(r.patient_id, "Paciente"), "estado": r.estado}
        for r in rows_hoy
        if r.estado in ("separada", "confirmada") and r.hora_inicio >= hora_actual
    ][:5]

    # Serie de 7 días (citas por día, incluida hoy).
    rows_semana = (await db.execute(
        select(ProgramacionMedica.fecha)
        .join(Cita, Cita.programacion_medica_id == ProgramacionMedica.id)
        .where(Cita.tenant_id == tid, ProgramacionMedica.medico_id == empleado_id,
               ProgramacionMedica.fecha >= desde, ProgramacionMedica.fecha <= hoy)
    )).all()
    serie = {d: 0 for d in dias}
    for (fecha,) in rows_semana:
        if fecha in serie:
            serie[fecha] += 1

    jornadas_mes = await db.scalar(select(func.count(ProgramacionMedica.id)).where(
        ProgramacionMedica.tenant_id == tid, ProgramacionMedica.medico_id == empleado_id,
        ProgramacionMedica.fecha >= inicio_mes, ProgramacionMedica.fecha <= hoy,
    )) or 0

    pacientes_semana = await db.scalar(
        select(func.count(func.distinct(Cita.patient_id)))
        .select_from(Cita)
        .join(ProgramacionMedica, ProgramacionMedica.id == Cita.programacion_medica_id)
        .where(Cita.tenant_id == tid, ProgramacionMedica.medico_id == empleado_id,
               ProgramacionMedica.fecha >= desde, ProgramacionMedica.fecha <= hoy)
    ) or 0

    return {
        "fecha": str(hoy),
        "kpis": {
            "citas_hoy_total": citas_hoy_total,
            "citas_hoy_pendientes": citas_hoy_pendientes,
            "citas_hoy_atendidas": citas_hoy_atendidas,
            "jornadas_mes": jornadas_mes,
            "pacientes_semana": pacientes_semana,
        },
        "serie_semana": [{"label": d.strftime("%d/%m"), "citas": serie[d]} for d in dias],
        "proximas_citas": proximas,
    }
