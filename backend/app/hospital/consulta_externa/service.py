import uuid
from io import BytesIO
from datetime import datetime, timedelta, date as date_type
from calendar import monthrange
from xml.sax.saxutils import escape
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, delete
from sqlalchemy.exc import IntegrityError
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.sigarh.laboratorio.models import ExamenLaboratorio
from app.sigarh.imagenologia.models import ExamenImagenologia
from app.tenants.hospitales.models import Tenant
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import (
    ProgramacionMedica,
    Cita,
    Triaje,
    AtencionMedica,
    AtencionDiagnostico,
    Receta,
    RecetaItem,
    Hospitalizacion,
    OrdenLaboratorio,
    OrdenLaboratorioItem,
    OrdenImagen,
    OrdenImagenItem,
    Interconsulta,
    Referencia,
)
from app.sigarh.general.models import DiagnosticoCIE10

from app.hospital.consulta_externa.schemas import (
    ProgramacionMedicaCreate,
    ProgramacionMedicaUpdate,
    CitaCreate,
    CitaUpdate,
    TriajeCreate,
    TriajeUpdate,
    AtencionMedicaCreate,
    AtencionMedicaUpdate,
    AtencionMedicaResponse,
)
from app.sigarh.rrhh.models import (
    Empleado,
    Especialidad,
    EmpleadoEspecialidad,
    Justificacion,
)
from app.sigarh.mantenimiento.models import (
    Actividad,
    HorarioGuardia,
    Servicio,
    ServicioEspecialidad,
    ServicioUPSS,
    UPSS,
)
from app.sigarh.infraestructura.models import Consultorio
from app.sigarh.creacion_roles.models import Rol, RolEmpleado, RolActividad, RolTurno


def _turno_desde_hora(hhmm: str | None) -> str:
    """Clasifica un turno genérico a partir de la hora de inicio (HH:MM)."""
    try:
        h = int(str(hhmm).split(":")[0])
    except (ValueError, TypeError, AttributeError):
        h = 0
    if h < 12:
        return "MAÑANA"
    if h < 18:
        return "TARDE"
    return "NOCHE"


# ─── Catalogos desde SIGARH ─────────────────────────────────────────────
async def get_servicios(db: AsyncSession, tenant_id: uuid.UUID) -> list[Servicio]:
    result = await db.execute(
        select(Servicio)
        .join(ServicioUPSS, ServicioUPSS.servicio_id == Servicio.id)
        .join(UPSS, UPSS.id == ServicioUPSS.upss_id)
        .where(
            Servicio.tenant_id == tenant_id,
            Servicio.is_active == True,
            UPSS.tenant_id == tenant_id,
            UPSS.is_active == True,
        )
        .distinct()
        .order_by(Servicio.nombre)
    )
    return result.scalars().all()


async def get_consultorios(db: AsyncSession, tenant_id: uuid.UUID) -> list[Consultorio]:
    result = await db.execute(
        select(Consultorio)
        .where(Consultorio.tenant_id == tenant_id, Consultorio.is_active == True)
        .order_by(Consultorio.nombre)
    )
    return result.scalars().all()


async def get_seguros(db: AsyncSession, tenant_id: uuid.UUID) -> list[dict]:
    from app.sigarh.config_financiera.models import Seguro
    result = await db.execute(
        select(Seguro).where(Seguro.tenant_id == tenant_id, Seguro.is_active == True).order_by(Seguro.nombre)
    )
    return [{"id": s.id, "nombre": s.nombre} for s in result.scalars().all()]


async def get_especialidades(
    db: AsyncSession, tenant_id: uuid.UUID, servicio_id: uuid.UUID | None = None
) -> list[Especialidad]:
    query = select(Especialidad).where(
        Especialidad.tenant_id == tenant_id, Especialidad.is_active == True
    )
    if servicio_id:
        query = query.join(
            ServicioEspecialidad,
            ServicioEspecialidad.especialidad_id == Especialidad.id,
        ).where(ServicioEspecialidad.servicio_id == servicio_id)
    result = await db.execute(query.order_by(Especialidad.nombre))
    return result.scalars().all()


async def get_medicos_por_especialidad(
    db: AsyncSession, tenant_id: uuid.UUID, especialidad_id: uuid.UUID
) -> list[Empleado]:
    result = await db.execute(
        select(Empleado)
        .join(EmpleadoEspecialidad, EmpleadoEspecialidad.empleado_id == Empleado.id)
        .where(
            Empleado.tenant_id == tenant_id,
            Empleado.is_active == True,
            EmpleadoEspecialidad.especialidad_id == especialidad_id,
        )
        .order_by(Empleado.apellido_paterno)
    )
    return result.scalars().all()


# ─── Programaciones ─────────────────────────────────────────────────────
async def sincronizar_programacion_sigarh(
    db: AsyncSession, tenant_id: uuid.UUID, mes: int, anio: int, *, commit: bool = True
) -> dict:
    """Materializa como agenda diaria las actividades asistenciales de roles aprobados."""
    if mes < 1 or mes > 12:
        raise ValueError("El mes debe estar entre 1 y 12")

    result = await db.execute(
        select(Rol, RolTurno, Actividad, HorarioGuardia, Empleado)
        .join(RolEmpleado, RolEmpleado.rol_id == Rol.id)
        .join(RolActividad, RolActividad.rol_empleado_id == RolEmpleado.id)
        .join(RolTurno, RolTurno.rol_actividad_id == RolActividad.id)
        .join(Actividad, Actividad.id == RolActividad.actividad_id)
        .join(HorarioGuardia, HorarioGuardia.id == RolTurno.horario_guardia_id)
        .join(Empleado, Empleado.id == RolEmpleado.empleado_id)
        .where(
            Rol.tenant_id == tenant_id,
            Rol.mes == mes,
            Rol.anio == anio,
            Rol.status == "approved",
            Empleado.tenant_id == tenant_id,
            Empleado.is_active == True,
            Actividad.tenant_id == tenant_id,
            Actividad.is_active == True,
            HorarioGuardia.tenant_id == tenant_id,
            HorarioGuardia.is_active == True,
            Actividad.genera_agenda == True,
        )
    )
    filas = result.all()

    empleado_ids = {empleado.id for *_, empleado in filas}
    especialidad_por_empleado: dict[uuid.UUID, list[uuid.UUID]] = {}
    if empleado_ids:
        especialidades = await db.execute(
            select(
                EmpleadoEspecialidad.empleado_id, EmpleadoEspecialidad.especialidad_id
            )
            .join(Especialidad, Especialidad.id == EmpleadoEspecialidad.especialidad_id)
            .where(EmpleadoEspecialidad.empleado_id.in_(empleado_ids), EmpleadoEspecialidad.validado == True,
                   Especialidad.tenant_id == tenant_id, Especialidad.is_active == True)
            .order_by(
                EmpleadoEspecialidad.validado.desc(), EmpleadoEspecialidad.created_at
            )
        )
        for empleado_id, especialidad_id in especialidades.all():
            especialidad_por_empleado.setdefault(empleado_id, []).append(especialidad_id)

    relaciones_validas = set(
        (
            await db.execute(
                select(
                    ServicioEspecialidad.servicio_id,
                    ServicioEspecialidad.especialidad_id,
                )
                .join(Servicio, Servicio.id == ServicioEspecialidad.servicio_id)
                .where(Servicio.tenant_id == tenant_id)
            )
        ).all()
    )

    ultimo_dia = monthrange(anio, mes)[1]
    primer_dia, ultimo_fecha = date_type(anio, mes, 1), date_type(anio, mes, ultimo_dia)

    # Ausencias aprobadas (licencia / vacaciones) que suprimen cupos ese día.
    rangos_ausencia: dict[uuid.UUID, list[tuple[date_type, date_type]]] = {}
    if empleado_ids:
        ausencias_rows = await db.execute(
            select(
                Justificacion.empleado_id,
                Justificacion.fecha_inicio,
                Justificacion.fecha_fin,
            ).where(
                Justificacion.empleado_id.in_(empleado_ids),
                Justificacion.estado == "aprobado",
                Justificacion.tipo.in_(("licencia", "vacacion")),
                Justificacion.fecha_inicio <= ultimo_fecha,
                Justificacion.fecha_fin >= primer_dia,
            )
        )
        for emp_id, ini, fin in ausencias_rows.all():
            rangos_ausencia.setdefault(emp_id, []).append((ini, fin))

    # Minutos por paciente definidos a nivel de servicio (NULL -> 15).
    tiempos_servicio = dict(
        (
            await db.execute(
                select(Servicio.id, Servicio.tiempo_atencion_min).where(
                    Servicio.tenant_id == tenant_id
                )
            )
        ).all()
    )

    existentes_result = await db.execute(
        select(ProgramacionMedica).where(
            ProgramacionMedica.tenant_id == tenant_id,
            ProgramacionMedica.origen_sigarh_turno_id.is_not(None),
            ProgramacionMedica.fecha.between(
                date_type(anio, mes, 1), date_type(anio, mes, ultimo_dia)
            ),
        )
    )
    existentes = {
        (p.origen_sigarh_turno_id, p.fecha): p
        for p in existentes_result.scalars().all()
    }
    creadas = actualizadas = omitidas = ausencias = 0
    claves_vigentes: set[tuple[uuid.UUID, date_type]] = set()

    roles_revisados = {}
    from app.sigarh.creacion_roles.service import obtener_rol_orm, diagnosticar_rol, errores_bloqueantes
    for fuente, *_ in filas:
        if fuente.id not in roles_revisados:
            completo = await obtener_rol_orm(db, fuente.id, tenant_id)
            roles_revisados[fuente.id] = errores_bloqueantes(await diagnosticar_rol(db, tenant_id, completo))
    for rol, turno, actividad, horario, empleado in filas:
        if roles_revisados[rol.id]:
            omitidas += 1
            continue
        dias = {
            int(d)
            for d in (turno.dias_semana or [])
            if str(d).isdigit() and 0 <= int(d) <= 6
        }
        servicio_id = rol.servicio_id or empleado.servicio_id
        especialidad_id = next((eid for eid in especialidad_por_empleado.get(empleado.id, [])
                                if (servicio_id, eid) in relaciones_validas), None)
        if not dias or not especialidad_id:
            omitidas += 1
            continue

        rangos = rangos_ausencia.get(empleado.id, ())
        servicio_id = rol.servicio_id or empleado.servicio_id
        if not servicio_id or (servicio_id, especialidad_id) not in relaciones_validas:
            omitidas += 1
            continue
        tiempo_atencion = tiempos_servicio.get(servicio_id) or 15

        for dia_mes in range(1, ultimo_dia + 1):
            fecha = date_type(anio, mes, dia_mes)
            if (fecha.weekday() + 1) % 7 not in dias:  # SIGARH usa domingo=0.
                continue
            from app.sigarh.rrhh.vigencia_laboral import impedimento_programacion
            if impedimento_programacion(empleado, fecha):
                omitidas += 1
                continue
            if any(
                ini <= fecha <= fin for ini, fin in rangos
            ):  # médico de licencia/vacaciones.
                ausencias += 1
                continue
            claves_vigentes.add((turno.id, fecha))
            valores = {
                "medico_id": empleado.id,
                "servicio_id": servicio_id,
                "especialidad_id": especialidad_id,
                "turno": _turno_desde_hora(horario.hora_inicio),
                "hora_inicio": horario.hora_inicio,
                "hora_fin": horario.hora_fin,
                "tiempo_promedio_atencion": tiempo_atencion,
                "tipo_servicio": "CONSULTORIO_EXTERNO",
                "descripcion": f"SIGARH: {actividad.nombre} · rol aprobado {mes:02d}/{anio}",
                "estado": "activo",
            }
            programacion = existentes.get((turno.id, fecha))
            if programacion is None:
                db.add(
                    ProgramacionMedica(
                        tenant_id=tenant_id,
                        origen_sigarh_turno_id=turno.id,
                        fecha=fecha,
                        mostrar_en_consultorio=True,
                        **valores,
                    )
                )
                creadas += 1
            elif any(
                getattr(programacion, campo) != valor
                for campo, valor in valores.items()
            ):
                for campo, valor in valores.items():
                    setattr(programacion, campo, valor)
                actualizadas += 1

    # Si el rol deja de estar aprobado o cambia sus días, ya no debe ofrecer nuevos cupos.
    # La inactivación no cancela citas ya reservadas sobre esa fecha: se cuentan aquí
    # para que el resultado de la sincronización avise de pacientes que requieren
    # gestión manual (reprogramar o contactar), en vez de quedar en silencio.
    citas_en_riesgo = 0
    for clave, programacion in existentes.items():
        if clave not in claves_vigentes and programacion.estado == "activo":
            pendientes = await db.scalar(
                select(func.count(Cita.id)).where(
                    Cita.programacion_medica_id == programacion.id,
                    Cita.estado.not_in(("cancelada", "atendida")),
                )
            )
            citas_en_riesgo += pendientes or 0
            programacion.estado = "inactivo"
            actualizadas += 1

    await db.flush()
    if commit:
        await db.commit()
    return {
        "creadas": creadas,
        "actualizadas": actualizadas,
        "omitidas": omitidas,
        "citas_en_riesgo": citas_en_riesgo,
        "ausencias": ausencias,
        "mes": mes,
        "anio": anio,
    }


