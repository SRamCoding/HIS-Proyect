import uuid
from datetime import date, datetime
from fastapi import HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.consulta_externa.models import (
    ProgramacionMedica, Cita, AtencionMedica, Interconsulta, Hospitalizacion,
    OrdenLaboratorio, OrdenImagen, Receta, Referencia,
)
from app.hospital.consulta_externa.service import _generar_slots
from app.hospital.emergencia.models import AtencionEmergencia, AdmisionEmergencia
from app.hospital.admision.models import ListaEspera
from app.sigarh.rrhh.models import Empleado, Especialidad
from app.sigarh.mantenimiento.models import Servicio
from app.sigarh.infraestructura_hosp.models import Cama


def _validar_rango(fecha_desde: date, fecha_hasta: date):
    if fecha_hasta < fecha_desde:
        raise HTTPException(400, detail="fecha_hasta no puede ser anterior a fecha_desde")


def _dia(fecha: date, fin: bool = False) -> datetime:
    return datetime.combine(fecha, datetime.max.time() if fin else datetime.min.time())


def _csv(rows: list[dict], keys: list[str]) -> bytes:
    import csv
    from io import StringIO
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(keys)

    def safe(v):
        value = str(v) if v is not None else ""
        return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else value
    for row in rows:
        writer.writerow([safe(row.get(k)) for k in keys])
    return ("﻿" + stream.getvalue()).encode("utf-8")


# ─── Reporte por Médico (productividad, Consulta Externa + Emergencia) ─────

async def reporte_medico(db: AsyncSession, tid: uuid.UUID, fecha_desde: date, fecha_hasta: date,
                          medico_id: uuid.UUID | None = None) -> list[dict]:
    """Productividad por médico en el rango: cupos/citas de Consulta Externa
    (via su ProgramacionMedica en el rango), atenciones firmadas de Consulta
    Externa y de Emergencia (AtencionEmergencia.medico_id es FK directa, a
    diferencia de Consulta Externa que pasa por Cita), e interconsultas que
    generó. Solo se listan médicos con alguna actividad real en el rango."""
    _validar_rango(fecha_desde, fecha_hasta)
    inicio, fin = _dia(fecha_desde), _dia(fecha_hasta, fin=True)

    ce_ids = select(ProgramacionMedica.medico_id).where(
        ProgramacionMedica.tenant_id == tid, ProgramacionMedica.fecha.between(fecha_desde, fecha_hasta)).distinct()
    em_ids = select(AtencionEmergencia.medico_id).where(
        AtencionEmergencia.tenant_id == tid, AtencionEmergencia.medico_id.isnot(None),
        AtencionEmergencia.estado == "firmado", AtencionEmergencia.firmado_at.between(inicio, fin)).distinct()
    medico_ids = {r for r in (await db.scalars(ce_ids)).all()} | {r for r in (await db.scalars(em_ids)).all()}
    if medico_id:
        medico_ids &= {medico_id}
    if not medico_ids:
        return []

    medicos = {m.id: m for m in (await db.scalars(
        select(Empleado).where(Empleado.id.in_(medico_ids)))).all()}

    items = []
    for mid in medico_ids:
        medico = medicos.get(mid)
        if medico is None:
            continue
        conteo_citas = dict((await db.execute(select(Cita.estado, func.count()).join(
            ProgramacionMedica, Cita.programacion_medica_id == ProgramacionMedica.id).where(
            ProgramacionMedica.tenant_id == tid, ProgramacionMedica.medico_id == mid,
            ProgramacionMedica.fecha.between(fecha_desde, fecha_hasta)).group_by(Cita.estado))).all())
        atenciones_ce = await db.scalar(select(func.count()).select_from(AtencionMedica).join(
            Cita, AtencionMedica.cita_id == Cita.id).join(
            ProgramacionMedica, Cita.programacion_medica_id == ProgramacionMedica.id).where(
            ProgramacionMedica.tenant_id == tid, ProgramacionMedica.medico_id == mid,
            AtencionMedica.estado == "firmado", AtencionMedica.firmado_at.between(inicio, fin))) or 0
        atenciones_em = await db.scalar(select(func.count()).where(
            AtencionEmergencia.tenant_id == tid, AtencionEmergencia.medico_id == mid,
            AtencionEmergencia.estado == "firmado", AtencionEmergencia.firmado_at.between(inicio, fin))) or 0
        interconsultas = await db.scalar(select(func.count()).select_from(Interconsulta).join(
            AtencionMedica, Interconsulta.atencion_medica_id == AtencionMedica.id).where(
            AtencionMedica.firmado_por_id == mid, AtencionMedica.firmado_at.between(inicio, fin))) or 0

        items.append({
            "medico_id": mid, "medico_nombre": medico.nombre_completo, "medico_dni": medico.dni,
            "citas_programadas": sum(conteo_citas.values()),
            "citas_atendidas": conteo_citas.get("atendida", 0),
            "citas_no_asistio": conteo_citas.get("no_asistio", 0),
            "citas_canceladas": conteo_citas.get("cancelada", 0),
            "atenciones_firmadas_consulta_externa": atenciones_ce,
            "atenciones_firmadas_emergencia": atenciones_em,
            "total_atenciones_firmadas": atenciones_ce + atenciones_em,
            "interconsultas_generadas": interconsultas,
        })
    items.sort(key=lambda i: i["medico_nombre"] or "")
    return items


