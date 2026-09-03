import uuid
from datetime import datetime, date
from pydantic import BaseModel


# ─── Racion Nutricion ─────────────────────────────────────────────────────────

class RacionNutricionCreate(BaseModel):
    dni: str
    nombre_completo: str
    dependencia: str
    tipo_racion: str
    fecha: date
    entregado: bool = False
    observacion: str | None = None


class RacionNutricionUpdate(BaseModel):
    entregado: bool | None = None
    fecha_entrega: datetime | None = None
    observacion: str | None = None


class RacionNutricionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    dni: str
    nombre_completo: str
    dependencia: str
    tipo_racion: str
    fecha: date
    entregado: bool
    fecha_entrega: datetime | None
    observacion: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Buscar Racion por DNI ────────────────────────────────────────────────────

class BuscarRacionRequest(BaseModel):
    dni: str
    fecha: date


# ─── Reporte Nutricion ────────────────────────────────────────────────────────

class ReporteNutricionRequest(BaseModel):
    opcion: str = "POR DEPENDENCIA Y/O SERVICIO"
    dependencia: str = "TODAS"
    fecha: str  # MM/YYYY


# ─── Cambio Turno Nutricion ───────────────────────────────────────────────────

class CambioTurnoNutricionCreate(BaseModel):
    fecha: date
    turno_saliente: str
    turno_entrante: str
    observaciones: str | None = None
    raciones_entregadas: int | None = None


class CambioTurnoNutricionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    fecha: date
    turno_saliente: str
    turno_entrante: str
    observaciones: str | None
    raciones_entregadas: int | None
    created_at: datetime

    model_config = {"from_attributes": True}