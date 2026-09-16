import uuid
from datetime import date, datetime
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.telesalud.models import TelesaludSolicitud
from app.hospital.admision.models import Patient
from app.hospital.consulta_externa.models import ProgramacionMedica, Cita, AtencionMedica
from app.sigarh.rrhh.models import Empleado, Especialidad, EmpleadoEspecialidad
from app.admin.auditoria.models import AuditLog


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


def audit(db, tid, user, model, obj_id, action, before=None, after=None):
    db.add(AuditLog(tenant_id=tid, user_id=uuid.UUID(user["sub"]), user_name=user.get("name"),
        model=model, model_id=str(obj_id), action=action,
        old_values=jsonable_encoder(before), new_values=jsonable_encoder(after)))


def _dia(fecha: date, fin: bool = False) -> datetime:
    return datetime.combine(fecha, datetime.max.time() if fin else datetime.min.time())


def _solicitud_out(s: TelesaludSolicitud, paciente: Patient, especialidad: Especialidad | None) -> dict:
    return {
        "id": s.id, "patient_id": s.patient_id, "paciente_nombre": paciente.full_name, "paciente_dni": paciente.dni,
        "especialidad_id": s.especialidad_id, "especialidad_nombre": especialidad.nombre if especialidad else None,
        "motivo": s.motivo, "medio_preferido": s.medio_preferido,
        "contacto": s.contacto or paciente.phone or paciente.email,
        "estado": s.estado, "motivo_rechazo": s.motivo_rechazo, "cita_id": s.cita_id,
        "created_at": s.created_at, "atendido_at": s.atendido_at,
    }


# ─── Formulario Solicitud ───────────────────────────────────────────────────

