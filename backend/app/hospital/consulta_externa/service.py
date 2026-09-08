import uuid
from datetime import datetime, timedelta, date as date_type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.sigarh.laboratorio.models import ExamenLaboratorio
from app.sigarh.imagenologia.models import ExamenImagenologia
from app.tenants.hospitales.models import Tenant
from app.hospital.gestion_pacientes.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import ProgramacionMedica, Cita, Triaje, AtencionMedica, AtencionDiagnostico, Receta, RecetaItem, Hospitalizacion, OrdenLaboratorio, OrdenLaboratorioItem, OrdenImagen, OrdenImagenItem, Interconsulta, Referencia
from app.sigarh.general.models import DiagnosticoCIE10

from app.hospital.consulta_externa.schemas import (
    ProgramacionMedicaCreate, ProgramacionMedicaUpdate, CitaCreate, CitaUpdate,TriajeCreate, TriajeUpdate, AtencionMedicaCreate, AtencionMedicaUpdate, AtencionMedicaResponse
)
from app.sigarh.rrhh.models import Empleado, Especialidad, EmpleadoEspecialidad
from app.sigarh.mantenimiento.models import Servicio


# ─── Catalogos desde SIGARH ─────────────────────────────────────────────
async def get_servicios(db: AsyncSession, tenant_id: uuid.UUID) -> list[Servicio]:
    result = await db.execute(
        select(Servicio).where(Servicio.tenant_id == tenant_id, Servicio.is_active == True).order_by(Servicio.nombre)
    )
    return result.scalars().all()


async def get_especialidades(db: AsyncSession, tenant_id: uuid.UUID) -> list[Especialidad]:
    result = await db.execute(
        select(Especialidad).where(Especialidad.tenant_id == tenant_id, Especialidad.is_active == True).order_by(Especialidad.nombre)
    )
    return result.scalars().all()


async def get_medicos_por_especialidad(db: AsyncSession, tenant_id: uuid.UUID, especialidad_id: uuid.UUID) -> list[Empleado]:
    result = await db.execute(
        select(Empleado)
        .join(EmpleadoEspecialidad, EmpleadoEspecialidad.empleado_id == Empleado.id)
        .where(Empleado.tenant_id == tenant_id, Empleado.is_active == True, EmpleadoEspecialidad.especialidad_id == especialidad_id)
        .order_by(Empleado.apellido_paterno)
    )
    return result.scalars().all()


# ─── Programaciones ─────────────────────────────────────────────────────
async def create_programacion(db: AsyncSession, tenant_id: uuid.UUID, data: ProgramacionMedicaCreate) -> dict:
    prog = ProgramacionMedica(tenant_id=tenant_id, **data.model_dump())
    db.add(prog)
    await db.commit()
    return await get_programacion_by_id(db, tenant_id, prog.id)


async def get_programacion_by_id(db: AsyncSession, tenant_id: uuid.UUID, prog_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(ProgramacionMedica, Empleado, Servicio, Especialidad)
        .join(Empleado, Empleado.id == ProgramacionMedica.medico_id)
        .outerjoin(Servicio, Servicio.id == ProgramacionMedica.servicio_id)
        .outerjoin(Especialidad, Especialidad.id == ProgramacionMedica.especialidad_id)
        .where(ProgramacionMedica.tenant_id == tenant_id, ProgramacionMedica.id == prog_id)
    )
    row = result.first()
    if not row:
        return None
    return _prog_to_dict(*row)


async def list_programaciones(
    db: AsyncSession, tenant_id: uuid.UUID,
    servicio_id: uuid.UUID | None = None,
    especialidad_id: uuid.UUID | None = None,
    medico_id: uuid.UUID | None = None,
    fecha: date_type | None = None,
) -> list[dict]:
    query = (
        select(ProgramacionMedica, Empleado, Servicio, Especialidad)
        .join(Empleado, Empleado.id == ProgramacionMedica.medico_id)
        .outerjoin(Servicio, Servicio.id == ProgramacionMedica.servicio_id)
        .outerjoin(Especialidad, Especialidad.id == ProgramacionMedica.especialidad_id)
        .where(ProgramacionMedica.tenant_id == tenant_id)
        .order_by(ProgramacionMedica.fecha.desc())
    )
    if servicio_id:
        query = query.where(ProgramacionMedica.servicio_id == servicio_id)
    if especialidad_id:
        query = query.where(ProgramacionMedica.especialidad_id == especialidad_id)
    if medico_id:
        query = query.where(ProgramacionMedica.medico_id == medico_id)
    if fecha:
        query = query.where(ProgramacionMedica.fecha == fecha)
    result = await db.execute(query)
    return [_prog_to_dict(*row) for row in result.all()]


async def update_programacion(db: AsyncSession, tenant_id: uuid.UUID, prog_id: uuid.UUID, data: ProgramacionMedicaUpdate) -> dict | None:
    result = await db.execute(select(ProgramacionMedica).where(ProgramacionMedica.tenant_id == tenant_id, ProgramacionMedica.id == prog_id))
    prog = result.scalar_one_or_none()
    if not prog:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(prog, field, value)
    await db.commit()
    return await get_programacion_by_id(db, tenant_id, prog_id)


