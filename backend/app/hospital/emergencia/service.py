import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.hospital.emergencia.models import AdmisionEmergencia, TriajeEmergencia, AtencionEmergencia, EmergenciaDiagnostico, DestinoEmergencia
from app.hospital.emergencia.schemas import AdmisionEmergenciaCreate, TriajeEmergenciaCreate, AtencionEmergenciaCreate, AtencionEmergenciaUpdate
from app.hospital.admision.models import Patient, ClinicalRecord
from app.sigarh.general.models import DiagnosticoCIE10


def _generar_numero_cuenta(secuencia: int) -> str:
    return f"EMG-{datetime.utcnow().year}-{secuencia:06d}"


async def create_admision(db: AsyncSession, tenant_id: uuid.UUID, data: AdmisionEmergenciaCreate) -> dict:
    count = await db.scalar(select(func.count(AdmisionEmergencia.id)))
    admision = AdmisionEmergencia(tenant_id=tenant_id, numero_cuenta=_generar_numero_cuenta((count or 0) + 1), **data.model_dump())
    db.add(admision)
    await db.commit()
    return await get_admision(db, tenant_id, admision.id)


async def get_admision(db: AsyncSession, tenant_id: uuid.UUID, admision_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(AdmisionEmergencia, Patient, ClinicalRecord, TriajeEmergencia)
        .join(Patient, Patient.id == AdmisionEmergencia.patient_id)
        .outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id)
        .outerjoin(TriajeEmergencia, TriajeEmergencia.admision_id == AdmisionEmergencia.id)
        .where(AdmisionEmergencia.tenant_id == tenant_id, AdmisionEmergencia.id == admision_id)
    )
    row = result.first()
    if not row:
        return None
    admision, paciente, clinical_record, triaje = row
    return _admision_to_dict(admision, paciente, clinical_record, triaje)


async def list_admisiones(db: AsyncSession, tenant_id: uuid.UUID, estado: str | None = None) -> list[dict]:
    query = (
        select(AdmisionEmergencia, Patient, ClinicalRecord, TriajeEmergencia)
        .join(Patient, Patient.id == AdmisionEmergencia.patient_id)
        .outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id)
        .outerjoin(TriajeEmergencia, TriajeEmergencia.admision_id == AdmisionEmergencia.id)
        .where(AdmisionEmergencia.tenant_id == tenant_id)
        .order_by(AdmisionEmergencia.created_at.desc())
    )
    if estado:
        query = query.where(AdmisionEmergencia.estado == estado)
    result = await db.execute(query)
    return [_admision_to_dict(a, p, cr, t) for a, p, cr, t in result.all()]


def _admision_to_dict(admision, paciente, clinical_record, triaje) -> dict:
    return {
        "id": admision.id, "patient_id": admision.patient_id, "paciente_nombre": paciente.full_name,
        "paciente_dni": paciente.dni, "paciente_edad": paciente.age,
        "paciente_hc": clinical_record.record_number if clinical_record else None,
        "numero_cuenta": admision.numero_cuenta, "servicio_emergencia": admision.servicio_emergencia,
        "fuente_financiamiento": admision.fuente_financiamiento,
        "acompanante_nombre": admision.acompanante_nombre, "acompanante_parentesco": admision.acompanante_parentesco,
        "acompanante_telefono": admision.acompanante_telefono, "observaciones": admision.observaciones,
        "estado": admision.estado, "paso_triaje": triaje is not None, "created_at": admision.created_at,
    }


async def create_triaje_emergencia(db: AsyncSession, tenant_id: uuid.UUID, admision_id: uuid.UUID, data: TriajeEmergenciaCreate) -> TriajeEmergencia:
    result = await db.execute(select(AdmisionEmergencia).where(AdmisionEmergencia.tenant_id == tenant_id, AdmisionEmergencia.id == admision_id))
    admision = result.scalar_one_or_none()
    if not admision:
        raise ValueError("Admisión no encontrada")

    existing = await db.execute(select(TriajeEmergencia).where(TriajeEmergencia.admision_id == admision_id))
    if existing.scalar_one_or_none():
        raise ValueError("Esta admisión ya tiene un triaje registrado")

    triaje = TriajeEmergencia(tenant_id=tenant_id, admision_id=admision_id, **data.model_dump())
    db.add(triaje)
    admision.estado = "en_triaje"
    await db.commit()
    await db.refresh(triaje)
    return triaje


async def get_triaje_emergencia(db: AsyncSession, tenant_id: uuid.UUID, admision_id: uuid.UUID) -> TriajeEmergencia | None:
    result = await db.execute(select(TriajeEmergencia).where(TriajeEmergencia.tenant_id == tenant_id, TriajeEmergencia.admision_id == admision_id))
    return result.scalar_one_or_none()


