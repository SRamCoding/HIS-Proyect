import re
import uuid
from datetime import datetime, date
from typing import Literal
from pydantic import BaseModel, field_validator, model_validator

# ─── Validadores reutilizables para Empleado ─────────────────────────────────

_RE_CORREO = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
_RE_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .-]*$")
_GRUPOS_SANGUINEOS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
_ESTADOS_CIVILES = {"soltero", "casado", "divorciado", "viudo", "conviviente"}


def _limpiar(v):
    """Trim y '' -> None para campos de texto opcionales."""
    if v is None:
        return None
    v = str(v).strip()
    return v or None


def _solo_digitos(v, largo: int, etiqueta: str, exacto: bool = True):
    v = _limpiar(v)
    if v is None:
        return None
    if not v.isdigit():
        raise ValueError(f"{etiqueta} solo debe contener dígitos")
    if exacto and len(v) != largo:
        raise ValueError(f"{etiqueta} debe tener {largo} dígitos")
    if not exacto and len(v) > largo:
        raise ValueError(f"{etiqueta} no debe superar {largo} dígitos")
    return v


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


class _EmpleadoCampos(BaseModel):
    """Campos + validaciones compartidas por creación y actualización.

    Todos opcionales aquí; `EmpleadoCreate` vuelve obligatorios los mínimos.
    """
    # Datos Personales
    dni: str | None = None
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

    # Datos Laborales
    tipo_trabajador_id: uuid.UUID | None = None
    nivel_remunerativo_id: uuid.UUID | None = None
    grupo_ocupacional_id: uuid.UUID | None = None
    profesion_id: uuid.UUID | None = None
    departamento_id: uuid.UUID | None = None
    servicio_id: uuid.UUID | None = None
    cargo_laboral: str | None = None
    es_jefe_servicio: bool = False
    modalidad: str | None = None
    codigo_minsa: str | None = None
    numero_cmp: str | None = None
    numero_colegiatura: str | None = None
    habilitado_colegio: bool = False
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

    # ── Validaciones de campo ───────────────────────────────────────────────

    @field_validator("dni")
    @classmethod
    def _v_dni(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El DNI es requerido")
        if not v.isdigit() or len(v) != 8:
            raise ValueError("El DNI debe tener 8 dígitos numéricos")
        return v

    @field_validator("nombres", "apellido_paterno", "apellido_materno")
    @classmethod
    def _v_nombres(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("Este campo es requerido")
        if len(v) < 2:
            raise ValueError("Debe tener al menos 2 caracteres")
        if not _RE_NOMBRE.match(v):
            raise ValueError("Solo se permiten letras, espacios, guiones y apóstrofos")
        return v

    @field_validator("celular")
    @classmethod
    def _v_celular(cls, v):
        v = _limpiar(v)
        if v is None:
            return None
        if not v.isdigit() or len(v) != 9:
            raise ValueError("El celular debe tener 9 dígitos")
        return v

    @field_validator("telefono_fijo")
    @classmethod
    def _v_telefono(cls, v):
        v = _limpiar(v)
        if v is None:
            return None
        digitos = re.sub(r"\D", "", v)
        if not 6 <= len(digitos) <= 9:
            raise ValueError("El teléfono fijo no es válido")
        return v

    @field_validator("ruc")
    @classmethod
    def _v_ruc(cls, v):
        return _solo_digitos(v, 11, "El RUC")

    @field_validator("numero_cmp", "numero_colegiatura", "codigo_minsa")
    @classmethod
    def _v_cod_corto(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 20:
            raise ValueError("No debe superar 20 caracteres")
        return v

    @field_validator("cargo_laboral")
    @classmethod
    def _v_cargo(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 100:
            raise ValueError("El cargo no debe superar 100 caracteres")
        return v

    @field_validator("modalidad")
    @classmethod
    def _v_modalidad(cls, v):
        v = _limpiar(v)
        if v is None:
            return None
        opciones = {"nombrado", "cas", "contrato", "snp", "tercero"}
        if v.lower() not in opciones:
            raise ValueError("Modalidad inválida. Opciones: Nombrado, CAS, Contrato, SNP, Tercero")
        return v

    @field_validator("numero_cuenta")
    @classmethod
    def _v_cuenta(cls, v):
        v = _limpiar(v)
        if v is None:
            return None
        if not v.isdigit() or not 10 <= len(v) <= 20:
            raise ValueError("La cuenta bancaria debe tener entre 10 y 20 dígitos")
        return v

    @field_validator("direccion")
    @classmethod
    def _v_direccion(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 200:
            raise ValueError("La dirección no debe superar 200 caracteres")
        return v

    @field_validator("correo")
    @classmethod
    def _v_correo(cls, v):
        v = _limpiar(v)
        if v is None:
            return None
        if not _RE_CORREO.match(v):
            raise ValueError("El correo no tiene un formato válido")
        return v.lower()

    @field_validator("sexo")
    @classmethod
    def _v_sexo(cls, v):
        v = _limpiar(v)
        if v is None:
            return None
        v = v.upper()
        if v not in {"M", "F"}:
            raise ValueError("El sexo debe ser M o F")
        return v

    @field_validator("grupo_sanguineo")
    @classmethod
    def _v_grupo_sang(cls, v):
        v = _limpiar(v)
        if v is None:
            return None
        v = v.upper()
        if v not in _GRUPOS_SANGUINEOS:
            raise ValueError("Grupo sanguíneo inválido")
        return v

    @field_validator("estado_civil")
    @classmethod
    def _v_estado_civil(cls, v):
        v = _limpiar(v)
        if v is None:
            return None
        if v.lower() not in _ESTADOS_CIVILES:
            raise ValueError("Estado civil inválido")
        return v.lower()

    @field_validator(
        "codigo_minsa", "resolucion_nombramiento", "resolucion_cese", "banco",
        "numero_cuenta", "numero_cci", "tipo_cuenta", "direccion",
        "departamento_ubigeo", "provincia_ubigeo", "distrito_ubigeo",
    )
    @classmethod
    def _v_texto_opcional(cls, v):
        return _limpiar(v)

    @model_validator(mode="after")
    def _v_coherencia_fechas(self):
        hoy = date.today()
        fn, fi = self.fecha_nacimiento, self.fecha_ingreso
        if fn:
            if fn >= hoy:
                raise ValueError("La fecha de nacimiento debe ser anterior a hoy")
            if (hoy - fn).days < 18 * 365:
                raise ValueError("El empleado debe ser mayor de edad")
            if (hoy - fn).days > 80 * 366:
                raise ValueError("La edad no puede superar los 80 años")
        if fn and fi and fi <= fn:
            raise ValueError("La fecha de ingreso debe ser posterior a la de nacimiento")
        if fi and self.fecha_cese and self.fecha_cese < fi:
            raise ValueError("La fecha de cese no puede ser anterior a la de ingreso")
        if fi and self.fecha_nombramiento and self.fecha_nombramiento < fi:
            raise ValueError("La fecha de nombramiento no puede ser anterior a la de ingreso")
        return self


class EmpleadoCreate(_EmpleadoCampos):
    dni: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    is_active: bool = True


class EmpleadoUpdate(_EmpleadoCampos):
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
    profesion_id: uuid.UUID | None
    departamento_id: uuid.UUID | None
    servicio_id: uuid.UUID | None
    cargo_laboral: str | None
    es_jefe_servicio: bool
    modalidad: str | None
    codigo_minsa: str | None
    numero_cmp: str | None
    numero_colegiatura: str | None
    habilitado_colegio: bool
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
    es_jefe_servicio: bool
    modalidad: str | None
    is_active: bool
    fecha_ingreso: date | None
    antiguedad: str | None

    model_config = {"from_attributes": True}


# ─── Especialidad catálogo ────────────────────────────────────────────────────

class EspecialidadCreate(BaseModel):
    nombre: str
    codigo: str | None = None
    descripcion: str | None = None
    is_active: bool = True
    tipo: Literal["especialidad", "subespecialidad"] = "especialidad"
    parent_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def _v_jerarquia(self):
        if self.tipo == "subespecialidad" and not self.parent_id:
            raise ValueError("Selecciona la especialidad principal")
        if self.tipo == "especialidad":
            self.parent_id = None
        return self

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El nombre de la especialidad es requerido")
        if len(v) > 100:
            raise ValueError("El nombre no debe superar 100 caracteres")
        return v

    @field_validator("codigo")
    @classmethod
    def _v_codigo(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 20:
            raise ValueError("El código no debe superar 20 caracteres")
        return v

    @field_validator("descripcion")
    @classmethod
    def _v_desc(cls, v):
        return _limpiar(v)


class EspecialidadUpdate(EspecialidadCreate):
    nombre: str | None = None
    is_active: bool | None = None

    @field_validator("nombre")
    @classmethod
    def _v_nombre_upd(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 100:
            raise ValueError("El nombre no debe superar 100 caracteres")
        return v


class EspecialidadResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    codigo: str | None
    descripcion: str | None
    is_active: bool
    medicos_asignados: int = 0
    created_at: datetime
    catalogo_id: uuid.UUID | None = None
    tipo: str = "especialidad"
    parent_id: uuid.UUID | None = None
    parent_nombre: str | None = None
    requisitos: str | None = None
    fuente: str | None = None
    norma: str | None = None
    fuente_url: str | None = None
    es_oficial: bool = False
    recomendada_nivel: bool = False
    hospital_level: str | None = None

    model_config = {"from_attributes": True}


# ─── Días Feriados ────────────────────────────────────────────────────────────

class DiasFeriadoCreate(BaseModel):
    nombre: str
    fecha: date
    tipo: str = "nacional"
    is_active: bool = True

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("La descripción del feriado es requerida")
        if len(v) > 150:
            raise ValueError("No debe superar 150 caracteres")
        return v

    @field_validator("tipo")
    @classmethod
    def _v_tipo(cls, v):
        v = (_limpiar(v) or "nacional").lower()
        if v not in {"nacional", "regional", "local"}:
            raise ValueError("Tipo inválido. Opciones: nacional, regional, local")
        return v


class DiasFeriadoUpdate(DiasFeriadoCreate):
    nombre: str | None = None
    fecha: date | None = None
    tipo: str | None = None
    is_active: bool | None = None

    @field_validator("nombre")
    @classmethod
    def _v_nombre_upd(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 150:
            raise ValueError("No debe superar 150 caracteres")
        return v


class DiasFeriadoResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    fecha: date
    tipo: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Motivo Justificación ─────────────────────────────────────────────────────

class MotivoJustificacionCreate(BaseModel):
    nombre: str
    codigo: str | None = None
    descripcion: str | None = None
    is_active: bool = True

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        v = _limpiar(v)
        if v is None:
            raise ValueError("El nombre del motivo es requerido")
        if len(v) > 150:
            raise ValueError("No debe superar 150 caracteres")
        return v

    @field_validator("codigo", "descripcion")
    @classmethod
    def _v_opt(cls, v):
        return _limpiar(v)


class MotivoJustificacionUpdate(MotivoJustificacionCreate):
    nombre: str | None = None
    is_active: bool | None = None

    @field_validator("nombre")
    @classmethod
    def _v_nombre_upd(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 150:
            raise ValueError("No debe superar 150 caracteres")
        return v


class MotivoJustificacionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    codigo: str | None
    descripcion: str | None
    is_active: bool
    usos: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Tolerancia ───────────────────────────────────────────────────────────────

class ToleranciaCreate(BaseModel):
    nombre: str | None = None
    dependencia_id: uuid.UUID
    grupo_ocupacional_id: uuid.UUID
    minutos_tolerancia: int = 0
    minutos_tolerancia_dia: int = 0
    is_active: bool = True

    @field_validator("minutos_tolerancia", "minutos_tolerancia_dia")
    @classmethod
    def _v_min(cls, v):
        if v is not None and v < 0:
            raise ValueError("Los minutos no pueden ser negativos")
        return v

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        return _limpiar(v)


class ToleranciaUpdate(BaseModel):
    nombre: str | None = None
    dependencia_id: uuid.UUID | None = None
    grupo_ocupacional_id: uuid.UUID | None = None
    minutos_tolerancia: int | None = None
    minutos_tolerancia_dia: int | None = None
    is_active: bool | None = None

    @field_validator("minutos_tolerancia", "minutos_tolerancia_dia")
    @classmethod
    def _v_min(cls, v):
        if v is not None and v < 0:
            raise ValueError("Los minutos no pueden ser negativos")
        return v


class ToleranciaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str | None
    dependencia_id: uuid.UUID | None
    dependencia_nombre: str | None = None
    grupo_ocupacional_id: uuid.UUID | None
    grupo_ocupacional_nombre: str | None = None
    minutos_tolerancia: int
    minutos_tolerancia_dia: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Registro Asistencia ──────────────────────────────────────────────────────

_RE_HORA = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class RegistroAsistenciaCreate(BaseModel):
    empleado_id: uuid.UUID
    grupo_ocupacional_id: uuid.UUID | None = None
    horario_guardia_id: uuid.UUID | None = None
    fecha: date
    actividad_texto: str | None = None
    servicio_texto: str | None = None
    hora_entrada_programada: str | None = None
    hora_salida_programada: str | None = None
    hora_entrada_real: str | None = None
    hora_salida_real: str | None = None
    estado: str = "presente"
    observacion: str | None = None

    @field_validator("fecha")
    @classmethod
    def _v_fecha(cls, v):
        if v and v > date.today():
            raise ValueError("La fecha no puede ser futura")
        return v

    @field_validator("estado")
    @classmethod
    def _v_estado(cls, v):
        v = (_limpiar(v) or "presente").lower()
        if v not in {"presente", "ausente", "tardanza", "justificado"}:
            raise ValueError("Estado inválido")
        return v

    @field_validator("hora_entrada_programada", "hora_salida_programada", "hora_entrada_real", "hora_salida_real")
    @classmethod
    def _v_hora(cls, v):
        v = _limpiar(v)
        if v is not None and not _RE_HORA.match(v):
            raise ValueError("La hora debe tener formato HH:MM")
        return v

    @field_validator("actividad_texto", "servicio_texto")
    @classmethod
    def _v_texto(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 100:
            raise ValueError("No debe superar 100 caracteres")
        return v


class RegistroAsistenciaUpdate(RegistroAsistenciaCreate):
    empleado_id: uuid.UUID | None = None
    fecha: date | None = None
    estado: str | None = None

    @field_validator("estado")
    @classmethod
    def _v_estado_upd(cls, v):
        if v is None:
            return None
        v = str(v).strip().lower()
        if v not in {"presente", "ausente", "tardanza", "justificado"}:
            raise ValueError("Estado inválido")
        return v


class RegistroAsistenciaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    empleado_id: uuid.UUID
    empleado_nombre: str | None = None
    grupo_ocupacional_id: uuid.UUID | None
    grupo_ocupacional_nombre: str | None = None
    horario_guardia_id: uuid.UUID | None
    horario_guardia_nombre: str | None = None
    fecha: date
    actividad_texto: str | None
    servicio_texto: str | None
    hora_entrada_programada: str | None
    hora_salida_programada: str | None
    hora_entrada_real: str | None
    hora_salida_real: str | None
    minutos_tardanza: int
    horas_trabajadas: str | None = None
    estado: str
    observacion: str | None
    registrado_por: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Justificación ────────────────────────────────────────────────────────────

_TIPOS_JUSTIFICACION = {"justificacion", "licencia", "vacacion"}


class JustificacionCreate(BaseModel):
    empleado_id: uuid.UUID
    motivo_id: uuid.UUID | None = None
    tipo: str = "justificacion"
    numero_documento: str | None = None
    fecha_tramite: date | None = None
    fecha_inicio: date
    fecha_fin: date
    descripcion: str | None = None
    documento_url: str | None = None
    estado: str = "pendiente"

    @field_validator("tipo")
    @classmethod
    def _v_tipo(cls, v):
        v = (_limpiar(v) or "justificacion").lower()
        if v not in _TIPOS_JUSTIFICACION:
            raise ValueError("Tipo inválido. Opciones: justificacion, licencia, vacacion")
        return v

    @field_validator("numero_documento")
    @classmethod
    def _v_doc(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 50:
            raise ValueError("El N° de documento no debe superar 50 caracteres")
        return v

    @field_validator("estado")
    @classmethod
    def _v_estado(cls, v):
        v = (_limpiar(v) or "pendiente").lower()
        if v not in {"pendiente", "aprobado", "rechazado"}:
            raise ValueError("Estado inválido. Opciones: pendiente, aprobado, rechazado")
        return v

    @model_validator(mode="after")
    def _v_fechas(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValueError("La fecha de fin no puede ser anterior a la de inicio")
        return self


class JustificacionUpdate(BaseModel):
    motivo_id: uuid.UUID | None = None
    tipo: str | None = None
    numero_documento: str | None = None
    fecha_tramite: date | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    descripcion: str | None = None
    documento_url: str | None = None
    estado: str | None = None

    @field_validator("tipo")
    @classmethod
    def _v_tipo(cls, v):
        if v is None:
            return None
        v = str(v).strip().lower()
        if v not in _TIPOS_JUSTIFICACION:
            raise ValueError("Tipo inválido")
        return v

    @field_validator("estado")
    @classmethod
    def _v_estado(cls, v):
        if v is None:
            return None
        v = str(v).strip().lower()
        if v not in {"pendiente", "aprobado", "rechazado"}:
            raise ValueError("Estado inválido")
        return v


class JustificacionDecision(BaseModel):
    """Cuerpo de POST /justificaciones/{id}/rechazar (opcional en /aprobar)."""
    motivo_rechazo: str | None = None

    @field_validator("motivo_rechazo")
    @classmethod
    def _v_mot(cls, v):
        v = _limpiar(v)
        if v is not None and len(v) > 500:
            raise ValueError("El motivo de rechazo no debe superar 500 caracteres")
        return v


class JustificacionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    empleado_id: uuid.UUID
    empleado_nombre: str | None = None
    empleado_dni: str | None = None
    empleado_regimen: str | None = None
    empleado_cargo: str | None = None
    motivo_id: uuid.UUID | None
    motivo_nombre: str | None = None
    tipo: str = "justificacion"
    numero_documento: str | None
    fecha_tramite: date | None
    fecha_inicio: date
    fecha_fin: date
    dias: int = 0
    descripcion: str | None
    documento_url: str | None
    estado: str
    registrado_por: str | None = None
    revisado_por: str | None = None
    revisado_at: datetime | None = None
    motivo_rechazo: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
