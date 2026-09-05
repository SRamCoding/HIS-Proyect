# backend/app/modules/admision/router.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.hospital.gestion_pacientes.schemas import (
    PatientCreate, PatientUpdate, PatientResponse,
    PatientSearchResult, ClinicalRecordMovementCreate,
)
from app.hospital.gestion_pacientes.service import (
    create_patient, get_patient_by_dni, get_patient_by_id,
    search_patients, update_patient, move_clinical_record,
)

router = APIRouter()


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


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
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("gestion_pacientes")),
):
    tenant_id = get_tenant_id(current_user, request)
    if len(q) < 2:
        raise HTTPException(400, detail="Ingresa al menos 2 caracteres")
    patients = await search_patients(db, tenant_id, q)
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
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("gestion_pacientes")),
):
    tenant_id = get_tenant_id(current_user, request)
    patient = await get_patient_by_dni(db, tenant_id, dni)
    if not patient:
        raise HTTPException(404, detail=f"Paciente con DNI {dni} no encontrado")
    return _to_response(patient)


@router.post("/", response_model=PatientResponse, status_code=201, summary="Registrar paciente")
async def registrar_paciente(
    data: PatientCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("gestion_pacientes")),
):
    tenant_id = get_tenant_id(current_user, request)
    existing = await get_patient_by_dni(db, tenant_id, data.dni)
    if existing:
        raise HTTPException(400, detail=f"Ya existe un paciente con DNI {data.dni}")
    patient = await create_patient(db, tenant_id, data)
    return _to_response(patient)


@router.get("/{patient_id}", response_model=PatientResponse, summary="Obtener paciente")
async def obtener_paciente(
    patient_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("gestion_pacientes")),
):
    tenant_id = get_tenant_id(current_user, request)
    patient = await get_patient_by_id(db, tenant_id, patient_id)
    if not patient:
        raise HTTPException(404, detail="Paciente no encontrado")
    return _to_response(patient)


@router.patch("/{patient_id}", response_model=PatientResponse, summary="Actualizar paciente")
async def actualizar_paciente(
    patient_id: uuid.UUID,
    data: PatientUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("gestion_pacientes")),
):
    tenant_id = get_tenant_id(current_user, request)
    patient = await update_patient(db, tenant_id, patient_id, data)
    if not patient:
        raise HTTPException(404, detail="Paciente no encontrado")
    return _to_response(patient)


@router.post("/historia-clinica/mover", summary="Mover historia clinica")
async def mover_historia_clinica(
    data: ClinicalRecordMovementCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("gestion_pacientes")),
):
    tenant_id = get_tenant_id(current_user, request)
    try:
        movement = await move_clinical_record(
            db, tenant_id, data.clinical_record_id, data.to_location,
            data.moved_by, data.notes,
        )
    except ValueError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    return {"ok": True, "movement_id": str(movement.id)}
