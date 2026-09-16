import uuid
from datetime import date
from fastapi import HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.hemodialisis.models import PacienteHemodialisis, SesionHemodialisis
from app.hospital.admision.models import Patient
from app.sigarh.general.models import DiagnosticoCIE10
from app.sigarh.rrhh.models import Empleado

_TRANSICIONES_SESION = {
    "programada": {"en_curso", "suspendida", "no_asistio"},
    "en_curso": {"completada", "suspendida"},
}


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


# ─── Hemodiálisis: programa de pacientes ────────────────────────────────────

async def crear_paciente(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    paciente = await db.get(Patient, data.patient_id)
    if paciente is None or paciente.tenant_id != tid:
        raise HTTPException(404, detail="Paciente no encontrado")
    existente = await db.scalar(select(PacienteHemodialisis).where(
        PacienteHemodialisis.tenant_id == tid, PacienteHemodialisis.patient_id == data.patient_id))
    if existente:
        raise HTTPException(409, detail="Este paciente ya está inscrito en el programa de hemodiálisis")

    hd = PacienteHemodialisis(id=uuid.uuid4(), tenant_id=tid, patient_id=data.patient_id,
        diagnostico_id=data.diagnostico_id, medico_nefrologo_id=data.medico_nefrologo_id,
        fecha_ingreso_programa=data.fecha_ingreso_programa or date.today(),
        acceso_vascular_tipo=data.acceso_vascular_tipo, fecha_creacion_acceso=data.fecha_creacion_acceso,
        peso_seco_kg=data.peso_seco_kg, turno_habitual=data.turno_habitual,
        frecuencia_semanal=data.frecuencia_semanal, observaciones=data.observaciones, registrado_por=actor(user))
    db.add(hd)
    await db.flush()
    await db.commit()
    return await _paciente_out(db, hd)


async def _paciente_out(db: AsyncSession, hd: PacienteHemodialisis) -> dict:
    paciente = await db.get(Patient, hd.patient_id)
    diagnostico = await db.get(DiagnosticoCIE10, hd.diagnostico_id) if hd.diagnostico_id else None
    medico = await db.get(Empleado, hd.medico_nefrologo_id) if hd.medico_nefrologo_id else None
    ultima_sesion = await db.scalar(select(func.max(SesionHemodialisis.fecha)).where(
        SesionHemodialisis.paciente_hemodialisis_id == hd.id, SesionHemodialisis.estado == "completada"))
    return {
        "id": hd.id, "patient_id": hd.patient_id, "paciente_nombre": paciente.full_name if paciente else None,
        "paciente_dni": paciente.dni if paciente else None,
        "diagnostico_id": hd.diagnostico_id,
        "diagnostico": f"{diagnostico.codigo_cie10} · {diagnostico.descripcion}" if diagnostico else None,
        "medico_nefrologo_id": hd.medico_nefrologo_id, "medico_nefrologo_nombre": medico.nombre_completo if medico else None,
        "fecha_ingreso_programa": hd.fecha_ingreso_programa, "acceso_vascular_tipo": hd.acceso_vascular_tipo,
        "fecha_creacion_acceso": hd.fecha_creacion_acceso, "peso_seco_kg": hd.peso_seco_kg,
        "turno_habitual": hd.turno_habitual, "frecuencia_semanal": hd.frecuencia_semanal,
        "estado": hd.estado, "fecha_estado": hd.fecha_estado, "observaciones": hd.observaciones,
        "ultima_sesion_completada": ultima_sesion,
    }


async def list_pacientes(db: AsyncSession, tid: uuid.UUID, estado: str | None = None, q: str = "") -> list[dict]:
    query = select(PacienteHemodialisis).where(PacienteHemodialisis.tenant_id == tid)
    if estado:
        query = query.where(PacienteHemodialisis.estado == estado)
    if q:
        query = query.join(Patient, PacienteHemodialisis.patient_id == Patient.id).where(or_(
            Patient.dni.icontains(q, autoescape=True), Patient.first_name.icontains(q, autoescape=True),
            Patient.last_name_paterno.icontains(q, autoescape=True)))
    pacientes = (await db.scalars(query.order_by(PacienteHemodialisis.created_at.desc()))).all()
    return [await _paciente_out(db, p) for p in pacientes]


async def get_paciente(db: AsyncSession, tid: uuid.UUID, paciente_id: uuid.UUID) -> dict:
    hd = await db.get(PacienteHemodialisis, paciente_id)
    if hd is None or hd.tenant_id != tid:
        raise HTTPException(404, detail="Paciente de hemodiálisis no encontrado")
    return await _paciente_out(db, hd)


async def update_paciente(db: AsyncSession, tid: uuid.UUID, user: dict, paciente_id: uuid.UUID, data) -> dict:
    hd = await db.get(PacienteHemodialisis, paciente_id)
    if hd is None or hd.tenant_id != tid:
        raise HTTPException(404, detail="Paciente de hemodiálisis no encontrado")
    cambios = data.model_dump(exclude_unset=True)
    for k, v in cambios.items():
        setattr(hd, k, v)
    await db.commit()
    return await _paciente_out(db, hd)


async def cambiar_estado_paciente(db: AsyncSession, tid: uuid.UUID, user: dict, paciente_id: uuid.UUID, data) -> dict:
    hd = await db.get(PacienteHemodialisis, paciente_id)
    if hd is None or hd.tenant_id != tid:
        raise HTTPException(404, detail="Paciente de hemodiálisis no encontrado")
    if hd.estado != "activo":
        raise HTTPException(409, detail=f"El paciente ya está en estado '{hd.estado}'")

    hd.estado = data.estado
    hd.fecha_estado = data.fecha_estado or date.today()
    if data.observaciones:
        hd.observaciones = data.observaciones
    await db.commit()
    return await _paciente_out(db, hd)


# ─── Sesiones ────────────────────────────────────────────────────────────

def _sesion_out(s: SesionHemodialisis) -> dict:
    return {
        "id": s.id, "paciente_hemodialisis_id": s.paciente_hemodialisis_id, "fecha": s.fecha, "turno": s.turno,
        "numero_maquina": s.numero_maquina, "hora_inicio": s.hora_inicio, "hora_fin": s.hora_fin,
        "tiempo_sesion_horas": s.tiempo_sesion_horas, "peso_pre_kg": s.peso_pre_kg, "peso_post_kg": s.peso_post_kg,
        "ultrafiltracion_litros": s.ultrafiltracion_litros,
        "presion_pre_sistolica": s.presion_pre_sistolica, "presion_pre_diastolica": s.presion_pre_diastolica,
        "presion_post_sistolica": s.presion_post_sistolica, "presion_post_diastolica": s.presion_post_diastolica,
        "acceso_vascular_utilizado": s.acceso_vascular_utilizado, "heparinizacion": s.heparinizacion,
        "complicaciones": s.complicaciones, "estado": s.estado, "observaciones": s.observaciones,
    }


async def crear_sesion(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    hd = await db.get(PacienteHemodialisis, data.paciente_hemodialisis_id)
    if hd is None or hd.tenant_id != tid:
        raise HTTPException(404, detail="Paciente de hemodiálisis no encontrado")
    if hd.estado != "activo":
        raise HTTPException(409, detail="Solo se pueden programar sesiones para pacientes activos en el programa")

    ultrafiltracion = data.ultrafiltracion_litros
    if ultrafiltracion is None and data.peso_pre_kg is not None and data.peso_post_kg is not None:
        ultrafiltracion = round(data.peso_pre_kg - data.peso_post_kg, 2)

    sesion = SesionHemodialisis(id=uuid.uuid4(), tenant_id=tid, paciente_hemodialisis_id=data.paciente_hemodialisis_id,
        fecha=data.fecha or date.today(), turno=data.turno, numero_maquina=data.numero_maquina,
        hora_inicio=data.hora_inicio, hora_fin=data.hora_fin, peso_pre_kg=data.peso_pre_kg,
        peso_post_kg=data.peso_post_kg, ultrafiltracion_litros=ultrafiltracion,
        presion_pre_sistolica=data.presion_pre_sistolica, presion_pre_diastolica=data.presion_pre_diastolica,
        presion_post_sistolica=data.presion_post_sistolica, presion_post_diastolica=data.presion_post_diastolica,
        acceso_vascular_utilizado=data.acceso_vascular_utilizado or hd.acceso_vascular_tipo,
        heparinizacion=data.heparinizacion, complicaciones=data.complicaciones,
        observaciones=data.observaciones, registrado_por=actor(user))
    db.add(sesion)
    await db.flush()
    await db.commit()
    return _sesion_out(sesion)


async def list_sesiones(db: AsyncSession, tid: uuid.UUID, paciente_hemodialisis_id: uuid.UUID | None = None,
                         fecha: date | None = None, estado: str | None = None) -> list[dict]:
    query = select(SesionHemodialisis, Patient).join(
        PacienteHemodialisis, SesionHemodialisis.paciente_hemodialisis_id == PacienteHemodialisis.id).join(
        Patient, PacienteHemodialisis.patient_id == Patient.id).where(SesionHemodialisis.tenant_id == tid)
    if paciente_hemodialisis_id:
        query = query.where(SesionHemodialisis.paciente_hemodialisis_id == paciente_hemodialisis_id)
    if fecha:
        query = query.where(SesionHemodialisis.fecha == fecha)
    if estado:
        query = query.where(SesionHemodialisis.estado == estado)
    rows = (await db.execute(query.order_by(SesionHemodialisis.fecha.desc(), SesionHemodialisis.turno))).all()
    resultado = []
    for s, p in rows:
        item = _sesion_out(s)
        item["paciente_nombre"] = p.full_name
        item["paciente_dni"] = p.dni
        resultado.append(item)
    return resultado


async def cambiar_estado_sesion(db: AsyncSession, tid: uuid.UUID, user: dict, sesion_id: uuid.UUID, data) -> dict:
    sesion = await db.get(SesionHemodialisis, sesion_id)
    if sesion is None or sesion.tenant_id != tid:
        raise HTTPException(404, detail="Sesión no encontrada")
    permitidas = _TRANSICIONES_SESION.get(sesion.estado, set())
    if data.estado not in permitidas:
        raise HTTPException(409, detail=f"No se puede pasar de '{sesion.estado}' a '{data.estado}'")

    sesion.estado = data.estado
    if data.hora_fin:
        sesion.hora_fin = data.hora_fin
    if data.peso_post_kg is not None:
        sesion.peso_post_kg = data.peso_post_kg
        if sesion.peso_pre_kg is not None and sesion.ultrafiltracion_litros is None:
            sesion.ultrafiltracion_litros = round(sesion.peso_pre_kg - data.peso_post_kg, 2)
    if data.complicaciones:
        sesion.complicaciones = data.complicaciones
    if data.observaciones:
        sesion.observaciones = data.observaciones

    await db.commit()
    return _sesion_out(sesion)
