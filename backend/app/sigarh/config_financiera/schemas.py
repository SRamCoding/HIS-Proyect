import uuid
from datetime import datetime
from pydantic import BaseModel


# ─── Plan Seguro ──────────────────────────────────────────────────────────────

class PlanSeguroCreate(BaseModel):
    nombre: str
    codigo: str | None = None
    precio_referencia: float | None = None
    detalle_cobertura: str | None = None
    is_active: bool = True


class PlanSeguroResponse(PlanSeguroCreate):
    id: uuid.UUID
    seguro_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Seguro ───────────────────────────────────────────────────────────────────

class SeguroCreate(BaseModel):
    nombre: str
    codigo: str | None = None
    tipo_entidad: str | None = None
    requiere_fua: bool = False
    notas: str | None = None
    is_active: bool = True
    planes: list[PlanSeguroCreate] = []


class SeguroUpdate(BaseModel):
    nombre: str | None = None
    codigo: str | None = None
    tipo_entidad: str | None = None
    requiere_fua: bool | None = None
    notas: str | None = None
    is_active: bool | None = None


class SeguroResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    codigo: str | None
    tipo_entidad: str | None
    requiere_fua: bool
    notas: str | None
    is_active: bool
    planes: list[PlanSeguroResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class SeguroListItem(BaseModel):
    id: uuid.UUID
    nombre: str
    codigo: str | None
    tipo_entidad: str | None
    requiere_fua: bool
    is_active: bool

    model_config = {"from_attributes": True}


# ─── Caja ─────────────────────────────────────────────────────────────────────

class CajaCreate(BaseModel):
    nombre: str
    codigo: str | None = None
    cajero_id: uuid.UUID | None = None
    estado: str = "cerrada"
    monto_apertura: float = 0.0
    is_active: bool = True


class CajaUpdate(BaseModel):
    nombre: str | None = None
    codigo: str | None = None
    cajero_id: uuid.UUID | None = None
    estado: str | None = None
    monto_apertura: float | None = None
    is_active: bool | None = None


class CajaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    codigo: str | None
    cajero_id: uuid.UUID | None
    estado: str
    monto_apertura: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Tarifario ────────────────────────────────────────────────────────────────

class TarifarioCreate(BaseModel):
    codigo: str | None = None
    descripcion_servicio: str
    tipo_servicio: str | None = None
    especialidad_id: uuid.UUID | None = None
    seguro_id: uuid.UUID | None = None
    precio: float = 0.0
    is_active: bool = True


class TarifarioUpdate(BaseModel):
    codigo: str | None = None
    descripcion_servicio: str | None = None
    tipo_servicio: str | None = None
    especialidad_id: uuid.UUID | None = None
    seguro_id: uuid.UUID | None = None
    precio: float | None = None
    is_active: bool | None = None


class TarifarioResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo: str | None
    descripcion_servicio: str
    tipo_servicio: str | None
    especialidad_id: uuid.UUID | None
    seguro_id: uuid.UUID | None
    precio: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}