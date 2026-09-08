import uuid
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.hospital.archivo_clinico.models import ClinicalRecord, ClinicalRecordMovement
from app.hospital.gestion_pacientes.models import Patient


def _historias(tenant_id: uuid.UUID):
    return select(ClinicalRecord, Patient).join(
        Patient, Patient.id == ClinicalRecord.patient_id
    ).where(Patient.tenant_id == tenant_id)


def _historia_out(record, patient):
    return {
        "id": record.id, "patient_id": patient.id,
        "patient_name": " ".join(filter(None, [patient.last_name_paterno,
            patient.last_name_materno, patient.first_name, patient.second_name])),
        "document_type": patient.document_type, "document_number": patient.dni,
        "record_number": record.record_number, "location": record.location,
        "is_digitized": record.is_digitized, "updated_at": record.updated_at,
    }


async def list_historias(db: AsyncSession, tenant_id: uuid.UUID, q: str | None,
                        location: str | None, is_digitized: bool | None,
                        page: int, page_size: int):
    query = _historias(tenant_id)
    for term in (q or "").split():
        query = query.where(or_(*[
            column.icontains(term, autoescape=True) for column in (
                ClinicalRecord.record_number, Patient.dni, Patient.first_name,
                Patient.second_name, Patient.last_name_paterno, Patient.last_name_materno,
            )
        ]))
    if location and location.strip():
        query = query.where(ClinicalRecord.location.icontains(location.strip(), autoescape=True))
    if is_digitized is not None:
        query = query.where(ClinicalRecord.is_digitized == is_digitized)
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    rows = await db.execute(query.order_by(ClinicalRecord.record_number, ClinicalRecord.id)
                            .offset((page - 1) * page_size).limit(page_size))
    return {"items": [_historia_out(r, p) for r, p in rows.all()],
            "total": total, "page": page, "page_size": page_size}


async def list_movimientos(db: AsyncSession, tenant_id: uuid.UUID, record_id: uuid.UUID,
                           page: int, page_size: int):
    row = (await db.execute(_historias(tenant_id).where(ClinicalRecord.id == record_id))).first()
    if row is None:
        return None
    query = select(ClinicalRecordMovement).join(
        ClinicalRecord, ClinicalRecord.id == ClinicalRecordMovement.clinical_record_id
    ).join(Patient, Patient.id == ClinicalRecord.patient_id).where(
        Patient.tenant_id == tenant_id, ClinicalRecord.id == record_id
    )
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    result = await db.execute(query.order_by(ClinicalRecordMovement.created_at.desc(),
        ClinicalRecordMovement.id.desc()).offset((page - 1) * page_size).limit(page_size))
    return {"historia": _historia_out(*row), "items": result.scalars().all(),
            "total": total, "page": page, "page_size": page_size}


async def set_digitalizada(db: AsyncSession, tenant_id: uuid.UUID,
                           record_id: uuid.UUID, is_digitized: bool):
    row = (await db.execute(_historias(tenant_id).where(ClinicalRecord.id == record_id)
                           .with_for_update(of=ClinicalRecord))).first()
    if row is None:
        return None
    record, patient = row
    record.is_digitized = is_digitized
    await db.flush()
    return _historia_out(record, patient)
