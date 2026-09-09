import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _limpiar(v):
    if v is None:
        return None
    v = str(v).strip()
    return v or None


def _max(v, n, campo):
    v = _limpiar(v)
    if v is not None and len(v) > n:
        raise ValueError(f"{campo} no debe superar {n} caracteres")
    return v


TIPOS_ALMACEN = {"farmacia", "almacen_central", "laboratorio", "dispensacion"}
FUENTES_FINANCIAMIENTO = {"sismed", "donaciones", "mixto"}
CONDICIONES_VENTA = {"sin_receta", "receta_simple", "receta_retenida", "control_medico"}
CONDICIONES_CON_RECETA = {"receta_simple", "receta_retenida", "control_medico"}
FORMAS_FARMACEUTICAS = {
    "tableta", "capsula", "ampolla", "frasco_ampolla", "jarabe", "suspension", "solucion",
    "crema", "pomada", "gel", "parche", "supositorio", "colirio", "inhalador",
    "polvo_reconstituir", "otro",
}
VIAS_ADMINISTRACION = {
    "oral", "intravenosa", "intramuscular", "subcutanea", "topica", "oftalmica",
    "inhalada", "rectal", "sublingual", "nasal", "otro",
}


# ─── Almacén ──────────────────────────────────────────────────────────────────

