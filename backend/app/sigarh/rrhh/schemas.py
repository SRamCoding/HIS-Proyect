import uuid
from datetime import datetime, date
from pydantic import BaseModel


# ─── Empleado ─────────────────────────────────────────────────────────────────

class EmpleadoEspecialidadCreate(BaseModel):
    especialidad_id: uuid.UUID
    numero_rne: str | None = None
    certificado_url: str | None = None
    validado: bool = False


class EmpleadoEspecialidadResponse(EmpleadoEspecialidadCreate):
    id: uuid.UUID
    empleado_id: uuid.UUID
    especialidad_nombre: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EmpleadoCreate(BaseModel):
    # Datos Personales
    dni: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: date | None = None
    sexo: str | None = None
    estado_civil: str | None = None
    grupo_sanguineo: str | None = None
    celular: str | None = None
    telefono_fijo: str | None = None
    correo: str | None = None

    # Datos Laborales
    tipo_trabajador_id: uuid.UUID | None = None
    nivel_remunerativo_id: uuid.UUID | None = None
    grupo_ocupacional_id: uuid.UUID | None = None
    departamento_id: uuid.UUID | None = None
    servicio_id: uuid.UUID | None = None
    cargo_laboral: str | None = None
    modalidad: str | None = None
    codigo_minsa: str | None = None
    numero_cmp: str | None = None
    fecha_ingreso: date | None = None
    fecha_nombramiento: date | None = None
    fecha_cese: date | None = None
    resolucion_nombramiento: str | None = None
    resolucion_cese: str | None = None

    # Datos Bancarios
    banco: str | None = None
    ruc: str | None = None
    numero_cuenta: str | None = None
    numero_cci: str | None = None
    tipo_cuenta: str | None = None

    # Ubicacion
    departamento_ubigeo: str | None = None
    provincia_ubigeo: str | None = None
    distrito_ubigeo: str | None = None
    direccion: str | None = None

    is_active: bool = True


class EmpleadoUpdate(BaseModel):
    nombres: str | None = None
    apellido_paterno: str | None = None
    apellido_materno: str | None = None
    fecha_nacimiento: date | None = None
    sexo: str | None = None
    estado_civil: str | None = None
    grupo_sanguineo: str | None = None
    celular: str | None = None
    telefono_fijo: str | None = None
    correo: str | None = None
    tipo_trabajador_id: uuid.UUID | None = None
    nivel_remunerativo_id: uuid.UUID | None = None
    grupo_ocupacional_id: uuid.UUID | None = None
    departamento_id: uuid.UUID | None = None
    servicio_id: uuid.UUID | None = None
    cargo_laboral: str | None = None
    modalidad: str | None = None
    codigo_minsa: str | None = None
    numero_cmp: str | None = None
    fecha_ingreso: date | None = None
    fecha_nombramiento: date | None = None
    fecha_cese: date | None = None
    resolucion_nombramiento: str | None = None
    resolucion_cese: str | None = None
    banco: str | None = None
    ruc: str | None = None
    numero_cuenta: str | None = None
    numero_cci: str | None = None
    tipo_cuenta: str | None = None
    departamento_ubigeo: str | None = None
    provincia_ubigeo: str | None = None
    distrito_ubigeo: str | None = None
    direccion: str | None = None
    is_active: bool | None = None


class EmpleadoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    dni: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    nombre_completo: str
    fecha_nacimiento: date | None
    sexo: str | None
    estado_civil: str | None
    grupo_sanguineo: str | None
    celular: str | None
    telefono_fijo: str | None
    correo: str | None
    tipo_trabajador_id: uuid.UUID | None
    nivel_remunerativo_id: uuid.UUID | None
    grupo_ocupacional_id: uuid.UUID | None
    departamento_id: uuid.UUID | None
    servicio_id: uuid.UUID | None
    cargo_laboral: str | None
    modalidad: str | None
    codigo_minsa: str | None
    numero_cmp: str | None
    fecha_ingreso: date | None
    fecha_nombramiento: date | None
    fecha_cese: date | None
    resolucion_nombramiento: str | None
    resolucion_cese: str | None
    banco: str | None
    ruc: str | None
    numero_cuenta: str | None
    numero_cci: str | None
    tipo_cuenta: str | None
    departamento_ubigeo: str | None
    provincia_ubigeo: str | None
    distrito_ubigeo: str | None
    direccion: str | None
    is_active: bool
    antiguedad: str | None
    created_at: datetime
    especialidades: list[EmpleadoEspecialidadResponse] = []

    model_config = {"from_attributes": True}


class EmpleadoListItem(BaseModel):
    id: uuid.UUID
    dni: str
    nombre_completo: str
    cargo_laboral: str | None
    modalidad: str | None
    is_active: bool
    fecha_ingreso: date | None
    antiguedad: str | None

    model_config = {"from_attributes": True}


# ─── Especialidad catálogo ────────────────────────────────────────────────────

class EspecialidadCreate(BaseModel):
    nombre: str
    codigo: str | None = None
    is_active: bool = True


class EspecialidadResponse(EspecialidadCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Días Feriados ────────────────────────────────────────────────────────────

class DiasFeriadoCreate(BaseModel):
    nombre: str
    fecha: date
    tipo: str = "nacional"
    is_active: bool = True


class DiasFeriadoResponse(DiasFeriadoCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Motivo Justificación ─────────────────────────────────────────────────────

class MotivoJustificacionCreate(BaseModel):
    nombre: str
    codigo: str | None = None
    descripcion: str | None = None
    is_active: bool = True


class MotivoJustificacionResponse(MotivoJustificacionCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Tolerancia ───────────────────────────────────────────────────────────────

class ToleranciaCreate(BaseModel):
    nombre: str
    minutos_entrada: int = 0
    minutos_salida: int = 0
    descripcion: str | None = None
    is_active: bool = True


class ToleranciaResponse(ToleranciaCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Registro Asistencia ──────────────────────────────────────────────────────

class RegistroAsistenciaCreate(BaseModel):
    empleado_id: uuid.UUID
    fecha: date
    hora_entrada: str | None = None
    hora_salida: str | None = None
    estado: str = "presente"
    observacion: str | None = None


class RegistroAsistenciaResponse(RegistroAsistenciaCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    empleado_nombre: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Justificación ────────────────────────────────────────────────────────────

class JustificacionCreate(BaseModel):
    empleado_id: uuid.UUID
    motivo_id: uuid.UUID | None = None
    fecha_inicio: date
    fecha_fin: date
    descripcion: str | None = None
    documento_url: str | None = None
    estado: str = "pendiente"


class JustificacionResponse(JustificacionCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    empleado_nombre: str | None = None
    motivo_nombre: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}