async def create_programacion(
    db: AsyncSession, tenant_id: uuid.UUID, data: ProgramacionMedicaCreate
) -> dict:
    await _validar_servicio_especialidad(
        db, tenant_id, data.servicio_id, data.especialidad_id
    )
    await _validar_vigencia_medico(db, tenant_id, data.medico_id, data.fecha)
    prog = ProgramacionMedica(tenant_id=tenant_id, **data.model_dump())
    db.add(prog)
    await db.commit()
    return await get_programacion_by_id(db, tenant_id, prog.id)


def _prog_select():
    return (
        select(ProgramacionMedica, Empleado, Servicio, Especialidad, Consultorio)
        .join(Empleado, Empleado.id == ProgramacionMedica.medico_id)
        .outerjoin(Servicio, Servicio.id == ProgramacionMedica.servicio_id)
        .outerjoin(Especialidad, Especialidad.id == ProgramacionMedica.especialidad_id)
        .outerjoin(Consultorio, Consultorio.id == ProgramacionMedica.consultorio_id)
    )


async def get_programacion_by_id(
    db: AsyncSession, tenant_id: uuid.UUID, prog_id: uuid.UUID
) -> dict | None:
    result = await db.execute(
        _prog_select().where(
            ProgramacionMedica.tenant_id == tenant_id, ProgramacionMedica.id == prog_id
        )
    )
    row = result.first()
    if not row:
        return None
    return _prog_to_dict(*row)


async def list_programaciones(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    servicio_id: uuid.UUID | None = None,
    especialidad_id: uuid.UUID | None = None,
    medico_id: uuid.UUID | None = None,
    fecha: date_type | None = None,
    anio: int | None = None,
    mes: int | None = None,
    estado: str | None = None,
    codigo: str | None = None,
    descripcion: str | None = None,
    tipo_servicio: str | None = None,
) -> list[dict]:
    # Sincroniza el periodo consultado (mes/año explícito, la fecha, o el mes actual).
    if mes and anio:
        sync_mes, sync_anio = mes, anio
    elif fecha:
        sync_mes, sync_anio = fecha.month, fecha.year
    else:
        hoy = date_type.today()
        sync_mes, sync_anio = hoy.month, hoy.year
    await sincronizar_programacion_sigarh(db, tenant_id, sync_mes, sync_anio)

    query = (
        _prog_select()
        .where(ProgramacionMedica.tenant_id == tenant_id)
        .order_by(ProgramacionMedica.fecha.desc(), ProgramacionMedica.codigo.desc())
    )
    if servicio_id:
        query = query.where(ProgramacionMedica.servicio_id == servicio_id)
    if especialidad_id:
        query = query.where(ProgramacionMedica.especialidad_id == especialidad_id)
    if medico_id:
        query = query.where(ProgramacionMedica.medico_id == medico_id)
    if fecha:
        query = query.where(ProgramacionMedica.fecha == fecha)
    elif mes and anio:
        ultimo = monthrange(anio, mes)[1]
        query = query.where(
            ProgramacionMedica.fecha.between(
                date_type(anio, mes, 1), date_type(anio, mes, ultimo)
            )
        )
    if estado:
        query = query.where(ProgramacionMedica.estado == estado)
    if tipo_servicio:
        query = query.where(ProgramacionMedica.tipo_servicio == tipo_servicio)
    if codigo:
        query = query.where(ProgramacionMedica.codigo.ilike(f"%{codigo}%"))
    if descripcion:
        query = query.where(ProgramacionMedica.descripcion.ilike(f"%{descripcion}%"))
    result = await db.execute(query)
    return [_prog_to_dict(*row) for row in result.all()]


async def update_programacion(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    prog_id: uuid.UUID,
    data: ProgramacionMedicaUpdate,
) -> dict | None:
    result = await db.execute(
        select(ProgramacionMedica).where(
            ProgramacionMedica.tenant_id == tenant_id, ProgramacionMedica.id == prog_id
        )
    )
    prog = result.scalar_one_or_none()
    if not prog:
        return None
    changes = data.model_dump(exclude_unset=True)
    await _validar_servicio_especialidad(
        db,
        tenant_id,
        changes.get("servicio_id", prog.servicio_id),
        changes.get("especialidad_id", prog.especialidad_id),
    )
    if changes.get("estado", prog.estado) == "activo":
        await _validar_vigencia_medico(db, tenant_id, changes.get("medico_id", prog.medico_id), changes.get("fecha", prog.fecha))
    for field, value in changes.items():
        setattr(prog, field, value)
    await db.commit()
    return await get_programacion_by_id(db, tenant_id, prog_id)


async def _validar_servicio_especialidad(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    servicio_id: uuid.UUID | None,
    especialidad_id: uuid.UUID | None,
) -> None:
    if not servicio_id or not especialidad_id:
        return
    linked = await db.scalar(
        select(ServicioEspecialidad.servicio_id)
        .join(Servicio, Servicio.id == ServicioEspecialidad.servicio_id)
        .where(
            Servicio.tenant_id == tenant_id,
            ServicioEspecialidad.servicio_id == servicio_id,
            ServicioEspecialidad.especialidad_id == especialidad_id,
        )
    )
    if not linked:
        raise HTTPException(
            422, "La especialidad no pertenece al servicio seleccionado"
        )


async def delete_programacion(
    db: AsyncSession, tenant_id: uuid.UUID, prog_id: uuid.UUID
) -> str:
    """'ok' si se eliminó, 'not_found', o 'sigarh' si proviene de un rol (no se borra aquí)."""
    prog = await db.scalar(
        select(ProgramacionMedica).where(
            ProgramacionMedica.tenant_id == tenant_id, ProgramacionMedica.id == prog_id
        )
    )
    if not prog:
        return "not_found"
    if prog.origen_sigarh_turno_id:
        return "sigarh"
    await db.delete(prog)
    await db.commit()
    return "ok"


def _prog_to_dict(
    prog: ProgramacionMedica,
    medico: Empleado,
    servicio: Servicio | None,
    especialidad: Especialidad | None,
    consultorio: "Consultorio | None" = None,
) -> dict:
    return {
        "id": prog.id,
        "codigo": prog.codigo,
        "medico_id": prog.medico_id,
        "medico_nombre": medico.nombre_completo,
        "servicio_id": prog.servicio_id,
        "servicio_nombre": servicio.nombre if servicio else None,
        "especialidad_id": prog.especialidad_id,
        "especialidad_nombre": especialidad.nombre if especialidad else None,
        "consultorio_id": prog.consultorio_id,
        "consultorio_nombre": consultorio.nombre if consultorio else None,
        "origen_sigarh_turno_id": prog.origen_sigarh_turno_id,
        "origen": "SIGARH" if prog.origen_sigarh_turno_id else "MANUAL",
        "fecha": prog.fecha,
        "turno": prog.turno,
        "hora_inicio": prog.hora_inicio,
        "hora_fin": prog.hora_fin,
        "tiempo_promedio_atencion": prog.tiempo_promedio_atencion,
        "tipo_servicio": prog.tipo_servicio,
        "modalidad": getattr(prog, "modalidad", "PRESENCIAL"),
        "mostrar_en_consultorio": prog.mostrar_en_consultorio,
        "descripcion": prog.descripcion,
        "estado": prog.estado,
        "created_at": prog.created_at,
    }


