import uuid
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


class GenerarFuaIn(Entrada):
    atencion_medica_id: uuid.UUID | None = None
    atencion_emergencia_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def un_solo_origen(self):
        if bool(self.atencion_medica_id) == bool(self.atencion_emergencia_id):
            raise ValueError("Indique exactamente un origen: atencion_medica_id o atencion_emergencia_id")
        return self


class CambiarEstadoFuaIn(Entrada):
    estado: Literal["enviado", "observado", "pagado", "anulado"]
    observaciones: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def observacion_requerida_si_observado_o_anulado(self):
        if self.estado in ("observado", "anulado") and not self.observaciones:
            raise ValueError("Indique el motivo al marcar el FUA como observado o anulado")
        return self
