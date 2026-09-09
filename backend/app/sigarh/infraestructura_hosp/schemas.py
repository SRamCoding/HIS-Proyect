import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator

ESTADOS_CAMA = ("DISPONIBLE", "OCUPADA", "MANTENIMIENTO", "RESERVADA")


def _limpiar(v):
    if v is None:
        return None
    v = str(v).strip()
    return v or None


# ─── Piso ─────────────────────────────────────────────────────────────────────

class PisoCreate(BaseModel):
    nombre: str
    orden: int = 0
    descripcion: str | None = None
    is_active: bool = True

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El nombre del piso es requerido")
        if len(v) > 100:
            raise ValueError("El nombre no debe superar 100 caracteres")
        return v

    @field_validator("orden")
    @classmethod
    def _v_orden(cls, v):
        if v is not None and v < 0:
            raise ValueError("El orden no puede ser negativo")
        return v

    @field_validator("descripcion")
    @classmethod
    def _v_desc(cls, v):
        return _limpiar(v)


class PisoUpdate(PisoCreate):
    nombre: str | None = None
    orden: int | None = None
    is_active: bool | None = None

    @field_validator("nombre")
    @classmethod
    def _v_nombre_upd(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 100:
            raise ValueError("El nombre no debe superar 100 caracteres")
        return v


class PisoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    orden: int
    descripcion: str | None
    is_active: bool
    total_servicios: int = 0
    total_salas: int = 0
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

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El nombre de la sala es requerido")
        if len(v) > 100:
            raise ValueError("El nombre no debe superar 100 caracteres")
        return v

    @field_validator("codigo")
    @classmethod
    def _v_codigo(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 30:
            raise ValueError("El código no debe superar 30 caracteres")
        return v

    @field_validator("capacidad")
    @classmethod
    def _v_capacidad(cls, v):
        if v is not None and v < 1:
            raise ValueError("La capacidad debe ser al menos 1")
        return v


class SalaUpdate(SalaCreate):
    nombre: str | None = None
    capacidad: int | None = None
    is_active: bool | None = None

    @field_validator("nombre")
    @classmethod
    def _v_nombre_upd(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 100:
            raise ValueError("El nombre no debe superar 100 caracteres")
        return v


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
    total_camas: int = 0
    camas_disponibles: int = 0
    camas_ocupadas: int = 0
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerarCamasRequest(BaseModel):
    prefijo: str | None = None
    tipo_cama: str

    @field_validator("tipo_cama")
    @classmethod
    def _v_tipo(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El tipo de cama es requerido")
        return v

    @field_validator("prefijo")
    @classmethod
    def _v_prefijo(cls, v):
        return _limpiar(v)


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

    @field_validator("codigo")
    @classmethod
    def _v_codigo(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El código de la cama es requerido")
        if len(v) > 20:
            raise ValueError("El código no debe superar 20 caracteres")
        return v.upper()

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El nombre de la cama es requerido")
        if len(v) > 100:
            raise ValueError("El nombre no debe superar 100 caracteres")
        return v

    @field_validator("estado")
    @classmethod
    def _v_estado(cls, v):
        v = (_limpiar(v) or "DISPONIBLE").upper()
        if v not in ESTADOS_CAMA:
            raise ValueError(f"Estado inválido. Opciones: {', '.join(ESTADOS_CAMA)}")
        return v

    @field_validator("tipo_cama", "sala_texto", "piso_texto", "servicio_texto")
    @classmethod
    def _v_texto(cls, v):
        return _limpiar(v)


class CamaUpdate(CamaCreate):
    codigo: str | None = None
    nombre: str | None = None
    estado: str | None = None
    is_active: bool | None = None

    @field_validator("codigo")
    @classmethod
    def _v_codigo_upd(cls, v):
        v = _limpiar(v)
        if v is not None:
            if len(v) > 20:
                raise ValueError("El código no debe superar 20 caracteres")
            return v.upper()
        return v

    @field_validator("nombre")
    @classmethod
    def _v_nombre_upd(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 100:
            raise ValueError("El nombre no debe superar 100 caracteres")
        return v

    @field_validator("estado")
    @classmethod
    def _v_estado_upd(cls, v):
        if v is None:
            return None
        v = str(v).strip().upper()
        if v not in ESTADOS_CAMA:
            raise ValueError(f"Estado inválido. Opciones: {', '.join(ESTADOS_CAMA)}")
        return v


class CambiarEstadoRequest(BaseModel):
    estado: str

    @field_validator("estado")
    @classmethod
    def _v_estado(cls, v):
        v = (_limpiar(v) or "").upper()
        if v not in ESTADOS_CAMA:
            raise ValueError(f"Estado inválido. Opciones: {', '.join(ESTADOS_CAMA)}")
        return v


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