async def list_citas_para_triaje(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    fecha: date_type | None = None,
    especialidad_id: uuid.UUID | None = None,
    servicio_id: uuid.UUID | None = None,
    medico_id: uuid.UUID | None = None,
) -> list[dict]:
    query = (
        select(
            Cita,
            Patient,
            ProgramacionMedica,
            Empleado,
            Servicio,
            Especialidad,
            Triaje,
            ClinicalRecord,
        )
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
    for (
        cita,
        paciente,
        prog,
        medico,
        servicio,
        especialidad,
        triaje,
        clinical_record,
    ) in result.all():
        items.append(
            {
                "cita_id": cita.id,
                "paciente_nombre": paciente.full_name,
                "paciente_dni": paciente.dni,
                "paciente_hc": clinical_record.record_number
                if clinical_record
                else None,
                "fuente_financiamiento": cita.fuente_financiamiento,
                "especialidad_nombre": especialidad.nombre if especialidad else None,
                "servicio_nombre": servicio.nombre if servicio else None,
                "medico_nombre": medico.nombre_completo,
                "fecha": prog.fecha,
                "hora_inicio": cita.hora_inicio,
                "paso_triaje": triaje is not None,
            }
        )
    return items


# ─── Cupos (calculados en memoria, no se guardan) ───────────────────────
def _generar_slots(
    hora_inicio: str, hora_fin: str, minutos: int
) -> list[tuple[str, str]]:
    fmt = "%H:%M"
    inicio = datetime.strptime(hora_inicio, fmt)
    fin = datetime.strptime(hora_fin, fmt)
    if minutos <= 0:
        raise ValueError("El tiempo de atenci\u00f3n debe ser mayor que cero")
    if fin <= inicio:
        fin += timedelta(days=1)
    slots = []
    actual = inicio
    while actual + timedelta(minutes=minutos) <= fin:
        siguiente = actual + timedelta(minutes=minutos)
        slots.append((actual.strftime(fmt), siguiente.strftime(fmt)))
        actual = siguiente
    return slots


async def _validar_rol_programacion(db, tenant_id, prog):
    if not prog.origen_sigarh_turno_id:
        return
    from app.sigarh.creacion_roles.service import obtener_rol_orm, diagnosticar_rol, errores_bloqueantes
    rol_id = await db.scalar(select(Rol.id)
        .join(RolEmpleado, RolEmpleado.rol_id == Rol.id)
        .join(RolActividad, RolActividad.rol_empleado_id == RolEmpleado.id)
        .join(RolTurno, RolTurno.rol_actividad_id == RolActividad.id)
        .where(Rol.tenant_id == tenant_id, RolTurno.id == prog.origen_sigarh_turno_id))
    rol = await obtener_rol_orm(db, rol_id, tenant_id) if rol_id else None
    if not rol or rol.status != "approved":
        raise ValueError("La programación requiere un rol aprobado vigente.")
    errores = errores_bloqueantes(await diagnosticar_rol(db, tenant_id, rol))
    if errores:
        raise ValueError("La programación no cumple validaciones: " + " · ".join(errores[:4]))


async def get_cupos(
    db: AsyncSession, tenant_id: uuid.UUID, programacion_id: uuid.UUID
) -> list[dict] | None:
    result = await db.execute(
        select(ProgramacionMedica).where(
            ProgramacionMedica.tenant_id == tenant_id,
            ProgramacionMedica.id == programacion_id,
        )
    )
    prog = result.scalar_one_or_none()
    if not prog:
        return None

    if prog.estado != "activo":
        return []
    await _validar_rol_programacion(db, tenant_id, prog)
    slots = _generar_slots(
        prog.hora_inicio, prog.hora_fin, prog.tiempo_promedio_atencion
    )

    result = await db.execute(
        select(Cita, Patient)
        .join(Patient, Patient.id == Cita.patient_id)
        .where(
            Cita.programacion_medica_id == programacion_id, Cita.estado != "cancelada"
        )
    )
    ocupados = {cita.hora_inicio: (cita, paciente) for cita, paciente in result.all()}

    cupos = []
    for inicio, fin in slots:
        if inicio in ocupados:
            cita, paciente = ocupados[inicio]
            cupos.append(
                {
                    "hora_inicio": inicio,
                    "hora_fin": fin,
                    "disponible": False,
                    "cita_id": cita.id,
                    "paciente_nombre": paciente.full_name,
                }
            )
        else:
            cupos.append(
                {
                    "hora_inicio": inicio,
                    "hora_fin": fin,
                    "disponible": True,
                    "cita_id": None,
                    "paciente_nombre": None,
                }
            )
    return cupos


# ─── Citas ───────────────────────────────────────────────────────────────
async def create_cita(db: AsyncSession, tenant_id: uuid.UUID, data: CitaCreate) -> dict:
    programacion_result = await db.execute(
        select(ProgramacionMedica).where(
            ProgramacionMedica.id == data.programacion_medica_id,
            ProgramacionMedica.tenant_id == tenant_id,
            ProgramacionMedica.estado == "activo",
        )
    )
    programacion = programacion_result.scalar_one_or_none()
    if not programacion:
        raise ValueError("La programación no existe o no está activa")

    await _validar_rol_programacion(db, tenant_id, programacion)
    paciente_result = await db.execute(
        select(Patient.id).where(
            Patient.id == data.patient_id, Patient.tenant_id == tenant_id
        )
    )
    if paciente_result.scalar_one_or_none() is None:
        raise ValueError("El paciente no pertenece al hospital")

    slots_validos = set(
        _generar_slots(
            programacion.hora_inicio,
            programacion.hora_fin,
            programacion.tiempo_promedio_atencion,
        )
    )
    if (data.hora_inicio, data.hora_fin) not in slots_validos:
        raise ValueError(
            "El horario seleccionado no pertenece a la programación médica"
        )

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
    try:
        await db.commit()
    except IntegrityError:
        # Otro operador reservó el mismo cupo entre la validación previa y este commit.
        await db.rollback()
        raise ValueError("Ese cupo ya está ocupado")
    return await get_cita_by_id(db, tenant_id, cita.id)


async def get_cita_by_id(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID
) -> dict | None:
    result = await db.execute(
        select(
            Cita,
            Patient,
            ProgramacionMedica,
            Empleado,
            Servicio,
            Especialidad,
            ClinicalRecord,
        )
        .join(Patient, Patient.id == Cita.patient_id)
        .join(ProgramacionMedica, ProgramacionMedica.id == Cita.programacion_medica_id)
        .join(Empleado, Empleado.id == ProgramacionMedica.medico_id)
        .outerjoin(Servicio, Servicio.id == ProgramacionMedica.servicio_id)
        .outerjoin(Especialidad, Especialidad.id == ProgramacionMedica.especialidad_id)
        .outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id)
        .where(Cita.tenant_id == tenant_id, Cita.id == cita_id)
    )
    row = result.first()
    if not row:
        return None
    cita, paciente, programacion, medico, servicio, especialidad, historia = row
    return _cita_to_dict(
        cita, paciente, programacion, medico, servicio, especialidad, historia
    )


