import uuid
from datetime import datetime, date
from pydantic import BaseModel


# ─── CIE-10 ───────────────────────────────────────────────────────────────────

class DiagnosticoCIE10Create(BaseModel):
    capitulo: str | None = None
    grupo: str | None = None
    categoria: str | None = None
    codigo_cie10: str
    codigo_cie9: str | None = None
    descripcion: str
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None
    sexo: str = "ambos"
    edad_minima: int | None = None
    edad_maxima: int | None = None
    morbilidad: bool = False
    intrahospitalario: bool = False
    gestacion: bool = False
    is_active: bool = True


class DiagnosticoCIE10Update(BaseModel):
    capitulo: str | None = None
    grupo: str | None = None
    categoria: str | None = None
    codigo_cie9: str | None = None
    descripcion: str | None = None
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None
    sexo: str | None = None
    edad_minima: int | None = None
    edad_maxima: int | None = None
    morbilidad: bool | None = None
    intrahospitalario: bool | None = None
    gestacion: bool | None = None
    is_active: bool | None = None


class DiagnosticoCIE10Response(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    capitulo: str | None
    grupo: str | None
    categoria: str | None
    codigo_cie10: str
    codigo_cie9: str | None
    descripcion: str
    vigencia_desde: date | None
    vigencia_hasta: date | None
    sexo: str
    edad_minima: int | None
    edad_maxima: int | None
    morbilidad: bool
    intrahospitalario: bool
    gestacion: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Paquete Item ─────────────────────────────────────────────────────────────

class PaqueteItemCreate(BaseModel):
    medicamento_id: uuid.UUID | None = None
    cantidad: int = 1


class PaqueteItemResponse(PaqueteItemCreate):
    id: uuid.UUID
    paquete_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Paquete ──────────────────────────────────────────────────────────────────

class PaqueteCreate(BaseModel):
    codigo: str | None = None
    nombre: str
    punto_carga: str | None = None
    especialidad_id: uuid.UUID | None = None
    descripcion: str | None = None
    is_active: bool = True
    items: list[PaqueteItemCreate] = []


class PaqueteUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    punto_carga: str | None = None
    especialidad_id: uuid.UUID | None = None
    descripcion: str | None = None
    is_active: bool | None = None


class PaqueteResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo: str | None
    nombre: str
    punto_carga: str | None
    especialidad_id: uuid.UUID | None
    descripcion: str | None
    is_active: bool
    items: list[PaqueteItemResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Tiempo Procedimiento ─────────────────────────────────────────────────────

class TiempoProcedimientoCreate(BaseModel):
    codigo: str | None = None
    nombre: str
    especialidad_id: uuid.UUID | None = None
    duracion_minutos: int = 30
    is_active: bool = True


class TiempoProcedimientoUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    especialidad_id: uuid.UUID | None = None
    duracion_minutos: int | None = None
    is_active: bool | None = None


class TiempoProcedimientoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo: str | None
    nombre: str
    especialidad_id: uuid.UUID | None
    duracion_minutos: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DiagnosticoCIE10Page(BaseModel):
    items: list[DiagnosticoCIE10Response]
    total: int
    page: int
    page_size: int
    pages: int
