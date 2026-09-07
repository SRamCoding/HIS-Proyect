import uuid
from datetime import datetime
from pydantic import BaseModel


# Base generica para catalogos simples 

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


# Departamento

class DepartamentoCreate(CatalogoBase):
    pass

class DepartamentoResponse(CatalogoResponse):
    pass


# Servicio 

class ServicioCreate(CatalogoBase):
    departamento_id: uuid.UUID | None = None
    piso_id: uuid.UUID | None = None

class ServicioResponse(CatalogoResponse):
    departamento_id: uuid.UUID | None = None
    departamento_nombre: str | None = None
    piso_id: uuid.UUID | None = None
    piso_nombre: str | None = None


# Tipo Trabajador 

class TipoTrabajadorCreate(CatalogoBase):
    pass

class TipoTrabajadorResponse(CatalogoResponse):
    pass


#  Tipo Guardia 

class TipoGuardiaCreate(CatalogoBase):
    horas: int | None = None
    es_laborable: bool = True
    requiere_epp: bool = False

class TipoGuardiaResponse(CatalogoResponse):
    horas: int | None = None
    es_laborable: bool = True
    requiere_epp: bool = False


# Nivel Remunerativo 

class NivelRemunerativoCreate(CatalogoBase):
    pass

class NivelRemunerativoResponse(CatalogoResponse):
    pass


# Horario Guardia 

class HorarioGuardiaCreate(BaseModel):
    nombre: str
    hora_inicio: str
    hora_fin: str
    horas_totales: int | None = None
    tipo_guardia_id: uuid.UUID | None = None
    is_active: bool = True

class HorarioGuardiaResponse(HorarioGuardiaCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    tipo_guardia_nombre: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


#  Grupo Ocupacional 

# --- Tipo Grupo Ocupacional ---

class TipoGrupoOcupacionalCreate(CatalogoBase):
    pass

class TipoGrupoOcupacionalResponse(CatalogoResponse):
    pass


class GrupoOcupacionalCreate(CatalogoBase):
    tipo_grupo_id: uuid.UUID | None = None

class GrupoOcupacionalResponse(CatalogoResponse):
    tipo_grupo_id: uuid.UUID | None = None


# Tipo Actividad 

class TipoActividadCreate(BaseModel):
    nombre: str
    codigo: str | None = None
    is_active: bool = True

class TipoActividadResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    codigo: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# Actividad 

class ActividadCreate(BaseModel):
    nombre: str
    codigo: str | None = None
    tipo_actividad_id: uuid.UUID | None = None
    requiere_consultorio: bool = False
    is_active: bool = True

class ActividadResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    codigo: str | None = None
    tipo_actividad_id: uuid.UUID | None = None
    requiere_consultorio: bool = False
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# Guardia Valorizada 

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


#Rol Sistema 

class RolSistemaCreate(BaseModel):
    codigo: str
    nombre: str
    panel: str = "sigarh"
    modulo_requerido: str | None = None
    modulos_permitidos: list[str] = []
    grupos_ocupacionales_permitidos: list[uuid.UUID] = []
    descripcion: str | None = None
    is_active: bool = True

class RolSistemaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo: str | None
    nombre: str
    panel: str
    modulo_requerido: str | None
    modulos_permitidos: list[str] = []
    grupos_ocupacionales_permitidos: list[uuid.UUID] = []
    descripcion: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

#Perfil Usuario 

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

class DependenciaCreate(BaseModel):
    nombre: str
    codigo: str | None = None
    clasificacion: str = "administrativa"
    departamento_id: uuid.UUID | None = None
    servicio_id: uuid.UUID | None = None
    is_active: bool = True

class DependenciaResponse(BaseModel):
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

    model_config = {"from_attributes": True}

class UsuarioSigarhCreate(BaseModel):
    empleado_id: uuid.UUID | None = None
    perfil_id: uuid.UUID | None = None
    username: str
    email: str
    password: str
    is_active: bool = True

class UsuarioSigarhResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    empleado_id: uuid.UUID | None
    perfil_id: uuid.UUID | None
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

