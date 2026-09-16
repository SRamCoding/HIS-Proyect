import uuid
from datetime import date, datetime
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.servicio_social.models import ServicioSocialCorrelativo, EvaluacionSocial, GestionSocial
from app.hospital.admision.models import Patient
from app.hospital.consulta_externa.models import AtencionMedica, Hospitalizacion
from app.hospital.emergencia.models import AtencionEmergencia
from app.sigarh.rrhh.models import Empleado
from app.sigarh.mantenimiento.models import Profesion
from app.admin.auditoria.models import AuditLog


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


def audit(db, tid, user, model, obj_id, action, before=None, after=None):
    db.add(AuditLog(tenant_id=tid, user_id=uuid.UUID(user["sub"]), user_name=user.get("name"),
        model=model, model_id=str(obj_id), action=action,
        old_values=jsonable_encoder(before), new_values=jsonable_encoder(after)))


async def _siguiente(db: AsyncSession, tid: uuid.UUID) -> str:
    stmt = insert(ServicioSocialCorrelativo).values(tenant_id=tid, tipo="FICHA", valor=1)
    stmt = stmt.on_conflict_do_update(index_elements=["tenant_id", "tipo"],
        set_={"valor": ServicioSocialCorrelativo.valor + 1}).returning(ServicioSocialCorrelativo.valor)
    n = await db.scalar(stmt)
    return f"SOC-{tid.hex[:6].upper()}-{n:08d}"


async def _validar_trabajador_social(db: AsyncSession, tid: uuid.UUID, empleado_id: uuid.UUID) -> Empleado:
    empleado = await db.scalar(select(Empleado).where(Empleado.id == empleado_id, Empleado.tenant_id == tid, Empleado.is_active.is_(True)))
    profesion = await db.scalar(select(Profesion.codigo).where(Profesion.id == empleado.profesion_id, Profesion.tenant_id == tid)) if empleado and empleado.profesion_id else None
    if not empleado or profesion != "TSO":
        raise HTTPException(400, detail="El profesional debe tener profesión Trabajador Social (TSO) registrada")
    return empleado


