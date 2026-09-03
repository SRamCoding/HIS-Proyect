import uuid
from datetime import datetime
from pydantic import BaseModel


class ExamenLaboratorioCreate(BaseModel):
    codigo: str | None = None
    nombre: str
    categoria: str | None = None
    tipo_muestra: str | None = None
    unidad_medida: str | None = None
    tiempo_resultado_horas: int | None = None
    precio: float = 0.0
    valores_referencia: str | None = None
    requiere_ayuno: bool = False
    is_active: bool = True


class ExamenLaboratorioUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    categoria: str | None = None
    tipo_muestra: str | None = None
    unidad_medida: str | None = None
    tiempo_resultado_horas: int | None = None
    precio: float | None = None
    valores_referencia: str | None = None
    requiere_ayuno: bool | None = None
    is_active: bool | None = None


class ExamenLaboratorioResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo: str | None
    nombre: str
    categoria: str | None
    tipo_muestra: str | None
    unidad_medida: str | None
    tiempo_resultado_horas: int | None
    precio: float
    valores_referencia: str | None
    requiere_ayuno: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}