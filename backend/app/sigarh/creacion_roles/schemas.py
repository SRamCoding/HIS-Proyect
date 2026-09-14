"""Esquemas compartidos por Creación de Roles, Roles Pendientes y Roles Aprobados."""
import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator

from app.sigarh.creacion_roles.models import (
    CATEGORIAS_PERSONAL, MODALIDADES, ESTADOS_SOLICITUD,
)


def _valida_modalidad(categoria: str, tipo: str):
    if categoria not in CATEGORIAS_PERSONAL:
        raise ValueError(f"categoria_personal inválida. Opciones: {', '.join(CATEGORIAS_PERSONAL)}")
    if tipo not in MODALIDADES[categoria]:
        raise ValueError(f"tipo_rol '{tipo}' no válido para '{categoria}'. Opciones: {', '.join(MODALIDADES[categoria])}")


# ─── Entrada ─────────────────────────────────────────────────────────────────

class RolCreate(BaseModel):
    categoria_personal: str
    tipo_rol: str
    departamento_id: uuid.UUID
    servicio_id: uuid.UUID
    mes: int
    anio: int

    @field_validator("mes")
    @classmethod
    def _v_mes(cls, v):
        if not 1 <= v <= 12:
            raise ValueError("El mes debe estar entre 1 y 12")
        return v

    @field_validator("anio")
    @classmethod
    def _v_anio(cls, v):
        if not 2000 <= v <= 2100:
            raise ValueError("El año no es válido")
        return v

    @model_validator(mode="after")
    def _v_combo(self):
        _valida_modalidad(self.categoria_personal, self.tipo_rol)
        return self


class RolUpdate(BaseModel):
    departamento_id: uuid.UUID | None = None
    servicio_id: uuid.UUID | None = None
    mes: int | None = None
    anio: int | None = None

    @field_validator("mes")
    @classmethod
    def _v_mes(cls, v):
        if v is not None and not 1 <= v <= 12:
            raise ValueError("El mes debe estar entre 1 y 12")
        return v


class PersonalRequest(BaseModel):
    empleado_ids: list[uuid.UUID]

    @field_validator("empleado_ids")
    @classmethod
    def _v(cls, v):
        if not v:
            raise ValueError("Debe seleccionar al menos un empleado")
        return list(dict.fromkeys(v))


class ActividadesRequest(BaseModel):
    actividad_ids: list[uuid.UUID]

    @field_validator("actividad_ids")
    @classmethod
    def _v(cls, v):
        if not v:
            raise ValueError("Debe seleccionar al menos una actividad")
        return list(dict.fromkeys(v))


class TurnoRequest(BaseModel):
    horario_guardia_id: uuid.UUID | None = None
    dias_semana: list[int] = []

    @field_validator("dias_semana")
    @classmethod
    def _v_dias(cls, v):
        for d in v:
            if not 0 <= d <= 6:
                raise ValueError("Los días deben estar entre 0 (domingo) y 6 (sábado)")
        return sorted(set(v))


class RechazoRequest(BaseModel):
    motivo: str

    @field_validator("motivo")
    @classmethod
    def _v(cls, v):
        v = (v or "").strip()
        if len(v) < 5:
            raise ValueError("El motivo del rechazo es obligatorio (mín. 5 caracteres)")
        return v


class SolicitudModificacionCreate(BaseModel):
    empleado_id: uuid.UUID
    motivo: str
    schedule_data: dict = {}

    @field_validator("motivo")
    @classmethod
    def _v(cls, v):
        v = (v or "").strip()
        if len(v) < 5:
            raise ValueError("El motivo es obligatorio (mín. 5 caracteres)")
        return v


# ─── Salida ──────────────────────────────────────────────────────────────────

class RolTurnoOut(BaseModel):
    id: uuid.UUID
    horario_guardia_id: uuid.UUID | None
    horario_nombre: str | None = None
    hora_inicio: str | None = None
    hora_fin: str | None = None
    dias_semana: list[int] = []


class RolActividadOut(BaseModel):
    id: uuid.UUID
    actividad_id: uuid.UUID
    actividad_nombre: str | None = None
    requiere_consultorio: bool = False
    turnos: list[RolTurnoOut] = []


class RolEmpleadoOut(BaseModel):
    id: uuid.UUID
    empleado_id: uuid.UUID
    empleado_nombre: str | None = None
    dni: str | None = None
    actividades: list[RolActividadOut] = []


class RolListItem(BaseModel):
    id: uuid.UUID
    categoria_personal: str
    tipo_rol: str
    departamento_id: uuid.UUID | None
    departamento_nombre: str | None = None
    servicio_id: uuid.UUID | None
    servicio_nombre: str | None = None
    mes: int
    anio: int
    status: str
    total_empleados: int = 0
    total_actividades: int = 0
    total_turnos: int = 0
    programacion_completa: bool = False
    created_by: str | None = None
    submitted_at: datetime | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    rejection_reason: str | None = None
    created_at: datetime


class RolDetail(RolListItem):
    empleados: list[RolEmpleadoOut] = []
    valorizacion_guardias: dict | None = None


class SolicitudModificacionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    rol_id: uuid.UUID
    role_type: str | None = None            # "categoria_personal/tipo_rol" del rol
    rol_periodo: str | None = None
    rol_servicio_nombre: str | None = None
    empleado_id: uuid.UUID | None
    empleado_nombre: str | None = None
    motivo: str
    schedule_data: dict = {}
    status: str
    requested_by: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    created_at: datetime

    @field_validator("status")
    @classmethod
    def _v_status(cls, v):
        return v if v in ESTADOS_SOLICITUD else "pendiente"
