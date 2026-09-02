import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module
from app.modules.admision.schemas import (
    PatientCreate, PatientUpdate, PatientResponse,
    PatientSearchResult, ClinicalRecordMovementCreate,
)
from app.modules.admision.service import (
    create_patient, get_patient_by_dni, get_patient_by_id,
    search_patients, update_patient, move_clinical_record,
)

router = APIRouter()


def _to_response(patient) -> PatientResponse:
    return PatientResponse(
        id=patient.id,
        dni=patient.dni,
        first_name=patient.first_name,
        last_name_paterno=patient.last_name_paterno,
        last_name_materno=patient.last_name_materno,
        full_name=patient.full_name,
        birth_date=patient.birth_date,
        gender=patient.gender,
        age=patient.age,
        phone=patient.phone,
        email=patient.email,
        address=patient.address,
        department_id=patient.department_id,
        province_id=patient.province_id,
        district_id=patient.district_id,
        insurance_type=patient.insurance_type,
        insurance_number=patient.insurance_number,
        is_active=patient.is_active,
        created_at=patient.created_at,
        record_number=patient.clinical_record.record_number if patient.clinical_record else None,
    )


@router.get("/buscar", response_model=list[PatientSearchResult], summary="Buscar pacientes")
async def buscar_pacientes(
    q: str,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module("pacientes")),
    current_user: dict = Depends(get_current_user),
):
    if len(q) < 2:
        raise HTTPException(400, detail="Ingresa al menos 2 caracteres")
    patients = await search_patients(db, q)
    return [
        PatientSearchResult(
            id=p.id,
            dni=p.dni,
            full_name=p.full_name,
            age=p.age,
            gender=p.gender,
            insurance_type=p.insurance_type,
            record_number=p.clinical_record.record_number if p.clinical_record else None,
        )
        for p in patients
    ]


@router.get("/dni/{dni}", response_model=PatientResponse, summary="Buscar por DNI")
async def buscar_por_dni(
    dni: str,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module("pacientes")),
    current_user: dict = Depends(get_current_user),
):
    patient = await get_patient_by_dni(db, dni)
    if not patient:
        raise HTTPException(404, detail=f"Paciente con DNI {dni} no encontrado")
    return _to_response(patient)


@router.post("/", response_model=PatientResponse, status_code=201, summary="Registrar paciente")
async def registrar_paciente(
    data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module("pacientes")),
    current_user: dict = Depends(get_current_user),
):
    existing = await get_patient_by_dni(db, data.dni)
    if existing:
        raise HTTPException(400, detail=f"Ya existe un paciente con DNI {data.dni}")
    patient = await create_patient(db, data)
    return _to_response(patient)


@router.get("/{patient_id}", response_model=PatientResponse, summary="Obtener paciente")
async def obtener_paciente(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module("pacientes")),
    current_user: dict = Depends(get_current_user),
):
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(404, detail="Paciente no encontrado")
    return _to_response(patient)


@router.patch("/{patient_id}", response_model=PatientResponse, summary="Actualizar paciente")
async def actualizar_paciente(
    patient_id: uuid.UUID,
    data: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module("pacientes")),
    current_user: dict = Depends(get_current_user),
):
    patient = await update_patient(db, patient_id, data)
    if not patient:
        raise HTTPException(404, detail="Paciente no encontrado")
    return _to_response(patient)


@router.post("/historia-clinica/mover", summary="Mover historia clinica")
async def mover_historia_clinica(
    data: ClinicalRecordMovementCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module("pacientes")),
    current_user: dict = Depends(get_current_user),
):
    movement = await move_clinical_record(
        db, data.clinical_record_id, data.to_location,
        data.moved_by, data.notes,
    )
    return {"ok": True, "movement_id": str(movement.id)}