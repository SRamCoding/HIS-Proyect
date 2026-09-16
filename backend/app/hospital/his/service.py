import uuid
from datetime import date, datetime
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.his.models import HisEnvio
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import (
    AtencionMedica, Cita, AtencionDiagnostico, ProgramacionMedica,
)
from app.hospital.emergencia.models import AtencionEmergencia, AdmisionEmergencia, EmergenciaDiagnostico
from app.sigarh.general.models import DiagnosticoCIE10
from app.sigarh.rrhh.models import Empleado, Especialidad
from app.sigarh.mantenimiento.models import Servicio
from app.sigarh.config_financiera.models import Seguro
from app.admin.auditoria.models import AuditLog


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


def columns(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def audit(db, tid, user, model, obj_id, action, before=None, after=None):
    db.add(AuditLog(tenant_id=tid, user_id=uuid.UUID(user["sub"]), user_name=user.get("name"),
        model=model, model_id=str(obj_id), action=action,
        old_values=jsonable_encoder(before), new_values=jsonable_encoder(after)))


async def _nombres_distritos(district_ids: set[str]) -> dict[str, str]:
    """Ubigeo vive en la BD central (catálogo nacional compartido, sin
    tenant_id) -- se resuelve con una sesión aparte, igual que
    get_tenant_by_id(). Si un distrito no se puede resolver, se muestra su
    código tal cual: nunca se inventa un nombre."""
    district_ids = {d for d in district_ids if d}
    if not district_ids:
        return {}
    from app.core.database import AsyncSessionLocal
    from app.shared.ubigeo.models import UbigeoDistrito
    async with AsyncSessionLocal() as central_db:
        rows = (await central_db.execute(select(UbigeoDistrito.id, UbigeoDistrito.nombre)
            .where(UbigeoDistrito.id.in_(district_ids)))).all()
    return {row[0]: row[1] for row in rows}


async def list_atenciones_his(db: AsyncSession, tid: uuid.UUID, fecha_desde: date, fecha_hasta: date) -> list[dict]:
    """Una fila HIS por (atención firmada, diagnóstico) -- así se reporta
    realmente al HIS-MINSA: si una atención tiene dos diagnósticos, genera dos
    líneas. Una atención sin diagnóstico registrado igual se reporta (una
    línea con el diagnóstico en blanco), porque la atención ocurrió."""
    inicio = datetime.combine(fecha_desde, datetime.min.time())
    fin = datetime.combine(fecha_hasta, datetime.max.time())
    filas: list[dict] = []
    district_ids: set[str] = set()

    q_medica = (select(AtencionMedica, Cita, Patient, ClinicalRecord.record_number, ProgramacionMedica, Empleado, Servicio, Especialidad)
        .join(Cita, Cita.id == AtencionMedica.cita_id)
        .join(Patient, Patient.id == Cita.patient_id)
        .outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id)
        .join(ProgramacionMedica, ProgramacionMedica.id == Cita.programacion_medica_id)
        .outerjoin(Empleado, Empleado.id == AtencionMedica.firmado_por_id)
        .outerjoin(Servicio, Servicio.id == ProgramacionMedica.servicio_id)
        .outerjoin(Especialidad, Especialidad.id == ProgramacionMedica.especialidad_id)
        .where(AtencionMedica.tenant_id == tid, AtencionMedica.estado == "firmado",
               AtencionMedica.firmado_at >= inicio, AtencionMedica.firmado_at <= fin))
    for atencion, cita, paciente, historia, prog, medico, servicio, especialidad in (await db.execute(q_medica)).all():
        district_ids.add(paciente.district_id)
        seguro = await db.scalar(select(Seguro.nombre).where(Seguro.tenant_id == tid, Seguro.is_active.is_(True),
            func.lower(Seguro.nombre) == func.lower(cita.fuente_financiamiento))) if cita.fuente_financiamiento else None
        base = dict(
            fecha_atencion=atencion.firmado_at, origen="CONSULTA_EXTERNA", tipo_atencion=atencion.destino_atencion,
            historia_clinica=historia, dni=paciente.dni, paciente_nombre=paciente.full_name,
            edad=paciente.age, sexo=paciente.gender, district_id=paciente.district_id,
            financiador=seguro or cita.fuente_financiamiento or "No especificado",
            profesional_nombre=medico.nombre_completo if medico else None,
            servicio_o_especialidad=(especialidad.nombre if especialidad else None) or (servicio.nombre if servicio else None),
        )
        dx_rows = (await db.execute(select(AtencionDiagnostico, DiagnosticoCIE10).join(
            DiagnosticoCIE10, DiagnosticoCIE10.id == AtencionDiagnostico.diagnostico_cie10_id
        ).where(AtencionDiagnostico.atencion_medica_id == atencion.id))).all()
        if dx_rows:
            for ad, dx in dx_rows:
                filas.append(dict(base, diagnostico_codigo=dx.codigo_cie10, diagnostico_descripcion=dx.descripcion, diagnostico_tipo=ad.tipo))
        else:
            filas.append(dict(base, diagnostico_codigo=None, diagnostico_descripcion=None, diagnostico_tipo=None))

    q_emerg = (select(AtencionEmergencia, AdmisionEmergencia, Patient, ClinicalRecord.record_number, Empleado)
        .join(AdmisionEmergencia, AdmisionEmergencia.id == AtencionEmergencia.admision_id)
        .join(Patient, Patient.id == AdmisionEmergencia.patient_id)
        .outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id)
        .outerjoin(Empleado, Empleado.id == AtencionEmergencia.medico_id)
        .where(AdmisionEmergencia.tenant_id == tid, AtencionEmergencia.estado == "firmado",
               AtencionEmergencia.firmado_at >= inicio, AtencionEmergencia.firmado_at <= fin))
    for atencion, admision, paciente, historia, medico in (await db.execute(q_emerg)).all():
        district_ids.add(paciente.district_id)
        seguro = await db.scalar(select(Seguro.nombre).where(Seguro.tenant_id == tid, Seguro.is_active.is_(True),
            func.lower(Seguro.nombre) == func.lower(admision.fuente_financiamiento))) if admision.fuente_financiamiento else None
        base = dict(
            fecha_atencion=atencion.firmado_at, origen="EMERGENCIA", tipo_atencion=atencion.destino_atencion,
            historia_clinica=historia, dni=paciente.dni, paciente_nombre=paciente.full_name,
            edad=paciente.age, sexo=paciente.gender, district_id=paciente.district_id,
            financiador=seguro or admision.fuente_financiamiento or "No especificado",
            profesional_nombre=medico.nombre_completo if medico else None,
            servicio_o_especialidad=admision.servicio_emergencia,
        )
        dx_rows = (await db.execute(select(EmergenciaDiagnostico, DiagnosticoCIE10).join(
            DiagnosticoCIE10, DiagnosticoCIE10.id == EmergenciaDiagnostico.diagnostico_cie10_id
        ).where(EmergenciaDiagnostico.atencion_emergencia_id == atencion.id))).all()
        if dx_rows:
            for ed, dx in dx_rows:
                filas.append(dict(base, diagnostico_codigo=dx.codigo_cie10, diagnostico_descripcion=dx.descripcion, diagnostico_tipo=ed.tipo))
        else:
            filas.append(dict(base, diagnostico_codigo=None, diagnostico_descripcion=None, diagnostico_tipo=None))

    nombres = await _nombres_distritos(district_ids)
    for fila in filas:
        fila["distrito_procedencia"] = nombres.get(fila.pop("district_id"), None) or "—"
    filas.sort(key=lambda f: f["fecha_atencion"], reverse=True)
    return filas


