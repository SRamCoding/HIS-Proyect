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


async def get_seguros(db: AsyncSession, tenant_id: uuid.UUID) -> list[dict]:
    from app.sigarh.config_financiera.models import Seguro
    result = await db.execute(
        select(Seguro).where(Seguro.tenant_id == tenant_id, Seguro.is_active == True).order_by(Seguro.nombre)
    )
    return [{"id": s.id, "nombre": s.nombre} for s in result.scalars().all()]


async def create_admision(db: AsyncSession, tenant_id: uuid.UUID, data: AdmisionEmergenciaCreate) -> dict:
    paciente_valido = await db.scalar(
        select(Patient.id).where(Patient.id == data.patient_id, Patient.tenant_id == tenant_id)
    )
    if not paciente_valido:
        raise ValueError("El paciente no pertenece a este hospital")
    count = await db.scalar(select(func.count(AdmisionEmergencia.id)).where(AdmisionEmergencia.tenant_id == tenant_id))
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

    dx_ids = {dx.diagnostico_cie10_id for dx in data.diagnosticos}
    if dx_ids:
        validos = set((await db.execute(
            select(DiagnosticoCIE10.id).where(DiagnosticoCIE10.id.in_(dx_ids), DiagnosticoCIE10.tenant_id == tenant_id)
        )).scalars().all())
        if validos != dx_ids:
            raise ValueError("Uno o más diagnósticos no pertenecen a este hospital")

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
        "estado": atencion.estado, "firmado_at": atencion.firmado_at, "firmado_por_id": atencion.firmado_por_id,
        "cierre_evidencia": atencion.cierre_evidencia, "diagnosticos": diagnosticos,
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


async def validar_autor_clinico_emergencia(db: AsyncSession, tenant_id: uuid.UUID, user: dict):
    """Mismo criterio que validar_autor_clinico de Consulta Externa (cuenta médica
    vinculada, profesión MED, colegiatura habilitada) -- Emergencia no tiene una
    ProgramacionMedica que preasigne al médico, así que el médico responsable
    queda fijado recién al firmar: quien firma es quien asume la atención."""
    from app.auth.models import User
    from app.sigarh.rrhh.models import Empleado
    from app.sigarh.mantenimiento.models import Profesion
    usuario = await db.scalar(select(User).where(User.id == uuid.UUID(user["sub"]), User.is_active == True)) if user else None
    if not usuario or usuario.panel != "app" or usuario.role != "medico" or not usuario.empleado_id:
        raise ValueError("La atención requiere una cuenta médica vinculada al empleado desde SIGARH > Mantenimiento > Usuarios.")
    medico = await db.scalar(select(Empleado).where(Empleado.id == usuario.empleado_id, Empleado.tenant_id == tenant_id, Empleado.is_active == True))
    profesion = await db.scalar(select(Profesion.codigo).where(Profesion.id == medico.profesion_id, Profesion.tenant_id == tenant_id)) if medico else None
    if not medico or profesion != "MED" or not medico.habilitado_colegio or not (medico.numero_cmp or medico.numero_colegiatura):
        raise ValueError("Solo un médico con colegiatura y habilitación registrada puede firmar la atención.")
    return usuario, medico


async def firmar_atencion_emergencia(db: AsyncSession, tenant_id: uuid.UUID, admision_id: uuid.UUID, user: dict | None = None) -> dict | None:
    import hashlib, json
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
    usuario, medico = await validar_autor_clinico_emergencia(db, tenant_id, user)
    contenido = {"motivo_consulta": atencion.motivo_consulta, "examen_clinico": atencion.examen_clinico,
        "plan_tratamiento": atencion.plan_tratamiento, "destino_atencion": atencion.destino_atencion}
    atencion.cierre_evidencia = {"tipo": "CIERRE_INTERNO_SIN_CERTIFICADO_DIGITAL", "usuario_id": str(usuario.id), "usuario_nombre": usuario.name,
        "medico_id": str(medico.id), "medico_nombre": medico.nombre_completo, "colegiatura": medico.numero_cmp or medico.numero_colegiatura,
        "contenido": contenido, "sha256": hashlib.sha256(json.dumps(contenido, sort_keys=True, ensure_ascii=False).encode()).hexdigest()}
    atencion.medico_id = atencion.medico_id or medico.id
    atencion.firmado_por_id = medico.id
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


# Destinos que generan un registro real en otro modulo al ser admitidos --
# HOSPITALIZACION en Hospitalizacion, INTERCONSULTA en Hospitalizacion,
# REFERENCIA en Referencias. Resolverlos aqui sin pasar por esos modulos
# dejaria el destino en "completado" sin la hospitalizacion/interconsulta/
# referencia real creada -- por eso resolver_destino_emergencia los rechaza.
DESTINOS_CON_ADMISION_PROPIA = {"HOSPITALIZACION", "INTERCONSULTA", "REFERENCIA"}


async def resolver_destino_emergencia(db: AsyncSession, tenant_id: uuid.UUID, destino_id: uuid.UUID, observacion: str | None) -> dict | None:
    destino = await db.scalar(select(DestinoEmergencia).where(DestinoEmergencia.id == destino_id, DestinoEmergencia.tenant_id == tenant_id))
    if not destino:
        return None
    if destino.estado == "completado":
        raise ValueError("El destino ya fue completado")
    if destino.destino in DESTINOS_CON_ADMISION_PROPIA:
        raise ValueError(
            f"Los destinos de tipo {destino.destino} se resuelven admitiéndolos en su módulo "
            "correspondiente (Hospitalización, Interconsultas o Referencias), no aquí."
        )
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