async def csv_reporte_medico(db, tid, fecha_desde, fecha_hasta, medico_id=None):
    items = await reporte_medico(db, tid, fecha_desde, fecha_hasta, medico_id)
    keys = ["medico_nombre", "medico_dni", "citas_programadas", "citas_atendidas", "citas_no_asistio",
            "citas_canceladas", "atenciones_firmadas_consulta_externa", "atenciones_firmadas_emergencia",
            "total_atenciones_firmadas", "interconsultas_generadas"]
    return _csv(items, keys)


# ─── Reportes de Hospitalización (indicadores del rango) ───────────────────

async def reportes_hospitalizacion(db: AsyncSession, tid: uuid.UUID, fecha_desde: date, fecha_hasta: date) -> dict:
    """Extiende el censo diario (un solo día) a indicadores hospitalarios
    estándar sobre un rango: egresos (altas), ingresos, promedio de
    permanencia y días-cama ocupados -- los mismos indicadores que reporta
    el área de Estadística e Informática a la Oficina de Epidemiología."""
    _validar_rango(fecha_desde, fecha_hasta)
    inicio, fin = _dia(fecha_desde), _dia(fecha_hasta, fin=True)

    ingresos = await db.scalar(select(func.count()).where(
        Hospitalizacion.tenant_id == tid, Hospitalizacion.fecha_ingreso.between(inicio, fin))) or 0
    altas_rows = (await db.scalars(select(Hospitalizacion).where(
        Hospitalizacion.tenant_id == tid, Hospitalizacion.fecha_alta.between(inicio, fin)))).all()
    dias_estancia = [(h.fecha_alta.date() - h.fecha_ingreso.date()).days + 1 for h in altas_rows]
    promedio_estancia = round(sum(dias_estancia) / len(dias_estancia), 1) if dias_estancia else None

    activos_rango = (await db.scalars(select(Hospitalizacion).where(
        Hospitalizacion.tenant_id == tid, Hospitalizacion.fecha_ingreso <= fin,
        or_(Hospitalizacion.fecha_alta.is_(None), Hospitalizacion.fecha_alta >= inicio)))).all()
    camas_dia = sum(max((min(h.fecha_alta or fin, fin).date() - max(h.fecha_ingreso, inicio).date()).days + 1, 0)
                     for h in activos_rango)
    total_camas = await db.scalar(select(func.count()).where(Cama.tenant_id == tid, Cama.is_active.is_(True))) or 0

    esp_rows = (await db.execute(select(Especialidad.nombre, func.count(Hospitalizacion.id)).join(
        Hospitalizacion, Hospitalizacion.especialidad_ingreso_id == Especialidad.id).where(
        Hospitalizacion.tenant_id == tid, Hospitalizacion.fecha_ingreso.between(inicio, fin)).group_by(
        Especialidad.nombre).order_by(func.count(Hospitalizacion.id).desc()))).all()

    return {
        "fecha_desde": fecha_desde, "fecha_hasta": fecha_hasta,
        "ingresos": ingresos, "altas": len(altas_rows),
        "promedio_estancia_dias": promedio_estancia,
        "camas_dia_ocupadas": camas_dia, "total_camas": total_camas,
        "porcentaje_ocupacion": round(camas_dia / (total_camas * ((fin.date() - inicio.date()).days + 1)) * 100, 1)
            if total_camas else 0.0,
        "por_especialidad": [{"especialidad": nombre, "ingresos": cnt} for nombre, cnt in esp_rows],
    }


# ─── Gestión de Cupos (configurados vs. usados por programación) ───────────

