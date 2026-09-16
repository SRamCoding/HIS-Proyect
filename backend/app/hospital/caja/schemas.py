import uuid
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

FormaPago = Literal["EFECTIVO", "TARJETA", "TRANSFERENCIA", "SEGURO"]
Origen = Literal["CONSULTA_EXTERNA", "EMERGENCIA", "LABORATORIO", "IMAGEN", "FARMACIA"]


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def limpiar(cls, data):
        if isinstance(data, dict):
            return {k: (v.strip() or None) if isinstance(v, str) else v for k, v in data.items()}
        return data


class SesionAbrir(Entrada):
    caja_id: uuid.UUID
    monto_apertura: Decimal = Field(ge=0, le=999999, decimal_places=4)
    observaciones_apertura: str | None = Field(default=None, max_length=2000)


class SesionCerrar(Entrada):
    monto_cierre_declarado: Decimal = Field(ge=0, le=999999, decimal_places=4)
    observaciones_cierre: str | None = Field(default=None, max_length=2000)


class ItemEntrada(Entrada):
    origen: Origen
    origen_id: uuid.UUID
    descripcion: str = Field(min_length=1, max_length=255)
    monto: Decimal = Field(gt=0, le=999999, decimal_places=4)


class CobroCreate(Entrada):
    numero_cuenta: str = Field(min_length=1, max_length=50)
    patient_id: uuid.UUID | None = None
    forma_pago: FormaPago
    fuente_financiamiento: str | None = Field(default=None, max_length=100)
    items: list[ItemEntrada] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def unicos(self):
        if len({(i.origen, i.origen_id) for i in self.items}) != len(self.items):
            raise ValueError("No repita el mismo cargo en el cobro")
        return self


class Anulacion(Entrada):
    motivo: str = Field(min_length=1, max_length=2000)
