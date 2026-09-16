import uuid
from pydantic import BaseModel, model_validator

_MEDIOS = {"LLAMADA", "WHATSAPP", "VIDEOLLAMADA"}


class SolicitudCreateIn(BaseModel):
    patient_id: uuid.UUID
    especialidad_id: uuid.UUID | None = None
    motivo: str
    medio_preferido: str = "LLAMADA"
    contacto: str | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.medio_preferido not in _MEDIOS:
            raise ValueError("medio_preferido debe ser LLAMADA, WHATSAPP o VIDEOLLAMADA")
        return self


class ProgramarSolicitudIn(BaseModel):
    cita_id: uuid.UUID


class RechazarSolicitudIn(BaseModel):
    motivo_rechazo: str