async def list_citas(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    programacion_medica_id: uuid.UUID | None = None,
    estado: str | None = None,
    fecha: date_type | None = None,
    fecha_desde: date_type | None = None,
    fecha_hasta: date_type | None = None,
    dni: str | None = None,
    cuenta: str | None = None,
    historia: str | None = None,
    apellido: str | None = None,
    medico_id: uuid.UUID | None = None,
) -> list[dict]:
    query = (
        select(
            Cita,
            Patient,
            ProgramacionMedica,
            Empleado,
            Servicio,
            Especialidad,
            ClinicalRecord,
        )
        .join(Patient, Patient.id == Cita.patient_id)
        .join(ProgramacionMedica, ProgramacionMedica.id == Cita.programacion_medica_id)
        .join(Empleado, Empleado.id == ProgramacionMedica.medico_id)
        .outerjoin(Servicio, Servicio.id == ProgramacionMedica.servicio_id)
        .outerjoin(Especialidad, Especialidad.id == ProgramacionMedica.especialidad_id)
        .outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id)
        .where(Cita.tenant_id == tenant_id)
    )
    if programacion_medica_id:
        query = query.where(Cita.programacion_medica_id == programacion_medica_id)
    if estado:
        query = query.where(Cita.estado == estado)
    if fecha:
        query = query.where(ProgramacionMedica.fecha == fecha)
    if fecha_desde:
        query = query.where(ProgramacionMedica.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.where(ProgramacionMedica.fecha <= fecha_hasta)
    if dni:
        query = query.where(Patient.dni.ilike(f"%{dni.strip()}%"))
    if cuenta:
        query = query.where(Cita.numero_cuenta.ilike(f"%{cuenta.strip()}%"))
    if historia:
        query = query.where(ClinicalRecord.record_number.ilike(f"%{historia.strip()}%"))
    if apellido:
        query = query.where(
            or_(
                Patient.last_name_paterno.ilike(f"%{apellido.strip()}%"),
                Patient.last_name_materno.ilike(f"%{apellido.strip()}%"),
            )
        )
    if medico_id:
        query = query.where(ProgramacionMedica.medico_id == medico_id)
    result = await db.execute(query.order_by(Cita.hora_inicio))
    return [_cita_to_dict(*row) for row in result.all()]


async def reprogramar_cita(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    cita_id: uuid.UUID,
    programacion_id: uuid.UUID,
    hora_inicio: str,
    hora_fin: str,
    mensaje: str | None = None,
) -> dict | None:
    cita = await db.scalar(
        select(Cita)
        .where(Cita.tenant_id == tenant_id, Cita.id == cita_id)
        .with_for_update()
    )
    if not cita:
        return None
    if await db.scalar(select(Triaje.id).where(Triaje.tenant_id == tenant_id, Triaje.cita_id == cita.id)):
        raise ValueError("La cita ya tiene triaje; no puede trasladar su registro clínico a otra programación.")
    if cita.estado in ("atendida", "cancelada"):
        raise ValueError(f"No se puede reprogramar una cita {cita.estado}")
    programacion = await db.scalar(
        select(ProgramacionMedica).where(
            ProgramacionMedica.id == programacion_id,
            ProgramacionMedica.tenant_id == tenant_id,
            ProgramacionMedica.estado == "activo",
            ProgramacionMedica.origen_sigarh_turno_id.is_not(None),
        )
    )
    if not programacion:
        raise ValueError("La programación seleccionada no está autorizada en SIGARH")
    cupos = await get_cupos(db, tenant_id, programacion_id)
    if not cupos or not any(
        c["hora_inicio"] == hora_inicio
        and c["hora_fin"] == hora_fin
        and c["disponible"]
        for c in cupos
    ):
        raise ValueError("El horario ya no está disponible")
    cita.programacion_medica_id = programacion_id
    cita.hora_inicio = hora_inicio
    cita.hora_fin = hora_fin
    if mensaje:
        cita.observacion = "\n".join(
            filter(None, [cita.observacion, f"Reprogramación: {mensaje.strip()}"])
        )
    await db.commit()
    return await get_cita_by_id(db, tenant_id, cita_id)


async def reprogramar_citas_bloque(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    cita_ids: list[uuid.UUID],
    programacion_id: uuid.UUID,
    mensaje: str | None = None,
) -> list[dict]:
    programacion = await db.scalar(
        select(ProgramacionMedica).where(
            ProgramacionMedica.id == programacion_id,
            ProgramacionMedica.tenant_id == tenant_id,
            ProgramacionMedica.estado == "activo",
            ProgramacionMedica.origen_sigarh_turno_id.is_not(None),
        )
    )
    if not programacion:
        raise ValueError("La programación seleccionada no está autorizada en SIGARH")
    cupos = [
        c
        for c in (await get_cupos(db, tenant_id, programacion_id) or [])
        if c["disponible"]
    ]
    if len(cupos) < len(cita_ids):
        raise ValueError(
            f"Solo hay {len(cupos)} cupos libres para {len(cita_ids)} citas"
        )
    citas = (
        await db.scalars(
            select(Cita)
            .where(Cita.tenant_id == tenant_id, Cita.id.in_(cita_ids))
            .with_for_update()
        )
    ).all()
    if len(citas) != len(set(cita_ids)):
        raise ValueError("Una o más citas no existen")
    if any(c.estado in ("atendida", "cancelada") for c in citas):
        raise ValueError("No se pueden reprogramar citas atendidas o canceladas")
    if await db.scalar(select(Triaje.id).where(Triaje.tenant_id == tenant_id, Triaje.cita_id.in_([c.id for c in citas])).limit(1)):
        raise ValueError("No puede reprogramar citas que ya tienen triaje.")
    for cita, cupo in zip(sorted(citas, key=lambda c: c.hora_inicio), cupos):
        cita.programacion_medica_id = programacion_id
        cita.hora_inicio = cupo["hora_inicio"]
        cita.hora_fin = cupo["hora_fin"]
        if mensaje:
            texto = mensaje.replace(
                "{paciente}",
                (await get_cita_by_id(db, tenant_id, cita.id) or {}).get(
                    "paciente_nombre", "paciente"
                ),
            )
            cita.observacion = "\n".join(
                filter(None, [cita.observacion, f"Reprogramación: {texto.strip()}"])
            )
    await db.commit()
    resultados = []
    for cita in citas:
        resultados.append(await get_cita_by_id(db, tenant_id, cita.id))
    return resultados


async def update_cita(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: CitaUpdate
) -> dict | None:
    result = await db.execute(
        select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id).with_for_update().execution_options(populate_existing=True)
    )
    cita = result.scalar_one_or_none()
    if not cita:
        return None
    cambios = data.model_dump(exclude_unset=True)
    nuevo_estado = cambios.get("estado", cita.estado)
    if nuevo_estado != cita.estado:
        if cita.estado not in ("separada", "confirmada") or nuevo_estado not in ("cancelada", "no_asistio"):
            raise ValueError("Confirme la cita con su acción específica. El estado atendida se registra desde la atención médica.")
        if await db.scalar(select(Triaje.id).where(Triaje.tenant_id == tenant_id, Triaje.cita_id == cita_id)):
            raise ValueError("La cita ya tiene triaje; continúe su atención clínica.")
        if nuevo_estado == "no_asistio":
            prog = await db.scalar(select(ProgramacionMedica).where(ProgramacionMedica.tenant_id == tenant_id, ProgramacionMedica.id == cita.programacion_medica_id))
            from zoneinfo import ZoneInfo
            if prog and prog.fecha > datetime.now(ZoneInfo("America/Lima")).date():
                raise ValueError("No puede marcar como no asistió una cita de una fecha futura.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cita, field, value)
    await db.commit()
    return await get_cita_by_id(db, tenant_id, cita_id)


def _cita_to_dict(
    cita: Cita,
    paciente: Patient,
    programacion: ProgramacionMedica | None = None,
    medico: Empleado | None = None,
    servicio: Servicio | None = None,
    especialidad: Especialidad | None = None,
    historia: ClinicalRecord | None = None,
) -> dict:
    data = {
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
    if programacion:
        data.update(
            {
                "fecha": programacion.fecha,
                "turno": programacion.turno,
                "medico_id": programacion.medico_id,
                "medico_nombre": medico.nombre_completo if medico else None,
                "servicio_nombre": servicio.nombre if servicio else None,
                "especialidad_nombre": especialidad.nombre if especialidad else None,
                "paciente_record": historia.record_number if historia else None,
                "paciente_insurance": paciente.insurance_type,
                "paciente_telefono": paciente.phone,
            }
        )
    return data


async def generar_comprobante_cita_pdf(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID
) -> tuple[bytes, str] | None:
    cita = await get_cita_by_id(db, tenant_id, cita_id)
    if not cita:
        return None
    from app.core.tenant_db import get_tenant_by_id
    hospital = await get_tenant_by_id(tenant_id)

    codigo = f"CITA-{str(cita_id).split('-')[0].upper()}"
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"Comprobante de cita {codigo}",
        author=hospital.name if hospital else "Hospital",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "CitaTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#123F59"),
        spaceAfter=4 * mm,
    )
    center = ParagraphStyle(
        "CitaCenter",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.HexColor("#4B6472"),
        leading=12,
    )
    normal = ParagraphStyle(
        "CitaNormal", parent=styles["Normal"], fontSize=9, leading=12
    )
    label = ParagraphStyle(
        "CitaLabel",
        parent=normal,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#425968"),
    )

    def p(value, style=normal):
        return Paragraph(escape(str(value if value not in (None, "") else "—")), style)

    fecha = cita.get("fecha")
    fecha_texto = fecha.strftime("%d/%m/%Y") if fecha else "—"
    medico = cita.get("medico_nombre") or "—"
    cmp = ""
    body = [
        p((hospital.name if hospital else "ESTABLECIMIENTO DE SALUD").upper(), title),
        p(
            "CONSTANCIA DE CITA MÉDICA",
            ParagraphStyle(
                "DocTitle", parent=title, fontSize=14, textColor=colors.black
            ),
        ),
        p(f"Código de cita: {codigo}", center),
        Spacer(1, 5 * mm),
    ]
    header_data = [
        [
            p("ESTABLECIMIENTO", label),
            p(hospital.name if hospital else "—"),
            p("RUC", label),
            p(hospital.ruc if hospital else "—"),
        ],
        [
            p("DIRECCIÓN", label),
            p(hospital.address if hospital else "—"),
            p("TELÉFONO", label),
            p(hospital.phone if hospital else "—"),
        ],
    ]
    detail_data = [
        [
            p("PACIENTE", label),
            p(cita["paciente_nombre"]),
            p("DNI / DOCUMENTO", label),
            p(cita.get("paciente_dni")),
        ],
        [
            p("HISTORIA CLÍNICA", label),
            p(cita.get("paciente_record")),
            p("N.° CUENTA", label),
            p(cita.get("numero_cuenta")),
        ],
        [
            p("FECHA", label),
            p(fecha_texto),
            p("HORA", label),
            p(f"{cita['hora_inicio']} - {cita['hora_fin']}"),
        ],
        [
            p("ESPECIALIDAD", label),
            p(cita.get("especialidad_nombre")),
            p("SERVICIO", label),
            p(cita.get("servicio_nombre")),
        ],
        [p("MÉDICO", label), p(medico + cmp), p("TURNO", label), p(cita.get("turno"))],
        [
            p("TIPO DE CONSULTA", label),
            p(cita.get("tipo_consulta")),
            p("ESTADO", label),
            p(str(cita.get("estado", "")).upper()),
        ],
        [
            p("FINANCIAMIENTO", label),
            p(cita.get("fuente_financiamiento")),
            p("PRODUCTO / PLAN", label),
            p(cita.get("producto_plan")),
        ],
        [p("OBSERVACIONES", label), p(cita.get("observacion")), "", ""],
    ]
    for data in (header_data, detail_data):
        table = Table(
            data, colWidths=[35 * mm, 58 * mm, 35 * mm, 48 * mm], hAlign="CENTER"
        )
        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#B8C9D2")),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF4F5")),
                    ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#EAF4F5")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ("SPAN", (1, -1), (3, -1))
                    if data is detail_data
                    else ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        body.extend([table, Spacer(1, 5 * mm)])
    body.extend(
        [
            p(
                "Indicaciones",
                ParagraphStyle(
                    "Instructions", parent=label, fontSize=10, spaceAfter=2 * mm
                ),
            ),
            p(
                "Presentarse 30 minutos antes de la hora indicada con su documento de identidad y esta constancia. "
                "En caso de no poder asistir, comuníquese con el establecimiento para reprogramar."
            ),
            Spacer(1, 14 * mm),
            Table(
                [
                    [
                        "______________________________",
                        "______________________________",
                    ],
                    [
                        p("Firma / sello del establecimiento", center),
                        p("Firma del paciente", center),
                    ],
                ],
                colWidths=[88 * mm, 88 * mm],
                style=TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]),
            ),
            Spacer(1, 8 * mm),
            p(
                f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} · {codigo}",
                center,
            ),
        ]
    )
    doc.build(body)
    return buffer.getvalue(), f"cita-{codigo}.pdf"


# ─── Confirmar cita (paso previo a Triaje) ──────────────────────────────
async def confirmar_cita(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID
) -> dict | None:
    result = await db.execute(
        select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id).with_for_update().execution_options(populate_existing=True)
    )
    cita = result.scalar_one_or_none()
    if not cita:
        return None
    if cita.estado != "separada":
        raise ValueError(f"No se puede confirmar una cita en estado '{cita.estado}'")
    prog = await db.scalar(select(ProgramacionMedica).where(ProgramacionMedica.tenant_id == tenant_id, ProgramacionMedica.id == cita.programacion_medica_id))
    if not prog or prog.estado != "activo":
        raise ValueError("La programación ya no está activa; reprograme la cita.")
    await _validar_rol_programacion(db, tenant_id, prog)
    cita.estado = "confirmada"
    await db.commit()
    return await get_cita_by_id(db, tenant_id, cita_id)


async def create_triaje(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: TriajeCreate
) -> dict:
    result = await db.execute(
        select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id).with_for_update().execution_options(populate_existing=True)
    )
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


async def get_triaje_by_cita(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID
) -> Triaje | None:
    result = await db.execute(
        select(Triaje).where(Triaje.tenant_id == tenant_id, Triaje.cita_id == cita_id)
    )
    return result.scalar_one_or_none()


async def update_triaje(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: "TriajeUpdate"
) -> Triaje | None:
    cita = await db.scalar(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id).with_for_update().execution_options(populate_existing=True))
    if not cita:
        return None
    if cita.estado != "confirmada":
        raise ValueError("Solo puede editar el triaje mientras la cita está confirmada, antes de la atención médica.")
    result = await db.execute(
        select(Triaje).where(Triaje.tenant_id == tenant_id, Triaje.cita_id == cita_id)
    )
    triaje = result.scalar_one_or_none()
    if not triaje:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(triaje, field, value)
    await db.commit()
    await db.refresh(triaje)
    return triaje


async def buscar_cie10(
    db: AsyncSession, tenant_id: uuid.UUID, q: str
) -> list[DiagnosticoCIE10]:
    result = await db.execute(
        select(DiagnosticoCIE10)
        .where(
            DiagnosticoCIE10.tenant_id == tenant_id,
            DiagnosticoCIE10.is_active == True,
            or_(
                DiagnosticoCIE10.codigo_cie10.ilike(f"%{q}%"),
                DiagnosticoCIE10.descripcion.ilike(f"%{q}%"),
            ),
        )
        .limit(20)
    )
    return result.scalars().all()


ANTECEDENTES = ("antecedente_quirurgico", "antecedente_patologico", "antecedente_alergias", "antecedentes_obstetricos", "antecedente_familiares", "antecedente_otros")


def expediente(atencion):
    return {k: getattr(atencion, k) for k in ("motivo_consulta", "enfermedad_actual", "examen_clinico", "plan_tratamiento", "observaciones", "destino_atencion", "indicaciones_alta", "antecedentes_snapshot", "prestaciones", "estado")}


