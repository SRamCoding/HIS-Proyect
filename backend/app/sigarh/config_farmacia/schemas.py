import uuid
from datetime import datetime
from pydantic import BaseModel


# ─── Almacén ──────────────────────────────────────────────────────────────────

class AlmacenCreate(BaseModel):
    codigo: str
    nombre: str
    tipo: str = "farmacia"
    fuente_financiamiento: str | None = None
    ubicacion_fisica: str | None = None
    despacha_recetas: bool = True
    is_active: bool = True


class AlmacenUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    tipo: str | None = None
    fuente_financiamiento: str | None = None
    ubicacion_fisica: str | None = None
    despacha_recetas: bool | None = None
    is_active: bool | None = None


class AlmacenResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo: str
    nombre: str
    tipo: str
    fuente_financiamiento: str | None
    ubicacion_fisica: str | None
    despacha_recetas: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Medicamento ──────────────────────────────────────────────────────────────

class MedicamentoCreate(BaseModel):
    codigo_interno: str
    nombre_comercial: str
    dci: str | None = None
    nombre_generico: str | None = None
    presentacion: str | None = None
    unidad: str | None = None
    concentracion: str | None = None
    forma_farmaceutica: str | None = None
    via_administracion: str | None = None
    codigo_atc: str | None = None
    numero_registro_sanitario: str | None = None
    laboratorio_fabricante: str | None = None
    pais_origen: str | None = None
    condicion_venta: str | None = None
    tipo_producto_id: uuid.UUID | None = None
    precio_referencia: float | None = None
    requiere_receta: bool = False
    controlado: bool = False
    fiscalizado_digemid: bool = False
    reporte_sismed: bool = False
    stock_minimo_alerta: int = 10
    requiere_cadena_frio: bool = False
    is_active: bool = True


class MedicamentoUpdate(BaseModel):
    codigo_interno: str | None = None
    nombre_comercial: str | None = None
    dci: str | None = None
    nombre_generico: str | None = None
    presentacion: str | None = None
    unidad: str | None = None
    concentracion: str | None = None
    forma_farmaceutica: str | None = None
    via_administracion: str | None = None
    codigo_atc: str | None = None
    numero_registro_sanitario: str | None = None
    laboratorio_fabricante: str | None = None
    pais_origen: str | None = None
    condicion_venta: str | None = None
    tipo_producto_id: uuid.UUID | None = None
    precio_referencia: float | None = None
    requiere_receta: bool | None = None
    controlado: bool | None = None
    fiscalizado_digemid: bool | None = None
    reporte_sismed: bool | None = None
    stock_minimo_alerta: int | None = None
    requiere_cadena_frio: bool | None = None
    is_active: bool | None = None


class MedicamentoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo_interno: str
    nombre_comercial: str
    dci: str | None
    nombre_generico: str | None
    presentacion: str | None
    unidad: str | None
    concentracion: str | None
    forma_farmaceutica: str | None
    via_administracion: str | None
    codigo_atc: str | None
    numero_registro_sanitario: str | None
    laboratorio_fabricante: str | None
    pais_origen: str | None
    condicion_venta: str | None
    tipo_producto_id: uuid.UUID | None
    precio_referencia: float | None
    requiere_receta: bool
    controlado: bool
    fiscalizado_digemid: bool
    reporte_sismed: bool
    stock_minimo_alerta: int
    requiere_cadena_frio: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MedicamentoListItem(BaseModel):
    id: uuid.UUID
    codigo_interno: str
    nombre_comercial: str
    nombre_generico: str | None
    presentacion: str | None
    unidad: str | None
    stock_minimo_alerta: int
    is_active: bool

    model_config = {"from_attributes": True}