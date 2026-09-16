import re
import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator

from app.sigarh.mantenimiento.schemas import validar_password


class HospitalListItem(BaseModel):
    id: uuid.UUID
    name: str
    domain: str
    hospital_level: str | None
    is_active: bool
    active_modules: list[str]
    created_at: datetime
    provisioning_status: str = "listo"
    provisioning_error: str | None = None

    model_config = {"from_attributes": True}


class ModuleToggle(BaseModel):
    tenant_id: uuid.UUID
    module_codes: list[str]


class ActiveToggle(BaseModel):
    is_active: bool


class ReintentarAprovisionamiento(BaseModel):
    """Credenciales para reintentar un hospital que quedó en provisioning_status
    'error'. Se piden de nuevo porque nunca se guardan en claro en ningún
    lado -- sólo viajaron hasheadas al worker de Celery en el intento
    anterior y se descartan apenas termina esa tarea."""
    admin_name: str
    admin_email: str
    admin_password: str
    sigarh_name: str
    sigarh_email: str
    sigarh_password: str

    @field_validator("admin_password", "sigarh_password")
    @classmethod
    def _v_password(cls, v):
        return validar_password(v)

    @field_validator("admin_email", "sigarh_email")
    @classmethod
    def _v_email(cls, value):
        value = value.lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("El correo electrónico no es válido")
        return value

    @model_validator(mode="after")
    def _v_correos_distintos(self):
        if self.admin_email == self.sigarh_email:
            raise ValueError("Los usuarios App y SIGARH deben usar correos diferentes")
        return self