async def gestion_cupos(db: AsyncSession, tid: uuid.UUID, fecha_desde: date, fecha_hasta: date,
                         medico_id: uuid.UUID | None = None, servicio_id: uuid.UUID | None = None) -> list[dict]:
    """Cupos configurados (slots calculados con la misma _generar_slots que usa
    Consulta Externa para agendar) vs. cupos usados (citas no canceladas),
    por cada ProgramacionMedica del rango."""
    _validar_rango(fecha_desde, fecha_hasta)
    q = select(ProgramacionMedica).where(
        ProgramacionMedica.tenant_id == tid, ProgramacionMedica.fecha.between(fecha_desde, fecha_hasta))
    if medico_id:
        q = q.where(ProgramacionMedica.medico_id == medico_id)
    if servicio_id:
        q = q.where(ProgramacionMedica.servicio_id == servicio_id)
    progs = (await db.scalars(q.order_by(ProgramacionMedica.fecha, ProgramacionMedica.hora_inicio))).all()
    if not progs:
        return []

    prog_ids = [p.id for p in progs]
    usados_por_prog = dict((await db.execute(select(Cita.programacion_medica_id, func.count()).where(
        Cita.programacion_medica_id.in_(prog_ids), Cita.estado != "cancelada").group_by(
        Cita.programacion_medica_id))).all())
    medicos = {m.id: m for m in (await db.scalars(select(Empleado).where(
        Empleado.id.in_({p.medico_id for p in progs}))))}
    servicio_ids = {p.servicio_id for p in progs if p.servicio_id}
    servicios = {s.id: s for s in (await db.scalars(select(Servicio).where(
        Servicio.id.in_(servicio_ids))))} if servicio_ids else {}

    items = []
    for p in progs:
        total = len(_generar_slots(p.hora_inicio, p.hora_fin, p.tiempo_promedio_atencion))
        usados = usados_por_prog.get(p.id, 0)
        medico = medicos.get(p.medico_id)
        servicio = servicios.get(p.servicio_id) if p.servicio_id else None
        items.append({
            "programacion_id": p.id, "codigo": p.codigo, "fecha": p.fecha, "turno": p.turno,
            "medico": medico.nombre_completo if medico else None,
            "servicio": servicio.nombre if servicio else None,
            "estado_programacion": p.estado,
            "cupos_totales": total, "cupos_usados": usados, "cupos_disponibles": max(total - usados, 0),
            "porcentaje_ocupacion": round(usados / total * 100, 1) if total else 0.0,
        })
    return items


async def csv_gestion_cupos(db, tid, fecha_desde, fecha_hasta, medico_id=None, servicio_id=None):
    items = await gestion_cupos(db, tid, fecha_desde, fecha_hasta, medico_id, servicio_id)
    keys = ["codigo", "fecha", "turno", "medico", "servicio", "estado_programacion",
            "cupos_totales", "cupos_usados", "cupos_disponibles", "porcentaje_ocupacion"]
    return _csv(items, keys)


# ─── Gestión de Tickets (volumen de órdenes/recetas de apoyo al diagnóstico) ─

async def gestion_tickets(db: AsyncSession, tid: uuid.UUID, fecha_desde: date, fecha_hasta: date) -> dict:
    """Volumen y estado de los 'tickets' de apoyo al diagnóstico y farmacia
    ya generados por otros módulos en el rango: órdenes de Laboratorio,
    órdenes de Imagenología y recetas de Farmacia."""
    _validar_rango(fecha_desde, fecha_hasta)
    inicio, fin = _dia(fecha_desde), _dia(fecha_hasta, fin=True)

    async def por_estado(model):
        rows = (await db.execute(select(model.estado, func.count()).where(
            model.tenant_id == tid, model.created_at.between(inicio, fin)).group_by(model.estado))).all()
        return {estado: cnt for estado, cnt in rows}

    lab, img, rec = await por_estado(OrdenLaboratorio), await por_estado(OrdenImagen), await por_estado(Receta)
    return {
        "fecha_desde": fecha_desde, "fecha_hasta": fecha_hasta,
        "laboratorio": {"total": sum(lab.values()), "por_estado": lab},
        "imagenologia": {"total": sum(img.values()), "por_estado": img},
        "farmacia_recetas": {"total": sum(rec.values()), "por_estado": rec},
    }


# ─── Visor de Colas (foto en vivo, sin rango de fechas) ────────────────────

