import uuid
from datetime import datetime
from pydantic import BaseModel
from app.sigarh.infraestructura.models import CATEGORIAS_CATALOGO


# ─── Catálogo ─────────────────────────────────────────────────────────────────

class CatalogoCreate(BaseModel):
    categoria: str
    codigo: str | None = None
    nombre: str
    descripcion: str | None = None
    orden: int = 0
    is_active: bool = True


class CatalogoUpdate(BaseModel):
    categoria: str | None = None
    codigo: str | None = None
    nombre: str | None = None
    descripcion: str | None = None
    orden: int | None = None
    is_active: bool | None = None


class CatalogoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    categoria: str
    codigo: str | None
    nombre: str
    descripcion: str | None
    orden: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Consultorio ──────────────────────────────────────────────────────────────

class ConsultorioCreate(BaseModel):
    nombre: str
    especialidad_id: uuid.UUID | None = None
    piso_id: uuid.UUID | None = None
    capacidad: int = 1
    equipamiento: str | None = None
    is_active: bool = True


class ConsultorioUpdate(BaseModel):
    nombre: str | None = None
    especialidad_id: uuid.UUID | None = None
    piso_id: uuid.UUID | None = None
    capacidad: int | None = None
    equipamiento: str | None = None
    is_active: bool | None = None


class ConsultorioResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    especialidad_id: uuid.UUID | None
    especialidad_nombre: str | None = None
    piso_id: uuid.UUID | None
    capacidad: int
    equipamiento: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Categorías disponibles ───────────────────────────────────────────────────

class CategoriasResponse(BaseModel):
    categorias: list[str]