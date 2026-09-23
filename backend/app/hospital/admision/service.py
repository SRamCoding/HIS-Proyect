import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, cast, String
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.hospital.admision.models import Patient, ClinicalRecord, ClinicalRecordMovement, ListaEspera, Anuncio, Mensaje
from app.hospital.admision.schemas import PatientCreate, PatientUpdate, ListaEsperaCreate, ListaEsperaUpdate, AnuncioCreate, AnuncioUpdate, MensajeCreate
from app.shared.ubigeo.models import UbigeoDepartamento, UbigeoProvincia, UbigeoDistrito
from app.shared.dni import lookup_dni_externo  # noqa: F401  (re-exportado: usado por el router)
from app.hospital.consulta_externa.models import Hospitalizacion, Cita
from app.hospital.emergencia.models import AtencionEmergencia, AdmisionEmergencia
from app.sigarh.mantenimiento.models import Servicio
from app.sigarh.rrhh.models import Especialidad
from app.auth.models import User
from app.hospital.admision.numeracion import numero_historia, numero_dni


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


def columns(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


async def _persistir_identidad(db, *, commit=False):
    try:
        if commit:
            await db.commit()
        else:
            await db.flush()
    except IntegrityError as exc:
        await db.rollback()
        if getattr(exc.orig, "sqlstate", None) == "23505":
            raise HTTPException(409, "El documento o número de HC ya está registrado") from exc
        raise


async def create_patient(db: AsyncSession, tenant_id: uuid.UUID, data: PatientCreate) -> Patient:
    patient = Patient(
        tenant_id=tenant_id,
        document_type=data.document_type,
        dni=data.dni,
        is_nn=data.is_nn,
        first_name=data.first_name,
        second_name=data.second_name,
        last_name_paterno=data.last_name_paterno,
        last_name_materno=data.last_name_materno,
        birth_date=data.birth_date,
        gender=data.gender,
        marital_status=data.marital_status,
        education_level=data.education_level,
        occupation=data.occupation,
        ethnicity=data.ethnicity,
        language=data.language,
        phone=data.phone,
        phone_is_whatsapp=data.phone_is_whatsapp,
        email=data.email,
        address=data.address,
        department_id=data.department_id,
        province_id=data.province_id,
        district_id=data.district_id,
        populated_center=data.populated_center,
        country=data.country,
        birth_same_as_address=data.birth_same_as_address,
        birth_department_id=data.department_id if data.birth_same_as_address else data.birth_department_id,
        birth_province_id=data.province_id if data.birth_same_as_address else data.birth_province_id,
        birth_district_id=data.district_id if data.birth_same_as_address else data.birth_district_id,
        birth_populated_center=data.populated_center if data.birth_same_as_address else data.birth_populated_center,
        birth_country=data.country if data.birth_same_as_address else data.birth_country,
        insurance_type=data.insurance_type,
        insurance_number=data.insurance_number,
    )
    db.add(patient)
    await _persistir_identidad(db)

    record = ClinicalRecord(
        patient_id=patient.id,
        record_number=numero_historia(patient.document_type, patient.dni, patient.is_nn),
        location="admision",
    )
    db.add(record)
    await _persistir_identidad(db, commit=True)
    return await get_patient_by_id(db, tenant_id, patient.id)


async def get_patient_by_dni(db: AsyncSession, tenant_id: uuid.UUID, dni: str) -> Patient | None:
    result = await db.execute(
        select(Patient)
        .options(selectinload(Patient.clinical_record))
        .where(Patient.tenant_id == tenant_id, Patient.dni == dni)
    )
    return result.scalar_one_or_none()


async def get_patient_by_id(db: AsyncSession, tenant_id: uuid.UUID, patient_id: uuid.UUID) -> Patient | None:
    result = await db.execute(
        select(Patient)
        .options(selectinload(Patient.clinical_record))
        .where(Patient.tenant_id == tenant_id, Patient.id == patient_id)
    )
    return result.scalar_one_or_none()


async def search_patients(db: AsyncSession, tenant_id: uuid.UUID, query: str | None = None,
                          page: int = 1, page_size: int = 20) -> tuple[list[Patient], int]:
    """Sin `query`, lista todos los pacientes del hospital (paginado) -- antes
    la pantalla de Pacientes exigia escribir algo para ver cualquier cosa.
    Con `query`, también busca por número de historia clínica además de
    DNI/nombres/apellidos, que es lo que el buscador ya prometía en su
    placeholder sin cumplirlo."""
    stmt = select(Patient).options(selectinload(Patient.clinical_record)).where(Patient.tenant_id == tenant_id)
    if query:
        stmt = stmt.outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id).where(
            or_(
                Patient.dni.ilike(f"%{query}%"),
                Patient.first_name.ilike(f"%{query}%"),
                Patient.last_name_paterno.ilike(f"%{query}%"),
                Patient.last_name_materno.ilike(f"%{query}%"),
                ClinicalRecord.record_number.ilike(f"%{query}%"),
                cast(ClinicalRecord.previous_record_numbers, String).icontains(query, autoescape=True),
            )
        )
    total = await db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    result = await db.execute(
        stmt.order_by(Patient.last_name_paterno, Patient.last_name_materno, Patient.first_name)
        .offset((page - 1) * page_size).limit(page_size)
    )
    return result.scalars().all(), total


