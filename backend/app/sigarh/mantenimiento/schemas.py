import re
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, create_model, field_serializer, field_validator, model_validator

Nombre = Annotated[str, Field(min_length=1, max_length=255)]
Codigo = Annotated[str, Field(min_length=1, max_length=50)]
Hora = Annotated[str, Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")]
PERMISOS = {"aprobar_roles_turno", "administrar_mantenimiento", "administrar_seguridad"}


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("codigo", mode="before", check_fields=False)
    @classmethod
    def codigo_normalizado(cls, value):
        return value.strip().upper() or None if isinstance(value, str) else value


class CatalogoBase(Entrada):
    nombre: Nombre
    codigo: Codigo | None = None
    descripcion: str | None = None
    is_active: bool = True


class CatalogoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    codigo: str | None = None
    descripcion: str | None = None
    is_active: bool
    created_at: datetime


class DepartamentoCreate(CatalogoBase):
    pass

class DepartamentoResponse(CatalogoResponse):
    pass

class ServicioCreate(CatalogoBase):
    departamento_id: uuid.UUID | None = None
    piso_id: uuid.UUID | None = None
    tiempo_atencion_min: Annotated[int, Field(ge=5, le=120)] | None = None

class ServicioResponse(CatalogoResponse):
    departamento_id: uuid.UUID | None = None
    departamento_nombre: str | None = None
    piso_id: uuid.UUID | None = None
    piso_nombre: str | None = None
    tiempo_atencion_min: int | None = None

class TipoTrabajadorCreate(CatalogoBase):
    pass

class TipoTrabajadorResponse(CatalogoResponse):
    pass

class TipoGuardiaCreate(CatalogoBase):
    horas: Annotated[int, Field(ge=1, le=24)] | None = None
    es_laborable: bool = True
    requiere_epp: bool = False

class TipoGuardiaResponse(CatalogoResponse):
    horas: int | None = None
    es_laborable: bool = True
    requiere_epp: bool = False

class NivelRemunerativoCreate(CatalogoBase):
    pass

class NivelRemunerativoResponse(CatalogoResponse):
    pass


def duracion_minutos(inicio: str, fin: str) -> int:
    def minutos(hora):
        h, m = map(int, hora.split(":"))
        return h * 60 + m
    resultado = (minutos(fin) - minutos(inicio)) % 1440
    if not resultado:
        raise ValueError("Inicio y fin deben ser distintos; divida las jornadas de 24 horas")
    return resultado


class HorarioGuardiaCreate(Entrada):
    nombre: Nombre
    hora_inicio: Hora
    hora_fin: Hora
    # Compatibilidad de lectura/escritura; la fuente exacta son los minutos.
    horas_totales: Annotated[float, Field(gt=0, lt=24, allow_inf_nan=False)] | None = None
    duracion_minutos: Annotated[int, Field(ge=1, le=1439)] | None = None
    tipo_guardia_id: uuid.UUID | None = None
    is_active: bool = True

    @model_validator(mode="after")
    def validar_duracion(self):
        minutos = duracion_minutos(self.hora_inicio, self.hora_fin)
        if self.duracion_minutos is not None and self.duracion_minutos != minutos:
            raise ValueError("La duración no coincide con el horario")
        if self.horas_totales is not None and abs(self.horas_totales * 60 - minutos) > 0.001:
            raise ValueError("Las horas totales no coinciden con inicio y fin")
        self.duracion_minutos = minutos
        self.horas_totales = minutos / 60
        return self

class HorarioGuardiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    hora_inicio: str
    hora_fin: str
    horas_totales: float | None = None
    duracion_minutos: int | None = None
    tipo_guardia_id: uuid.UUID | None = None
    tipo_guardia_nombre: str | None = None
    is_active: bool
    created_at: datetime

class TipoGrupoOcupacionalCreate(CatalogoBase):
    pass

class TipoGrupoOcupacionalResponse(CatalogoResponse):
    pass

class GrupoOcupacionalCreate(CatalogoBase):
    tipo_grupo_id: uuid.UUID | None = None

class GrupoOcupacionalResponse(CatalogoResponse):
    tipo_grupo_id: uuid.UUID | None = None

class TipoActividadCreate(Entrada):
    nombre: Nombre
    codigo: Codigo | None = None
    is_active: bool = True

class TipoActividadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    codigo: str | None = None
    is_active: bool
    created_at: datetime

class ActividadCreate(TipoActividadCreate):
    tipo_actividad_id: uuid.UUID | None = None
    requiere_consultorio: bool = False
    genera_agenda: bool = False

class ActividadResponse(TipoActividadResponse):
    tipo_actividad_id: uuid.UUID | None = None
    requiere_consultorio: bool = False
    genera_agenda: bool = False

class GuardiaValorizadaCreate(Entrada):
    tipo_guardia_id: uuid.UUID
    grupo_ocupacional_id: uuid.UUID | None = None
    nivel_remunerativo_id: uuid.UUID | None = None
    valor: Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2, allow_inf_nan=False)]
    moneda: Literal["PEN"] = "PEN"
    vigencia_desde: date
    vigencia_hasta: date | None = None
    sustento: Annotated[str, Field(min_length=1, max_length=2000)]
    is_active: bool = True

    @model_validator(mode="after")
    def validar_vigencia(self):
        if self.vigencia_hasta and self.vigencia_hasta < self.vigencia_desde:
            raise ValueError("La vigencia final no puede ser anterior a la inicial")
        return self

class GuardiaValorizadaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    tipo_guardia_id: uuid.UUID | None = None
    grupo_ocupacional_id: uuid.UUID | None = None
    nivel_remunerativo_id: uuid.UUID | None = None
    valor: Decimal
    moneda: str = "PEN"
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None
    sustento: str | None = None
    tipo_guardia_nombre: str | None = None
    grupo_ocupacional_nombre: str | None = None
    nivel_remunerativo_nombre: str | None = None
    is_active: bool
    created_at: datetime

    @field_serializer("valor", when_used="json")
    def importe_json(self, value):
        return float(value)  # compatibilidad de la interfaz; cálculo/almacenamiento Decimal

class RolSistemaCreate(Entrada):
    codigo: Annotated[str, Field(min_length=1, max_length=100)]
    nombre: Nombre
    panel: Literal["sigarh"] = "sigarh"
    modulo_requerido: str | None = None
    modulos_permitidos: list[str] = []
    grupos_ocupacionales_permitidos: list[uuid.UUID] = []
    permisos_accion: list[str] = []
    alcance_global: bool = False
    descripcion: str | None = None
    is_active: bool = True

    @field_validator("permisos_accion")
    @classmethod
    def permisos_conocidos(cls, value):
        if set(value) - PERMISOS:
            raise ValueError("Permiso de acción desconocido")
        return sorted(set(value))

class RolSistemaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo: str | None = None
    nombre: str
    panel: str
    modulo_requerido: str | None = None
    modulos_permitidos: list[str] = []
    grupos_ocupacionales_permitidos: list[uuid.UUID] = []
    permisos_accion: list[str] = []
    alcance_global: bool = False
    descripcion: str | None = None
    is_active: bool
    created_at: datetime

class PerfilUsuarioCreate(Entrada):
    nombre: Nombre
    rol_sistema_id: uuid.UUID
    modulos_acceso: list[str] = []
    descripcion: str | None = None
    is_active: bool = True

class PerfilUsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    rol_sistema_id: uuid.UUID | None = None
    modulos_acceso: list[str] = []
    descripcion: str | None = None
    is_active: bool
    created_at: datetime

class DependenciaCreate(Entrada):
    nombre: Nombre
    codigo: Codigo | None = None
    clasificacion: Literal["administrativa", "asistencial"] = "administrativa"
    departamento_id: uuid.UUID | None = None
    servicio_id: uuid.UUID | None = None
    is_active: bool = True

class DependenciaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    codigo: str | None = None
    clasificacion: str
    departamento_id: uuid.UUID | None = None
    servicio_id: uuid.UUID | None = None
    departamento_nombre: str | None = None
    servicio_nombre: str | None = None
    is_active: bool
    created_at: datetime


def validar_password(value: str) -> str:
    if not 12 <= len(value) or len(value.encode("utf-8")) > 72:
        raise ValueError("La contraseña debe tener al menos 12 caracteres y como máximo 72 bytes")
    return value

class UsuarioSigarhCreate(Entrada):
    empleado_id: uuid.UUID | None = None
    perfil_id: uuid.UUID
    username: Annotated[str, Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9._-]+$")]
    email: Annotated[str, Field(max_length=255, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")]
    password: str
    is_active: bool = True

    @field_validator("username", "email")
    @classmethod
    def identidad_normalizada(cls, value):
        return value.lower()

    @field_validator("password", mode="before")
    @classmethod
    def password_seguro(cls, value):
        return validar_password(value)

    @model_validator(mode="after")
    def password_distinto(self):
        if self.password.casefold() in {self.username.casefold(), self.email.casefold()}:
            raise ValueError("La contraseña no puede ser el usuario ni el correo")
        return self

class UsuarioSigarhResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    empleado_id: uuid.UUID | None
    perfil_id: uuid.UUID | None
    username: str
    email: str
    is_active: bool
    created_at: datetime


def esquema_parcial(schema):
    # La validación completa se ejecuta después de combinar los campos con el registro.
    # Omitir es diferente de enviar NULL, y se conservan límites/formatos de cada campo.
    fields = {}
    for name, info in schema.model_fields.items():
        annotation = Annotated[info.annotation, *info.metadata] if info.metadata else info.annotation
        fields[name] = (annotation, None)
    return create_model(schema.__name__.replace("Create", "Update"), __base__=Entrada, **fields)


UsuarioSigarhUpdate = esquema_parcial(UsuarioSigarhCreate)