async def auditar_atencion(db, tenant_id, atencion, user, accion, antes=None):
    from app.admin.auditoria.models import AuditLog
    await db.flush()
    dx = (await db.scalars(select(AtencionDiagnostico).where(AtencionDiagnostico.atencion_medica_id == atencion.id))).all()
    datos = expediente(atencion) | {"diagnosticos": [{"id": str(d.diagnostico_cie10_id), "tipo": d.tipo} for d in dx], "cierre_evidencia": atencion.cierre_evidencia}
    db.add(AuditLog(tenant_id=tenant_id, user_id=uuid.UUID(user["sub"]) if user and user.get("sub") else None,
        action=accion, model="AtencionMedica", model_id=str(atencion.id), old_values=antes,
        new_values=datos))


async def validar_diagnosticos(db, tenant_id, diagnosticos):
    ids = [d.diagnostico_cie10_id for d in diagnosticos]
    if len(ids) != len(set(ids)):
        raise ValueError("No repita un diagnóstico en la misma atención.")
    if ids:
        activos = (await db.scalars(select(DiagnosticoCIE10.id).where(DiagnosticoCIE10.tenant_id == tenant_id,
            DiagnosticoCIE10.id.in_(ids), DiagnosticoCIE10.is_active == True))).all()
        if set(activos) != set(ids):
            raise ValueError("Seleccione diagnósticos activos del catálogo CIE-10 de este hospital.")


async def reemplazar_diagnosticos(db, atencion_id, diagnosticos):
    await db.execute(delete(AtencionDiagnostico).where(AtencionDiagnostico.atencion_medica_id == atencion_id))
    for dx in diagnosticos:
        db.add(AtencionDiagnostico(atencion_medica_id=atencion_id, diagnostico_cie10_id=dx.diagnostico_cie10_id, tipo=dx.tipo))


async def validar_autor_clinico(db, tenant_id, cita, user):
    from app.auth.models import User
    from app.sigarh.mantenimiento.models import Profesion
    usuario = await db.scalar(select(User).where(User.id == uuid.UUID(user["sub"]), User.is_active == True)) if user else None
    if not usuario or usuario.panel != "app" or usuario.role != "medico" or not usuario.empleado_id:
        raise ValueError("La atención requiere una cuenta médica vinculada al empleado desde SIGARH > Mantenimiento > Usuarios.")
    prog = await db.scalar(select(ProgramacionMedica).where(ProgramacionMedica.id == cita.programacion_medica_id, ProgramacionMedica.tenant_id == tenant_id))
    medico = await db.scalar(select(Empleado).where(Empleado.id == usuario.empleado_id, Empleado.tenant_id == tenant_id, Empleado.is_active == True))
    profesion = await db.scalar(select(Profesion.codigo).where(Profesion.id == medico.profesion_id, Profesion.tenant_id == tenant_id)) if medico else None
    if not medico or not prog or prog.medico_id != medico.id or profesion != "MED" or not medico.habilitado_colegio or not (medico.numero_cmp or medico.numero_colegiatura):
        raise ValueError("Solo el médico programado con colegiatura y habilitación registrada puede modificar o cerrar la atención.")
    return usuario, medico, prog


async def create_atencion_medica(db, tenant_id, cita_id, data, user=None):
    cita = await db.scalar(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id).with_for_update().execution_options(populate_existing=True))
    if not cita or cita.estado != "confirmada":
        raise ValueError("La atención requiere una cita confirmada.")
    if user:
        await validar_autor_clinico(db, tenant_id, cita, user)
    if not await db.scalar(select(Triaje.id).where(Triaje.tenant_id == tenant_id, Triaje.cita_id == cita_id)):
        raise ValueError("Registre el triaje antes de iniciar la atención médica.")
    if await db.scalar(select(AtencionMedica.id).where(AtencionMedica.cita_id == cita_id)):
        raise ValueError("Esta cita ya tiene atención médica.")
    await validar_diagnosticos(db, tenant_id, data.diagnosticos)
    paciente = await db.scalar(select(Patient).where(Patient.id == cita.patient_id, Patient.tenant_id == tenant_id))
    snapshot = data.antecedentes.model_dump() if data.antecedentes else {k: getattr(paciente, k) for k in ANTECEDENTES}
    payload = data.model_dump(exclude={"diagnosticos", "antecedentes"})
    atencion = AtencionMedica(tenant_id=tenant_id, cita_id=cita_id, antecedentes_snapshot=snapshot, **payload)
    db.add(atencion)
    await db.flush()
    await reemplazar_diagnosticos(db, atencion.id, data.diagnosticos)
    await auditar_atencion(db, tenant_id, atencion, user, "atencion_creada")
    await db.commit()
    return await get_atencion_medica(db, tenant_id, cita_id)


async def get_atencion_medica(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID
) -> dict | None:
    result = await db.execute(
        select(
            AtencionMedica,
            Cita,
            Patient,
            ProgramacionMedica,
            Empleado,
            Servicio,
            Especialidad,
            Triaje,
        )
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
        .join(
            DiagnosticoCIE10,
            DiagnosticoCIE10.id == AtencionDiagnostico.diagnostico_cie10_id,
        )
        .where(AtencionDiagnostico.atencion_medica_id == atencion.id)
    )
    diagnosticos = [
        {
            "id": d.id,
            "diagnostico_cie10_id": d.diagnostico_cie10_id,
            "codigo_cie10": c.codigo_cie10,
            "descripcion": c.descripcion,
            "tipo": d.tipo,
        }
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
        "enfermedad_actual": atencion.enfermedad_actual,
        "prestaciones": atencion.prestaciones or [],
        "antecedentes_documentados": atencion.antecedentes_snapshot is not None,
        "cierre_evidencia": atencion.cierre_evidencia,
        "examen_clinico": atencion.examen_clinico,
        "plan_tratamiento": atencion.plan_tratamiento,
        "observaciones": atencion.observaciones,
        "destino_atencion": atencion.destino_atencion,
        "indicaciones_alta": atencion.indicaciones_alta,
        "estado": atencion.estado,
        "firmado_at": atencion.firmado_at,
        "diagnosticos": diagnosticos,
        "antecedente_quirurgico": (atencion.antecedentes_snapshot or {}).get("antecedente_quirurgico"),
        "antecedente_patologico": (atencion.antecedentes_snapshot or {}).get("antecedente_patologico"),
        "antecedente_alergias": (atencion.antecedentes_snapshot or {}).get("antecedente_alergias"),
        "antecedentes_obstetricos": (atencion.antecedentes_snapshot or {}).get("antecedentes_obstetricos"),
        "antecedente_familiares": (atencion.antecedentes_snapshot or {}).get("antecedente_familiares"),
        "antecedente_otros": (atencion.antecedentes_snapshot or {}).get("antecedente_otros"),
        "triaje": {
            "pulso": triaje.pulso,
            "temperatura": triaje.temperatura,
            "presion_sistolica": triaje.presion_sistolica,
            "presion_diastolica": triaje.presion_diastolica,
            "frecuencia_cardiaca": triaje.frecuencia_cardiaca,
            "frecuencia_respiratoria": triaje.frecuencia_respiratoria,
            "peso": triaje.peso,
            "talla": triaje.talla,
            "imc": triaje.imc,
            "saturacion_o2": triaje.saturacion_o2,
        }
        if triaje
        else None,
        "created_at": atencion.created_at,
    }


async def update_atencion_medica(db, tenant_id, cita_id, data, user=None):
    atencion = await db.scalar(select(AtencionMedica).where(AtencionMedica.tenant_id == tenant_id,
        AtencionMedica.cita_id == cita_id).with_for_update().execution_options(populate_existing=True))
    if not atencion:
        return None
    if atencion.estado != "borrador":
        raise ValueError("No puede editar una atención cerrada.")
    if user:
        cita = await db.scalar(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id))
        await validar_autor_clinico(db, tenant_id, cita, user)
    payload = data.model_dump(exclude_unset=True, exclude={"diagnosticos", "antecedentes"})
    if data.diagnosticos is not None:
        await validar_diagnosticos(db, tenant_id, data.diagnosticos)
    # Evita dejar documentos emitidos fuera de la selección guardada.
    for prestacion, modelo in (("FARMACIA", Receta), ("LABORATORIO", OrdenLaboratorio), ("IMAGEN", OrdenImagen), ("INTERCONSULTA", Interconsulta), ("HOSPITALIZACION", Hospitalizacion), ("REFERENCIA", Referencia)):
        requerida = prestacion in payload.get("prestaciones", atencion.prestaciones or []) or prestacion == payload.get("destino_atencion", atencion.destino_atencion)
        if not requerida and await db.scalar(select(modelo.id).where(modelo.atencion_medica_id == atencion.id)):
            raise ValueError("Ya existe un documento de " + prestacion + "; no puede quitarlo de esta atención.")
    antes = expediente(atencion)
    for k, v in payload.items():
        setattr(atencion, k, v)
    if data.antecedentes is not None:
        atencion.antecedentes_snapshot = data.antecedentes.model_dump()
    if data.diagnosticos is not None:
        await reemplazar_diagnosticos(db, atencion.id, data.diagnosticos)
    await auditar_atencion(db, tenant_id, atencion, user, "atencion_editada", antes)
    await db.commit()
    return await get_atencion_medica(db, tenant_id, cita_id)


