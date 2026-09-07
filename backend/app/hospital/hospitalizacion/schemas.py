import uuid
from datetime import datetime
from pydantic import BaseModel


class PisoOut(BaseModel):
    id: uuid.UUID
    nombre: str
    model_config = {"from_attributes": True}


class CamaConPacienteOut(BaseModel):
    id: uuid.UUID
    codigo: str
    nombre: str
    tipo_cama: str | None
    estado: str
    sala_nombre: str | None
    servicio_nombre: str | None
    paciente_nombre: str | None = None
    paciente_dni: str | None = None
    fecha_ingreso: datetime | None = None
    numero_hospitalizacion: str | None = None
    hospitalizacion_cita_id: uuid.UUID | None = None