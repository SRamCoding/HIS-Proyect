import uuid
from datetime import datetime
from pydantic import BaseModel


# ─── Piso ─────────────────────────────────────────────────────────────────────

class PisoCreate(BaseModel):
    nombre: str
    orden: int = 0
    descripcion: str | None = None
    is_active: bool = True


class PisoUpdate(BaseModel):
    nombre: str | None = None
    orden: int | None = None
    descripcion: str | None = None
    is_active: bool | None = None


class PisoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    orden: int
    descripcion: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Sala ─────────────────────────────────────────────────────────────────────

class SalaCreate(BaseModel):
    piso_id: uuid.UUID | None = None
    servicio_id: uuid.UUID | None = None
    nombre: str
    codigo: str | None = None
    capacidad: int = 1
    is_active: bool = True


class SalaUpdate(BaseModel):
    piso_id: uuid.UUID | None = None
    servicio_id: uuid.UUID | None = None
    nombre: str | None = None
    codigo: str | None = None
    capacidad: int | None = None
    is_active: bool | None = None


class SalaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    piso_id: uuid.UUID | None
    servicio_id: uuid.UUID | None
    piso_nombre: str | None = None
    servicio_nombre: str | None = None
    nombre: str
    codigo: str | None
    capacidad: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Cama ─────────────────────────────────────────────────────────────────────

class CamaCreate(BaseModel):
    sala_id: uuid.UUID | None = None
    piso_id: uuid.UUID | None = None
    servicio_id: uuid.UUID | None = None
    codigo: str
    nombre: str
    sala_texto: str | None = None
    piso_texto: str | None = None
    servicio_texto: str | None = None
    tipo_cama: str | None = None
    estado: str = "DISPONIBLE"
    is_active: bool = True


class CamaUpdate(BaseModel):
    sala_id: uuid.UUID | None = None
    piso_id: uuid.UUID | None = None
    servicio_id: uuid.UUID | None = None
    codigo: str | None = None
    nombre: str | None = None
    sala_texto: str | None = None
    piso_texto: str | None = None
    servicio_texto: str | None = None
    tipo_cama: str | None = None
    estado: str | None = None
    is_active: bool | None = None


class CamaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    sala_id: uuid.UUID | None
    piso_id: uuid.UUID | None
    servicio_id: uuid.UUID | None
    codigo: str
    nombre: str
    sala_texto: str | None
    piso_texto: str | None
    servicio_texto: str | None
    tipo_cama: str | None
    estado: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}