def _prog_to_dict(prog: ProgramacionMedica, medico: Empleado, servicio: Servicio | None, especialidad: Especialidad | None) -> dict:
    return {
        "id": prog.id,
        "medico_id": prog.medico_id,
        "medico_nombre": medico.nombre_completo,
        "servicio_id": prog.servicio_id,
        "servicio_nombre": servicio.nombre if servicio else None,
        "especialidad_id": prog.especialidad_id,
        "especialidad_nombre": especialidad.nombre if especialidad else None,
        "fecha": prog.fecha,
        "turno": prog.turno,
        "hora_inicio": prog.hora_inicio,
        "hora_fin": prog.hora_fin,
        "tiempo_promedio_atencion": prog.tiempo_promedio_atencion,
        "tipo_servicio": prog.tipo_servicio,
        "mostrar_en_consultorio": prog.mostrar_en_consultorio,
        "descripcion": prog.descripcion,
        "estado": prog.estado,
        "created_at": prog.created_at,
    }



async def list_citas_para_triaje(
    db: AsyncSession, tenant_id: uuid.UUID,
    fecha: date_type | None = None,
    especialidad_id: uuid.UUID | None = None,
    servicio_id: uuid.UUID | None = None,
    medico_id: uuid.UUID | None = None,
) -> list[dict]:
    query = (
        select(Cita, Patient, ProgramacionMedica, Empleado, Servicio, Especialidad, Triaje, ClinicalRecord)
        .join(Patient, Patient.id == Cita.patient_id)
        .join(ProgramacionMedica, ProgramacionMedica.id == Cita.programacion_medica_id)
        .join(Empleado, Empleado.id == ProgramacionMedica.medico_id)
        .outerjoin(Servicio, Servicio.id == ProgramacionMedica.servicio_id)
        .outerjoin(Especialidad, Especialidad.id == ProgramacionMedica.especialidad_id)
        .outerjoin(Triaje, Triaje.cita_id == Cita.id)
        .outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id)
        .where(Cita.tenant_id == tenant_id, Cita.estado == "confirmada")
    )
    if fecha:
        query = query.where(ProgramacionMedica.fecha == fecha)
    if especialidad_id:
        query = query.where(ProgramacionMedica.especialidad_id == especialidad_id)
    if servicio_id:
        query = query.where(ProgramacionMedica.servicio_id == servicio_id)
    if medico_id:
        query = query.where(ProgramacionMedica.medico_id == medico_id)

    result = await db.execute(query.order_by(Cita.hora_inicio))
    items = []
    for cita, paciente, prog, medico, servicio, especialidad, triaje, clinical_record in result.all():
        items.append({
            "cita_id": cita.id,
            "paciente_nombre": paciente.full_name,
            "paciente_dni": paciente.dni,
            "paciente_hc": clinical_record.record_number if clinical_record else None,
            "fuente_financiamiento": cita.fuente_financiamiento,
            "especialidad_nombre": especialidad.nombre if especialidad else None,
            "servicio_nombre": servicio.nombre if servicio else None,
            "medico_nombre": medico.nombre_completo,
            "fecha": prog.fecha,
            "hora_inicio": cita.hora_inicio,
            "paso_triaje": triaje is not None,
        })
    return items
    
# ─── Cupos (calculados en memoria, no se guardan) ───────────────────────
def _generar_slots(hora_inicio: str, hora_fin: str, minutos: int) -> list[tuple[str, str]]:
    fmt = "%H:%M"
    inicio = datetime.strptime(hora_inicio, fmt)
    fin = datetime.strptime(hora_fin, fmt)
    slots = []
    actual = inicio
    while actual + timedelta(minutes=minutos) <= fin:
        siguiente = actual + timedelta(minutes=minutos)
        slots.append((actual.strftime(fmt), siguiente.strftime(fmt)))
        actual = siguiente
    return slots


async def get_cupos(db: AsyncSession, tenant_id: uuid.UUID, programacion_id: uuid.UUID) -> list[dict] | None:
    result = await db.execute(
        select(ProgramacionMedica).where(ProgramacionMedica.tenant_id == tenant_id, ProgramacionMedica.id == programacion_id)
    )
    prog = result.scalar_one_or_none()
    if not prog:
        return None

    slots = _generar_slots(prog.hora_inicio, prog.hora_fin, prog.tiempo_promedio_atencion)

    result = await db.execute(
        select(Cita, Patient)
        .join(Patient, Patient.id == Cita.patient_id)
        .where(Cita.programacion_medica_id == programacion_id, Cita.estado != "cancelada")
    )
    ocupados = {cita.hora_inicio: (cita, paciente) for cita, paciente in result.all()}

    cupos = []
    for inicio, fin in slots:
        if inicio in ocupados:
            cita, paciente = ocupados[inicio]
            cupos.append({"hora_inicio": inicio, "hora_fin": fin, "disponible": False, "cita_id": cita.id, "paciente_nombre": paciente.full_name})
        else:
            cupos.append({"hora_inicio": inicio, "hora_fin": fin, "disponible": True, "cita_id": None, "paciente_nombre": None})
    return cupos


