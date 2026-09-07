import uuid
import httpx
from app.core.config import settings
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.hospital.gestion_pacientes.models import Patient, ClinicalRecord, ClinicalRecordMovement
from app.hospital.gestion_pacientes.schemas import PatientCreate, PatientUpdate
from app.shared.ubigeo.models import UbigeoDepartamento, UbigeoProvincia, UbigeoDistrito


def generate_record_number(sequence: int) -> str:
    year = datetime.utcnow().year
    return f"HC-{year}-{sequence:06d}"


async def get_next_sequence(db: AsyncSession) -> int:
    count = await db.scalar(select(func.count(ClinicalRecord.id)))
    return (count or 0) + 1


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
    await db.flush()

    sequence = await get_next_sequence(db)
    record = ClinicalRecord(
        patient_id=patient.id,
        record_number=generate_record_number(sequence),
        location="admision",
    )
    db.add(record)
    await db.commit()
    return await get_patient_by_id(db, tenant_id, patient.id)


async def get_patient_by_dni(db: AsyncSession, tenant_id: uuid.UUID, dni: str) -> Patient | None:
    result = await db.execute(
        select(Patient)
        .options(selectinload(Patient.clinical_record))
        .where(Patient.tenant_id == tenant_id, Patient.dni == dni)
    )
    return result.scalar_one_or_none()


# --- Consulta DNI externa (servicio propio, ver dni_app.py) ---
async def lookup_dni_externo(dni: str) -> dict | None:
    """Devuelve {'nombres', 'apellidoPaterno', 'apellidoMaterno'} o None si no se encontro
    o el servicio no esta disponible. Nunca lanza excepcion — el registro manual
    debe seguir funcionando si este servicio falla o esta apagado."""
    if not settings.DNI_API_URL or not settings.DNI_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                settings.DNI_API_URL,
                json={"dni": dni},
                headers={"X-API-Key": settings.DNI_API_KEY},
            )
        if resp.status_code != 200:
            return None
        return resp.json()
    except (httpx.TimeoutException, httpx.ConnectError):
        return None

async def get_patient_by_id(db: AsyncSession, tenant_id: uuid.UUID, patient_id: uuid.UUID) -> Patient | None:
    result = await db.execute(
        select(Patient)
        .options(selectinload(Patient.clinical_record))
        .where(Patient.tenant_id == tenant_id, Patient.id == patient_id)
    )
    return result.scalar_one_or_none()


async def search_patients(db: AsyncSession, tenant_id: uuid.UUID, query: str) -> list[Patient]:
    result = await db.execute(
        select(Patient)
        .options(selectinload(Patient.clinical_record))
        .where(
            Patient.tenant_id == tenant_id,
            or_(
                Patient.dni.ilike(f"%{query}%"),
                Patient.first_name.ilike(f"%{query}%"),
                Patient.last_name_paterno.ilike(f"%{query}%"),
                Patient.last_name_materno.ilike(f"%{query}%"),
            )
        )
        .limit(20)
    )
    return result.scalars().all()


async def update_patient(db: AsyncSession, tenant_id: uuid.UUID, patient_id: uuid.UUID, data: PatientUpdate) -> Patient | None:
    patient = await get_patient_by_id(db, tenant_id, patient_id)
    if not patient:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    await db.commit()
    await db.refresh(patient)
    return patient


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
    )
    record = result.scalar_one_or_none()
    if not record:
        raise ValueError("Historia clinica no encontrada")

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