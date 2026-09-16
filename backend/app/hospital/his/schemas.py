import uuid
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def limpiar(cls, data):
        if isinstance(data, dict):
            return {k: (v.strip() or None) if isinstance(v, str) else v for k, v in data.items()}
        return data


class CrearEnvioIn(Entrada):
    periodo: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="Formato AAAA-MM")
    fecha_desde: date
    fecha_hasta: date
    observaciones: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def rango_valido(self):
        if self.fecha_hasta < self.fecha_desde:
            raise ValueError("La fecha hasta no puede ser anterior a la fecha desde")
        return self


class CerrarEnvioIn(Entrada):
    observaciones: str | None = Field(default=None, max_length=2000)
