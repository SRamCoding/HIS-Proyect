import uuid
from datetime import date, datetime
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.epidemiologia.models import EpidemiologiaCorrelativo, FichaEpidemiologica
from app.hospital.admision.models import Patient
from app.hospital.consulta_externa.models import AtencionMedica, Cita
from app.hospital.emergencia.models import AtencionEmergencia, AdmisionEmergencia
from app.sigarh.rrhh.models import Empleado
from app.sigarh.mantenimiento.models import Profesion
from app.sigarh.general.models import DiagnosticoCIE10
from app.admin.auditoria.models import AuditLog


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


def audit(db, tid, user, model, obj_id, action, before=None, after=None):
    db.add(AuditLog(tenant_id=tid, user_id=uuid.UUID(user["sub"]), user_name=user.get("name"),
        model=model, model_id=str(obj_id), action=action,
        old_values=jsonable_encoder(before), new_values=jsonable_encoder(after)))


async def _siguiente(db: AsyncSession, tid: uuid.UUID, tipo: str) -> str:
    stmt = insert(EpidemiologiaCorrelativo).values(tenant_id=tid, tipo=tipo, valor=1)
    stmt = stmt.on_conflict_do_update(index_elements=["tenant_id", "tipo"],
        set_={"valor": EpidemiologiaCorrelativo.valor + 1}).returning(EpidemiologiaCorrelativo.valor)
    n = await db.scalar(stmt)
    return f"{tipo}-{tid.hex[:6].upper()}-{n:08d}"


async def _validar_medico_notificante(db: AsyncSession, tid: uuid.UUID, medico_id: uuid.UUID) -> Empleado:
    """La notificación epidemiológica obligatoria (ENO) es responsabilidad de
    un médico -- mismo criterio de colegiatura habilitada que Firma
    Electrónica y Defunciones."""
    medico = await db.scalar(select(Empleado).where(Empleado.id == medico_id, Empleado.tenant_id == tid, Empleado.is_active.is_(True)))
    profesion = await db.scalar(select(Profesion.codigo).where(Profesion.id == medico.profesion_id, Profesion.tenant_id == tid)) if medico and medico.profesion_id else None
    if not medico or profesion != "MED" or not medico.habilitado_colegio or not (medico.numero_cmp or medico.numero_colegiatura):
        raise HTTPException(400, detail="El médico notificante debe tener colegiatura y habilitación registrada")
    return medico