# ─── Citas ───────────────────────────────────────────────────────────────
async def create_cita(db: AsyncSession, tenant_id: uuid.UUID, data: CitaCreate) -> dict:
    existing = await db.execute(
        select(Cita).where(
            Cita.programacion_medica_id == data.programacion_medica_id,
            Cita.hora_inicio == data.hora_inicio,
            Cita.estado != "cancelada",
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Ese cupo ya está ocupado")

    cita = Cita(tenant_id=tenant_id, **data.model_dump())
    db.add(cita)
    await db.commit()
    return await get_cita_by_id(db, tenant_id, cita.id)


async def get_cita_by_id(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(Cita, Patient).join(Patient, Patient.id == Cita.patient_id)
        .where(Cita.tenant_id == tenant_id, Cita.id == cita_id)
    )
    row = result.first()
    if not row:
        return None
    return _cita_to_dict(*row)


async def list_citas(
    db: AsyncSession, tenant_id: uuid.UUID,
    programacion_medica_id: uuid.UUID | None = None,
    estado: str | None = None,
    fecha: date_type | None = None,
) -> list[dict]:
    query = (
        select(Cita, Patient, ProgramacionMedica)
        .join(Patient, Patient.id == Cita.patient_id)
        .join(ProgramacionMedica, ProgramacionMedica.id == Cita.programacion_medica_id)
        .where(Cita.tenant_id == tenant_id)
    )
    if programacion_medica_id:
        query = query.where(Cita.programacion_medica_id == programacion_medica_id)
    if estado:
        query = query.where(Cita.estado == estado)
    if fecha:
        query = query.where(ProgramacionMedica.fecha == fecha)
    result = await db.execute(query.order_by(Cita.hora_inicio))
    return [_cita_to_dict(c, p) for c, p, prog in result.all()]


async def update_cita(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: CitaUpdate) -> dict | None:
    result = await db.execute(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id))
    cita = result.scalar_one_or_none()
    if not cita:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cita, field, value)
    await db.commit()
    return await get_cita_by_id(db, tenant_id, cita_id)


def _cita_to_dict(cita: Cita, paciente: Patient) -> dict:
    return {
        "id": cita.id,
        "programacion_medica_id": cita.programacion_medica_id,
        "patient_id": cita.patient_id,
        "paciente_nombre": paciente.full_name,
        "paciente_dni": paciente.dni,
        "hora_inicio": cita.hora_inicio,
        "hora_fin": cita.hora_fin,
        "tipo_consulta": cita.tipo_consulta,
        "observacion": cita.observacion,
        "numero_cuenta": cita.numero_cuenta,
        "cuenta_vinculada": cita.cuenta_vinculada,
        "fuente_financiamiento": cita.fuente_financiamiento,
        "producto_plan": cita.producto_plan,
        "estado": cita.estado,
        "created_at": cita.created_at,
    }



# ─── Confirmar cita (paso previo a Triaje) ──────────────────────────────
async def confirmar_cita(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID) -> dict | None:
    result = await db.execute(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id))
    cita = result.scalar_one_or_none()
    if not cita:
        return None
    if cita.estado != "separada":
        raise ValueError(f"No se puede confirmar una cita en estado '{cita.estado}'")
    cita.estado = "confirmada"
    await db.commit()
    return await get_cita_by_id(db, tenant_id, cita_id)





async def create_triaje(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: TriajeCreate) -> dict:
    result = await db.execute(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id))
    cita = result.scalar_one_or_none()
    if not cita:
        raise ValueError("Cita no encontrada")
    if cita.estado != "confirmada":
        raise ValueError("Solo se puede registrar triaje a una cita confirmada")

    existing = await db.execute(select(Triaje).where(Triaje.cita_id == cita_id))
    if existing.scalar_one_or_none():
        raise ValueError("Esta cita ya tiene un triaje registrado")

    triaje = Triaje(tenant_id=tenant_id, cita_id=cita_id, **data.model_dump())
    db.add(triaje)
    await db.commit()
    await db.refresh(triaje)
    return triaje


async def get_triaje_by_cita(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID) -> Triaje | None:
    result = await db.execute(select(Triaje).where(Triaje.tenant_id == tenant_id, Triaje.cita_id == cita_id))
    return result.scalar_one_or_none()


async def update_triaje(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: "TriajeUpdate") -> Triaje | None:
    result = await db.execute(select(Triaje).where(Triaje.tenant_id == tenant_id, Triaje.cita_id == cita_id))
    triaje = result.scalar_one_or_none()
    if not triaje:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(triaje, field, value)
    await db.commit()
    await db.refresh(triaje)
    return triaje




async def buscar_cie10(db: AsyncSession, tenant_id: uuid.UUID, q: str) -> list[DiagnosticoCIE10]:
    result = await db.execute(
        select(DiagnosticoCIE10)
        .where(
            DiagnosticoCIE10.tenant_id == tenant_id,
            DiagnosticoCIE10.is_active == True,
            or_(
                DiagnosticoCIE10.codigo_cie10.ilike(f"%{q}%"),
                DiagnosticoCIE10.descripcion.ilike(f"%{q}%"),
            )
        )
        .limit(20)
    )
    return result.scalars().all()


async def create_atencion_medica(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: "AtencionMedicaCreate") -> dict:
    result = await db.execute(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id))
    cita = result.scalar_one_or_none()
    if not cita:
        raise ValueError("Cita no encontrada")
    if cita.estado != "confirmada":
        raise ValueError("Solo se puede registrar atencion sobre una cita confirmada")

    existing = await db.execute(select(AtencionMedica).where(AtencionMedica.cita_id == cita_id))
    if existing.scalar_one_or_none():
        raise ValueError("Esta cita ya tiene una atencion medica registrada")

    atencion = AtencionMedica(
        tenant_id=tenant_id, cita_id=cita_id,
        motivo_consulta=data.motivo_consulta,
        examen_clinico=data.examen_clinico,
        plan_tratamiento=data.plan_tratamiento,
        observaciones=data.observaciones,
        destino_atencion=data.destino_atencion,
        indicaciones_alta=data.indicaciones_alta,
    )
    db.add(atencion)
    await db.flush()

    for dx in data.diagnosticos:
        db.add(AtencionDiagnostico(atencion_medica_id=atencion.id, diagnostico_cie10_id=dx.diagnostico_cie10_id, tipo=dx.tipo))

    cita.estado = "atendida"
    await db.commit()
    return await get_atencion_medica(db, tenant_id, cita_id)


