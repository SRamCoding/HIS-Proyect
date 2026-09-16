import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.procedimientos.models import (
    ProcedimientosCorrelativo, ProcedimientoAsignacion, AtencionProcedimiento,
)
from app.hospital.admision.models import Patient
from app.hospital.consulta_externa.models import AtencionMedica, Cita, Hospitalizacion
from app.hospital.emergencia.models import AtencionEmergencia, AdmisionEmergencia
from app.sigarh.rrhh.models import Empleado
from app.sigarh.general.models import TiempoProcedimiento


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


async def _siguiente(db: AsyncSession, tid: uuid.UUID) -> str:
    stmt = insert(ProcedimientosCorrelativo).values(tenant_id=tid, tipo="ATENCION", valor=1)
    stmt = stmt.on_conflict_do_update(index_elements=["tenant_id", "tipo"],
        set_={"valor": ProcedimientosCorrelativo.valor + 1}).returning(ProcedimientosCorrelativo.valor)
    n = await db.scalar(stmt)
    return f"PROC-{tid.hex[:6].upper()}-{n:08d}"


# ─── Catálogo (reutiliza TiempoProcedimiento de SIGARH > General) ───────────

async def list_catalogo(db: AsyncSession, tid: uuid.UUID, q: str = "") -> list[dict]:
    query = select(TiempoProcedimiento).where(TiempoProcedimiento.tenant_id == tid, TiempoProcedimiento.is_active.is_(True))
    if q:
        query = query.where(TiempoProcedimiento.nombre.icontains(q, autoescape=True))
    procedimientos = (await db.scalars(query.order_by(TiempoProcedimiento.nombre))).all()
    return [{"id": p.id, "codigo": p.codigo, "nombre": p.nombre, "duracion_minutos": p.duracion_minutos} for p in procedimientos]


async def list_pacientes(db: AsyncSession, tid: uuid.UUID, q: str = "") -> list[dict]:
    query = select(Patient).where(Patient.tenant_id == tid, Patient.is_active.is_(True))
    for term in q.split():
        query = query.where(or_(Patient.dni.icontains(term, autoescape=True),
            Patient.first_name.icontains(term, autoescape=True),
            Patient.last_name_paterno.icontains(term, autoescape=True),
            Patient.last_name_materno.icontains(term, autoescape=True)))
    rows = (await db.scalars(query.order_by(Patient.last_name_paterno, Patient.first_name).limit(50))).all()
    return [{"id": p.id, "nombre": p.full_name, "documento": p.dni} for p in rows]


async def list_empleados(db: AsyncSession, tid: uuid.UUID, q: str = "") -> list[dict]:
    query = select(Empleado).where(Empleado.tenant_id == tid, Empleado.is_active.is_(True))
    for term in q.split():
        query = query.where(or_(Empleado.nombre_completo.icontains(term, autoescape=True),
            Empleado.dni.icontains(term, autoescape=True)))
    rows = (await db.scalars(query.order_by(Empleado.apellido_paterno, Empleado.apellido_materno,
        Empleado.nombres).limit(100))).all()
    return [{"id": e.id, "nombre": e.nombre_completo, "documento": e.dni} for e in rows]


# ─── Asignaciones (personal habilitado por procedimiento) ───────────────────

