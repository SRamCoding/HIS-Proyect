import uuid
from datetime import date
from pydantic import BaseModel, Field, model_validator

_TURNOS = {"MAÑANA", "TARDE", "NOCHE"}
_ESTADOS_SESION_CIERRE = {"atendida", "cancelada", "no_asistio"}


class ProgramaCreateIn(BaseModel):
    nombre: str
    descripcion: str | None = None
    duracion_sesion_minutos: int = 30

    @model_validator(mode="after")
    def _v(self):
        if self.duracion_sesion_minutos < 5:
            raise ValueError("duracion_sesion_minutos debe ser al menos 5")
        return self


class ProgramaUpdateIn(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    duracion_sesion_minutos: int | None = None
    is_active: bool | None = None


class TecnologoProgramaIn(BaseModel):
    empleado_id: uuid.UUID


class ProgramacionMFCreateIn(BaseModel):
    programa_id: uuid.UUID
    tecnologo_id: uuid.UUID
    fecha: date
    turno: str
    hora_inicio: str
    hora_fin: str
    tiempo_sesion_minutos: int | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.turno not in _TURNOS:
            raise ValueError("turno debe ser MAÑANA, TARDE o NOCHE")
        return self


class BloquearProgramacionIn(BaseModel):
    motivo: str


class SesionCreateIn(BaseModel):
    programacion_mf_id: uuid.UUID
    patient_id: uuid.UUID
    hora_inicio: str
    hora_fin: str


class SesionEjecutarIn(BaseModel):
    estado: str
    escala_dolor_eva: int | None = None
    actividades_realizadas: str | None = None
    evolucion: str | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.estado not in _ESTADOS_SESION_CIERRE:
            raise ValueError(f"estado debe ser uno de: {', '.join(sorted(_ESTADOS_SESION_CIERRE))}")
        if self.escala_dolor_eva is not None and not (0 <= self.escala_dolor_eva <= 10):
            raise ValueError("escala_dolor_eva debe estar entre 0 y 10")
        return self


class SesionesReprogramarBloqueIn(BaseModel):
    sesion_ids: list[uuid.UUID] = Field(min_length=1)
    programacion_mf_id: uuid.UUID
    mensaje: str | None = Field(default=None, max_length=500)
