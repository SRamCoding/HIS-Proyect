import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, StrictBool, model_validator


class HistoriaOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    patient_name: str
    document_type: str
    document_number: str | None
    record_number: str
    location: str
    is_digitized: bool
    updated_at: datetime


class HistoriasPage(BaseModel):
    items: list[HistoriaOut]
    total: int
    page: int
    page_size: int


class DigitalizarRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    is_digitized: StrictBool

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: None if v == "" else v for k, v in data.items()}
        return data


class MovimientoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    clinical_record_id: uuid.UUID
    from_location: str
    to_location: str
    moved_by: str | None
    notes: str | None
    created_at: datetime


class MovimientosPage(BaseModel):
    historia: HistoriaOut
    items: list[MovimientoOut]
    total: int
    page: int
    page_size: int


class PersonalArchivoOut(BaseModel):
    id: uuid.UUID
    name: str
    email: str | None
    role: str
    is_active: bool
    empleado_id: uuid.UUID | None
    empleado_nombre: str | None
    empleado_dni: str | None
    perfil_nombre: str | None
    created_at: datetime