async def get_atencion_medica(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(AtencionMedica, Cita, Patient, ProgramacionMedica, Empleado, Servicio, Especialidad, Triaje)
        .join(Cita, Cita.id == AtencionMedica.cita_id)
        .join(Patient, Patient.id == Cita.patient_id)
        .join(ProgramacionMedica, ProgramacionMedica.id == Cita.programacion_medica_id)
        .join(Empleado, Empleado.id == ProgramacionMedica.medico_id)
        .outerjoin(Servicio, Servicio.id == ProgramacionMedica.servicio_id)
        .outerjoin(Especialidad, Especialidad.id == ProgramacionMedica.especialidad_id)
        .outerjoin(Triaje, Triaje.cita_id == Cita.id)
        .where(AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id)
    )
    row = result.first()
    if not row:
        return None
    atencion, cita, paciente, prog, medico, servicio, especialidad, triaje = row

    dx_result = await db.execute(
        select(AtencionDiagnostico, DiagnosticoCIE10)
        .join(DiagnosticoCIE10, DiagnosticoCIE10.id == AtencionDiagnostico.diagnostico_cie10_id)
        .where(AtencionDiagnostico.atencion_medica_id == atencion.id)
    )
    diagnosticos = [
        {"id": d.id, "diagnostico_cie10_id": d.diagnostico_cie10_id, "codigo_cie10": c.codigo_cie10, "descripcion": c.descripcion, "tipo": d.tipo}
        for d, c in dx_result.all()
    ]

    return {
        "id": atencion.id,
        "cita_id": atencion.cita_id,
        "paciente_nombre": paciente.full_name,
        "paciente_dni": paciente.dni,
        "paciente_edad": paciente.age,
        "medico_nombre": medico.nombre_completo,
        "especialidad_nombre": especialidad.nombre if especialidad else None,
        "servicio_nombre": servicio.nombre if servicio else None,
        "motivo_consulta": atencion.motivo_consulta,
        "examen_clinico": atencion.examen_clinico,
        "plan_tratamiento": atencion.plan_tratamiento,
        "observaciones": atencion.observaciones,
        "destino_atencion": atencion.destino_atencion,
        "indicaciones_alta": atencion.indicaciones_alta,

        "estado": atencion.estado,
        "firmado_at": atencion.firmado_at,
        "diagnosticos": diagnosticos,
        "antecedente_quirurgico": paciente.antecedente_quirurgico,
        "antecedente_patologico": paciente.antecedente_patologico,
        "antecedente_alergias": paciente.antecedente_alergias,
        "antecedentes_obstetricos": paciente.antecedentes_obstetricos,
        "antecedente_familiares": paciente.antecedente_familiares,
        "antecedente_otros": paciente.antecedente_otros,
        "triaje": {
            "pulso": triaje.pulso, "temperatura": triaje.temperatura,
            "presion_sistolica": triaje.presion_sistolica, "presion_diastolica": triaje.presion_diastolica,
            "frecuencia_cardiaca": triaje.frecuencia_cardiaca, "frecuencia_respiratoria": triaje.frecuencia_respiratoria,
            "peso": triaje.peso, "talla": triaje.talla, "imc": triaje.imc, "saturacion_o2": triaje.saturacion_o2,
        } if triaje else None,
        "created_at": atencion.created_at,
    }


async def update_atencion_medica(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: "AtencionMedicaUpdate") -> dict | None:
    result = await db.execute(select(AtencionMedica).where(AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id))
    atencion = result.scalar_one_or_none()
    if not atencion:
        return None
    if atencion.estado == "firmado":
        raise ValueError("No se puede editar una atencion ya firmada")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(atencion, field, value)
    await db.commit()
    return await get_atencion_medica(db, tenant_id, cita_id)


async def firmar_atencion_medica(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, firmado_por_id: uuid.UUID | None = None) -> dict | None:
    result = await db.execute(select(AtencionMedica).where(AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id))
    atencion = result.scalar_one_or_none()
    if not atencion:
        return None
    if atencion.estado == "firmado":
        raise ValueError("Esta atencion ya esta firmada")
    atencion.estado = "firmado"
    atencion.firmado_at = datetime.utcnow()
    atencion.firmado_por_id = firmado_por_id
    await db.commit()
    return await get_atencion_medica(db, tenant_id, cita_id)


async def list_atenciones_medicas(
    db: AsyncSession, tenant_id: uuid.UUID,
    fecha: date_type | None = None,
    especialidad_id: uuid.UUID | None = None,
    medico_id: uuid.UUID | None = None,
    paciente_dni: str | None = None,
) -> list[dict]:
    query = (
        select(AtencionMedica, Cita, Patient, ProgramacionMedica, Empleado, Servicio, Especialidad)
        .join(Cita, Cita.id == AtencionMedica.cita_id)
        .join(Patient, Patient.id == Cita.patient_id)
        .join(ProgramacionMedica, ProgramacionMedica.id == Cita.programacion_medica_id)
        .join(Empleado, Empleado.id == ProgramacionMedica.medico_id)
        .outerjoin(Servicio, Servicio.id == ProgramacionMedica.servicio_id)
        .outerjoin(Especialidad, Especialidad.id == ProgramacionMedica.especialidad_id)
        .where(AtencionMedica.tenant_id == tenant_id)
        .order_by(AtencionMedica.created_at.desc())
    )
    if fecha:
        query = query.where(ProgramacionMedica.fecha == fecha)
    if especialidad_id:
        query = query.where(ProgramacionMedica.especialidad_id == especialidad_id)
    if medico_id:
        query = query.where(ProgramacionMedica.medico_id == medico_id)
    if paciente_dni:
        query = query.where(Patient.dni.ilike(f"%{paciente_dni}%"))

    result = await db.execute(query)
    items = []
    for atencion, cita, paciente, prog, medico, servicio, especialidad in result.all():
        items.append({
            "cita_id": atencion.cita_id,
            "paciente_nombre": paciente.full_name,
            "paciente_dni": paciente.dni,
            "medico_nombre": medico.nombre_completo,
            "especialidad_nombre": especialidad.nombre if especialidad else None,
            "servicio_nombre": servicio.nombre if servicio else None,
            "fecha": prog.fecha,
            "hora_inicio": cita.hora_inicio,
            "destino_atencion": atencion.destino_atencion,
            "estado": atencion.estado,
            "created_at": atencion.created_at,
        })
    return items



