import uuid
from datetime import datetime
from pydantic import BaseModel


# ─── Base genérica para catálogos simples ─────────────────────────────────────

class CatalogoBase(BaseModel):
    nombre: str
    codigo: str | None = None
    descripcion: str | None = None
    is_active: bool = True


class CatalogoResponse(CatalogoBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Departamento ──────────────────────────────────────────────────────────────

class DepartamentoCreate(CatalogoBase):
    pass

class DepartamentoResponse(CatalogoResponse):
    pass


# ─── Servicio ──────────────────────────────────────────────────────────────────

class ServicioCreate(CatalogoBase):
    departamento_id: uuid.UUID | None = None

class ServicioResponse(CatalogoResponse):
    departamento_id: uuid.UUID | None = None
    departamento_nombre: str | None = None


# ─── Tipo Trabajador ──────────────────────────────────────────────────────────

class TipoTrabajadorCreate(CatalogoBase):
    pass

class TipoTrabajadorResponse(CatalogoResponse):
    pass


# ─── Tipo Guardia ─────────────────────────────────────────────────────────────

class TipoGuardiaCreate(CatalogoBase):
    horas: int | None = None

class TipoGuardiaResponse(CatalogoResponse):
    horas: int | None = None


# ─── Nivel Remunerativo ───────────────────────────────────────────────────────

class NivelRemunerativoCreate(CatalogoBase):
    pass

class NivelRemunerativoResponse(CatalogoResponse):
    pass


# ─── Horario Guardia ──────────────────────────────────────────────────────────

class HorarioGuardiaCreate(BaseModel):
    nombre: str
    hora_inicio: str
    hora_fin: str
    horas_totales: int | None = None
    is_active: bool = True

class HorarioGuardiaResponse(HorarioGuardiaCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Grupo Ocupacional ────────────────────────────────────────────────────────

class GrupoOcupacionalCreate(CatalogoBase):
    pass

class GrupoOcupacionalResponse(CatalogoResponse):
    pass


# ─── Tipo Actividad ───────────────────────────────────────────────────────────

class TipoActividadCreate(CatalogoBase):
    pass

class TipoActividadResponse(CatalogoResponse):
    pass


# ─── Actividad ────────────────────────────────────────────────────────────────

class ActividadCreate(CatalogoBase):
    tipo_actividad_id: uuid.UUID | None = None

class ActividadResponse(CatalogoResponse):
    tipo_actividad_id: uuid.UUID | None = None


# ─── Guardia Valorizada ───────────────────────────────────────────────────────

class GuardiaValorizadaCreate(BaseModel):
    tipo_guardia_id: uuid.UUID | None = None
    grupo_ocupacional_id: uuid.UUID | None = None
    nivel_remunerativo_id: uuid.UUID | None = None
    valor: float = 0.0
    is_active: bool = True

class GuardiaValorizadaResponse(GuardiaValorizadaCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Rol Sistema ──────────────────────────────────────────────────────────────

class RolSistemaCreate(BaseModel):
    nombre: str
    descripcion: str | None = None
    is_active: bool = True

class RolSistemaResponse(RolSistemaCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Perfil Usuario ───────────────────────────────────────────────────────────

class PerfilUsuarioCreate(BaseModel):
    nombre: str
    rol_sistema_id: uuid.UUID | None = None
    modulos_acceso: list[str] = []
    descripcion: str | None = None
    is_active: bool = True

class PerfilUsuarioResponse(PerfilUsuarioCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}

class DependenciaCreate(CatalogoBase):
    pass

class DependenciaResponse(CatalogoResponse):
    pass