async def visor_colas(db: AsyncSession, tid: uuid.UUID) -> dict:
    """Foto en vivo de las colas reales de cada módulo -- no hay tabla propia,
    solo cuenta filas pendientes de las tablas reales de cada módulo, igual
    que hace el Dashboard general pero consolidado en una sola vista."""
    hoy = date.today()
    lista_espera = await db.scalar(select(func.count()).where(
        ListaEspera.tenant_id == tid, ListaEspera.estado == "pendiente")) or 0
    citas_pendientes_hoy = await db.scalar(select(func.count()).select_from(Cita).join(
        ProgramacionMedica, Cita.programacion_medica_id == ProgramacionMedica.id).where(
        ProgramacionMedica.tenant_id == tid, ProgramacionMedica.fecha == hoy, Cita.estado == "separada")) or 0
    admitidos_sin_triaje = await db.scalar(select(func.count()).where(
        AdmisionEmergencia.tenant_id == tid, AdmisionEmergencia.estado == "admitido")) or 0
    en_atencion_emergencia = await db.scalar(select(func.count()).where(
        AdmisionEmergencia.tenant_id == tid, AdmisionEmergencia.estado == "en_atencion")) or 0
    lab_pendientes = await db.scalar(select(func.count()).where(
        OrdenLaboratorio.tenant_id == tid, OrdenLaboratorio.estado == "pendiente")) or 0
    img_pendientes = await db.scalar(select(func.count()).where(
        OrdenImagen.tenant_id == tid, OrdenImagen.estado == "pendiente")) or 0
    recetas_pendientes = await db.scalar(select(func.count()).where(
        Receta.tenant_id == tid, Receta.estado == "pendiente")) or 0

    return {
        "generado_at": datetime.utcnow(),
        "admision_lista_espera_pendientes": lista_espera,
        "consulta_externa_citas_pendientes_hoy": citas_pendientes_hoy,
        "emergencia_admitidos_sin_triaje": admitidos_sin_triaje,
        "emergencia_en_atencion": en_atencion_emergencia,
        "laboratorio_ordenes_pendientes": lab_pendientes,
        "imagenologia_ordenes_pendientes": img_pendientes,
        "farmacia_recetas_pendientes": recetas_pendientes,
    }


# ─── Externos (Referencias a otros establecimientos) ───────────────────────

async def externos(db: AsyncSession, tid: uuid.UUID, fecha_desde: date, fecha_hasta: date) -> dict:
    """Reporte agregado sobre Referencias reales del rango: por estado, por
    establecimiento destino y tiempo hasta la contrarreferencia -- no
    duplica la tabla de Referencias, solo la resume."""
    _validar_rango(fecha_desde, fecha_hasta)
    inicio, fin = _dia(fecha_desde), _dia(fecha_hasta, fin=True)
    rows = (await db.scalars(select(Referencia).where(
        Referencia.tenant_id == tid, Referencia.created_at.between(inicio, fin)).order_by(
        Referencia.created_at.desc()))).all()

    nombres_tenant: dict[uuid.UUID, str | None] = {}
    destinos_internos = {r.tenant_destino_id for r in rows if r.tenant_destino_id}
    if destinos_internos:
        from app.core.tenant_db import get_tenant_by_id
        for t in destinos_internos:
            tenant = await get_tenant_by_id(t)
            nombres_tenant[t] = tenant.name if tenant else None

    items = []
    for r in rows:
        destino = r.nombre_ipress_destino or nombres_tenant.get(r.tenant_destino_id) or "No especificado"
        dias = (r.fecha_contrarreferencia - r.created_at.date()).days if r.fecha_contrarreferencia else None
        items.append({
            "id": r.id, "numero_referencia": r.numero_referencia, "fecha": r.created_at,
            "destino": destino, "especialidad_destino": r.especialidad_destino, "estado": r.estado,
            "fecha_contrarreferencia": r.fecha_contrarreferencia, "dias_hasta_contrarreferencia": dias,
        })

    por_estado: dict[str, int] = {}
    for it in items:
        por_estado[it["estado"]] = por_estado.get(it["estado"], 0) + 1
    tiempos = [i["dias_hasta_contrarreferencia"] for i in items if i["dias_hasta_contrarreferencia"] is not None]

    return {
        "fecha_desde": fecha_desde, "fecha_hasta": fecha_hasta, "total": len(items),
        "por_estado": por_estado,
        "promedio_dias_contrarreferencia": round(sum(tiempos) / len(tiempos), 1) if tiempos else None,
        "items": items,
    }


async def csv_externos(db, tid, fecha_desde, fecha_hasta):
    reporte = await externos(db, tid, fecha_desde, fecha_hasta)
    keys = ["numero_referencia", "fecha", "destino", "especialidad_destino", "estado",
            "fecha_contrarreferencia", "dias_hasta_contrarreferencia"]
    return _csv(reporte["items"], keys)