from app.sigarh.config_farmacia.models import Medicamento

async def buscar_medicamentos(db: AsyncSession, tenant_id: uuid.UUID, q: str) -> list[Medicamento]:
    result = await db.execute(
        select(Medicamento)
        .where(
            Medicamento.tenant_id == tenant_id,
            Medicamento.is_active == True,
            or_(
                Medicamento.codigo_interno.ilike(f"%{q}%"),
                Medicamento.nombre_comercial.ilike(f"%{q}%"),
                Medicamento.dci.ilike(f"%{q}%"),
            )
        )
        .limit(20)
    )
    return result.scalars().all()


def _generar_numero_receta(secuencia: int) -> str:
    return f"RX-{datetime.utcnow().year}-{secuencia:06d}"


async def create_receta(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: "RecetaCreate") -> dict:
    result = await db.execute(select(AtencionMedica).where(AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id))
    atencion = result.scalar_one_or_none()
    if not atencion:
        raise ValueError("Debe registrar la atencion medica antes de generar la receta")
    if atencion.destino_atencion != "FARMACIA":
        raise ValueError("El destino de la atencion debe ser FARMACIA para generar una receta")

    existing = await db.execute(select(Receta).where(Receta.atencion_medica_id == atencion.id))
    if existing.scalar_one_or_none():
        raise ValueError("Esta atencion ya tiene una receta generada")

    count = await db.scalar(select(func.count(Receta.id)))
    receta = Receta(tenant_id=tenant_id, atencion_medica_id=atencion.id, numero_receta=_generar_numero_receta((count or 0) + 1))
    db.add(receta)
    await db.flush()

    for item in data.items:
        db.add(RecetaItem(receta_id=receta.id, **item.model_dump()))

    await db.commit()
    return await get_receta(db, tenant_id, cita_id)


async def get_receta(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(Receta, AtencionMedica)
        .join(AtencionMedica, AtencionMedica.id == Receta.atencion_medica_id)
        .where(Receta.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id)
    )
    row = result.first()
    if not row:
        return None
    receta, atencion = row

    items_result = await db.execute(
        select(RecetaItem, Medicamento)
        .join(Medicamento, Medicamento.id == RecetaItem.medicamento_id)
        .where(RecetaItem.receta_id == receta.id)
    )
    items = [
        {"id": i.id, "medicamento_id": i.medicamento_id, "codigo_interno": m.codigo_interno, "nombre_comercial": m.nombre_comercial,
         "cantidad": i.cantidad, "dosis": i.dosis, "frecuencia": i.frecuencia, "duracion_dias": i.duracion_dias, "indicaciones": i.indicaciones}
        for i, m in items_result.all()
    ]
    return {"id": receta.id, "atencion_medica_id": receta.atencion_medica_id, "numero_receta": receta.numero_receta,
            "estado": receta.estado, "items": items, "created_at": receta.created_at}


from app.sigarh.infraestructura_hosp.models import Cama

async def get_camas_disponibles(db: AsyncSession, tenant_id: uuid.UUID, servicio_id: uuid.UUID | None = None) -> list[Cama]:
    query = select(Cama).where(Cama.tenant_id == tenant_id, Cama.is_active == True, Cama.estado == "DISPONIBLE")
    if servicio_id:
        query = query.where(Cama.servicio_id == servicio_id)
    result = await db.execute(query.order_by(Cama.codigo))
    return result.scalars().all()


def _generar_numero_hospitalizacion(secuencia: int) -> str:
    return f"HOSP-{datetime.utcnow().year}-{secuencia:06d}"


async def create_hospitalizacion(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: "HospitalizacionCreate") -> dict:
    result = await db.execute(select(AtencionMedica).where(AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id))
    atencion = result.scalar_one_or_none()
    if not atencion:
        raise ValueError("Debe registrar la atencion medica antes de generar la hospitalizacion")
    if atencion.destino_atencion != "HOSPITALIZACION":
        raise ValueError("El destino de la atencion debe ser HOSPITALIZACION")

    existing = await db.execute(select(Hospitalizacion).where(Hospitalizacion.atencion_medica_id == atencion.id))
    if existing.scalar_one_or_none():
        raise ValueError("Esta atencion ya tiene una hospitalizacion registrada")

    cama_result = await db.execute(select(Cama).where(Cama.id == data.cama_id, Cama.tenant_id == tenant_id))
    cama = cama_result.scalar_one_or_none()
    if not cama:
        raise ValueError("Cama no encontrada")
    if cama.estado != "DISPONIBLE":
        raise ValueError(f"La cama {cama.codigo} no esta disponible (estado actual: {cama.estado})")

    count = await db.scalar(select(func.count(Hospitalizacion.id)))
    hosp = Hospitalizacion(
        tenant_id=tenant_id, atencion_medica_id=atencion.id, cama_id=cama.id,
        especialidad_ingreso_id=data.especialidad_ingreso_id,
        diagnostico_ingreso_id=data.diagnostico_ingreso_id,
        numero_hospitalizacion=_generar_numero_hospitalizacion((count or 0) + 1),
    )
    db.add(hosp)
    cama.estado = "OCUPADA"
    await db.commit()
    return await get_hospitalizacion(db, tenant_id, cita_id)