async def crear_ficha(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    medico = await _validar_medico_notificante(db, tid, data.medico_notificante_id)

    patient_id = data.patient_id
    if data.atencion_medica_id:
        atencion = await db.get(AtencionMedica, data.atencion_medica_id)
        if atencion is None or atencion.tenant_id != tid:
            raise HTTPException(404, detail="Atención médica no encontrada")
        cita = await db.get(Cita, atencion.cita_id)
        patient_id = cita.patient_id
        if await db.scalar(select(FichaEpidemiologica.id).where(
                FichaEpidemiologica.atencion_medica_id == data.atencion_medica_id, FichaEpidemiologica.tipo_ficha == data.tipo_ficha)):
            raise HTTPException(409, detail=f"Ya existe una ficha {data.tipo_ficha} para esta atención")
    elif data.atencion_emergencia_id:
        atencion = await db.get(AtencionEmergencia, data.atencion_emergencia_id)
        if atencion is None or atencion.tenant_id != tid:
            raise HTTPException(404, detail="Atención de emergencia no encontrada")
        admision = await db.get(AdmisionEmergencia, atencion.admision_id)
        patient_id = admision.patient_id
        if await db.scalar(select(FichaEpidemiologica.id).where(
                FichaEpidemiologica.atencion_emergencia_id == data.atencion_emergencia_id, FichaEpidemiologica.tipo_ficha == data.tipo_ficha)):
            raise HTTPException(409, detail=f"Ya existe una ficha {data.tipo_ficha} para esta atención")

    paciente = await db.get(Patient, patient_id)
    if paciente is None or paciente.tenant_id != tid:
        raise HTTPException(404, detail="Paciente no encontrado")

    if data.diagnostico_cie10_id and not await db.scalar(select(DiagnosticoCIE10.id).where(
            DiagnosticoCIE10.id == data.diagnostico_cie10_id, DiagnosticoCIE10.tenant_id == tid)):
        raise HTTPException(400, detail="Diagnóstico CIE-10 no encontrado")

    numero = await _siguiente(db, tid, data.tipo_ficha)
    ficha = FichaEpidemiologica(id=uuid.uuid4(), tenant_id=tid, atencion_medica_id=data.atencion_medica_id,
        atencion_emergencia_id=data.atencion_emergencia_id, patient_id=patient_id,
        diagnostico_cie10_id=data.diagnostico_cie10_id, medico_notificante_id=data.medico_notificante_id,
        numero_ficha=numero, tipo_ficha=data.tipo_ficha, fecha_notificacion=data.fecha_notificacion or date.today(),
        datos_clinicos=data.datos_clinicos, observaciones=data.observaciones, registrado_por=actor(user))
    db.add(ficha)
    await db.flush()
    audit(db, tid, user, "FichaEpidemiologica", ficha.id, "crear", after={"tipo_ficha": data.tipo_ficha, "numero_ficha": numero})
    await db.commit()
    return await _ficha_out(db, ficha)


async def _ficha_out(db: AsyncSession, f: FichaEpidemiologica) -> dict:
    paciente = await db.get(Patient, f.patient_id)
    medico = await db.get(Empleado, f.medico_notificante_id)
    diagnostico = await db.get(DiagnosticoCIE10, f.diagnostico_cie10_id) if f.diagnostico_cie10_id else None
    return {
        "id": f.id, "numero_ficha": f.numero_ficha, "tipo_ficha": f.tipo_ficha, "patient_id": f.patient_id,
        "paciente_nombre": paciente.full_name if paciente else None, "paciente_dni": paciente.dni if paciente else None,
        "origen": "Consulta Externa" if f.atencion_medica_id else "Emergencia" if f.atencion_emergencia_id else "Directo",
        "diagnostico": f"{diagnostico.codigo_cie10} · {diagnostico.descripcion}" if diagnostico else None,
        "medico_notificante_nombre": medico.nombre_completo if medico else None,
        "fecha_notificacion": f.fecha_notificacion, "datos_clinicos": f.datos_clinicos,
        "estado_envio": f.estado_envio, "fecha_envio": f.fecha_envio, "observaciones": f.observaciones,
        "created_at": f.created_at,
    }


async def list_fichas(db: AsyncSession, tid: uuid.UUID, tipo_ficha: str | None = None,
                       estado_envio: str | None = None) -> list[dict]:
    query = select(FichaEpidemiologica).where(FichaEpidemiologica.tenant_id == tid)
    if tipo_ficha:
        query = query.where(FichaEpidemiologica.tipo_ficha == tipo_ficha)
    if estado_envio:
        query = query.where(FichaEpidemiologica.estado_envio == estado_envio)
    fichas = (await db.scalars(query.order_by(FichaEpidemiologica.created_at.desc()))).all()
    return [await _ficha_out(db, f) for f in fichas]


async def get_ficha(db: AsyncSession, tid: uuid.UUID, ficha_id: uuid.UUID) -> dict:
    f = await db.get(FichaEpidemiologica, ficha_id)
    if f is None or f.tenant_id != tid:
        raise HTTPException(404, detail="Ficha no encontrada")
    return await _ficha_out(db, f)


async def marcar_enviado(db: AsyncSession, tid: uuid.UUID, user: dict, ficha_id: uuid.UUID) -> dict:
    f = await db.get(FichaEpidemiologica, ficha_id)
    if f is None or f.tenant_id != tid:
        raise HTTPException(404, detail="Ficha no encontrada")
    if f.estado_envio == "enviada_red_salud":
        raise HTTPException(409, detail="Esta ficha ya fue marcada como enviada")
    f.estado_envio = "enviada_red_salud"
    f.fecha_envio = datetime.utcnow()
    audit(db, tid, user, "FichaEpidemiologica", f.id, "marcar_enviado")
    await db.commit()
    return await _ficha_out(db, f)
