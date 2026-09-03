import uuid
from datetime import datetime
from pydantic import BaseModel


class ExamenImagenologiaCreate(BaseModel):
    modalidad: str
    codigo: str | None = None
    nombre: str
    parte_cuerpo: str | None = None
    duracion_min: int = 30
    precio: float = 0.0
    requiere_contraste: bool = False
    is_active: bool = True


class ExamenImagenologiaUpdate(BaseModel):
    modalidad: str | None = None
    codigo: str | None = None
    nombre: str | None = None
    parte_cuerpo: str | None = None
    duracion_min: int | None = None
    precio: float | None = None
    requiere_contraste: bool | None = None
    is_active: bool | None = None


class ExamenImagenologiaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    modalidad: str
    codigo: str | None
    nombre: str
    parte_cuerpo: str | None
    duracion_min: int
    precio: float
    requiere_contraste: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}