async def crear_solicitud(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    paciente = await db.get(Patient, data.patient_id)
    if paciente is None or paciente.tenant_id != tid:
        raise HTTPException(404, detail="Paciente no encontrado")
    especialidad = await db.get(Especialidad, data.especialidad_id) if data.especialidad_id else None

    solicitud = TelesaludSolicitud(id=uuid.uuid4(), tenant_id=tid, patient_id=data.patient_id,
        especialidad_id=data.especialidad_id, motivo=data.motivo, medio_preferido=data.medio_preferido,
        contacto=data.contacto, registrado_por=actor(user))
    db.add(solicitud)
    await db.flush()
    audit(db, tid, user, "TelesaludSolicitud", solicitud.id, "crear", after={"patient_id": str(data.patient_id), "motivo": data.motivo})
    await db.commit()
    return _solicitud_out(solicitud, paciente, especialidad)


async def list_solicitudes(db: AsyncSession, tid: uuid.UUID, estado: str | None = None) -> list[dict]:
    q = select(TelesaludSolicitud, Patient, Especialidad).join(
        Patient, TelesaludSolicitud.patient_id == Patient.id).outerjoin(
        Especialidad, TelesaludSolicitud.especialidad_id == Especialidad.id).where(
        TelesaludSolicitud.tenant_id == tid)
    if estado:
        q = q.where(TelesaludSolicitud.estado == estado)
    rows = (await db.execute(q.order_by(TelesaludSolicitud.created_at.desc()))).all()
    return [_solicitud_out(s, p, e) for s, p, e in rows]


async def programar_solicitud(db: AsyncSession, tid: uuid.UUID, user: dict, solicitud_id: uuid.UUID, data) -> dict:
    solicitud = await db.get(TelesaludSolicitud, solicitud_id)
    if solicitud is None or solicitud.tenant_id != tid:
        raise HTTPException(404, detail="Solicitud no encontrada")
    if solicitud.estado != "pendiente":
        raise HTTPException(409, detail=f"La solicitud ya está en estado '{solicitud.estado}'")

    cita = await db.get(Cita, data.cita_id)
    if cita is None or cita.tenant_id != tid:
        raise HTTPException(404, detail="Cita no encontrada")
    if cita.patient_id != solicitud.patient_id:
        raise HTTPException(400, detail="La cita pertenece a otro paciente")
    programacion = await db.get(ProgramacionMedica, cita.programacion_medica_id)
    if programacion is None or programacion.modalidad != "VIRTUAL":
        raise HTTPException(400, detail="La cita debe pertenecer a una programación con modalidad VIRTUAL")
    ya_enlazada = await db.scalar(select(func.count()).where(TelesaludSolicitud.cita_id == data.cita_id))
    if ya_enlazada:
        raise HTTPException(409, detail="Esa cita ya está enlazada a otra solicitud")

    before = {"estado": solicitud.estado}
    solicitud.estado = "programada"
    solicitud.cita_id = data.cita_id
    solicitud.atendido_at = datetime.utcnow()
    audit(db, tid, user, "TelesaludSolicitud", solicitud.id, "programar", before=before, after={"estado": "programada", "cita_id": str(data.cita_id)})
    await db.commit()

    paciente = await db.get(Patient, solicitud.patient_id)
    especialidad = await db.get(Especialidad, solicitud.especialidad_id) if solicitud.especialidad_id else None
    return _solicitud_out(solicitud, paciente, especialidad)


async def rechazar_solicitud(db: AsyncSession, tid: uuid.UUID, user: dict, solicitud_id: uuid.UUID, data) -> dict:
    solicitud = await db.get(TelesaludSolicitud, solicitud_id)
    if solicitud is None or solicitud.tenant_id != tid:
        raise HTTPException(404, detail="Solicitud no encontrada")
    if solicitud.estado != "pendiente":
        raise HTTPException(409, detail=f"La solicitud ya está en estado '{solicitud.estado}'")

    before = {"estado": solicitud.estado}
    solicitud.estado = "rechazada"
    solicitud.motivo_rechazo = data.motivo_rechazo
    solicitud.atendido_at = datetime.utcnow()
    audit(db, tid, user, "TelesaludSolicitud", solicitud.id, "rechazar", before=before, after={"estado": "rechazada", "motivo_rechazo": data.motivo_rechazo})
    await db.commit()

    paciente = await db.get(Patient, solicitud.patient_id)
    especialidad = await db.get(Especialidad, solicitud.especialidad_id) if solicitud.especialidad_id else None
    return _solicitud_out(solicitud, paciente, especialidad)


# ─── Resumen Teleconsultas (reporte, sin tabla propia) ──────────────────────

async def resumen_teleconsultas(db: AsyncSession, tid: uuid.UUID, fecha_desde: date, fecha_hasta: date) -> dict:
    """Estadística de teleconsultas ya realizadas: toda Cita cuya ProgramacionMedica
    tiene modalidad='VIRTUAL' -- no duplica nada de Consulta Externa, solo lo filtra
    y agrega por médico/especialidad, igual que hace Informes con las presenciales."""
    if fecha_hasta < fecha_desde:
        raise HTTPException(400, detail="fecha_hasta no puede ser anterior a fecha_desde")
    inicio, fin = _dia(fecha_desde), _dia(fecha_hasta, fin=True)

    conteo_citas = dict((await db.execute(select(Cita.estado, func.count()).join(
        ProgramacionMedica, Cita.programacion_medica_id == ProgramacionMedica.id).where(
        ProgramacionMedica.tenant_id == tid, ProgramacionMedica.modalidad == "VIRTUAL",
        ProgramacionMedica.fecha.between(fecha_desde, fecha_hasta)).group_by(Cita.estado))).all())
    total_citas = sum(conteo_citas.values())
    no_asistio = conteo_citas.get("no_asistio", 0)

    total_firmadas = await db.scalar(select(func.count()).select_from(AtencionMedica).join(
        Cita, AtencionMedica.cita_id == Cita.id).join(
        ProgramacionMedica, Cita.programacion_medica_id == ProgramacionMedica.id).where(
        ProgramacionMedica.tenant_id == tid, ProgramacionMedica.modalidad == "VIRTUAL",
        AtencionMedica.estado == "firmado", AtencionMedica.firmado_at.between(inicio, fin))) or 0

    por_medico_rows = (await db.execute(select(Empleado.id, Empleado.nombres, Empleado.apellido_paterno,
        Empleado.apellido_materno, func.count(AtencionMedica.id)).join(
        AtencionMedica, AtencionMedica.firmado_por_id == Empleado.id).join(
        Cita, AtencionMedica.cita_id == Cita.id).join(
        ProgramacionMedica, Cita.programacion_medica_id == ProgramacionMedica.id).where(
        ProgramacionMedica.tenant_id == tid, ProgramacionMedica.modalidad == "VIRTUAL",
        AtencionMedica.estado == "firmado", AtencionMedica.firmado_at.between(inicio, fin)).group_by(
        Empleado.id, Empleado.nombres, Empleado.apellido_paterno, Empleado.apellido_materno).order_by(
        func.count(AtencionMedica.id).desc()))).all()
    por_medico = [{"medico_nombre": f"{ap}, {n} {am}".strip(), "teleconsultas_firmadas": cnt}
                  for _, n, ap, am, cnt in por_medico_rows]

    por_especialidad_rows = (await db.execute(select(Especialidad.nombre, func.count(Cita.id)).join(
        ProgramacionMedica, ProgramacionMedica.especialidad_id == Especialidad.id).join(
        Cita, Cita.programacion_medica_id == ProgramacionMedica.id).where(
        ProgramacionMedica.tenant_id == tid, ProgramacionMedica.modalidad == "VIRTUAL",
        ProgramacionMedica.fecha.between(fecha_desde, fecha_hasta)).group_by(Especialidad.nombre).order_by(
        func.count(Cita.id).desc()))).all()

    return {
        "fecha_desde": fecha_desde, "fecha_hasta": fecha_hasta,
        "citas_virtuales_programadas": total_citas,
        "teleconsultas_firmadas": total_firmadas,
        "no_asistio": no_asistio,
        "tasa_no_asistio": round(no_asistio / total_citas * 100, 1) if total_citas else 0.0,
        "por_medico": por_medico,
        "por_especialidad": [{"especialidad": nombre, "citas": cnt} for nombre, cnt in por_especialidad_rows],
    }


# ─── Monitor (foto en vivo del día) ─────────────────────────────────────────

async def monitor_hoy(db: AsyncSession, tid: uuid.UUID) -> list[dict]:
    hoy = date.today()
    rows = (await db.execute(select(Cita, Patient, Empleado).join(
        Patient, Cita.patient_id == Patient.id).join(
        ProgramacionMedica, Cita.programacion_medica_id == ProgramacionMedica.id).join(
        Empleado, ProgramacionMedica.medico_id == Empleado.id).where(
        ProgramacionMedica.tenant_id == tid, ProgramacionMedica.modalidad == "VIRTUAL",
        ProgramacionMedica.fecha == hoy).order_by(Cita.hora_inicio))).all()
    return [{
        "cita_id": c.id, "hora_inicio": c.hora_inicio, "hora_fin": c.hora_fin,
        "paciente_nombre": p.full_name, "paciente_dni": p.dni,
        "medico_nombre": m.nombre_completo, "estado": c.estado,
    } for c, p, m in rows]


# ─── Médicos habilitados para telesalud (derivado, sin campo nuevo) ─────────

async def medicos_habilitados(db: AsyncSession, tid: uuid.UUID) -> list[dict]:
    """No hay un campo de 'habilitado para telesalud': se listan los médicos que
    ya tienen (o tuvieron) al menos una ProgramacionMedica con modalidad='VIRTUAL'
    -- refleja quién realmente atiende teleconsultas hoy, sin inventar un catálogo
    paralelo de habilitación."""
    medico_ids = (await db.scalars(select(ProgramacionMedica.medico_id).where(
        ProgramacionMedica.tenant_id == tid, ProgramacionMedica.modalidad == "VIRTUAL").distinct())).all()
    if not medico_ids:
        return []
    medicos = (await db.scalars(select(Empleado).where(Empleado.id.in_(medico_ids)).order_by(
        Empleado.apellido_paterno))).all()
    especialidades = (await db.execute(select(EmpleadoEspecialidad.empleado_id, Especialidad.nombre,
        EmpleadoEspecialidad.numero_rne).join(Especialidad, EmpleadoEspecialidad.especialidad_id == Especialidad.id).where(
        EmpleadoEspecialidad.empleado_id.in_(medico_ids)))).all()
    esp_por_medico: dict[uuid.UUID, list[dict]] = {}
    for eid, nombre, rne in especialidades:
        esp_por_medico.setdefault(eid, []).append({"especialidad": nombre, "numero_rne": rne})

    return [{
        "id": m.id, "nombre": m.nombre_completo, "dni": m.dni, "celular": m.celular,
        "correo": m.correo, "numero_cmp": m.numero_cmp,
        "especialidades": esp_por_medico.get(m.id, []),
    } for m in medicos]


# ─── Guía Rápida MINSA (contenido estático, marco legal real) ──────────────

def guia_rapida() -> dict:
    return {
        "titulo": "Guía Rápida de Telesalud",
        "marco_legal": [
            {"norma": "Ley N.° 30421", "descripcion": "Ley Marco de Telesalud (2016)."},
            {"norma": "Decreto Legislativo N.° 1490", "descripcion": "Modifica la Ley N.° 30421 para fortalecer la prestación de servicios de telesalud."},
            {"norma": "Ley N.° 31166", "descripcion": "Ley de Telesalud: consolida y reconoce las modalidades sincrónicas y asincrónicas de telesalud."},
        ],
        "modalidades": [
            {"nombre": "Teleorientación", "descripcion": "Orientación e información en salud a distancia, sin llegar a un diagnóstico."},
            {"nombre": "Teleconsulta", "descripcion": "Consulta médica a distancia, en tiempo real (sincrónica), entre profesional y paciente."},
            {"nombre": "Teleinterconsulta", "descripcion": "Interconsulta a distancia entre profesionales de salud sobre el caso de un paciente."},
            {"nombre": "Telemonitoreo", "descripcion": "Seguimiento a distancia de parámetros de salud de un paciente."},
        ],
        "checklist_operativa": [
            "Verificar la identidad del paciente antes de iniciar la teleconsulta.",
            "Registrar consentimiento informado del paciente para la atención remota.",
            "Confirmar el medio de contacto (llamada, WhatsApp o videollamada) antes de la hora programada.",
            "Registrar la atención en la Historia Clínica igual que una atención presencial (queda como AtencionMedica con modalidad VIRTUAL).",
            "Ante una emergencia detectada durante la teleconsulta, derivar al paciente al establecimiento más cercano.",
        ],
    }
