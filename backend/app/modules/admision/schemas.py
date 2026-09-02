import uuid
from datetime import datetime, date
from pydantic import BaseModel


class PatientCreate(BaseModel):
    dni: str
    first_name: str
    last_name_paterno: str
    last_name_materno: str
    birth_date: date
    gender: str
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    department_id: str | None = None
    province_id: str | None = None
    district_id: str | None = None
    insurance_type: str | None = None
    insurance_number: str | None = None


class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name_paterno: str | None = None
    last_name_materno: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    insurance_type: str | None = None
    insurance_number: str | None = None


class PatientResponse(BaseModel):
    id: uuid.UUID
    dni: str
    first_name: str
    last_name_paterno: str
    last_name_materno: str
    full_name: str
    birth_date: date
    gender: str
    age: int
    phone: str | None
    email: str | None
    address: str | None
    department_id: str | None
    province_id: str | None
    district_id: str | None
    insurance_type: str | None
    insurance_number: str | None
    is_active: bool
    created_at: datetime
    record_number: str | None = None

    model_config = {"from_attributes": True}


class PatientSearchResult(BaseModel):
    id: uuid.UUID
    dni: str
    full_name: str
    age: int
    gender: str
    insurance_type: str | None
    record_number: str | None

    model_config = {"from_attributes": True}


class ClinicalRecordMovementCreate(BaseModel):
    clinical_record_id: uuid.UUID
    to_location: str
    moved_by: str | None = None
    notes: str | None = None