async def create_atencion_emergencia(db: AsyncSession, tenant_id: uuid.UUID, admision_id: uuid.UUID, data: AtencionEmergenciaCreate) -> dict:
    result = await db.execute(select(AdmisionEmergencia).where(AdmisionEmergencia.tenant_id == tenant_id, AdmisionEmergencia.id == admision_id))
    admision = result.scalar_one_or_none()
    if not admision:
        raise ValueError("Admisión no encontrada")

    existing = await db.execute(select(AtencionEmergencia).where(AtencionEmergencia.admision_id == admision_id))
    if existing.scalar_one_or_none():
        raise ValueError("Esta admisión ya tiene una atención registrada")

    atencion = AtencionEmergencia(
        tenant_id=tenant_id, admision_id=admision_id,
        motivo_consulta=data.motivo_consulta, examen_clinico=data.examen_clinico,
        plan_tratamiento=data.plan_tratamiento, observaciones=data.observaciones,
        destino_atencion=data.destino_atencion,
    )
    db.add(atencion)
    await db.flush()
    for dx in data.diagnosticos:
        db.add(EmergenciaDiagnostico(atencion_emergencia_id=atencion.id, diagnostico_cie10_id=dx.diagnostico_cie10_id, tipo=dx.tipo))
    admision.estado = "en_atencion"
    await db.commit()
    return await get_atencion_emergencia(db, tenant_id, admision_id)


async def get_atencion_emergencia(db: AsyncSession, tenant_id: uuid.UUID, admision_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(AtencionEmergencia, AdmisionEmergencia, Patient, TriajeEmergencia)
        .join(AdmisionEmergencia, AdmisionEmergencia.id == AtencionEmergencia.admision_id)
        .join(Patient, Patient.id == AdmisionEmergencia.patient_id)
        .outerjoin(TriajeEmergencia, TriajeEmergencia.admision_id == AdmisionEmergencia.id)
        .where(AtencionEmergencia.tenant_id == tenant_id, AtencionEmergencia.admision_id == admision_id)
    )
    row = result.first()
    if not row:
        return None
    atencion, admision, paciente, triaje = row

    dx_result = await db.execute(
        select(EmergenciaDiagnostico, DiagnosticoCIE10)
        .join(DiagnosticoCIE10, DiagnosticoCIE10.id == EmergenciaDiagnostico.diagnostico_cie10_id)
        .where(EmergenciaDiagnostico.atencion_emergencia_id == atencion.id)
    )
    diagnosticos = [
        {"id": d.id, "diagnostico_cie10_id": d.diagnostico_cie10_id, "codigo_cie10": c.codigo_cie10, "descripcion": c.descripcion, "tipo": d.tipo}
        for d, c in dx_result.all()
    ]

    return {
        "id": atencion.id, "admision_id": atencion.admision_id, "paciente_nombre": paciente.full_name,
        "paciente_dni": paciente.dni, "motivo_consulta": atencion.motivo_consulta,
        "examen_clinico": atencion.examen_clinico, "plan_tratamiento": atencion.plan_tratamiento,
        "observaciones": atencion.observaciones, "destino_atencion": atencion.destino_atencion,
        "estado": atencion.estado, "firmado_at": atencion.firmado_at, "diagnosticos": diagnosticos,
        "triaje": {
            "prioridad": triaje.prioridad, "pulso": triaje.pulso, "temperatura": triaje.temperatura,
            "presion_sistolica": triaje.presion_sistolica, "presion_diastolica": triaje.presion_diastolica,
            "frecuencia_cardiaca": triaje.frecuencia_cardiaca, "frecuencia_respiratoria": triaje.frecuencia_respiratoria,
            "peso": triaje.peso, "talla": triaje.talla, "imc": triaje.imc, "saturacion_o2": triaje.saturacion_o2,
        } if triaje else None,
        "created_at": atencion.created_at,
    }


async def update_atencion_emergencia(db: AsyncSession, tenant_id: uuid.UUID, admision_id: uuid.UUID, data: AtencionEmergenciaUpdate) -> dict | None:
    result = await db.execute(select(AtencionEmergencia).where(AtencionEmergencia.tenant_id == tenant_id, AtencionEmergencia.admision_id == admision_id))
    atencion = result.scalar_one_or_none()
    if not atencion:
        return None
    if atencion.estado == "firmado":
        raise ValueError("No se puede editar una atención ya firmada")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(atencion, field, value)
    await db.commit()
    return await get_atencion_emergencia(db, tenant_id, admision_id)


async def firmar_atencion_emergencia(db: AsyncSession, tenant_id: uuid.UUID, admision_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(AtencionEmergencia, AdmisionEmergencia)
        .join(AdmisionEmergencia, AdmisionEmergencia.id == AtencionEmergencia.admision_id)
        .where(AtencionEmergencia.tenant_id == tenant_id, AtencionEmergencia.admision_id == admision_id)
    )
    row = result.first()
    atencion, admision = row if row else (None, None)
    if not atencion:
        return None
    if atencion.estado == "firmado":
        raise ValueError("Esta atención ya está firmada")
    atencion.estado = "firmado"
    atencion.firmado_at = datetime.utcnow()
    finales = {"AMBULATORIA", "ALTA", "FALLECIDO"}
    db.add(DestinoEmergencia(
        tenant_id=tenant_id,
        atencion_id=atencion.id,
        destino=atencion.destino_atencion,
        estado="completado" if atencion.destino_atencion in finales else "pendiente",
        resolved_at=datetime.utcnow() if atencion.destino_atencion in finales else None,
    ))
    admision.estado = {
        "ALTA": "alta",
        "FALLECIDO": "fallecido",
        "AMBULATORIA": "atendido",
    }.get(atencion.destino_atencion, "derivado")
    await db.commit()
    return await get_atencion_emergencia(db, tenant_id, admision_id)


