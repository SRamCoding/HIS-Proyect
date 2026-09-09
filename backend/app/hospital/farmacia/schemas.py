import uuid
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, model_validator

class MovimientoItemIn(BaseModel):
    medicamento_id: uuid.UUID
    lote_id: uuid.UUID | None = None
    numero_lote: str = Field(min_length=1, max_length=80)
    fecha_vencimiento: date
    registro_sanitario: str | None = None
    cantidad: Decimal = Field(gt=0)
    precio_unitario: Decimal = Field(default=0, ge=0)
    @model_validator(mode="after")
    def validar_vencimiento(self):
        if self.fecha_vencimiento < date.today():
            raise ValueError("no se puede ingresar o movilizar un lote vencido")
        return self

class MovimientoIn(BaseModel):
    tipo: str; ambito: str; concepto: str = Field(min_length=1, max_length=100)
    almacen_origen_id: uuid.UUID | None = None; almacen_destino_id: uuid.UUID | None = None
    patient_id: uuid.UUID | None = None; numero_cuenta: str | None = None; fuente_financiamiento: str | None = None
    tipo_documento: str | None = None; numero_documento: str | None = None; tipo_documento_origen: str | None = None
    numero_documento_origen: str | None = None; fecha_documento_origen: date | None = None; tipo_proceso: str | None = None
    numero_proceso: str | None = None; tipo_compra: str | None = None; proveedor_id: uuid.UUID | None = None
    observaciones: str | None = None; confirmar: bool = True
    items: list[MovimientoItemIn] = Field(min_length=1)
    @model_validator(mode="after")
    def validar(self):
        self.tipo, self.ambito = self.tipo.upper(), self.ambito.upper()
        if self.tipo not in {"INGRESO", "SALIDA"}: raise ValueError("tipo debe ser INGRESO o SALIDA")
        if self.ambito not in {"ALMACEN", "FARMACIA"}: raise ValueError("ámbito inválido")
        if self.tipo == "INGRESO" and not self.almacen_destino_id: raise ValueError("almacén destino requerido")
        if self.tipo == "SALIDA" and not self.almacen_origen_id: raise ValueError("almacén origen requerido")
        if self.almacen_origen_id and self.almacen_destino_id and self.almacen_origen_id == self.almacen_destino_id:
            raise ValueError("el almacén de origen y destino deben ser diferentes")
        return self

class DispensarItem(BaseModel):
    receta_item_id: uuid.UUID; cantidad: Decimal = Field(gt=0)
class DispensarIn(BaseModel):
    almacen_id: uuid.UUID; items: list[DispensarItem] = Field(min_length=1); observaciones: str | None = None
class FarmacotecniaIn(BaseModel):
    receta_id: uuid.UUID | None = None; tipo_requerimiento: str; formula: str
    cantidad: Decimal = Field(default=1, gt=0); unidad: str = "UNIDAD"; via_administracion: str | None = None
    estabilidad_horas: int | None = Field(default=None, ge=0); condiciones_conservacion: str | None = None; observaciones: str | None = None
class FarmacotecniaEstado(BaseModel):
    estado: str; control_calidad: dict = {}; observaciones: str | None = None
class AnulacionIn(BaseModel):
    motivo: str = Field(min_length=5, max_length=1000)