async def get_hospitalizacion(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(Hospitalizacion, AtencionMedica, Cama, Especialidad, DiagnosticoCIE10)
        .join(AtencionMedica, AtencionMedica.id == Hospitalizacion.atencion_medica_id)
        .join(Cama, Cama.id == Hospitalizacion.cama_id)
        .outerjoin(Especialidad, Especialidad.id == Hospitalizacion.especialidad_ingreso_id)
        .outerjoin(DiagnosticoCIE10, DiagnosticoCIE10.id == Hospitalizacion.diagnostico_ingreso_id)
        .where(Hospitalizacion.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id)
    )
    row = result.first()
    if not row:
        return None
    hosp, atencion, cama, especialidad, diagnostico = row
    return {
        "id": hosp.id, "atencion_medica_id": hosp.atencion_medica_id, "numero_hospitalizacion": hosp.numero_hospitalizacion,
        "cama_codigo": cama.codigo, "cama_nombre": cama.nombre,
        "especialidad_ingreso_nombre": especialidad.nombre if especialidad else None,
        "diagnostico_ingreso_codigo": diagnostico.codigo_cie10 if diagnostico else None,
        "diagnostico_ingreso_descripcion": diagnostico.descripcion if diagnostico else None,
        "fecha_ingreso": hosp.fecha_ingreso, "fecha_alta": hosp.fecha_alta, "estado": hosp.estado,
    }


async def dar_alta_hospitalizacion(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(Hospitalizacion, AtencionMedica)
        .join(AtencionMedica, AtencionMedica.id == Hospitalizacion.atencion_medica_id)
        .where(Hospitalizacion.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id)
    )
    row = result.first()
    if not row:
        return None
    hosp, _ = row
    if hosp.estado == "alta":
        raise ValueError("Esta hospitalizacion ya tiene alta registrada")

    cama_result = await db.execute(select(Cama).where(Cama.id == hosp.cama_id))
    cama = cama_result.scalar_one_or_none()
    if cama:
        cama.estado = "DISPONIBLE"

    hosp.estado = "alta"
    hosp.fecha_alta = datetime.utcnow()
    await db.commit()
    return await get_hospitalizacion(db, tenant_id, cita_id)

async def get_examenes_laboratorio(db: AsyncSession, tenant_id: uuid.UUID, q: str | None = None) -> list[ExamenLaboratorio]:
    query = select(ExamenLaboratorio).where(ExamenLaboratorio.tenant_id == tenant_id, ExamenLaboratorio.is_active == True)
    if q:
        query = query.where(or_(ExamenLaboratorio.nombre.ilike(f"%{q}%"), ExamenLaboratorio.codigo.ilike(f"%{q}%")))
    result = await db.execute(query.order_by(ExamenLaboratorio.nombre).limit(50))
    return result.scalars().all()


def _generar_numero_orden(secuencia: int) -> str:
    return f"LAB-{datetime.utcnow().year}-{secuencia:06d}"


async def create_orden_laboratorio(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: "OrdenLaboratorioCreate") -> dict:
    result = await db.execute(select(AtencionMedica).where(AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id).with_for_update())
    atencion = result.scalar_one_or_none()
    if not atencion:
        raise ValueError("Debe registrar la atencion medica antes de generar la orden")
    if atencion.destino_atencion != "LABORATORIO":
        raise ValueError("El destino de la atencion debe ser LABORATORIO")

    existing = await db.execute(select(OrdenLaboratorio).where(OrdenLaboratorio.atencion_medica_id == atencion.id))
    if existing.scalar_one_or_none():
        raise ValueError("Esta atencion ya tiene una orden de laboratorio generada")

    if not data.examen_ids or len(set(data.examen_ids)) != len(data.examen_ids):
        raise ValueError("Seleccione exámenes sin duplicados")
    examenes_validos = (await db.scalars(select(ExamenLaboratorio.id).where(
        ExamenLaboratorio.tenant_id == tenant_id,
        ExamenLaboratorio.is_active.is_(True),
        ExamenLaboratorio.id.in_(data.examen_ids),
    ))).all()
    if len(examenes_validos) != len(data.examen_ids):
        raise ValueError("Examen no disponible en este hospital")
    from app.hospital.laboratorio.service import number
    orden = OrdenLaboratorio(
        tenant_id=tenant_id, atencion_medica_id=atencion.id,
        numero_orden=await number(db, tenant_id, "OL"),
        indicacion_clinica=data.indicacion_clinica,
    )
    db.add(orden)
    await db.flush()

    for examen_id in data.examen_ids:
        db.add(OrdenLaboratorioItem(orden_id=orden.id, examen_id=examen_id))

    await db.commit()
    return await get_orden_laboratorio(db, tenant_id, cita_id)


async def get_orden_laboratorio(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(OrdenLaboratorio, AtencionMedica)
        .join(AtencionMedica, AtencionMedica.id == OrdenLaboratorio.atencion_medica_id)
        .where(OrdenLaboratorio.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id)
    )
    row = result.first()
    if not row:
        return None
    orden, _ = row

    items_result = await db.execute(
        select(OrdenLaboratorioItem, ExamenLaboratorio)
        .join(ExamenLaboratorio, ExamenLaboratorio.id == OrdenLaboratorioItem.examen_id)
        .where(OrdenLaboratorioItem.orden_id == orden.id)
    )
    items = [
        {"id": i.id, "examen_id": i.examen_id, "codigo": e.codigo, "nombre": e.nombre, "categoria": e.categoria, "tipo_muestra": e.tipo_muestra}
        for i, e in items_result.all()
    ]
    return {
        "id": orden.id, "atencion_medica_id": orden.atencion_medica_id, "numero_orden": orden.numero_orden,
        "indicacion_clinica": orden.indicacion_clinica, "estado": orden.estado, "items": items, "created_at": orden.created_at,
    }