async def firmar_atencion_medica(db, tenant_id, cita_id, firmado_por_id=None, user=None):
    import hashlib, json
    from app.auth.models import User
    cita = await db.scalar(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id).with_for_update().execution_options(populate_existing=True))
    if not cita:
        return None
    atencion = await db.scalar(select(AtencionMedica).where(AtencionMedica.tenant_id == tenant_id,
        AtencionMedica.cita_id == cita_id).with_for_update().execution_options(populate_existing=True))
    if not atencion:
        return None
    if atencion.estado != "borrador":
        raise ValueError("Esta atención ya está cerrada.")
    usuario, medico, prog = await validar_autor_clinico(db, tenant_id, cita, user)
    faltantes = [k for k in ("motivo_consulta", "enfermedad_actual", "examen_clinico", "plan_tratamiento") if not (getattr(atencion, k) or "").strip()]
    if faltantes:
        raise ValueError("Complete los datos clínicos: " + ", ".join(faltantes))
    if not atencion.antecedentes_snapshot or any(not (atencion.antecedentes_snapshot.get(k) or "").strip() for k in ANTECEDENTES):
        raise ValueError("Documente los antecedentes; indique expresamente cuando no aplica o el paciente no refiere.")
    triaje = await get_triaje_by_cita(db, tenant_id, cita_id)
    if not triaje:
        raise ValueError("La atención requiere triaje registrado.")
    diagnosticos = (await db.scalars(select(AtencionDiagnostico).where(AtencionDiagnostico.atencion_medica_id == atencion.id))).all()
    if not diagnosticos:
        raise ValueError("Registre al menos un diagnóstico CIE-10.")
    await validar_diagnosticos(db, tenant_id, diagnosticos)
    if atencion.destino_atencion not in ("ALTA", "HOSPITALIZACION", "REFERENCIA"):
        raise ValueError("Seleccione un destino del paciente válido.")
    if atencion.destino_atencion == "ALTA" and not (atencion.indicaciones_alta or "").strip():
        raise ValueError("Registre las indicaciones de alta.")
    for prestacion, modelo in (("FARMACIA", Receta), ("LABORATORIO", OrdenLaboratorio), ("IMAGEN", OrdenImagen), ("INTERCONSULTA", Interconsulta), ("HOSPITALIZACION", Hospitalizacion), ("REFERENCIA", Referencia)):
        if prestacion in (atencion.prestaciones or []) or prestacion == atencion.destino_atencion:
            if not await db.scalar(select(modelo.id).where(modelo.atencion_medica_id == atencion.id)):
                raise ValueError("Complete el documento de " + prestacion + " antes del cierre.")
    antes = expediente(atencion)
    contenido = expediente(atencion) | {"diagnosticos": [{"id": str(d.diagnostico_cie10_id), "tipo": d.tipo} for d in diagnosticos],
        "triaje": {k: getattr(triaje, k) for k in ("pulso", "temperatura", "presion_sistolica", "presion_diastolica", "frecuencia_cardiaca", "frecuencia_respiratoria", "peso", "talla", "saturacion_o2")},
        "cita_id": str(cita_id), "tenant_id": str(tenant_id)}
    paciente = await db.scalar(select(Patient).where(Patient.id == cita.patient_id, Patient.tenant_id == tenant_id))
    historia = await db.scalar(select(ClinicalRecord).where(ClinicalRecord.patient_id == cita.patient_id))
    contenido["paciente"] = {"id": str(paciente.id), "nombre": paciente.full_name, "documento": paciente.dni, "historia_clinica": historia.record_number if historia else None}
    atencion.cierre_evidencia = {"tipo": "CIERRE_INTERNO_SIN_CERTIFICADO_DIGITAL", "usuario_id": str(usuario.id), "usuario_nombre": usuario.name,
        "medico_id": str(medico.id), "medico_nombre": medico.nombre_completo, "colegiatura": medico.numero_cmp or medico.numero_colegiatura,
        "contenido": contenido, "sha256": hashlib.sha256(json.dumps(contenido, sort_keys=True, ensure_ascii=False).encode()).hexdigest()}
    atencion.estado = "firmado"
    atencion.firmado_at = datetime.utcnow()
    atencion.firmado_por_id = medico.id
    cita.estado = "atendida"
    await auditar_atencion(db, tenant_id, atencion, user, "atencion_cerrada", antes)
    await db.commit()
    return await get_atencion_medica(db, tenant_id, cita_id)


async def list_atenciones_medicas(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    fecha: date_type | None = None,
    especialidad_id: uuid.UUID | None = None,
    medico_id: uuid.UUID | None = None,
    paciente_dni: str | None = None,
    estado: str | None = None,
) -> list[dict]:
    query = (
        select(
            AtencionMedica,
            Cita,
            Patient,
            ProgramacionMedica,
            Empleado,
            Servicio,
            Especialidad,
        )
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
    if estado:
        query = query.where(AtencionMedica.estado == estado)
    if medico_id:
        query = query.where(ProgramacionMedica.medico_id == medico_id)
    if paciente_dni:
        query = query.where(Patient.dni.ilike(f"%{paciente_dni}%"))

    result = await db.execute(query)
    items = []
    for atencion, cita, paciente, prog, medico, servicio, especialidad in result.all():
        items.append(
            {
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
            }
        )
    return items


async def bandeja_electronica(db: AsyncSession, tenant_id: uuid.UUID, empleado_id: uuid.UUID | None) -> dict:
    """Bandeja de tareas pendientes del médico: atenciones sin firmar, citas de
    hoy aún no atendidas e interconsultas de Consulta Externa dirigidas a su
    especialidad. Sin tabla propia -- agrega datos ya existentes, igual que
    Auditoría/General/Fact-Config."""
    atenciones_pendientes = (
        await list_atenciones_medicas(db, tenant_id, medico_id=empleado_id, estado="borrador")
        if empleado_id else []
    )
    citas_hoy_pendientes = (
        await list_citas(db, tenant_id, estado="separada", fecha=date_type.today(), medico_id=empleado_id)
        if empleado_id else []
    )

    interconsultas_pendientes: list[dict] = []
    if empleado_id:
        especialidad_ids = (await db.scalars(select(EmpleadoEspecialidad.especialidad_id).where(
            EmpleadoEspecialidad.empleado_id == empleado_id))).all()
        if especialidad_ids:
            query = (
                select(Interconsulta, Patient, Especialidad)
                .join(Patient, Patient.id == Interconsulta.patient_id)
                .join(Especialidad, Especialidad.id == Interconsulta.especialidad_destino_id)
                .where(Interconsulta.tenant_id == tenant_id, Interconsulta.estado == "pendiente",
                       Interconsulta.especialidad_destino_id.in_(especialidad_ids))
                .order_by(Interconsulta.urgente.desc(), Interconsulta.created_at)
            )
            interconsultas_pendientes = [await _interconsulta_row_to_dict(db, row) for row in (await db.execute(query)).all()]

    return {
        "atenciones_pendientes_firma": atenciones_pendientes,
        "citas_hoy_pendientes": citas_hoy_pendientes,
        "interconsultas_pendientes": interconsultas_pendientes,
    }


from app.sigarh.config_farmacia.models import Medicamento


async def buscar_medicamentos(
    db: AsyncSession, tenant_id: uuid.UUID, q: str
) -> list[Medicamento]:
    result = await db.execute(
        select(Medicamento)
        .where(
            Medicamento.tenant_id == tenant_id,
            Medicamento.is_active == True,
            or_(
                Medicamento.codigo_interno.ilike(f"%{q}%"),
                Medicamento.nombre_comercial.ilike(f"%{q}%"),
                Medicamento.dci.ilike(f"%{q}%"),
            ),
        )
        .limit(20)
    )
    return result.scalars().all()


def _generar_numero_receta(secuencia: int) -> str:
    return f"RX-{datetime.utcnow().year}-{secuencia:06d}"


async def create_receta(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: "RecetaCreate", user=None
) -> dict:
    result = await db.execute(
        select(AtencionMedica).where(
            AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id
        ).with_for_update().execution_options(populate_existing=True)
    )
    atencion = result.scalar_one_or_none()
    if not atencion:
        raise ValueError("Debe registrar la atencion medica antes de generar la receta")
    if user:
        cita = await db.scalar(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id))
        await validar_autor_clinico(db, tenant_id, cita, user)
    if atencion.estado != "borrador":
        raise ValueError("La atención está cerrada; no puede generar documentos nuevos.")
    if atencion.destino_atencion != "FARMACIA" and "FARMACIA" not in (atencion.prestaciones or []):
        raise ValueError(
            "Seleccione la prestación Farmacia y guarde la atención antes de generar una receta"
        )

    existing = await db.execute(
        select(Receta).where(Receta.atencion_medica_id == atencion.id)
    )
    if existing.scalar_one_or_none():
        raise ValueError("Esta atencion ya tiene una receta generada")

    ids = [item.medicamento_id for item in data.items]
    validos = (await db.scalars(select(Medicamento.id).where(Medicamento.tenant_id == tenant_id, Medicamento.id.in_(ids), Medicamento.is_active == True))).all()
    if set(validos) != set(ids):
        raise ValueError("Seleccione medicamentos activos de este hospital.")
    if any(not (item.indicaciones or "").strip() and (not (item.dosis or "").strip() or not (item.frecuencia or "").strip()) for item in data.items):
        raise ValueError("Documente dosis y frecuencia o las indicaciones completas de cada medicamento.")
    count = await db.scalar(select(func.count(Receta.id)))
    receta = Receta(
        tenant_id=tenant_id,
        atencion_medica_id=atencion.id,
        numero_receta=_generar_numero_receta((count or 0) + 1),
    )
    db.add(receta)
    await db.flush()

    for item in data.items:
        db.add(RecetaItem(receta_id=receta.id, **item.model_dump()))

    await db.commit()
    return await get_receta(db, tenant_id, cita_id)


async def get_receta(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID
) -> dict | None:
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
        {
            "id": i.id,
            "medicamento_id": i.medicamento_id,
            "codigo_interno": m.codigo_interno,
            "nombre_comercial": m.nombre_comercial,
            "cantidad": i.cantidad,
            "dosis": i.dosis,
            "frecuencia": i.frecuencia,
            "duracion_dias": i.duracion_dias,
            "indicaciones": i.indicaciones,
        }
        for i, m in items_result.all()
    ]
    return {
        "id": receta.id,
        "atencion_medica_id": receta.atencion_medica_id,
        "numero_receta": receta.numero_receta,
        "estado": receta.estado,
        "items": items,
        "created_at": receta.created_at,
    }


from app.sigarh.infraestructura_hosp.models import Cama


async def get_camas_disponibles(
    db: AsyncSession, tenant_id: uuid.UUID, servicio_id: uuid.UUID | None = None
) -> list[Cama]:
    query = select(Cama).where(
        Cama.tenant_id == tenant_id, Cama.is_active == True, Cama.estado == "DISPONIBLE"
    )
    if servicio_id:
        query = query.where(Cama.servicio_id == servicio_id)
    result = await db.execute(query.order_by(Cama.codigo))
    return result.scalars().all()


def _generar_numero_hospitalizacion(secuencia: int) -> str:
    return f"HOSP-{datetime.utcnow().year}-{secuencia:06d}"


