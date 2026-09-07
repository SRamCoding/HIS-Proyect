import uuid
from datetime import datetime, date
from pydantic import BaseModel, model_validator


class PatientCreate(BaseModel):
    document_type: str = "DNI"
    dni: str | None = None
    is_nn: bool = False

    first_name: str
    second_name: str | None = None
    last_name_paterno: str
    last_name_materno: str
    birth_date: date
    gender: str
    marital_status: str | None = None
    education_level: str | None = None
    occupation: str | None = None
    ethnicity: str | None = None
    language: str | None = None

    phone: str | None = None
    phone_is_whatsapp: bool = False
    email: str | None = None

    address: str | None = None
    department_id: str | None = None
    province_id: str | None = None
    district_id: str | None = None
    populated_center: str | None = None
    country: str = "Peru"

    birth_same_as_address: bool = True
    birth_department_id: str | None = None
    birth_province_id: str | None = None
    birth_district_id: str | None = None
    birth_populated_center: str | None = None
    birth_country: str = "Peru"

    insurance_type: str | None = None
    insurance_number: str | None = None
    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data

    @model_validator(mode="after")
    def validar_dni_o_nn(self):
        if not self.is_nn and not self.dni:
            raise ValueError("El DNI/documento es obligatorio salvo que el paciente sea No Identificado (NN)")
        return self
    


class PatientUpdate(BaseModel):
    document_type: str | None = None
    dni: str | None = None
    is_nn: bool | None = None
    first_name: str | None = None
    second_name: str | None = None
    last_name_paterno: str | None = None
    last_name_materno: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    marital_status: str | None = None
    education_level: str | None = None
    occupation: str | None = None
    ethnicity: str | None = None
    language: str | None = None
    phone: str | None = None
    phone_is_whatsapp: bool | None = None
    email: str | None = None
    address: str | None = None
    department_id: str | None = None
    province_id: str | None = None
    district_id: str | None = None
    populated_center: str | None = None
    country: str | None = None
    birth_same_as_address: bool | None = None
    birth_department_id: str | None = None
    birth_province_id: str | None = None
    birth_district_id: str | None = None
    birth_populated_center: str | None = None
    birth_country: str | None = None
    insurance_type: str | None = None
    insurance_number: str | None = None


class PatientResponse(BaseModel):
    id: uuid.UUID
    document_type: str
    dni: str | None
    is_nn: bool
    first_name: str
    second_name: str | None
    last_name_paterno: str
    last_name_materno: str
    full_name: str
    birth_date: date
    gender: str
    age: int
    marital_status: str | None
    education_level: str | None
    occupation: str | None
    ethnicity: str | None
    language: str | None
    phone: str | None
    phone_is_whatsapp: bool
    email: str | None
    address: str | None
    department_id: str | None
    province_id: str | None
    district_id: str | None
    populated_center: str | None
    country: str
    birth_same_as_address: bool
    birth_department_id: str | None
    birth_province_id: str | None
    birth_district_id: str | None
    birth_populated_center: str | None
    birth_country: str
    insurance_type: str | None
    insurance_number: str | None
    is_active: bool
    created_at: datetime
    record_number: str | None = None

    model_config = {"from_attributes": True}


class PatientSearchResult(BaseModel):
    id: uuid.UUID
    dni: str | None
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


# --- Ubigeo (solo lectura, para los selects en cascada del frontend) ---
class UbigeoDepartamentoOut(BaseModel):
    id: str
    nombre: str
    model_config = {"from_attributes": True}


class UbigeoProvinciaOut(BaseModel):
    id: str
    nombre: str
    model_config = {"from_attributes": True}


class UbigeoDistritoOut(BaseModel):
    id: str
    nombre: str
    model_config = {"from_attributes": True}