# --- Imagen ---
async def get_examenes_imagen(db: AsyncSession, tenant_id: uuid.UUID, q: str | None = None) -> list[ExamenImagenologia]:
    query = select(ExamenImagenologia).where(ExamenImagenologia.tenant_id == tenant_id, ExamenImagenologia.is_active == True)
    if q:
        query = query.where(or_(ExamenImagenologia.nombre.ilike(f"%{q}%"), ExamenImagenologia.codigo.ilike(f"%{q}%")))
    result = await db.execute(query.order_by(ExamenImagenologia.nombre).limit(50))
    return result.scalars().all()


def _generar_numero_orden_imagen(secuencia: int) -> str:
    return f"IMG-{datetime.utcnow().year}-{secuencia:06d}"


async def create_orden_imagen(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: "OrdenImagenCreate") -> dict:
    result = await db.execute(select(AtencionMedica).where(AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id))
    atencion = result.scalar_one_or_none()
    if not atencion:
        raise ValueError("Debe registrar la atencion medica antes de generar la orden")
    if atencion.destino_atencion != "IMAGEN":
        raise ValueError("El destino de la atencion debe ser IMAGEN")

    existing = await db.execute(select(OrdenImagen).where(OrdenImagen.atencion_medica_id == atencion.id))
    if existing.scalar_one_or_none():
        raise ValueError("Esta atencion ya tiene una orden de imagen generada")

    count = await db.scalar(select(func.count(OrdenImagen.id)))
    orden = OrdenImagen(
        tenant_id=tenant_id, atencion_medica_id=atencion.id,
        numero_orden=_generar_numero_orden_imagen((count or 0) + 1),
        indicacion_clinica=data.indicacion_clinica,
    )
    db.add(orden)
    await db.flush()
    for examen_id in data.examen_ids:
        db.add(OrdenImagenItem(orden_id=orden.id, examen_id=examen_id))
    await db.commit()
    return await get_orden_imagen(db, tenant_id, cita_id)


async def get_orden_imagen(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(OrdenImagen, AtencionMedica)
        .join(AtencionMedica, AtencionMedica.id == OrdenImagen.atencion_medica_id)
        .where(OrdenImagen.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id)
    )
    row = result.first()
    if not row:
        return None
    orden, _ = row
    items_result = await db.execute(
        select(OrdenImagenItem, ExamenImagenologia)
        .join(ExamenImagenologia, ExamenImagenologia.id == OrdenImagenItem.examen_id)
        .where(OrdenImagenItem.orden_id == orden.id)
    )
    items = [
        {"id": i.id, "examen_id": i.examen_id, "codigo": e.codigo, "nombre": e.nombre, "modalidad": e.modalidad, "parte_cuerpo": e.parte_cuerpo}
        for i, e in items_result.all()
    ]
    return {"id": orden.id, "atencion_medica_id": orden.atencion_medica_id, "numero_orden": orden.numero_orden,
            "indicacion_clinica": orden.indicacion_clinica, "estado": orden.estado, "items": items, "created_at": orden.created_at}


# --- Interconsulta ---
async def create_interconsulta(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: "InterconsultaCreate") -> dict:
    result = await db.execute(select(AtencionMedica).where(AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id))
    atencion = result.scalar_one_or_none()
    if not atencion:
        raise ValueError("Debe registrar la atencion medica antes de generar la interconsulta")
    if atencion.destino_atencion != "INTERCONSULTA":
        raise ValueError("El destino de la atencion debe ser INTERCONSULTA")

    existing = await db.execute(select(Interconsulta).where(Interconsulta.atencion_medica_id == atencion.id))
    if existing.scalar_one_or_none():
        raise ValueError("Esta atencion ya tiene una interconsulta generada")

    interc = Interconsulta(tenant_id=tenant_id, atencion_medica_id=atencion.id, **data.model_dump())
    db.add(interc)
    await db.commit()
    return await get_interconsulta(db, tenant_id, cita_id)


async def get_interconsulta(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(Interconsulta, AtencionMedica, Cita, Patient, Especialidad)
        .join(AtencionMedica, AtencionMedica.id == Interconsulta.atencion_medica_id)
        .join(Cita, Cita.id == AtencionMedica.cita_id)
        .join(Patient, Patient.id == Cita.patient_id)
        .join(Especialidad, Especialidad.id == Interconsulta.especialidad_destino_id)
        .where(Interconsulta.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id)
    )
    row = result.first()
    if not row:
        return None
    return await _interconsulta_row_to_dict(db, row)


async def list_interconsultas_pendientes(db: AsyncSession, tenant_id: uuid.UUID, especialidad_id: uuid.UUID | None = None) -> list[dict]:
    query = (
        select(Interconsulta, AtencionMedica, Cita, Patient, Especialidad)
        .join(AtencionMedica, AtencionMedica.id == Interconsulta.atencion_medica_id)
        .join(Cita, Cita.id == AtencionMedica.cita_id)
        .join(Patient, Patient.id == Cita.patient_id)
        .join(Especialidad, Especialidad.id == Interconsulta.especialidad_destino_id)
        .where(Interconsulta.tenant_id == tenant_id, Interconsulta.estado == "pendiente")
        .order_by(Interconsulta.urgente.desc(), Interconsulta.created_at)
    )
    if especialidad_id:
        query = query.where(Interconsulta.especialidad_destino_id == especialidad_id)
    result = await db.execute(query)
    return [await _interconsulta_row_to_dict(db, row) for row in result.all()]


