import uuid
from datetime import date
from pydantic import BaseModel, model_validator

_ACCESOS = {"FAV", "CATETER_VENOSO_CENTRAL", "INJERTO"}
_TURNOS = {"MAÑANA", "TARDE", "NOCHE"}
_ESTADOS_PACIENTE = {"activo", "transferido", "trasplantado", "fallecido", "alta"}
_ESTADOS_SESION = {"programada", "en_curso", "completada", "suspendida", "no_asistio"}


class PacienteCreateIn(BaseModel):
    patient_id: uuid.UUID
    diagnostico_id: uuid.UUID | None = None
    medico_nefrologo_id: uuid.UUID | None = None
    fecha_ingreso_programa: date | None = None
    acceso_vascular_tipo: str
    fecha_creacion_acceso: date | None = None
    peso_seco_kg: float
    turno_habitual: str = "MAÑANA"
    frecuencia_semanal: int = 3
    observaciones: str | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.acceso_vascular_tipo not in _ACCESOS:
            raise ValueError("acceso_vascular_tipo debe ser FAV, CATETER_VENOSO_CENTRAL o INJERTO")
        if self.turno_habitual not in _TURNOS:
            raise ValueError("turno_habitual debe ser MAÑANA, TARDE o NOCHE")
        if self.peso_seco_kg <= 0:
            raise ValueError("peso_seco_kg debe ser mayor a 0")
        if self.frecuencia_semanal < 1 or self.frecuencia_semanal > 7:
            raise ValueError("frecuencia_semanal debe estar entre 1 y 7")
        return self


class PacienteUpdateIn(BaseModel):
    diagnostico_id: uuid.UUID | None = None
    medico_nefrologo_id: uuid.UUID | None = None
    acceso_vascular_tipo: str | None = None
    fecha_creacion_acceso: date | None = None
    peso_seco_kg: float | None = None
    turno_habitual: str | None = None
    frecuencia_semanal: int | None = None
    observaciones: str | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.acceso_vascular_tipo is not None and self.acceso_vascular_tipo not in _ACCESOS:
            raise ValueError("acceso_vascular_tipo debe ser FAV, CATETER_VENOSO_CENTRAL o INJERTO")
        if self.turno_habitual is not None and self.turno_habitual not in _TURNOS:
            raise ValueError("turno_habitual debe ser MAÑANA, TARDE o NOCHE")
        return self


class PacienteEstadoIn(BaseModel):
    estado: str
    fecha_estado: date | None = None
    observaciones: str | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.estado not in _ESTADOS_PACIENTE:
            raise ValueError(f"estado debe ser uno de: {', '.join(sorted(_ESTADOS_PACIENTE))}")
        return self


class SesionCreateIn(BaseModel):
    paciente_hemodialisis_id: uuid.UUID
    fecha: date | None = None
    turno: str
    numero_maquina: str | None = None
    hora_inicio: str | None = None
    hora_fin: str | None = None
    peso_pre_kg: float | None = None
    peso_post_kg: float | None = None
    ultrafiltracion_litros: float | None = None
    presion_pre_sistolica: int | None = None
    presion_pre_diastolica: int | None = None
    presion_post_sistolica: int | None = None
    presion_post_diastolica: int | None = None
    acceso_vascular_utilizado: str | None = None
    heparinizacion: bool = True
    complicaciones: str | None = None
    observaciones: str | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.turno not in _TURNOS:
            raise ValueError("turno debe ser MAÑANA, TARDE o NOCHE")
        if self.acceso_vascular_utilizado is not None and self.acceso_vascular_utilizado not in _ACCESOS:
            raise ValueError("acceso_vascular_utilizado debe ser FAV, CATETER_VENOSO_CENTRAL o INJERTO")
        return self


class SesionEstadoIn(BaseModel):
    estado: str
    hora_fin: str | None = None
    peso_post_kg: float | None = None
    complicaciones: str | None = None
    observaciones: str | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.estado not in _ESTADOS_SESION:
            raise ValueError(f"estado debe ser uno de: {', '.join(sorted(_ESTADOS_SESION))}")
        return self
