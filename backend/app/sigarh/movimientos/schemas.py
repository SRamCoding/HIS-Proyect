import uuid
from datetime import datetime, date
from pydantic import BaseModel, field_validator, model_validator

# Licencias y "Justificación y Vacaciones" comparten la tabla sigarh_justificaciones
# (modelo RRHH). Estos submódulos usan directamente los schemas de RRHH.
from app.sigarh.rrhh.schemas import (  # noqa: F401
    JustificacionCreate, JustificacionUpdate, JustificacionResponse, JustificacionDecision,
)


def _limpiar(v):
    if v is None:
        return None
    v = str(v).strip()
    return v or None


# ─── Cambio de Turno ──────────────────────────────────────────────────────────

class CambioTurnoCreate(BaseModel):
    servicio_id: uuid.UUID | None = None
    numero_documento: str | None = None
    solicitante_id: uuid.UUID
    fecha_original: date
    modalidad_solicitante: str | None = None
    aceptante_id: uuid.UUID
    fecha_reemplazo: date
    modalidad_aceptante: str | None = None
    estado: str = "pendiente"

    @field_validator("numero_documento")
    @classmethod
    def _v_doc(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 50:
            raise ValueError("El N° de documento no debe superar 50 caracteres")
        return v

    @model_validator(mode="after")
    def _v_reglas(self):
        if self.solicitante_id == self.aceptante_id:
            raise ValueError("El solicitante y el aceptante deben ser personas distintas")
        if self.fecha_original == self.fecha_reemplazo:
            raise ValueError("La fecha original y la de reemplazo deben ser diferentes")
        if self.fecha_original and self.fecha_original < date.today():
            raise ValueError("La fecha original no puede ser una fecha pasada")
        return self


class CambioTurnoResponse(CambioTurnoCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    solicitante_nombre: str | None = None
    solicitante_dni: str | None = None
    aceptante_nombre: str | None = None
    aceptante_dni: str | None = None
    servicio_nombre: str | None = None
    registrado_por: str | None = None
    revisado_por: str | None = None
    revisado_at: datetime | None = None
    motivo_rechazo: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Papeletas ────────────────────────────────────────────────────────────────

_MOTIVOS_PAPELETA = {"asuntos_particulares", "comision", "salud", "tramite_personal", "otro"}


class PapeletaCreate(BaseModel):
    empleado_id: uuid.UUID
    motivo: str
    numero_documento: str | None = None
    fecha_tramite: date | None = None
    documento_url: str | None = None
    detalle: str | None = None

    @field_validator("motivo")
    @classmethod
    def _v_motivo(cls, v):
        v = (_limpiar(v) or "").lower().replace(" ", "_")
        if v not in _MOTIVOS_PAPELETA:
            raise ValueError("Motivo inválido. Opciones: asuntos_particulares, comision, salud, tramite_personal, otro")
        return v

    @field_validator("numero_documento")
    @classmethod
    def _v_doc(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 50:
            raise ValueError("El N° de documento no debe superar 50 caracteres")
        return v

    @field_validator("detalle")
    @classmethod
    def _v_detalle(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 500:
            raise ValueError("El detalle no debe superar 500 caracteres")
        return v

    @model_validator(mode="after")
    def _v_salud(self):
        if self.motivo == "salud" and not self.documento_url:
            raise ValueError("Para el motivo 'Salud' es obligatorio adjuntar el documento sustentatorio")
        return self


class PapeletaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    empleado_id: uuid.UUID
    empleado_nombre: str | None = None
    empleado_cargo: str | None = None
    motivo: str | None
    numero_documento: str | None
    fecha_tramite: date
    documento_url: str | None
    detalle: str | None
    estado: str
    hora_salida: str | None
    hora_retorno: str | None
    registrado_por: str | None
    revisado_por: str | None
    revisado_at: datetime | None
    motivo_rechazo: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
