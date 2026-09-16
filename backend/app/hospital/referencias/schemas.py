import uuid
from datetime import date
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


class AdmisionDesdeEmergencia(Entrada):
    destino_id: uuid.UUID
    codigo_renipress_destino: str | None = Field(default=None, max_length=20)
    nombre_ipress_destino: str | None = Field(default=None, max_length=255)
    tenant_destino_id: uuid.UUID | None = None
    especialidad_destino: str | None = Field(default=None, max_length=150)
    diagnostico_id: uuid.UUID | None = None
    motivo: str = Field(min_length=1, max_length=4000)

    @model_validator(mode="after")
    def destino_valido(self):
        if not self.codigo_renipress_destino and not self.nombre_ipress_destino and not self.tenant_destino_id:
            raise ValueError("Indique el establecimiento destino (IPRESS externo u hospital del sistema)")
        return self


class ResolucionEntrada(Entrada):
    estado: Literal["aceptada", "rechazada"]
    observacion_resolucion: str | None = Field(default=None, max_length=2000)


class ContrarreferenciaEntrada(Entrada):
    fecha_contrarreferencia: date
    profesional_receptor: str = Field(min_length=1, max_length=255)
    diagnostico_contrarreferencia_id: uuid.UUID | None = None
    resumen_contrarreferencia: str = Field(min_length=1, max_length=4000)
