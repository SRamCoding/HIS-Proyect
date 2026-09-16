import uuid
from datetime import datetime, date
from pydantic import BaseModel, Field, model_validator, field_validator


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
    to_location: str = Field(min_length=1, max_length=50)
    moved_by: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (v.strip() or None) if isinstance(v, str) else v
                    for k, v in data.items()}
        return data


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


# --- Altas (vista de solo lectura, sin tabla propia) ---
class AltaItem(BaseModel):
    origen: str  # hospitalizacion | emergencia
    id: uuid.UUID
    patient_id: uuid.UUID
    paciente_nombre: str
    paciente_dni: str | None
    numero: str | None = None  # numero_hospitalizacion o numero_cuenta
    fecha_alta: datetime | None
    resumen: str | None
    servicio_o_especialidad: str | None = None


# --- Lista de Espera ---
class ListaEsperaCreate(BaseModel):
    patient_id: uuid.UUID
    servicio_id: uuid.UUID | None = None
    especialidad_id: uuid.UUID | None = None
    motivo: str | None = Field(default=None, max_length=2000)
    prioridad: str = "normal"

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, v):
        if v not in ("normal", "urgente"):
            raise ValueError("prioridad debe ser 'normal' o 'urgente'")
        return v

    @model_validator(mode="after")
    def requiere_servicio_o_especialidad(self):
        if not self.servicio_id and not self.especialidad_id:
            raise ValueError("Debe indicar al menos servicio_id o especialidad_id")
        return self


class ListaEsperaUpdate(BaseModel):
    motivo: str | None = Field(default=None, max_length=2000)
    prioridad: str | None = None

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, v):
        if v is not None and v not in ("normal", "urgente"):
            raise ValueError("prioridad debe ser 'normal' o 'urgente'")
        return v


class ListaEsperaAtender(BaseModel):
    cita_id: uuid.UUID | None = None


class ListaEsperaResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    paciente_nombre: str
    paciente_dni: str | None
    servicio_id: uuid.UUID | None
    servicio_nombre: str | None
    especialidad_id: uuid.UUID | None
    especialidad_nombre: str | None
    cita_id: uuid.UUID | None
    motivo: str | None
    prioridad: str
    estado: str
    registrado_por: str | None
    created_at: datetime
    atendido_at: datetime | None


# --- Anuncios ---
class AnuncioCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=150)
    contenido: str = Field(min_length=1, max_length=5000)


class AnuncioUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=150)
    contenido: str | None = Field(default=None, min_length=1, max_length=5000)
    is_active: bool | None = None


class AnuncioResponse(BaseModel):
    id: uuid.UUID
    titulo: str
    contenido: str
    publicado_por: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Mensajito ---
class MensajeCreate(BaseModel):
    contenido: str = Field(min_length=1, max_length=500)
    destinatario_user_id: uuid.UUID | None = None
    destinatario_role: str | None = None
    patient_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def requiere_destinatario(self):
        if not self.destinatario_user_id and not self.destinatario_role:
            raise ValueError("Debe indicar destinatario_user_id o destinatario_role")
        return self


class MensajeResponse(BaseModel):
    id: uuid.UUID
    remitente_user_id: uuid.UUID
    remitente_nombre: str | None
    destinatario_user_id: uuid.UUID | None
    destinatario_role: str | None
    patient_id: uuid.UUID | None
    paciente_nombre: str | None = None
    contenido: str
    leido: bool
    leido_at: datetime | None
    created_at: datetime


class DestinatarioOut(BaseModel):
    id: uuid.UUID
    name: str
    role: str
