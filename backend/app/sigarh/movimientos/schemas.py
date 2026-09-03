import uuid
from datetime import datetime, date
from pydantic import BaseModel


# ─── Vacaciones ───────────────────────────────────────────────────────────────

class VacacionCreate(BaseModel):
    empleado_id: uuid.UUID
    motivo_id: uuid.UUID | None = None
    tipo: str = "vacacion"
    fecha_inicio: date
    fecha_fin: date
    dias: int | None = None
    detalle: str | None = None
    documento_url: str | None = None
    estado: str = "pendiente"
    mes_actual: bool = True


class VacacionResponse(VacacionCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    empleado_nombre: str | None = None
    motivo_nombre: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Licencias ────────────────────────────────────────────────────────────────

class LicenciaCreate(BaseModel):
    empleado_id: uuid.UUID
    motivo_id: uuid.UUID | None = None
    fecha_tramite: date
    fecha_inicio: date
    fecha_fin: date
    dias: int | None = None
    documento_url: str | None = None
    detalle: str | None = None
    estado: str = "pendiente"


class LicenciaResponse(LicenciaCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    empleado_nombre: str | None = None
    cargo_laboral: str | None = None
    motivo_nombre: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Cambio de Turno ──────────────────────────────────────────────────────────

class CambioTurnoCreate(BaseModel):
    servicio_id: uuid.UUID | None = None
    numero_documento: str | None = None
    solicitante_id: uuid.UUID
    fecha_original: date
    modalidad_solicitante: str | None = None
    aceptante_id: uuid.UUID | None = None
    fecha_reemplazo: date
    modalidad_aceptante: str | None = None
    estado: str = "pendiente"


class CambioTurnoResponse(CambioTurnoCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    solicitante_nombre: str | None = None
    aceptante_nombre: str | None = None
    servicio_nombre: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Papeletas ────────────────────────────────────────────────────────────────

class PapeletaCreate(BaseModel):
    empleado_id: uuid.UUID
    motivo_id: uuid.UUID | None = None
    fecha_tramite: date
    documento_url: str | None = None
    detalle: str | None = None
    estado: str = "pendiente"
    mes_actual: bool = True


class PapeletaResponse(PapeletaCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    empleado_nombre: str | None = None
    cargo_laboral: str | None = None
    motivo_nombre: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}