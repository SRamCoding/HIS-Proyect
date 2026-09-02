import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.modules.admision.models import Patient, ClinicalRecord, ClinicalRecordMovement
from app.modules.admision.schemas import PatientCreate, PatientUpdate


def generate_record_number(sequence: int) -> str:
    year = datetime.utcnow().year
    return f"HC-{year}-{sequence:06d}"


async def get_next_sequence(db: AsyncSession) -> int:
    count = await db.scalar(select(func.count(ClinicalRecord.id)))
    return (count or 0) + 1


async def create_patient(db: AsyncSession, data: PatientCreate) -> Patient:
    patient = Patient(
        dni=data.dni,
        first_name=data.first_name,
        last_name_paterno=data.last_name_paterno,
        last_name_materno=data.last_name_materno,
        birth_date=data.birth_date,
        gender=data.gender,
        phone=data.phone,
        email=data.email,
        address=data.address,
        department_id=data.department_id,
        province_id=data.province_id,
        district_id=data.district_id,
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
    await db.refresh(patient)
    await db.refresh(record)
    return patient


async def get_patient_by_dni(db: AsyncSession, dni: str) -> Patient | None:
    result = await db.execute(
        select(Patient)
        .options(selectinload(Patient.clinical_record))
        .where(Patient.dni == dni)
    )
    return result.scalar_one_or_none()


async def get_patient_by_id(db: AsyncSession, patient_id: uuid.UUID) -> Patient | None:
    result = await db.execute(
        select(Patient)
        .options(selectinload(Patient.clinical_record))
        .where(Patient.id == patient_id)
    )
    return result.scalar_one_or_none()


async def search_patients(db: AsyncSession, query: str) -> list[Patient]:
    result = await db.execute(
        select(Patient)
        .options(selectinload(Patient.clinical_record))
        .where(
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


async def update_patient(db: AsyncSession, patient_id: uuid.UUID, data: PatientUpdate) -> Patient | None:
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    await db.commit()
    await db.refresh(patient)
    return patient


async def move_clinical_record(
    db: AsyncSession,
    clinical_record_id: uuid.UUID,
    to_location: str,
    moved_by: str | None = None,
    notes: str | None = None,
) -> ClinicalRecordMovement:
    result = await db.execute(
        select(ClinicalRecord).where(ClinicalRecord.id == clinical_record_id)
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