async def list_atenciones_emergencia(db: AsyncSession, tenant_id: uuid.UUID, destino: str | None = None) -> list[dict]:
    query = (
        select(AtencionEmergencia, AdmisionEmergencia, Patient, TriajeEmergencia, DestinoEmergencia)
        .join(AdmisionEmergencia, AdmisionEmergencia.id == AtencionEmergencia.admision_id)
        .join(Patient, Patient.id == AdmisionEmergencia.patient_id)
        .outerjoin(TriajeEmergencia, TriajeEmergencia.admision_id == AdmisionEmergencia.id)
        .outerjoin(DestinoEmergencia, DestinoEmergencia.atencion_id == AtencionEmergencia.id)
        .where(AtencionEmergencia.tenant_id == tenant_id)
        .order_by(AtencionEmergencia.created_at.desc())
    )
    if destino:
        query = query.where(AtencionEmergencia.destino_atencion == destino.upper())
    rows = (await db.execute(query)).all()
    return [{
        "id": a.id, "admision_id": adm.id, "numero_cuenta": adm.numero_cuenta,
        "paciente_nombre": patient.full_name, "paciente_dni": patient.dni,
        "prioridad": triage.prioridad if triage else None, "motivo_consulta": a.motivo_consulta,
        "destino_atencion": a.destino_atencion, "estado": a.estado,
        "destino_estado": derivacion.estado if derivacion else None,
        "created_at": a.created_at, "firmado_at": a.firmado_at,
    } for a, adm, patient, triage, derivacion in rows]


async def list_destinos_emergencia(db: AsyncSession, tenant_id: uuid.UUID, destino: str | None = None, estado: str | None = None) -> list[dict]:
    query = (
        select(DestinoEmergencia, AtencionEmergencia, AdmisionEmergencia, Patient)
        .join(AtencionEmergencia, AtencionEmergencia.id == DestinoEmergencia.atencion_id)
        .join(AdmisionEmergencia, AdmisionEmergencia.id == AtencionEmergencia.admision_id)
        .join(Patient, Patient.id == AdmisionEmergencia.patient_id)
        .where(DestinoEmergencia.tenant_id == tenant_id)
        .order_by(DestinoEmergencia.created_at.desc())
    )
    if destino:
        query = query.where(DestinoEmergencia.destino == destino.upper())
    if estado:
        query = query.where(DestinoEmergencia.estado == estado.lower())
    rows = (await db.execute(query)).all()
    return [{
        "id": d.id, "atencion_id": a.id, "admision_id": adm.id,
        "numero_cuenta": adm.numero_cuenta, "paciente_nombre": patient.full_name,
        "paciente_dni": patient.dni, "destino": d.destino, "estado": d.estado,
        "observacion": d.observacion, "created_at": d.created_at, "resolved_at": d.resolved_at,
    } for d, a, adm, patient in rows]


async def resolver_destino_emergencia(db: AsyncSession, tenant_id: uuid.UUID, destino_id: uuid.UUID, observacion: str | None) -> dict | None:
    destino = await db.scalar(select(DestinoEmergencia).where(DestinoEmergencia.id == destino_id, DestinoEmergencia.tenant_id == tenant_id))
    if not destino:
        return None
    if destino.estado == "completado":
        raise ValueError("El destino ya fue completado")
    destino.estado = "completado"
    destino.observacion = observacion
    destino.resolved_at = datetime.utcnow()
    atencion = await db.scalar(select(AtencionEmergencia).where(AtencionEmergencia.id == destino.atencion_id))
    admision = await db.scalar(select(AdmisionEmergencia).where(AdmisionEmergencia.id == atencion.admision_id))
    admision.estado = "atendido"
    await db.commit()
    row = (await db.execute(
        select(DestinoEmergencia, AtencionEmergencia, AdmisionEmergencia, Patient)
        .join(AtencionEmergencia, AtencionEmergencia.id == DestinoEmergencia.atencion_id)
        .join(AdmisionEmergencia, AdmisionEmergencia.id == AtencionEmergencia.admision_id)
        .join(Patient, Patient.id == AdmisionEmergencia.patient_id)
        .where(DestinoEmergencia.id == destino_id, DestinoEmergencia.tenant_id == tenant_id)
    )).one()
    d, a, adm, patient = row
    return {
        "id": d.id, "atencion_id": a.id, "admision_id": adm.id,
        "numero_cuenta": adm.numero_cuenta, "paciente_nombre": patient.full_name,
        "paciente_dni": patient.dni, "destino": d.destino, "estado": d.estado,
        "observacion": d.observacion, "created_at": d.created_at, "resolved_at": d.resolved_at,
    }