async def csv_his(db, tid, fecha_desde, fecha_hasta):
    import csv
    from io import StringIO
    filas = await list_atenciones_his(db, tid, fecha_desde, fecha_hasta)
    keys = ["fecha_atencion", "origen", "tipo_atencion", "historia_clinica", "dni", "paciente_nombre",
            "edad", "sexo", "distrito_procedencia", "financiador", "diagnostico_codigo",
            "diagnostico_descripcion", "diagnostico_tipo", "profesional_nombre", "servicio_o_especialidad"]
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(keys)
    def safe(v):
        value = str(v) if v is not None else ""
        return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else value
    for fila in filas:
        writer.writerow([safe(fila.get(k)) for k in keys])
    return ("﻿" + stream.getvalue()).encode("utf-8")


# ─── Envíos (cierre administrativo del periodo) ─────────────────────────────

async def list_envios(db, tid):
    rows = (await db.scalars(select(HisEnvio).where(HisEnvio.tenant_id == tid)
        .order_by(HisEnvio.periodo.desc()))).all()
    return [columns(e) for e in rows]


async def crear_envio(db, tid, user, data):
    if await db.scalar(select(HisEnvio.id).where(HisEnvio.tenant_id == tid, HisEnvio.periodo == data.periodo)):
        raise HTTPException(409, detail=f"Ya existe un envío registrado para el periodo {data.periodo}")
    total = len(await list_atenciones_his(db, tid, data.fecha_desde, data.fecha_hasta))
    envio = HisEnvio(tenant_id=tid, periodo=data.periodo, fecha_desde=data.fecha_desde, fecha_hasta=data.fecha_hasta,
        total_registros=total, observaciones=data.observaciones, registrado_por=actor(user))
    db.add(envio)
    await db.flush()
    audit(db, tid, user, "HisEnvio", envio.id, "crear", after=columns(envio))
    await db.commit()
    return columns(envio)


async def cerrar_envio(db, tid, user, envio_id, data):
    envio = (await db.execute(select(HisEnvio).where(HisEnvio.id == envio_id, HisEnvio.tenant_id == tid)
        .with_for_update())).scalar_one_or_none()
    if not envio:
        raise HTTPException(404, detail="Envío no encontrado")
    if envio.estado == "enviado":
        raise HTTPException(409, detail="Este envío ya fue marcado como enviado")
    before = columns(envio)
    # Recalcula el total al cerrar -- puede haber cambiado desde que se creó el borrador.
    envio.total_registros = len(await list_atenciones_his(db, tid, envio.fecha_desde, envio.fecha_hasta))
    envio.estado = "enviado"
    envio.fecha_envio = datetime.utcnow()
    if data.observaciones:
        envio.observaciones = data.observaciones
    await db.flush()
    audit(db, tid, user, "HisEnvio", envio.id, "cerrar", before=before, after=columns(envio))
    await db.commit()
    return columns(envio)