async def crear_evaluacion(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    await _validar_trabajador_social(db, tid, data.trabajador_social_id)

    paciente = await db.get(Patient, data.patient_id)
    if paciente is None or paciente.tenant_id != tid:
        raise HTTPException(404, detail="Paciente no encontrado")

    for campo, modelo, oid in (("atencion_medica_id", AtencionMedica, data.atencion_medica_id),
                                ("atencion_emergencia_id", AtencionEmergencia, data.atencion_emergencia_id),
                                ("hospitalizacion_id", Hospitalizacion, data.hospitalizacion_id)):
        if oid is not None:
            origen = await db.get(modelo, oid)
            if origen is None or origen.tenant_id != tid:
                raise HTTPException(404, detail=f"{campo}: registro no encontrado")

    numero = await _siguiente(db, tid)
    evaluacion = EvaluacionSocial(id=uuid.uuid4(), tenant_id=tid, patient_id=data.patient_id,
        atencion_medica_id=data.atencion_medica_id, atencion_emergencia_id=data.atencion_emergencia_id,
        hospitalizacion_id=data.hospitalizacion_id, trabajador_social_id=data.trabajador_social_id,
        numero_ficha=numero, fecha_evaluacion=data.fecha_evaluacion or date.today(),
        tipo_vivienda=data.tipo_vivienda, clasificacion_socioeconomica=data.clasificacion_socioeconomica,
        red_apoyo_familiar=data.red_apoyo_familiar, factores_riesgo=data.factores_riesgo,
        requiere_derivacion_externa=data.requiere_derivacion_externa, entidad_derivacion=data.entidad_derivacion,
        recomendaciones=data.recomendaciones, registrado_por=actor(user))
    db.add(evaluacion)
    await db.flush()
    audit(db, tid, user, "EvaluacionSocial", evaluacion.id, "crear", after={"numero_ficha": numero, "patient_id": str(data.patient_id)})
    await db.commit()
    return await _evaluacion_out(db, evaluacion)


async def _evaluacion_out(db: AsyncSession, e: EvaluacionSocial) -> dict:
    paciente = await db.get(Patient, e.patient_id)
    trabajador = await db.get(Empleado, e.trabajador_social_id)
    gestiones = (await db.scalars(select(GestionSocial).where(
        GestionSocial.evaluacion_social_id == e.id).order_by(GestionSocial.fecha.desc()))).all()
    return {
        "id": e.id, "numero_ficha": e.numero_ficha, "patient_id": e.patient_id,
        "paciente_nombre": paciente.full_name if paciente else None, "paciente_dni": paciente.dni if paciente else None,
        "paciente_datos_admision": {
            "estado_civil": paciente.marital_status, "grado_instruccion": paciente.education_level,
            "ocupacion": paciente.occupation, "telefono": paciente.phone, "direccion": paciente.address,
        } if paciente else None,
        "origen": "Consulta Externa" if e.atencion_medica_id else "Emergencia" if e.atencion_emergencia_id else "Hospitalización" if e.hospitalizacion_id else "Directo",
        "trabajador_social_nombre": trabajador.nombre_completo if trabajador else None,
        "fecha_evaluacion": e.fecha_evaluacion, "tipo_vivienda": e.tipo_vivienda,
        "clasificacion_socioeconomica": e.clasificacion_socioeconomica, "red_apoyo_familiar": e.red_apoyo_familiar,
        "factores_riesgo": e.factores_riesgo or [], "requiere_derivacion_externa": e.requiere_derivacion_externa,
        "entidad_derivacion": e.entidad_derivacion, "recomendaciones": e.recomendaciones,
        "estado": e.estado, "fecha_cierre": e.fecha_cierre, "created_at": e.created_at,
        "gestiones": [{
            "id": g.id, "fecha": g.fecha, "tipo_gestion": g.tipo_gestion, "descripcion": g.descripcion,
            "registrado_por": g.registrado_por,
        } for g in gestiones],
    }


async def list_evaluaciones(db: AsyncSession, tid: uuid.UUID, estado: str | None = None,
                             patient_id: uuid.UUID | None = None) -> list[dict]:
    query = select(EvaluacionSocial).where(EvaluacionSocial.tenant_id == tid)
    if estado:
        query = query.where(EvaluacionSocial.estado == estado)
    if patient_id:
        query = query.where(EvaluacionSocial.patient_id == patient_id)
    evaluaciones = (await db.scalars(query.order_by(EvaluacionSocial.created_at.desc()))).all()
    return [await _evaluacion_out(db, e) for e in evaluaciones]


async def get_evaluacion(db: AsyncSession, tid: uuid.UUID, evaluacion_id: uuid.UUID) -> dict:
    e = await db.get(EvaluacionSocial, evaluacion_id)
    if e is None or e.tenant_id != tid:
        raise HTTPException(404, detail="Evaluación social no encontrada")
    return await _evaluacion_out(db, e)


async def cerrar_evaluacion(db: AsyncSession, tid: uuid.UUID, user: dict, evaluacion_id: uuid.UUID, data) -> dict:
    e = await db.get(EvaluacionSocial, evaluacion_id)
    if e is None or e.tenant_id != tid:
        raise HTTPException(404, detail="Evaluación social no encontrada")
    if e.estado != "abierto":
        raise HTTPException(409, detail="Este caso ya está cerrado")
    e.estado = "cerrado"
    e.fecha_cierre = date.today()
    if data.recomendaciones:
        e.recomendaciones = data.recomendaciones
    audit(db, tid, user, "EvaluacionSocial", e.id, "cerrar")
    await db.commit()
    return await _evaluacion_out(db, e)


async def crear_gestion(db: AsyncSession, tid: uuid.UUID, user: dict, evaluacion_id: uuid.UUID, data) -> dict:
    evaluacion = await db.get(EvaluacionSocial, evaluacion_id)
    if evaluacion is None or evaluacion.tenant_id != tid:
        raise HTTPException(404, detail="Evaluación social no encontrada")
    if evaluacion.estado != "abierto":
        raise HTTPException(409, detail="No se pueden registrar gestiones en un caso cerrado")
    gestion = GestionSocial(id=uuid.uuid4(), tenant_id=tid, evaluacion_social_id=evaluacion_id,
        fecha=data.fecha or datetime.utcnow(), tipo_gestion=data.tipo_gestion, descripcion=data.descripcion,
        registrado_por=actor(user))
    db.add(gestion)
    await db.flush()
    audit(db, tid, user, "GestionSocial", gestion.id, "crear", after={"tipo_gestion": data.tipo_gestion})
    await db.commit()
    return await _evaluacion_out(db, evaluacion)
