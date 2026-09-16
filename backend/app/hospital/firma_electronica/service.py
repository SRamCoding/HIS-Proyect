import uuid
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.firma_electronica.models import FirmaElectronicaRegistro
from app.hospital.consulta_externa.models import AtencionMedica, Cita, ProgramacionMedica
from app.hospital.emergencia.models import AtencionEmergencia, AdmisionEmergencia
from app.hospital.admision.models import Patient
from app.auth.models import User


async def _empleado_medico_actual(db: AsyncSession, user: dict) -> uuid.UUID | None:
    """Devuelve el empleado_id del usuario si es una cuenta médica válida
    (panel='app', role='medico', vinculada a un Empleado), o None si no lo es
    -- una Bandeja vacía para quien no es médico es más honesto que un error."""
    if not user:
        return None
    usuario = await db.scalar(select(User).where(User.id == uuid.UUID(user["sub"]), User.is_active == True))
    if not usuario or usuario.panel != "app" or usuario.role != "medico" or not usuario.empleado_id:
        return None
    return usuario.empleado_id


async def bandeja(db: AsyncSession, tid: uuid.UUID, user: dict) -> list[dict]:
    empleado_id = await _empleado_medico_actual(db, user)
    if empleado_id is None:
        return []

    pendientes: list[dict] = []

    ce_rows = (await db.execute(select(AtencionMedica, Cita, Patient).join(
        Cita, AtencionMedica.cita_id == Cita.id).join(
        ProgramacionMedica, Cita.programacion_medica_id == ProgramacionMedica.id).join(
        Patient, Cita.patient_id == Patient.id).where(
        AtencionMedica.tenant_id == tid, AtencionMedica.estado == "borrador",
        ProgramacionMedica.medico_id == empleado_id))).all()
    for atencion, cita, paciente in ce_rows:
        pendientes.append({
            "documento_tipo": "ATENCION_MEDICA", "documento_id": atencion.id,
            "patient_id": paciente.id, "paciente_nombre": paciente.full_name, "paciente_dni": paciente.dni,
            "origen": "Consulta Externa", "resumen": (atencion.motivo_consulta or "")[:150],
            "created_at": atencion.created_at,
        })

    em_rows = (await db.execute(select(AtencionEmergencia, Patient).join(
        AdmisionEmergencia, AtencionEmergencia.admision_id == AdmisionEmergencia.id).join(
        Patient, AdmisionEmergencia.patient_id == Patient.id).where(
        AtencionEmergencia.tenant_id == tid, AtencionEmergencia.estado == "borrador",
        (AtencionEmergencia.medico_id.is_(None)) | (AtencionEmergencia.medico_id == empleado_id)))).all()
    for atencion, paciente in em_rows:
        pendientes.append({
            "documento_tipo": "ATENCION_EMERGENCIA", "documento_id": atencion.id,
            "patient_id": paciente.id, "paciente_nombre": paciente.full_name, "paciente_dni": paciente.dni,
            "origen": "Emergencia", "resumen": (atencion.motivo_consulta or "")[:150],
            "created_at": atencion.created_at,
        })

    pendientes.sort(key=lambda p: p["created_at"])
    return pendientes


async def firmar_documento(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    from app.hospital.consulta_externa.service import firmar_atencion_medica
    from app.hospital.emergencia.service import firmar_atencion_emergencia

    if data.documento_tipo == "ATENCION_MEDICA":
        atencion = await db.get(AtencionMedica, data.documento_id)
        if atencion is None or atencion.tenant_id != tid:
            raise HTTPException(404, detail="Documento no encontrado")
        try:
            resultado = await firmar_atencion_medica(db, tid, atencion.cita_id, user=user)
        except ValueError as exc:
            raise HTTPException(400, detail=str(exc)) from exc
    else:
        atencion = await db.get(AtencionEmergencia, data.documento_id)
        if atencion is None or atencion.tenant_id != tid:
            raise HTTPException(404, detail="Documento no encontrado")
        try:
            resultado = await firmar_atencion_emergencia(db, tid, atencion.admision_id, user)
        except ValueError as exc:
            raise HTTPException(400, detail=str(exc)) from exc
    if resultado is None:
        raise HTTPException(404, detail="Documento no encontrado")

    evidencia = resultado.get("cierre_evidencia") or {}
    if not evidencia.get("medico_id") or not evidencia.get("sha256"):
        raise HTTPException(500, detail="La firma se aplicó pero no se pudo generar su evidencia de trazabilidad")

    registro = FirmaElectronicaRegistro(id=uuid.uuid4(), tenant_id=tid, documento_tipo=data.documento_tipo,
        documento_id=data.documento_id, patient_id=await _patient_id_de(db, data),
        firmante_id=uuid.UUID(evidencia["medico_id"]), firmante_nombre=evidencia.get("medico_nombre") or "",
        numero_colegiatura=evidencia.get("colegiatura"), sha256=evidencia["sha256"])
    db.add(registro)
    await db.commit()
    return resultado


async def _patient_id_de(db: AsyncSession, data) -> uuid.UUID:
    """AtencionMedica/AtencionEmergencia no exponen patient_id directo en su dict
    de salida (viene vía Cita/Admision) -- se resuelve aparte solo para el registro."""
    if data.documento_tipo == "ATENCION_MEDICA":
        atencion = await db.get(AtencionMedica, data.documento_id)
        cita = await db.get(Cita, atencion.cita_id)
        return cita.patient_id
    atencion = await db.get(AtencionEmergencia, data.documento_id)
    admision = await db.get(AdmisionEmergencia, atencion.admision_id)
    return admision.patient_id


async def list_registros(db: AsyncSession, tid: uuid.UUID, documento_tipo: str | None = None) -> list[dict]:
    query = select(FirmaElectronicaRegistro, Patient).join(
        Patient, FirmaElectronicaRegistro.patient_id == Patient.id).where(
        FirmaElectronicaRegistro.tenant_id == tid)
    if documento_tipo:
        query = query.where(FirmaElectronicaRegistro.documento_tipo == documento_tipo)
    rows = (await db.execute(query.order_by(FirmaElectronicaRegistro.created_at.desc()))).all()
    return [{
        "id": r.id, "documento_tipo": r.documento_tipo, "documento_id": r.documento_id,
        "paciente_nombre": p.full_name, "paciente_dni": p.dni,
        "firmante_nombre": r.firmante_nombre, "numero_colegiatura": r.numero_colegiatura,
        "sha256": r.sha256, "created_at": r.created_at,
    } for r, p in rows]