async def _interconsulta_row_to_dict(db: AsyncSession, row) -> dict:
    interc, atencion, cita, paciente, especialidad = row
    diagnostico_codigo = diagnostico_desc = None
    if interc.diagnostico_id:
        dx_result = await db.execute(select(DiagnosticoCIE10).where(DiagnosticoCIE10.id == interc.diagnostico_id))
        dx = dx_result.scalar_one_or_none()
        if dx:
            diagnostico_codigo, diagnostico_desc = dx.codigo_cie10, dx.descripcion
    return {
        "id": interc.id, "atencion_medica_id": interc.atencion_medica_id,
        "paciente_nombre": paciente.full_name, "paciente_dni": paciente.dni,
        "especialidad_destino_id": interc.especialidad_destino_id, "especialidad_destino_nombre": especialidad.nombre,
        "diagnostico_codigo": diagnostico_codigo, "diagnostico_descripcion": diagnostico_desc,
        "motivo": interc.motivo, "urgente": interc.urgente, "estado": interc.estado,
        "cita_generada_id": interc.cita_generada_id, "created_at": interc.created_at,
    }


async def programar_interconsulta(db: AsyncSession, tenant_id: uuid.UUID, interconsulta_id: uuid.UUID, programacion_medica_id: uuid.UUID, hora_inicio: str, hora_fin: str) -> dict:
    result = await db.execute(select(Interconsulta).where(Interconsulta.tenant_id == tenant_id, Interconsulta.id == interconsulta_id))
    interc = result.scalar_one_or_none()
    if not interc:
        raise ValueError("Interconsulta no encontrada")
    if interc.estado != "pendiente":
        raise ValueError("Esta interconsulta ya fue programada")

    atencion_result = await db.execute(select(AtencionMedica).where(AtencionMedica.id == interc.atencion_medica_id))
    atencion = atencion_result.scalar_one_or_none()
    cita_result = await db.execute(select(Cita).where(Cita.id == atencion.cita_id))
    cita_original = cita_result.scalar_one_or_none()

    nueva_cita = await create_cita(db, tenant_id, CitaCreate(
        programacion_medica_id=programacion_medica_id, patient_id=cita_original.patient_id,
        hora_inicio=hora_inicio, hora_fin=hora_fin, tipo_consulta="Interconsulta", observacion=interc.motivo,
    ))

    interc.estado = "programada"
    interc.cita_generada_id = nueva_cita["id"]
    await db.commit()
    return await get_interconsulta(db, tenant_id, cita_original.id) if False else nueva_cita



def _generar_numero_referencia(secuencia: int) -> str:
    return f"REF-{datetime.utcnow().year}-{secuencia:06d}"


async def get_tenants_disponibles(db: AsyncSession, tenant_id_actual: uuid.UUID) -> list[Tenant]:
    result = await db.execute(select(Tenant).where(Tenant.id != tenant_id_actual, Tenant.is_active == True).order_by(Tenant.name))
    return result.scalars().all()


async def create_referencia(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: "ReferenciaCreate") -> dict:
    result = await db.execute(select(AtencionMedica).where(AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id))
    atencion = result.scalar_one_or_none()
    if not atencion:
        raise ValueError("Debe registrar la atencion medica antes de generar la referencia")
    if atencion.destino_atencion != "REFERENCIA":
        raise ValueError("El destino de la atencion debe ser REFERENCIA")

    existing = await db.execute(select(Referencia).where(Referencia.atencion_medica_id == atencion.id))
    if existing.scalar_one_or_none():
        raise ValueError("Esta atencion ya tiene una referencia generada")

    count = await db.scalar(select(func.count(Referencia.id)))
    ref = Referencia(
        tenant_id=tenant_id, atencion_medica_id=atencion.id,
        numero_referencia=_generar_numero_referencia((count or 0) + 1),
        **data.model_dump(),
    )
    db.add(ref)
    await db.commit()
    return await get_referencia(db, tenant_id, cita_id)


async def get_referencia(db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(Referencia, AtencionMedica)
        .join(AtencionMedica, AtencionMedica.id == Referencia.atencion_medica_id)
        .where(Referencia.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id)
    )
    row = result.first()
    if not row:
        return None
    ref, _ = row

    tenant_destino_nombre = None
    if ref.tenant_destino_id:
        t_result = await db.execute(select(Tenant).where(Tenant.id == ref.tenant_destino_id))
        t = t_result.scalar_one_or_none()
        tenant_destino_nombre = t.name if t else None

    diagnostico_codigo = diagnostico_desc = None
    if ref.diagnostico_id:
        dx_result = await db.execute(select(DiagnosticoCIE10).where(DiagnosticoCIE10.id == ref.diagnostico_id))
        dx = dx_result.scalar_one_or_none()
        if dx:
            diagnostico_codigo, diagnostico_desc = dx.codigo_cie10, dx.descripcion

    return {
        "id": ref.id, "atencion_medica_id": ref.atencion_medica_id, "numero_referencia": ref.numero_referencia,
        "codigo_renipress_destino": ref.codigo_renipress_destino, "nombre_ipress_destino": ref.nombre_ipress_destino,
        "tenant_destino_id": ref.tenant_destino_id, "tenant_destino_nombre": tenant_destino_nombre,
        "especialidad_destino": ref.especialidad_destino,
        "diagnostico_codigo": diagnostico_codigo, "diagnostico_descripcion": diagnostico_desc,
        "motivo": ref.motivo, "estado": ref.estado, "created_at": ref.created_at,
    }