async def create_hospitalizacion(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    cita_id: uuid.UUID,
    data: "HospitalizacionCreate",
    user=None,
) -> dict:
    result = await db.execute(
        select(AtencionMedica).where(
            AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id
        ).with_for_update().execution_options(populate_existing=True)
    )
    atencion = result.scalar_one_or_none()
    if not atencion:
        raise ValueError(
            "Debe registrar la atencion medica antes de generar la hospitalizacion"
        )
    if user:
        cita = await db.scalar(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id))
        await validar_autor_clinico(db, tenant_id, cita, user)
    if atencion.estado != "borrador":
        raise ValueError("La atención está cerrada; no puede generar documentos nuevos.")
    if atencion.destino_atencion != "HOSPITALIZACION" and "HOSPITALIZACION" not in (atencion.prestaciones or []):
        raise ValueError("El destino de la atencion debe ser HOSPITALIZACION")

    if data.diagnostico_ingreso_id:
        valido = await db.scalar(select(DiagnosticoCIE10.id).where(DiagnosticoCIE10.id == data.diagnostico_ingreso_id, DiagnosticoCIE10.tenant_id == tenant_id, DiagnosticoCIE10.is_active == True))
        if not valido:
            raise ValueError("Seleccione un diagnóstico activo de este hospital.")

    if data.especialidad_ingreso_id and not await db.scalar(select(Especialidad.id).where(Especialidad.id == data.especialidad_ingreso_id, Especialidad.tenant_id == tenant_id, Especialidad.is_active == True)):
        raise ValueError("Seleccione una especialidad activa de este hospital.")
    existing = await db.execute(
        select(Hospitalizacion).where(Hospitalizacion.atencion_medica_id == atencion.id)
    )
    if existing.scalar_one_or_none():
        raise ValueError("Esta atencion ya tiene una hospitalizacion registrada")

    cama_result = await db.execute(
        select(Cama).where(Cama.id == data.cama_id, Cama.tenant_id == tenant_id).with_for_update().execution_options(populate_existing=True)
    )
    cama = cama_result.scalar_one_or_none()
    if not cama:
        raise ValueError("Cama no encontrada")
    if cama.estado != "DISPONIBLE":
        raise ValueError(
            f"La cama {cama.codigo} no esta disponible (estado actual: {cama.estado})"
        )

    from app.hospital.hospitalizacion.service import number as numero_hospitalizacion
    cita_de_atencion = await db.scalar(select(Cita).where(Cita.id == atencion.cita_id))
    hosp = Hospitalizacion(
        tenant_id=tenant_id,
        atencion_medica_id=atencion.id,
        patient_id=cita_de_atencion.patient_id if cita_de_atencion else None,
        cama_id=cama.id,
        especialidad_ingreso_id=data.especialidad_ingreso_id,
        diagnostico_ingreso_id=data.diagnostico_ingreso_id,
        numero_hospitalizacion=await numero_hospitalizacion(db, tenant_id, "HOSP"),
        registrado_por=(user.get("name") if user else None),
    )
    db.add(hosp)
    cama.estado = "OCUPADA"
    await db.commit()
    return await get_hospitalizacion(db, tenant_id, cita_id)


async def get_hospitalizacion(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID
) -> dict | None:
    result = await db.execute(
        select(Hospitalizacion, AtencionMedica, Cama, Especialidad, DiagnosticoCIE10)
        .join(AtencionMedica, AtencionMedica.id == Hospitalizacion.atencion_medica_id)
        .join(Cama, Cama.id == Hospitalizacion.cama_id)
        .outerjoin(
            Especialidad, Especialidad.id == Hospitalizacion.especialidad_ingreso_id
        )
        .outerjoin(
            DiagnosticoCIE10,
            DiagnosticoCIE10.id == Hospitalizacion.diagnostico_ingreso_id,
        )
        .where(
            Hospitalizacion.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id
        ).with_for_update().execution_options(populate_existing=True)
    )
    row = result.first()
    if not row:
        return None
    hosp, atencion, cama, especialidad, diagnostico = row
    return {
        "id": hosp.id,
        "atencion_medica_id": hosp.atencion_medica_id,
        "numero_hospitalizacion": hosp.numero_hospitalizacion,
        "cama_codigo": cama.codigo,
        "cama_nombre": cama.nombre,
        "especialidad_ingreso_nombre": especialidad.nombre if especialidad else None,
        "diagnostico_ingreso_codigo": diagnostico.codigo_cie10 if diagnostico else None,
        "diagnostico_ingreso_descripcion": diagnostico.descripcion
        if diagnostico
        else None,
        "fecha_ingreso": hosp.fecha_ingreso,
        "fecha_alta": hosp.fecha_alta,
        "estado": hosp.estado,
    }


async def dar_alta_hospitalizacion(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID
) -> dict | None:
    result = await db.execute(
        select(Hospitalizacion, AtencionMedica)
        .join(AtencionMedica, AtencionMedica.id == Hospitalizacion.atencion_medica_id)
        .where(
            Hospitalizacion.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id
        ).with_for_update().execution_options(populate_existing=True)
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


async def get_examenes_laboratorio(
    db: AsyncSession, tenant_id: uuid.UUID, q: str | None = None
) -> list[ExamenLaboratorio]:
    query = select(ExamenLaboratorio).where(
        ExamenLaboratorio.tenant_id == tenant_id, ExamenLaboratorio.is_active == True
    )
    if q:
        query = query.where(
            or_(
                ExamenLaboratorio.nombre.ilike(f"%{q}%"),
                ExamenLaboratorio.codigo.ilike(f"%{q}%"),
            )
        )
    result = await db.execute(query.order_by(ExamenLaboratorio.nombre).limit(50))
    return result.scalars().all()


def _generar_numero_orden(secuencia: int) -> str:
    return f"LAB-{datetime.utcnow().year}-{secuencia:06d}"


async def create_orden_laboratorio(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    cita_id: uuid.UUID,
    data: "OrdenLaboratorioCreate",
    user=None,
) -> dict:
    result = await db.execute(
        select(AtencionMedica)
        .where(AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id)
        .with_for_update()
    )
    atencion = result.scalar_one_or_none()
    if not atencion:
        raise ValueError("Debe registrar la atencion medica antes de generar la orden")
    if user:
        cita = await db.scalar(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id))
        await validar_autor_clinico(db, tenant_id, cita, user)
    if atencion.estado != "borrador":
        raise ValueError("La atención está cerrada; no puede generar documentos nuevos.")
    if atencion.destino_atencion != "LABORATORIO" and "LABORATORIO" not in (atencion.prestaciones or []):
        raise ValueError("Seleccione la prestación LABORATORIO y guarde la atención")

    existing = await db.execute(
        select(OrdenLaboratorio).where(
            OrdenLaboratorio.atencion_medica_id == atencion.id
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Esta atencion ya tiene una orden de laboratorio generada")

    if not data.examen_ids or len(set(data.examen_ids)) != len(data.examen_ids):
        raise ValueError("Seleccione exámenes sin duplicados")
    examenes_validos = (
        await db.scalars(
            select(ExamenLaboratorio.id).where(
                ExamenLaboratorio.tenant_id == tenant_id,
                ExamenLaboratorio.is_active.is_(True),
                ExamenLaboratorio.id.in_(data.examen_ids),
            )
        )
    ).all()
    if len(examenes_validos) != len(data.examen_ids):
        raise ValueError("Examen no disponible en este hospital")
    from app.hospital.laboratorio.service import number

    orden = OrdenLaboratorio(
        tenant_id=tenant_id,
        atencion_medica_id=atencion.id,
        numero_orden=await number(db, tenant_id, "OL"),
        indicacion_clinica=data.indicacion_clinica,
    )
    db.add(orden)
    await db.flush()

    for examen_id in data.examen_ids:
        db.add(OrdenLaboratorioItem(orden_id=orden.id, examen_id=examen_id))

    await db.commit()
    return await get_orden_laboratorio(db, tenant_id, cita_id)


async def get_orden_laboratorio(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID
) -> dict | None:
    result = await db.execute(
        select(OrdenLaboratorio, AtencionMedica)
        .join(AtencionMedica, AtencionMedica.id == OrdenLaboratorio.atencion_medica_id)
        .where(
            OrdenLaboratorio.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id
        ).with_for_update().execution_options(populate_existing=True)
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
        {
            "id": i.id,
            "examen_id": i.examen_id,
            "codigo": e.codigo,
            "nombre": e.nombre,
            "categoria": e.categoria,
            "tipo_muestra": e.tipo_muestra,
        }
        for i, e in items_result.all()
    ]
    return {
        "id": orden.id,
        "atencion_medica_id": orden.atencion_medica_id,
        "numero_orden": orden.numero_orden,
        "indicacion_clinica": orden.indicacion_clinica,
        "estado": orden.estado,
        "items": items,
        "created_at": orden.created_at,
    }


# --- Imagen ---
async def get_examenes_imagen(
    db: AsyncSession, tenant_id: uuid.UUID, q: str | None = None
) -> list[ExamenImagenologia]:
    query = select(ExamenImagenologia).where(
        ExamenImagenologia.tenant_id == tenant_id, ExamenImagenologia.is_active == True
    )
    if q:
        query = query.where(
            or_(
                ExamenImagenologia.nombre.ilike(f"%{q}%"),
                ExamenImagenologia.codigo.ilike(f"%{q}%"),
            )
        )
    result = await db.execute(query.order_by(ExamenImagenologia.nombre).limit(50))
    return result.scalars().all()


def _generar_numero_orden_imagen(secuencia: int) -> str:
    return f"IMG-{datetime.utcnow().year}-{secuencia:06d}"


async def create_orden_imagen(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    cita_id: uuid.UUID,
    data: "OrdenImagenCreate",
    user=None,
) -> dict:
    result = await db.execute(
        select(AtencionMedica).where(
            AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id
        ).with_for_update().execution_options(populate_existing=True)
    )
    atencion = result.scalar_one_or_none()
    if not atencion:
        raise ValueError("Debe registrar la atencion medica antes de generar la orden")
    if user:
        cita = await db.scalar(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id))
        await validar_autor_clinico(db, tenant_id, cita, user)
    if atencion.estado != "borrador":
        raise ValueError("La atención está cerrada; no puede generar documentos nuevos.")
    if atencion.destino_atencion != "IMAGEN" and "IMAGEN" not in (atencion.prestaciones or []):
        raise ValueError("Seleccione la prestación IMAGEN y guarde la atención")

    existing = await db.execute(
        select(OrdenImagen).where(OrdenImagen.atencion_medica_id == atencion.id)
    )
    if existing.scalar_one_or_none():
        raise ValueError("Esta atencion ya tiene una orden de imagen generada")

    if not data.examen_ids or len(set(data.examen_ids)) != len(data.examen_ids):
        raise ValueError("Seleccione estudios de imagen sin duplicados.")
    validos = (await db.scalars(select(ExamenImagenologia.id).where(
        ExamenImagenologia.tenant_id == tenant_id,
        ExamenImagenologia.is_active.is_(True),
        ExamenImagenologia.id.in_(data.examen_ids),
    ))).all()
    if len(validos) != len(data.examen_ids):
        raise ValueError("Estudio de imagen no disponible en este hospital.")
    from app.hospital.imagenes.service import number
    orden = OrdenImagen(
        tenant_id=tenant_id,
        atencion_medica_id=atencion.id,
        numero_orden=await number(db, tenant_id, "OI"),
        indicacion_clinica=data.indicacion_clinica,
    )
    db.add(orden)
    await db.flush()
    for examen_id in data.examen_ids:
        db.add(OrdenImagenItem(orden_id=orden.id, examen_id=examen_id))
    await db.commit()
    return await get_orden_imagen(db, tenant_id, cita_id)


async def get_orden_imagen(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID
) -> dict | None:
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
        {
            "id": i.id,
            "examen_id": i.examen_id,
            "codigo": e.codigo,
            "nombre": e.nombre,
            "modalidad": e.modalidad,
            "parte_cuerpo": e.parte_cuerpo,
        }
        for i, e in items_result.all()
    ]
    return {
        "id": orden.id,
        "atencion_medica_id": orden.atencion_medica_id,
        "numero_orden": orden.numero_orden,
        "indicacion_clinica": orden.indicacion_clinica,
        "estado": orden.estado,
        "items": items,
        "created_at": orden.created_at,
    }


