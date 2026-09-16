import uuid
from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

TipoServicio = Literal["CONSULTA_EXTERNA", "APOYO_DIAGNOSTICO", "HOSPITALIZACION", "EMERGENCIA"]


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def limpiar(cls, data):
        if isinstance(data, dict):
            return {k: (v.strip() or None) if isinstance(v, str) else v for k, v in data.items()}
        return data


class OrdenCreate(Entrada):
    patient_id: uuid.UUID
    tipo_servicio: TipoServicio
    emergencia_id: uuid.UUID | None = None
    servicio_id: uuid.UUID
    especialidad_id: uuid.UUID | None = None
    medico_id: uuid.UUID
    numero_cuenta: str | None = Field(default=None, max_length=50)
    fuente_financiamiento: str = Field(min_length=1, max_length=100)
    indicacion_clinica: str | None = Field(default=None, max_length=4000)
    examen_ids: list[uuid.UUID] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def unicos(self):
        if len(set(self.examen_ids)) != len(self.examen_ids):
            raise ValueError("No repita estudios en la orden")
        if self.tipo_servicio == "EMERGENCIA" and not self.emergencia_id:
            raise ValueError("Seleccione la admisión de emergencia asociada")
        if self.tipo_servicio != "EMERGENCIA" and self.emergencia_id:
            raise ValueError("La admisión de emergencia solo corresponde al tipo EMERGENCIA")
        return self


class ItemEntrada(Entrada):
    examen_id: uuid.UUID
    cantidad: int = Field(default=1, ge=1, le=1000)
    precio: Decimal | None = Field(default=None, ge=0, le=999999, decimal_places=4)


class MovimientoCreate(Entrada):
    orden_id: uuid.UUID
    fecha: date
    tecnico_id: uuid.UUID
    medico_id: uuid.UUID | None = None
    agendamiento_por: Literal["PACIENTE", "ORDEN"] = "PACIENTE"
    registrar_por: Literal["ORDEN", "CUENTA", "HISTORIA"] = "ORDEN"
    cuenta_nueva: bool = False
    comprobante: str | None = Field(default=None, max_length=100)
    observaciones: str | None = Field(default=None, max_length=4000)
    items: list[ItemEntrada] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def unicos(self):
        if len({i.examen_id for i in self.items}) != len(self.items):
            raise ValueError("No repita estudios")
        return self


class MovimientoUpdate(MovimientoCreate):
    version: int = Field(ge=1)


class Accion(Entrada):
    version: int = Field(ge=1)
    motivo: str | None = Field(default=None, max_length=2000)


class InformeItem(Entrada):
    item_id: uuid.UUID
    tecnica: str | None = Field(default=None, max_length=4000)
    hallazgos: str = Field(min_length=1, max_length=8000)
    impresion_diagnostica: str = Field(min_length=1, max_length=4000)


class InformeEntrada(Entrada):
    version: int = Field(ge=1)
    items: list[InformeItem] = Field(min_length=1, max_length=100)