async def update_patient(db: AsyncSession, tenant_id: uuid.UUID, patient_id: uuid.UUID, data: PatientUpdate) -> Patient | None:
    # Serializar correcciones de identidad para no perder números anteriores.
    await db.execute(select(Patient.id).where(Patient.id == patient_id,
        Patient.tenant_id == tenant_id).with_for_update())
    patient = await get_patient_by_id(db, tenant_id, patient_id)
    if not patient:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    if patient.clinical_record:
        record = patient.clinical_record
        new_number = numero_dni(patient)
        if not new_number and record.record_number.isdigit():
            new_number = numero_historia(None, None)
        if new_number and new_number != record.record_number:
            with db.no_autoflush:
                existing = await db.scalar(select(ClinicalRecord.id).where(
                    ClinicalRecord.record_number == new_number, ClinicalRecord.id != record.id))
            if existing:
                raise HTTPException(409, "El número de HC ya pertenece a otro paciente")
            record.previous_record_numbers = list(dict.fromkeys([
                *(record.previous_record_numbers or []), record.record_number]))
            record.record_number = new_number
    await _persistir_identidad(db, commit=True)
    await db.refresh(patient)
    return await get_patient_by_id(db, tenant_id, patient_id)


async def move_clinical_record(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    clinical_record_id: uuid.UUID,
    to_location: str,
    moved_by: str | None = None,
    notes: str | None = None,
) -> ClinicalRecordMovement:
    result = await db.execute(
        select(ClinicalRecord)
        .join(Patient, Patient.id == ClinicalRecord.patient_id)
        .where(ClinicalRecord.id == clinical_record_id, Patient.tenant_id == tenant_id)
        .with_for_update(of=ClinicalRecord)
        .execution_options(populate_existing=True)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise LookupError("Historia clinica no encontrada")

    to_location = to_location.strip()
    if not to_location or len(to_location) > 50:
        raise ValueError("La ubicación debe contener entre 1 y 50 caracteres")
    if record.location.casefold() == to_location.casefold():
        raise ValueError("La historia clínica ya se encuentra en esa ubicación")

    movement = ClinicalRecordMovement(
        clinical_record_id=clinical_record_id,
        from_location=record.location,
        to_location=to_location,
        moved_by=moved_by,
        notes=notes,
    )
    record.location = to_location
    db.add(movement)
    await db.commit()
    return movement


# --- Ubigeo (catalogo compartido, sin filtro de tenant) ---
async def get_departamentos(db: AsyncSession) -> list[UbigeoDepartamento]:
    result = await db.execute(select(UbigeoDepartamento).order_by(UbigeoDepartamento.nombre))
    return result.scalars().all()


async def get_provincias(db: AsyncSession, departamento_id: str) -> list[UbigeoProvincia]:
    result = await db.execute(
        select(UbigeoProvincia)
        .where(UbigeoProvincia.departamento_id == departamento_id)
        .order_by(UbigeoProvincia.nombre)
    )
    return result.scalars().all()


async def get_distritos(db: AsyncSession, provincia_id: str) -> list[UbigeoDistrito]:
    result = await db.execute(
        select(UbigeoDistrito)
        .where(UbigeoDistrito.provincia_id == provincia_id)
        .order_by(UbigeoDistrito.nombre)
    )
    return result.scalars().all()


# --- Altas (vista de solo lectura sobre datos ya existentes) ---
async def list_altas(db: AsyncSession, tid: uuid.UUID, fecha_desde=None, fecha_hasta=None, q: str | None = None) -> list[dict]:
    items: list[dict] = []

    q_hosp = (
        select(Hospitalizacion, Patient)
        .join(Patient, Patient.id == Hospitalizacion.patient_id)
        .where(Hospitalizacion.tenant_id == tid, Hospitalizacion.estado == "alta")
    )
    if fecha_desde:
        q_hosp = q_hosp.where(Hospitalizacion.fecha_alta >= fecha_desde)
    if fecha_hasta:
        q_hosp = q_hosp.where(Hospitalizacion.fecha_alta <= fecha_hasta)
    for h, p in (await db.execute(q_hosp)).all():
        items.append({
            "origen": "hospitalizacion", "id": h.id, "patient_id": p.id,
            "paciente_nombre": p.full_name, "paciente_dni": p.dni,
            "numero": h.numero_hospitalizacion, "fecha_alta": h.fecha_alta,
            "resumen": h.resumen_alta, "servicio_o_especialidad": None,
        })

    q_emerg = (
        select(AtencionEmergencia, AdmisionEmergencia, Patient)
        .join(AdmisionEmergencia, AdmisionEmergencia.id == AtencionEmergencia.admision_id)
        .join(Patient, Patient.id == AdmisionEmergencia.patient_id)
        .where(AdmisionEmergencia.tenant_id == tid, AtencionEmergencia.destino_atencion == "ALTA",
               AtencionEmergencia.estado == "firmado")
    )
    if fecha_desde:
        q_emerg = q_emerg.where(AtencionEmergencia.firmado_at >= fecha_desde)
    if fecha_hasta:
        q_emerg = q_emerg.where(AtencionEmergencia.firmado_at <= fecha_hasta)
    for a, ad, p in (await db.execute(q_emerg)).all():
        items.append({
            "origen": "emergencia", "id": a.id, "patient_id": p.id,
            "paciente_nombre": p.full_name, "paciente_dni": p.dni,
            "numero": ad.numero_cuenta, "fecha_alta": a.firmado_at,
            "resumen": a.plan_tratamiento, "servicio_o_especialidad": ad.servicio_emergencia,
        })

    if q:
        ql = q.casefold()
        items = [i for i in items if ql in i["paciente_nombre"].casefold() or (i["paciente_dni"] or "").casefold().find(ql) >= 0]
    items.sort(key=lambda i: i["fecha_alta"] or datetime.min, reverse=True)
    return items


# --- Lista de Espera ---
async def _lista_espera_out(db, row) -> dict:
    le, patient, servicio, especialidad = row
    return {
        "id": le.id, "patient_id": le.patient_id,
        "paciente_nombre": patient.full_name, "paciente_dni": patient.dni,
        "servicio_id": le.servicio_id, "servicio_nombre": servicio.nombre if servicio else None,
        "especialidad_id": le.especialidad_id, "especialidad_nombre": especialidad.nombre if especialidad else None,
        "cita_id": le.cita_id, "motivo": le.motivo, "prioridad": le.prioridad, "estado": le.estado,
        "registrado_por": le.registrado_por, "created_at": le.created_at, "atendido_at": le.atendido_at,
    }


def _lista_espera_query(tid):
    return (
        select(ListaEspera, Patient, Servicio, Especialidad)
        .join(Patient, Patient.id == ListaEspera.patient_id)
        .outerjoin(Servicio, Servicio.id == ListaEspera.servicio_id)
        .outerjoin(Especialidad, Especialidad.id == ListaEspera.especialidad_id)
        .where(ListaEspera.tenant_id == tid)
    )


async def list_lista_espera(db: AsyncSession, tid: uuid.UUID, estado: str | None = None,
                             servicio_id: uuid.UUID | None = None, especialidad_id: uuid.UUID | None = None,
                             q: str | None = None) -> list[dict]:
    query = _lista_espera_query(tid)
    query = query.where(ListaEspera.estado == estado) if estado else query.where(ListaEspera.estado == "pendiente")
    if servicio_id:
        query = query.where(ListaEspera.servicio_id == servicio_id)
    if especialidad_id:
        query = query.where(ListaEspera.especialidad_id == especialidad_id)
    if q:
        query = query.where(or_(Patient.first_name.icontains(q, autoescape=True),
            Patient.last_name_paterno.icontains(q, autoescape=True), Patient.dni.icontains(q, autoescape=True)))
    query = query.order_by((ListaEspera.prioridad == "urgente").desc(), ListaEspera.created_at)
    rows = (await db.execute(query)).all()
    return [await _lista_espera_out(db, r) for r in rows]


async def create_lista_espera(db: AsyncSession, tid: uuid.UUID, data: ListaEsperaCreate, user: dict) -> dict:
    patient = (await db.execute(select(Patient).where(Patient.id == data.patient_id, Patient.tenant_id == tid))).scalar_one_or_none()
    if not patient:
        raise HTTPException(404, detail="Paciente no encontrado")
    le = ListaEspera(tenant_id=tid, patient_id=data.patient_id, servicio_id=data.servicio_id,
        especialidad_id=data.especialidad_id, motivo=data.motivo, prioridad=data.prioridad,
        registrado_por=actor(user))
    db.add(le)
    await db.flush()
    await db.commit()
    row = (await db.execute(_lista_espera_query(tid).where(ListaEspera.id == le.id))).first()
    return await _lista_espera_out(db, row)


async def update_lista_espera(db: AsyncSession, tid: uuid.UUID, item_id: uuid.UUID, data: ListaEsperaUpdate, user: dict) -> dict:
    le = (await db.execute(select(ListaEspera).where(ListaEspera.id == item_id, ListaEspera.tenant_id == tid)
        .with_for_update())).scalar_one_or_none()
    if not le:
        raise HTTPException(404, detail="Registro de lista de espera no encontrado")
    if le.estado != "pendiente":
        raise HTTPException(409, detail="Solo se puede editar un registro pendiente")
    columns(le)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(le, field, value)
    await db.flush()
    await db.commit()
    row = (await db.execute(_lista_espera_query(tid).where(ListaEspera.id == le.id))).first()
    return await _lista_espera_out(db, row)


async def atender_lista_espera(db: AsyncSession, tid: uuid.UUID, item_id: uuid.UUID, cita_id: uuid.UUID | None, user: dict) -> dict:
    le = (await db.execute(select(ListaEspera).where(ListaEspera.id == item_id, ListaEspera.tenant_id == tid)
        .with_for_update())).scalar_one_or_none()
    if not le:
        raise HTTPException(404, detail="Registro de lista de espera no encontrado")
    if le.estado != "pendiente":
        raise HTTPException(409, detail="Este registro ya fue resuelto")
    if cita_id:
        cita = (await db.execute(select(Cita).where(Cita.id == cita_id, Cita.tenant_id == tid,
            Cita.patient_id == le.patient_id))).scalar_one_or_none()
        if not cita:
            raise HTTPException(404, detail="La cita indicada no existe o no pertenece a este paciente")
        le.cita_id = cita_id
    columns(le)
    le.estado = "atendido"
    le.atendido_at = datetime.utcnow()
    await db.flush()
    await db.commit()
    row = (await db.execute(_lista_espera_query(tid).where(ListaEspera.id == le.id))).first()
    return await _lista_espera_out(db, row)


async def cancelar_lista_espera(db: AsyncSession, tid: uuid.UUID, item_id: uuid.UUID, user: dict) -> dict:
    le = (await db.execute(select(ListaEspera).where(ListaEspera.id == item_id, ListaEspera.tenant_id == tid)
        .with_for_update())).scalar_one_or_none()
    if not le:
        raise HTTPException(404, detail="Registro de lista de espera no encontrado")
    if le.estado != "pendiente":
        raise HTTPException(409, detail="Este registro ya fue resuelto")
    columns(le)
    le.estado = "cancelado"
    await db.flush()
    await db.commit()
    row = (await db.execute(_lista_espera_query(tid).where(ListaEspera.id == le.id))).first()
    return await _lista_espera_out(db, row)


# --- Anuncios ---
async def list_anuncios(db: AsyncSession, tid: uuid.UUID, incluir_inactivos: bool = False) -> list[Anuncio]:
    query = select(Anuncio).where(Anuncio.tenant_id == tid)
    if not incluir_inactivos:
        query = query.where(Anuncio.is_active.is_(True))
    result = await db.execute(query.order_by(Anuncio.created_at.desc()))
    return result.scalars().all()


async def create_anuncio(db: AsyncSession, tid: uuid.UUID, data: AnuncioCreate, user: dict) -> Anuncio:
    anuncio = Anuncio(tenant_id=tid, titulo=data.titulo, contenido=data.contenido, publicado_por=actor(user))
    db.add(anuncio)
    await db.flush()
    await db.commit()
    await db.refresh(anuncio)
    return anuncio


async def update_anuncio(db: AsyncSession, tid: uuid.UUID, anuncio_id: uuid.UUID, data: AnuncioUpdate, user: dict) -> Anuncio:
    anuncio = (await db.execute(select(Anuncio).where(Anuncio.id == anuncio_id, Anuncio.tenant_id == tid)
        .with_for_update())).scalar_one_or_none()
    if not anuncio:
        raise HTTPException(404, detail="Anuncio no encontrado")
    columns(anuncio)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(anuncio, field, value)
    await db.flush()
    await db.commit()
    await db.refresh(anuncio)
    return anuncio


# --- Mensajito ---
async def _mensaje_out(msg: Mensaje, remitente: User | None, paciente: Patient | None) -> dict:
    return {
        "id": msg.id, "remitente_user_id": msg.remitente_user_id,
        "remitente_nombre": msg.remitente_nombre or (remitente.name if remitente else None),
        "destinatario_user_id": msg.destinatario_user_id, "destinatario_role": msg.destinatario_role,
        "patient_id": msg.patient_id, "paciente_nombre": paciente.full_name if paciente else None,
        "contenido": msg.contenido, "leido": msg.leido, "leido_at": msg.leido_at, "created_at": msg.created_at,
    }


async def list_inbox(db: AsyncSession, tid: uuid.UUID, user: dict) -> list[dict]:
    user_id = uuid.UUID(user["sub"])
    role = user.get("role")
    query = (
        select(Mensaje, User, Patient)
        .join(User, User.id == Mensaje.remitente_user_id)
        .outerjoin(Patient, Patient.id == Mensaje.patient_id)
        .where(Mensaje.tenant_id == tid, or_(Mensaje.destinatario_user_id == user_id, Mensaje.destinatario_role == role))
        .order_by(Mensaje.created_at.desc())
        .limit(200)
    )
    rows = (await db.execute(query)).all()
    return [await _mensaje_out(m, u, p) for m, u, p in rows]


async def list_enviados(db: AsyncSession, tid: uuid.UUID, user: dict) -> list[dict]:
    user_id = uuid.UUID(user["sub"])
    query = (
        select(Mensaje, User, Patient)
        .join(User, User.id == Mensaje.remitente_user_id)
        .outerjoin(Patient, Patient.id == Mensaje.patient_id)
        .where(Mensaje.tenant_id == tid, Mensaje.remitente_user_id == user_id)
        .order_by(Mensaje.created_at.desc())
        .limit(200)
    )
    rows = (await db.execute(query)).all()
    return [await _mensaje_out(m, u, p) for m, u, p in rows]


async def enviar_mensaje(db: AsyncSession, tid: uuid.UUID, data: MensajeCreate, user: dict) -> dict:
    if data.destinatario_user_id:
        destinatario = (await db.execute(select(User).where(User.id == data.destinatario_user_id,
            User.panel == "app"))).scalar_one_or_none()
        if not destinatario:
            raise HTTPException(404, detail="Destinatario no encontrado")
    if data.patient_id:
        paciente = (await db.execute(select(Patient).where(Patient.id == data.patient_id, Patient.tenant_id == tid))).scalar_one_or_none()
        if not paciente:
            raise HTTPException(404, detail="Paciente no encontrado")
    msg = Mensaje(tenant_id=tid, remitente_user_id=uuid.UUID(user["sub"]), remitente_nombre=user.get("name"),
        destinatario_user_id=data.destinatario_user_id, destinatario_role=data.destinatario_role,
        patient_id=data.patient_id, contenido=data.contenido)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    remitente = (await db.execute(select(User).where(User.id == msg.remitente_user_id))).scalar_one_or_none()
    paciente = (await db.execute(select(Patient).where(Patient.id == msg.patient_id))).scalar_one_or_none() if msg.patient_id else None
    return await _mensaje_out(msg, remitente, paciente)


async def marcar_leido(db: AsyncSession, tid: uuid.UUID, mensaje_id: uuid.UUID, user: dict) -> None:
    user_id = uuid.UUID(user["sub"])
    msg = (await db.execute(select(Mensaje).where(Mensaje.id == mensaje_id, Mensaje.tenant_id == tid)
        .with_for_update())).scalar_one_or_none()
    if not msg:
        raise HTTPException(404, detail="Mensaje no encontrado")
    if msg.destinatario_user_id != user_id and msg.destinatario_role != user.get("role"):
        raise HTTPException(403, detail="Este mensaje no está dirigido a ti")
    if not msg.leido:
        msg.leido = True
        msg.leido_at = datetime.utcnow()
        await db.commit()


async def list_destinatarios(db: AsyncSession, tid: uuid.UUID) -> list[User]:
    # Mismo motivo que en Seguridad: User.tenant_id no se llena para panel='app',
    # el aislamiento real es por base de datos fisica del hospital.
    result = await db.execute(select(User).where(User.panel == "app", User.is_active.is_(True)).order_by(User.name))
    return result.scalars().all()