# --- Interconsulta ---
async def create_interconsulta(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    cita_id: uuid.UUID,
    data: "InterconsultaCreate",
    user=None,
) -> dict:
    result = await db.execute(
        select(AtencionMedica).where(
            AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id
        ).with_for_update().execution_options(populate_existing=True)
    )
    atencion = result.scalar_one_or_none()
    if not atencion:
        raise ValueError(
            "Debe registrar la atencion medica antes de generar la interconsulta"
        )
    cita = await db.scalar(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id))
    if user:
        await validar_autor_clinico(db, tenant_id, cita, user)
    if atencion.estado != "borrador":
        raise ValueError("La atención está cerrada; no puede generar documentos nuevos.")
    if atencion.destino_atencion != "INTERCONSULTA" and "INTERCONSULTA" not in (atencion.prestaciones or []):
        raise ValueError("Seleccione la prestación INTERCONSULTA y guarde la atención")

    if data.diagnostico_id:
        valido = await db.scalar(select(DiagnosticoCIE10.id).where(DiagnosticoCIE10.id == data.diagnostico_id, DiagnosticoCIE10.tenant_id == tenant_id, DiagnosticoCIE10.is_active == True))
        if not valido:
            raise ValueError("Seleccione un diagnóstico activo de este hospital.")

    if not data.motivo.strip():
        raise ValueError("Documente el motivo de la interconsulta.")
    if not await db.scalar(select(Especialidad.id).where(Especialidad.id == data.especialidad_destino_id, Especialidad.tenant_id == tenant_id, Especialidad.is_active == True)):
        raise ValueError("Seleccione una especialidad activa de este hospital.")
    existing = await db.execute(
        select(Interconsulta).where(Interconsulta.atencion_medica_id == atencion.id)
    )
    if existing.scalar_one_or_none():
        raise ValueError("Esta atencion ya tiene una interconsulta generada")

    interc = Interconsulta(
        tenant_id=tenant_id, atencion_medica_id=atencion.id, patient_id=cita.patient_id if cita else None,
        **data.model_dump()
    )
    db.add(interc)
    await db.commit()
    return await get_interconsulta(db, tenant_id, cita_id)


async def get_interconsulta(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID
) -> dict | None:
    result = await db.execute(
        select(Interconsulta, Patient, Especialidad)
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


async def list_interconsultas_pendientes(
    db: AsyncSession, tenant_id: uuid.UUID, especialidad_id: uuid.UUID | None = None
) -> list[dict]:
    # La interconsulta puede originarse en una Atencion Medica (Consulta Externa),
    # una Hospitalizacion o una Atencion de Emergencia -- en los 3 casos el
    # paciente ya queda resuelto en Interconsulta.patient_id desde su creacion
    # (igual que en Laboratorio/Imagenologia), asi que no hace falta reconstruirlo
    # via outerjoin/coalesce por cada origen.
    query = (
        select(Interconsulta, Patient, Especialidad)
        .join(Patient, Patient.id == Interconsulta.patient_id)
        .join(Especialidad, Especialidad.id == Interconsulta.especialidad_destino_id)
        .where(
            Interconsulta.tenant_id == tenant_id, Interconsulta.estado == "pendiente"
        )
        .order_by(Interconsulta.urgente.desc(), Interconsulta.created_at)
    )
    if especialidad_id:
        query = query.where(Interconsulta.especialidad_destino_id == especialidad_id)
    result = await db.execute(query)
    return [await _interconsulta_row_to_dict(db, row) for row in result.all()]


async def _interconsulta_row_to_dict(db: AsyncSession, row) -> dict:
    interc, paciente, especialidad = row
    diagnostico_codigo = diagnostico_desc = None
    if interc.diagnostico_id:
        dx_result = await db.execute(
            select(DiagnosticoCIE10).where(DiagnosticoCIE10.id == interc.diagnostico_id)
        )
        dx = dx_result.scalar_one_or_none()
        if dx:
            diagnostico_codigo, diagnostico_desc = dx.codigo_cie10, dx.descripcion
    return {
        "id": interc.id,
        "atencion_medica_id": interc.atencion_medica_id,
        "hospitalizacion_id": interc.hospitalizacion_id,
        "atencion_emergencia_id": interc.atencion_emergencia_id,
        "origen": "HOSPITALIZACION" if interc.hospitalizacion_id else ("EMERGENCIA" if interc.atencion_emergencia_id else "CONSULTA_EXTERNA"),
        "paciente_nombre": paciente.full_name,
        "paciente_dni": paciente.dni,
        "especialidad_destino_id": interc.especialidad_destino_id,
        "especialidad_destino_nombre": especialidad.nombre,
        "diagnostico_codigo": diagnostico_codigo,
        "diagnostico_descripcion": diagnostico_desc,
        "motivo": interc.motivo,
        "urgente": interc.urgente,
        "estado": interc.estado,
        "cita_generada_id": interc.cita_generada_id,
        "created_at": interc.created_at,
    }


async def programar_interconsulta(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    interconsulta_id: uuid.UUID,
    programacion_medica_id: uuid.UUID,
    hora_inicio: str,
    hora_fin: str,
) -> dict:
    result = await db.execute(
        select(Interconsulta).where(
            Interconsulta.tenant_id == tenant_id, Interconsulta.id == interconsulta_id
        )
    )
    interc = result.scalar_one_or_none()
    if not interc:
        raise ValueError("Interconsulta no encontrada")
    if interc.estado != "pendiente":
        raise ValueError("Esta interconsulta ya fue programada")

    # El paciente ya queda resuelto en Interconsulta.patient_id desde su creacion,
    # cualquiera sea el origen (Consulta Externa, Hospitalizacion o Emergencia).
    patient_id = interc.patient_id
    if not patient_id:
        raise ValueError("No se pudo determinar el paciente de esta interconsulta")

    nueva_cita = await create_cita(
        db,
        tenant_id,
        CitaCreate(
            programacion_medica_id=programacion_medica_id,
            patient_id=patient_id,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            tipo_consulta="Interconsulta",
            observacion=interc.motivo,
        ),
    )

    interc.estado = "programada"
    interc.cita_generada_id = nueva_cita["id"]
    await db.commit()
    return nueva_cita


def _generar_numero_referencia(secuencia: int) -> str:
    return f"REF-{datetime.utcnow().year}-{secuencia:06d}"


async def get_tenants_disponibles(
    db: AsyncSession, tenant_id_actual: uuid.UUID
) -> list[Tenant]:
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as central:
        result = await central.execute(
            select(Tenant).where(Tenant.id != tenant_id_actual, Tenant.is_active.is_(True)).order_by(Tenant.name)
        )
        return result.scalars().all()


async def create_referencia(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID, data: "ReferenciaCreate", user=None
) -> dict:
    result = await db.execute(
        select(AtencionMedica).where(
            AtencionMedica.tenant_id == tenant_id, AtencionMedica.cita_id == cita_id
        ).with_for_update().execution_options(populate_existing=True)
    )
    atencion = result.scalar_one_or_none()
    if not atencion:
        raise ValueError(
            "Debe registrar la atencion medica antes de generar la referencia"
        )
    if user:
        cita = await db.scalar(select(Cita).where(Cita.tenant_id == tenant_id, Cita.id == cita_id))
        await validar_autor_clinico(db, tenant_id, cita, user)
    if atencion.estado != "borrador":
        raise ValueError("La atención está cerrada; no puede generar documentos nuevos.")
    if atencion.destino_atencion != "REFERENCIA" and "REFERENCIA" not in (atencion.prestaciones or []):
        raise ValueError("El destino de la atencion debe ser REFERENCIA")

    if data.diagnostico_id:
        valido = await db.scalar(select(DiagnosticoCIE10.id).where(DiagnosticoCIE10.id == data.diagnostico_id, DiagnosticoCIE10.tenant_id == tenant_id, DiagnosticoCIE10.is_active == True))
        if not valido:
            raise ValueError("Seleccione un diagnóstico activo de este hospital.")

    existing = await db.execute(
        select(Referencia).where(Referencia.atencion_medica_id == atencion.id)
    )
    if existing.scalar_one_or_none():
        raise ValueError("Esta atencion ya tiene una referencia generada")

    from app.hospital.referencias.service import number as numero_referencia
    ref = Referencia(
        tenant_id=tenant_id,
        atencion_medica_id=atencion.id,
        patient_id=cita.patient_id if user else (await db.scalar(select(Cita.patient_id).where(Cita.id == cita_id))),
        registrado_por=(user.get("name") if user else None),
        numero_referencia=await numero_referencia(db, tenant_id, "REF"),
        **data.model_dump(),
    )
    db.add(ref)
    await db.commit()
    return await get_referencia(db, tenant_id, cita_id)


async def get_referencia(
    db: AsyncSession, tenant_id: uuid.UUID, cita_id: uuid.UUID
) -> dict | None:
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
        from app.core.tenant_db import get_tenant_by_id
        t = await get_tenant_by_id(ref.tenant_destino_id)
        tenant_destino_nombre = t.name if t else None

    diagnostico_codigo = diagnostico_desc = None
    if ref.diagnostico_id:
        dx_result = await db.execute(
            select(DiagnosticoCIE10).where(DiagnosticoCIE10.id == ref.diagnostico_id)
        )
        dx = dx_result.scalar_one_or_none()
        if dx:
            diagnostico_codigo, diagnostico_desc = dx.codigo_cie10, dx.descripcion

    return {
        "id": ref.id,
        "atencion_medica_id": ref.atencion_medica_id,
        "numero_referencia": ref.numero_referencia,
        "codigo_renipress_destino": ref.codigo_renipress_destino,
        "nombre_ipress_destino": ref.nombre_ipress_destino,
        "tenant_destino_id": ref.tenant_destino_id,
        "tenant_destino_nombre": tenant_destino_nombre,
        "especialidad_destino": ref.especialidad_destino,
        "diagnostico_codigo": diagnostico_codigo,
        "diagnostico_descripcion": diagnostico_desc,
        "motivo": ref.motivo,
        "estado": ref.estado,
        "created_at": ref.created_at,
    }


async def _validar_vigencia_medico(db, tenant_id, medico_id, fecha):
    from fastapi import HTTPException
    from app.sigarh.rrhh.vigencia_laboral import impedimento_programacion
    medico = await db.scalar(select(Empleado).where(Empleado.id == medico_id, Empleado.tenant_id == tenant_id))
    if fecha is None:
        raise HTTPException(409, "La programacion requiere una fecha.")
    error = impedimento_programacion(medico, fecha)
    if error:
        raise HTTPException(409, error)
