import uuid
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def limpiar(cls, data):
        if isinstance(data, dict):
            return {k: (v.strip() or None) if isinstance(v, str) else v for k, v in data.items()}
        return data


class PisoOut(BaseModel):
    id: uuid.UUID
    nombre: str
    model_config = {"from_attributes": True}


class CamaConPacienteOut(BaseModel):
    id: uuid.UUID
    codigo: str
    nombre: str
    tipo_cama: str | None
    estado: str
    sala_nombre: str | None
    servicio_nombre: str | None
    paciente_nombre: str | None = None
    paciente_dni: str | None = None
    fecha_ingreso: datetime | None = None
    numero_hospitalizacion: str | None = None
    hospitalizacion_cita_id: uuid.UUID | None = None


class AdmisionDesdeEmergencia(Entrada):
    destino_id: uuid.UUID
    cama_id: uuid.UUID
    especialidad_ingreso_id: uuid.UUID | None = None
    diagnostico_ingreso_id: uuid.UUID | None = None


class NotaEvolucionCreate(Entrada):
    tipo: Literal["MEDICA", "ENFERMERIA"]
    pulso: int | None = Field(default=None, ge=0, le=300)
    temperatura: float | None = Field(default=None, ge=25, le=45)
    presion_sistolica: int | None = Field(default=None, ge=0, le=300)
    presion_diastolica: int | None = Field(default=None, ge=0, le=200)
    frecuencia_cardiaca: int | None = Field(default=None, ge=0, le=300)
    frecuencia_respiratoria: int | None = Field(default=None, ge=0, le=100)
    saturacion_o2: float | None = Field(default=None, ge=0, le=100)
    contenido: str = Field(min_length=1, max_length=8000)
    plan_indicaciones: str | None = Field(default=None, max_length=4000)


class InterconsultaHospCreate(Entrada):
    especialidad_destino_id: uuid.UUID
    diagnostico_id: uuid.UUID | None = None
    motivo: str = Field(min_length=1, max_length=4000)
    urgente: bool = False


class AdmitirInterconsultaEmergencia(Entrada):
    destino_id: uuid.UUID
    especialidad_destino_id: uuid.UUID
    diagnostico_id: uuid.UUID | None = None
    motivo: str = Field(min_length=1, max_length=4000)
    urgente: bool = False


class ConsentimientoCreate(Entrada):
    procedimiento: str = Field(min_length=1, max_length=255)
    riesgos_beneficios: str = Field(min_length=1, max_length=4000)
    firmante_nombre: str = Field(min_length=1, max_length=255)
    firmante_documento: str = Field(min_length=1, max_length=20)
    relacion_firmante: Literal["PACIENTE", "REPRESENTANTE"] = "PACIENTE"
    testigo_nombre: str | None = Field(default=None, max_length=255)
    fecha: date


class ConsentimientoRevocar(Entrada):
    motivo_revocacion: str = Field(min_length=1, max_length=2000)


class AltaHospitalizacion(Entrada):
    resumen_alta: str | None = Field(default=None, max_length=4000)