class AlmacenCreate(BaseModel):
    codigo: str
    nombre: str
    tipo: str = "farmacia"
    fuente_financiamiento: str | None = None
    ubicacion_fisica: str | None = None
    despacha_recetas: bool = True
    is_active: bool = True

    @field_validator("codigo")
    @classmethod
    def _v_codigo(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El código del almacén es requerido")
        if len(v) > 20:
            raise ValueError("El código no debe superar 20 caracteres")
        return v.upper()

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El nombre es requerido")
        if len(v) > 100:
            raise ValueError("El nombre no debe superar 100 caracteres")
        return v

    @field_validator("tipo")
    @classmethod
    def _v_tipo(cls, v):
        v = (_limpiar(v) or "farmacia").lower()
        if v not in TIPOS_ALMACEN:
            raise ValueError("Tipo inválido. Opciones: farmacia, almacen_central, laboratorio, dispensacion")
        return v

    @field_validator("fuente_financiamiento")
    @classmethod
    def _v_fuente(cls, v):
        v = _limpiar(v)
        if v is not None and v.lower() not in FUENTES_FINANCIAMIENTO:
            raise ValueError("Fuente inválida. Opciones: sismed, donaciones, mixto")
        return v.lower() if v else None


class AlmacenUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    tipo: str | None = None
    fuente_financiamiento: str | None = None
    ubicacion_fisica: str | None = None
    despacha_recetas: bool | None = None
    is_active: bool | None = None

    @field_validator("codigo")
    @classmethod
    def _v_codigo(cls, v):
        v = _max(v, 20, "El código")
        return v.upper() if v else None

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        return _max(v, 100, "El nombre")

    @field_validator("tipo")
    @classmethod
    def _v_tipo(cls, v):
        if v is None:
            return None
        v = str(v).strip().lower()
        if v not in TIPOS_ALMACEN:
            raise ValueError("Tipo inválido")
        return v

    @field_validator("fuente_financiamiento")
    @classmethod
    def _v_fuente(cls, v):
        v = _limpiar(v)
        if v is not None and v.lower() not in FUENTES_FINANCIAMIENTO:
            raise ValueError("Fuente inválida")
        return v.lower() if v else None


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

class _MedicamentoCampos(BaseModel):
    dci: str | None = None
    presentacion: str | None = None
    concentracion: str | None = None
    forma_farmaceutica: str | None = None
    via_administracion: str | None = None
    codigo_atc: str | None = None
    numero_registro_sanitario: str | None = None
    laboratorio_fabricante: str | None = None
    pais_origen: str | None = None
    tipo_producto_id: uuid.UUID | None = None
    precio_referencia: float | None = None
    precio_referencia_sismed: float | None = None
    requiere_receta: bool | None = None
    controlado: bool | None = None
    fiscalizado_digemid: bool | None = None
    reporte_sismed: bool | None = None
    requiere_cadena_frio: bool | None = None
    temperatura_min: int | None = None
    temperatura_max: int | None = None

    @field_validator("dci")
    @classmethod
    def _v_dci(cls, v): return _max(v, 150, "La DCI")

    @field_validator("presentacion")
    @classmethod
    def _v_pres(cls, v): return _max(v, 100, "La presentación")

    @field_validator("concentracion")
    @classmethod
    def _v_conc(cls, v): return _max(v, 100, "La concentración")

    @field_validator("codigo_atc")
    @classmethod
    def _v_atc(cls, v): return _max(v, 10, "El código ATC")

    @field_validator("numero_registro_sanitario")
    @classmethod
    def _v_rs(cls, v): return _max(v, 50, "El N° de registro sanitario")

    @field_validator("laboratorio_fabricante")
    @classmethod
    def _v_lab(cls, v): return _max(v, 150, "El laboratorio")

    @field_validator("pais_origen")
    @classmethod
    def _v_pais(cls, v): return _max(v, 100, "El país de origen")

    @field_validator("forma_farmaceutica")
    @classmethod
    def _v_forma(cls, v):
        v = _limpiar(v)
        if v is not None and v.lower() not in FORMAS_FARMACEUTICAS:
            raise ValueError("Forma farmacéutica inválida")
        return v.lower() if v else None

    @field_validator("via_administracion")
    @classmethod
    def _v_via(cls, v):
        v = _limpiar(v)
        if v is not None and v.lower() not in VIAS_ADMINISTRACION:
            raise ValueError("Vía de administración inválida")
        return v.lower() if v else None

    @field_validator("precio_referencia", "precio_referencia_sismed")
    @classmethod
    def _v_precio(cls, v):
        if v is not None and v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v

    @model_validator(mode="after")
    def _v_temperaturas(self):
        if self.temperatura_min is not None and self.temperatura_max is not None:
            if self.temperatura_min > self.temperatura_max:
                raise ValueError("La temperatura mínima no puede ser mayor que la máxima")
        return self


class MedicamentoCreate(_MedicamentoCampos):
    codigo_interno: str
    nombre_comercial: str
    nombre_generico: str
    unidad: str = "unidad"
    condicion_venta: str = "sin_receta"
    stock_minimo_alerta: int = 10
    requiere_receta: bool = False
    controlado: bool = False
    fiscalizado_digemid: bool = False
    reporte_sismed: bool = False
    requiere_cadena_frio: bool = False
    is_active: bool = True

    @field_validator("codigo_interno")
    @classmethod
    def _v_cod(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El código interno / DIGEMID es requerido")
        if len(v) > 50:
            raise ValueError("El código no debe superar 50 caracteres")
        return v

    @field_validator("nombre_comercial")
    @classmethod
    def _v_nc(cls, v):
        v = _max(v, 255, "El nombre comercial")
        if v is None:
            raise ValueError("El nombre comercial es requerido")
        return v

    @field_validator("nombre_generico")
    @classmethod
    def _v_ng(cls, v):
        v = _max(v, 255, "El nombre genérico")
        if v is None:
            raise ValueError("El nombre genérico es requerido")
        return v

    @field_validator("unidad")
    @classmethod
    def _v_unidad(cls, v):
        v = _limpiar(v) or "unidad"
        if len(v) > 20:
            raise ValueError("La unidad no debe superar 20 caracteres")
        return v

    @field_validator("condicion_venta")
    @classmethod
    def _v_cv(cls, v):
        v = (_limpiar(v) or "sin_receta").lower()
        if v not in CONDICIONES_VENTA:
            raise ValueError("Condición de venta inválida. Opciones: sin_receta, receta_simple, receta_retenida, control_medico")
        return v

    @field_validator("stock_minimo_alerta")
    @classmethod
    def _v_stock(cls, v):
        if v is None or v < 1:
            raise ValueError("El stock mínimo de alerta debe ser 1 o mayor")
        return v

    @model_validator(mode="after")
    def _v_sync_receta(self):
        # Coherencia: si la condición de venta exige receta, marcar requiere_receta.
        if self.condicion_venta in CONDICIONES_CON_RECETA:
            self.requiere_receta = True
        return self


class MedicamentoUpdate(_MedicamentoCampos):
    codigo_interno: str | None = None
    nombre_comercial: str | None = None
    nombre_generico: str | None = None
    unidad: str | None = None
    condicion_venta: str | None = None
    stock_minimo_alerta: int | None = None
    is_active: bool | None = None

    @field_validator("codigo_interno")
    @classmethod
    def _v_cod(cls, v): return _max(v, 50, "El código interno")

    @field_validator("nombre_comercial")
    @classmethod
    def _v_nc(cls, v): return _max(v, 255, "El nombre comercial")

    @field_validator("nombre_generico")
    @classmethod
    def _v_ng(cls, v): return _max(v, 255, "El nombre genérico")

    @field_validator("unidad")
    @classmethod
    def _v_unidad(cls, v): return _max(v, 20, "La unidad")

    @field_validator("condicion_venta")
    @classmethod
    def _v_cv(cls, v):
        if v is None:
            return None
        v = str(v).strip().lower()
        if v not in CONDICIONES_VENTA:
            raise ValueError("Condición de venta inválida")
        return v

    @field_validator("stock_minimo_alerta")
    @classmethod
    def _v_stock(cls, v):
        if v is not None and v < 1:
            raise ValueError("El stock mínimo de alerta debe ser 1 o mayor")
        return v

    @model_validator(mode="after")
    def _v_sync_receta(self):
        if self.condicion_venta in CONDICIONES_CON_RECETA:
            self.requiere_receta = True
        return self


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
    tipo_producto_nombre: str | None = None
    precio_referencia: float | None
    precio_referencia_sismed: float | None
    requiere_receta: bool
    controlado: bool
    fiscalizado_digemid: bool
    reporte_sismed: bool
    stock_minimo_alerta: int
    requiere_cadena_frio: bool
    temperatura_min: int | None
    temperatura_max: int | None
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
    concentracion: str | None
    forma_farmaceutica: str | None
    condicion_venta: str | None
    tipo_producto_nombre: str | None = None
    controlado: bool
    fiscalizado_digemid: bool
    reporte_sismed: bool
    requiere_cadena_frio: bool
    stock_minimo_alerta: int
    is_active: bool

    model_config = {"from_attributes": True}


class ProveedorCreate(BaseModel):
    ruc: str
    razon_social: str
    direccion: str | None = None
    telefono: str | None = None
    email: str | None = None
    registro_digemid: str | None = None
    is_active: bool = True


class CatalogoFarmaciaCreate(BaseModel):
    categoria: str
    codigo: str
    nombre: str
    is_active: bool = True
