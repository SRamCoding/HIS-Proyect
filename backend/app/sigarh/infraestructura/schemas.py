import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator
from app.sigarh.infraestructura.models import CATEGORIAS_CATALOGO


def _limpiar(v):
    if v is None:
        return None
    v = str(v).strip()
    return v or None


def _max(v, n, etiqueta):
    v = _limpiar(v)
    if v is not None and len(v) > n:
        raise ValueError(f"{etiqueta} no debe superar {n} caracteres")
    return v


# ─── Catálogo ─────────────────────────────────────────────────────────────────

class CatalogoCreate(BaseModel):
    categoria: str
    codigo: str | None = None
    nombre: str
    descripcion: str | None = None
    orden: int = 0
    is_active: bool = True

    @field_validator("categoria")
    @classmethod
    def _v_categoria(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("La categoría es requerida")
        if v not in CATEGORIAS_CATALOGO:
            raise ValueError(f"Categoría inválida. Opciones: {', '.join(CATEGORIAS_CATALOGO)}")
        return v

    @field_validator("codigo")
    @classmethod
    def _v_codigo(cls, v):
        return _max(v, 20, "El código")

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El nombre es requerido")
        if len(v) > 100:
            raise ValueError("El nombre no debe superar 100 caracteres")
        return v

    @field_validator("descripcion")
    @classmethod
    def _v_desc(cls, v):
        return _max(v, 255, "La descripción")

    @field_validator("orden")
    @classmethod
    def _v_orden(cls, v):
        if v is not None and v < 0:
            raise ValueError("El orden no puede ser negativo")
        return v


class CatalogoUpdate(CatalogoCreate):
    categoria: str | None = None
    nombre: str | None = None
    orden: int | None = None
    is_active: bool | None = None

    @field_validator("categoria")
    @classmethod
    def _v_categoria_upd(cls, v):
        v = _limpiar(v)
        if v is not None and v not in CATEGORIAS_CATALOGO:
            raise ValueError(f"Categoría inválida. Opciones: {', '.join(CATEGORIAS_CATALOGO)}")
        return v

    @field_validator("nombre")
    @classmethod
    def _v_nombre_upd(cls, v):
        return _max(v, 100, "El nombre")


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

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El nombre del consultorio es requerido")
        if len(v) > 100:
            raise ValueError("El nombre no debe superar 100 caracteres")
        return v

    @field_validator("capacidad")
    @classmethod
    def _v_capacidad(cls, v):
        if v is not None and v < 1:
            raise ValueError("La capacidad debe ser al menos 1")
        return v

    @field_validator("equipamiento")
    @classmethod
    def _v_equipamiento(cls, v):
        return _max(v, 255, "El equipamiento")


class ConsultorioUpdate(ConsultorioCreate):
    nombre: str | None = None
    capacidad: int | None = None
    is_active: bool | None = None

    @field_validator("nombre")
    @classmethod
    def _v_nombre_upd(cls, v):
        return _max(v, 100, "El nombre")


class ConsultorioResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    especialidad_id: uuid.UUID | None
    especialidad_nombre: str | None = None
    piso_id: uuid.UUID | None
    piso_nombre: str | None = None
    capacidad: int
    equipamiento: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Categorías disponibles ───────────────────────────────────────────────────

class CategoriasResponse(BaseModel):
    categorias: list[str]