async def crear_asignacion(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    procedimiento = await db.get(TiempoProcedimiento, data.tiempo_procedimiento_id)
    if procedimiento is None or procedimiento.tenant_id != tid:
        raise HTTPException(404, detail="Procedimiento no encontrado en el catálogo")
    empleado = await db.get(Empleado, data.empleado_id)
    if empleado is None or empleado.tenant_id != tid:
        raise HTTPException(404, detail="Empleado no encontrado")
    existente = await db.scalar(select(ProcedimientoAsignacion).where(
        ProcedimientoAsignacion.tiempo_procedimiento_id == data.tiempo_procedimiento_id,
        ProcedimientoAsignacion.empleado_id == data.empleado_id))
    if existente:
        if existente.is_active:
            raise HTTPException(409, detail="Este empleado ya está habilitado para este procedimiento")
        existente.is_active = True
    else:
        db.add(ProcedimientoAsignacion(id=uuid.uuid4(), tenant_id=tid, tiempo_procedimiento_id=data.tiempo_procedimiento_id,
            empleado_id=data.empleado_id))
    await db.commit()
    return {"tiempo_procedimiento_id": data.tiempo_procedimiento_id, "tiempo_procedimiento_nombre": procedimiento.nombre,
            "empleado_id": data.empleado_id, "empleado_nombre": empleado.nombre_completo}


async def desasignar(db: AsyncSession, tid: uuid.UUID, user: dict, tiempo_procedimiento_id: uuid.UUID, empleado_id: uuid.UUID):
    asignacion = await db.scalar(select(ProcedimientoAsignacion).where(
        ProcedimientoAsignacion.tenant_id == tid, ProcedimientoAsignacion.tiempo_procedimiento_id == tiempo_procedimiento_id,
        ProcedimientoAsignacion.empleado_id == empleado_id))
    if asignacion is None or not asignacion.is_active:
        raise HTTPException(404, detail="Asignación no encontrada")
    asignacion.is_active = False
    await db.commit()
    return {"ok": True}


async def list_asignaciones(db: AsyncSession, tid: uuid.UUID, tiempo_procedimiento_id: uuid.UUID | None = None) -> list[dict]:
    query = select(ProcedimientoAsignacion, TiempoProcedimiento, Empleado).join(
        TiempoProcedimiento, ProcedimientoAsignacion.tiempo_procedimiento_id == TiempoProcedimiento.id).join(
        Empleado, ProcedimientoAsignacion.empleado_id == Empleado.id).where(
        ProcedimientoAsignacion.tenant_id == tid, ProcedimientoAsignacion.is_active.is_(True))
    if tiempo_procedimiento_id:
        query = query.where(ProcedimientoAsignacion.tiempo_procedimiento_id == tiempo_procedimiento_id)
    rows = (await db.execute(query.order_by(TiempoProcedimiento.nombre))).all()
    return [{"id": a.id, "tiempo_procedimiento_id": p.id, "tiempo_procedimiento_nombre": p.nombre,
             "empleado_id": e.id, "empleado_nombre": e.nombre_completo} for a, p, e in rows]


# ─── Atenciones (ejecución del procedimiento sobre un paciente) ────────────

async def _resolver_patient_id(db: AsyncSession, tid: uuid.UUID, data) -> uuid.UUID:
    if data.atencion_medica_id:
        atencion = await db.get(AtencionMedica, data.atencion_medica_id)
        if atencion is None or atencion.tenant_id != tid:
            raise HTTPException(404, detail="Atención médica no encontrada")
        cita = await db.get(Cita, atencion.cita_id)
        return cita.patient_id
    if data.atencion_emergencia_id:
        atencion = await db.get(AtencionEmergencia, data.atencion_emergencia_id)
        if atencion is None or atencion.tenant_id != tid:
            raise HTTPException(404, detail="Atención de emergencia no encontrada")
        admision = await db.get(AdmisionEmergencia, atencion.admision_id)
        return admision.patient_id
    if data.hospitalizacion_id:
        hospitalizacion = await db.get(Hospitalizacion, data.hospitalizacion_id)
        if hospitalizacion is None or hospitalizacion.tenant_id != tid:
            raise HTTPException(404, detail="Hospitalización no encontrada")
        return hospitalizacion.patient_id
    return data.patient_id


async def crear_atencion(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    procedimiento = await db.get(TiempoProcedimiento, data.tiempo_procedimiento_id)
    if procedimiento is None or procedimiento.tenant_id != tid:
        raise HTTPException(404, detail="Procedimiento no encontrado en el catálogo")

    habilitado = await db.scalar(select(ProcedimientoAsignacion.id).where(
        ProcedimientoAsignacion.tiempo_procedimiento_id == data.tiempo_procedimiento_id,
        ProcedimientoAsignacion.empleado_id == data.empleado_ejecutor_id, ProcedimientoAsignacion.is_active.is_(True)))
    if not habilitado:
        raise HTTPException(400, detail="El empleado no está habilitado para realizar este procedimiento")

    patient_id = await _resolver_patient_id(db, tid, data)
    paciente = await db.get(Patient, patient_id)
    if paciente is None or paciente.tenant_id != tid:
        raise HTTPException(404, detail="Paciente no encontrado")

    numero = await _siguiente(db, tid)
    atencion = AtencionProcedimiento(id=uuid.uuid4(), tenant_id=tid, atencion_medica_id=data.atencion_medica_id,
        atencion_emergencia_id=data.atencion_emergencia_id, hospitalizacion_id=data.hospitalizacion_id,
        patient_id=patient_id, tiempo_procedimiento_id=data.tiempo_procedimiento_id,
        empleado_ejecutor_id=data.empleado_ejecutor_id, numero_atencion=numero,
        fecha_hora=data.fecha_hora or datetime.utcnow(), consentimiento_informado=data.consentimiento_informado,
        registrado_por=actor(user))
    db.add(atencion)
    await db.flush()
    await db.commit()
    return await _atencion_out(db, atencion)


async def _atencion_out(db: AsyncSession, a: AtencionProcedimiento) -> dict:
    paciente = await db.get(Patient, a.patient_id)
    procedimiento = await db.get(TiempoProcedimiento, a.tiempo_procedimiento_id)
    empleado = await db.get(Empleado, a.empleado_ejecutor_id)
    return {
        "id": a.id, "numero_atencion": a.numero_atencion, "patient_id": a.patient_id,
        "paciente_nombre": paciente.full_name if paciente else None, "paciente_dni": paciente.dni if paciente else None,
        "origen": "Consulta Externa" if a.atencion_medica_id else "Emergencia" if a.atencion_emergencia_id else "Hospitalización" if a.hospitalizacion_id else "Directo",
        "tiempo_procedimiento_id": a.tiempo_procedimiento_id, "procedimiento_nombre": procedimiento.nombre if procedimiento else None,
        "empleado_ejecutor_id": a.empleado_ejecutor_id, "empleado_ejecutor_nombre": empleado.nombre_completo if empleado else None,
        "fecha_hora": a.fecha_hora, "consentimiento_informado": a.consentimiento_informado,
        "hallazgos": a.hallazgos, "complicaciones": a.complicaciones, "motivo_cancelacion": a.motivo_cancelacion,
        "estado": a.estado, "created_at": a.created_at,
    }


async def list_atenciones(db: AsyncSession, tid: uuid.UUID, estado: str | None = None,
                           patient_id: uuid.UUID | None = None) -> list[dict]:
    query = select(AtencionProcedimiento).where(AtencionProcedimiento.tenant_id == tid)
    if estado:
        query = query.where(AtencionProcedimiento.estado == estado)
    if patient_id:
        query = query.where(AtencionProcedimiento.patient_id == patient_id)
    atenciones = (await db.scalars(query.order_by(AtencionProcedimiento.fecha_hora.desc()))).all()
    return [await _atencion_out(db, a) for a in atenciones]


async def confirmar_consentimiento(db: AsyncSession, tid: uuid.UUID, user: dict, atencion_id: uuid.UUID) -> dict:
    a = await db.get(AtencionProcedimiento, atencion_id)
    if a is None or a.tenant_id != tid:
        raise HTTPException(404, detail="Atención no encontrada")
    if a.estado != "programado":
        raise HTTPException(409, detail=f"La atención está en estado '{a.estado}'")
    a.consentimiento_informado = True
    await db.commit()
    return await _atencion_out(db, a)


async def realizar_atencion(db: AsyncSession, tid: uuid.UUID, user: dict, atencion_id: uuid.UUID, data) -> dict:
    a = await db.get(AtencionProcedimiento, atencion_id)
    if a is None or a.tenant_id != tid:
        raise HTTPException(404, detail="Atención no encontrada")
    if a.estado != "programado":
        raise HTTPException(409, detail=f"La atención está en estado '{a.estado}'")
    if not a.consentimiento_informado:
        raise HTTPException(400, detail="No se puede realizar el procedimiento sin consentimiento informado (Ley N.° 26842, art. 4)")
    a.estado = "realizado"
    a.hallazgos = data.hallazgos
    a.complicaciones = data.complicaciones
    await db.commit()
    return await _atencion_out(db, a)


async def cancelar_atencion(db: AsyncSession, tid: uuid.UUID, user: dict, atencion_id: uuid.UUID, data) -> dict:
    a = await db.get(AtencionProcedimiento, atencion_id)
    if a is None or a.tenant_id != tid:
        raise HTTPException(404, detail="Atención no encontrada")
    if a.estado != "programado":
        raise HTTPException(409, detail=f"La atención está en estado '{a.estado}'")
    a.estado = "cancelado"
    a.motivo_cancelacion = data.motivo
    await db.commit()
    return await _atencion_out(db, a)
