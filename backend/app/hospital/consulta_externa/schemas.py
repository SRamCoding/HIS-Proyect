import uuid
from datetime import datetime, date
from pydantic import BaseModel, Field, model_validator
from typing import Literal


_MODALIDADES = {"PRESENCIAL", "VIRTUAL"}


class ProgramacionMedicaCreate(BaseModel):
    medico_id: uuid.UUID
    servicio_id: uuid.UUID
    especialidad_id: uuid.UUID | None = None
    consultorio_id: uuid.UUID | None = None
    fecha: date
    turno: str
    hora_inicio: str
    hora_fin: str
    tiempo_promedio_atencion: int = 15
    tipo_servicio: str = "CONSULTORIO_EXTERNO"
    modalidad: str = "PRESENCIAL"
    mostrar_en_consultorio: bool = False
    descripcion: str | None = None

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data

    @model_validator(mode="after")
    def _v_modalidad(self):
        if self.modalidad not in _MODALIDADES:
            raise ValueError("modalidad debe ser PRESENCIAL o VIRTUAL")
        return self


class ProgramacionMedicaUpdate(BaseModel):
    servicio_id: uuid.UUID | None = None
    especialidad_id: uuid.UUID | None = None
    consultorio_id: uuid.UUID | None = None
    fecha: date | None = None
    turno: str | None = None
    hora_inicio: str | None = None
    hora_fin: str | None = None
    tiempo_promedio_atencion: int | None = None
    tipo_servicio: str | None = None
    modalidad: str | None = None
    mostrar_en_consultorio: bool | None = None
    descripcion: str | None = None
    estado: str | None = None

    @model_validator(mode="after")
    def _v_modalidad(self):
        if self.modalidad is not None and self.modalidad not in _MODALIDADES:
            raise ValueError("modalidad debe ser PRESENCIAL o VIRTUAL")
        return self


class ProgramacionMedicaResponse(BaseModel):
    id: uuid.UUID
    codigo: str | None = None
    medico_id: uuid.UUID
    medico_nombre: str
    servicio_id: uuid.UUID | None
    servicio_nombre: str | None
    especialidad_id: uuid.UUID | None
    especialidad_nombre: str | None
    consultorio_id: uuid.UUID | None = None
    consultorio_nombre: str | None = None
    origen_sigarh_turno_id: uuid.UUID | None = None
    origen: str = "MANUAL"
    fecha: date
    turno: str
    hora_inicio: str
    hora_fin: str
    tiempo_promedio_atencion: int
    tipo_servicio: str
    modalidad: str = "PRESENCIAL"
    mostrar_en_consultorio: bool
    descripcion: str | None
    estado: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConsultorioOut(BaseModel):
    id: uuid.UUID
    nombre: str
    especialidad_id: uuid.UUID | None = None


class SincronizacionSIGARHResponse(BaseModel):
    creadas: int
    actualizadas: int
    omitidas: int
    ausencias: int = 0
    citas_en_riesgo: int = 0
    mes: int
    anio: int


class ServicioOut(BaseModel):
    id: uuid.UUID
    nombre: str
    model_config = {"from_attributes": True}


class EspecialidadOut(BaseModel):
    id: uuid.UUID
    nombre: str
    model_config = {"from_attributes": True}


class MedicoOut(BaseModel):
    id: uuid.UUID
    nombre_completo: str
    model_config = {"from_attributes": True}


# --- Cupos (slots calculados, no se guardan en BD) ---
class CupoOut(BaseModel):
    hora_inicio: str
    hora_fin: str
    disponible: bool
    cita_id: uuid.UUID | None = None
    paciente_nombre: str | None = None


# --- Citas ---
class CitaCreate(BaseModel):
    programacion_medica_id: uuid.UUID
    patient_id: uuid.UUID
    hora_inicio: str
    hora_fin: str
    tipo_consulta: str | None = None
    observacion: str | None = None
    cuenta_vinculada: str | None = None
    fuente_financiamiento: str | None = None
    producto_plan: str | None = None

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


class CitaUpdate(BaseModel):
    estado: str | None = None
    observacion: str | None = None
    tipo_consulta: str | None = None
    cuenta_vinculada: str | None = None
    fuente_financiamiento: str | None = None
    producto_plan: str | None = None


class CitaReprogramar(BaseModel):
    programacion_medica_id: uuid.UUID
    hora_inicio: str
    hora_fin: str
    mensaje: str | None = Field(default=None, max_length=500)


class CitasReprogramarBloque(BaseModel):
    cita_ids: list[uuid.UUID] = Field(min_length=1)
    programacion_medica_id: uuid.UUID
    mensaje: str | None = Field(default=None, max_length=500)


class CitaResponse(BaseModel):
    id: uuid.UUID
    programacion_medica_id: uuid.UUID
    patient_id: uuid.UUID
    paciente_nombre: str
    paciente_dni: str | None
    hora_inicio: str
    hora_fin: str
    tipo_consulta: str | None
    observacion: str | None
    numero_cuenta: str | None
    cuenta_vinculada: str | None
    fuente_financiamiento: str | None
    producto_plan: str | None
    estado: str
    created_at: datetime
    fecha: date | None = None
    turno: str | None = None
    medico_id: uuid.UUID | None = None
    medico_nombre: str | None = None
    servicio_nombre: str | None = None
    especialidad_nombre: str | None = None
    paciente_record: str | None = None
    paciente_insurance: str | None = None
    paciente_telefono: str | None = None

    model_config = {"from_attributes": True}


class TriajeCampos(BaseModel):
    pulso: int | None = Field(default=None, ge=0)
    temperatura: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    presion_sistolica: int | None = Field(default=None, ge=0)
    presion_diastolica: int | None = Field(default=None, ge=0)
    frecuencia_cardiaca: int | None = Field(default=None, ge=0)
    frecuencia_respiratoria: int | None = Field(default=None, ge=0)
    peso: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    talla: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    perimetro_abdominal: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    perimetro_cefalico: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    saturacion_o2: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


class TriajeCreate(TriajeCampos):
    pulso: int = Field(ge=0)
    temperatura: float = Field(gt=0, allow_inf_nan=False)
    presion_sistolica: int = Field(ge=0)
    presion_diastolica: int = Field(ge=0)
    frecuencia_cardiaca: int = Field(ge=0)
    frecuencia_respiratoria: int = Field(ge=0)


class TriajeResponse(BaseModel):
    id: uuid.UUID
    cita_id: uuid.UUID
    pulso: int | None
    temperatura: float | None
    presion_sistolica: int | None
    presion_diastolica: int | None
    frecuencia_cardiaca: int | None
    frecuencia_respiratoria: int | None
    peso: float | None
    talla: float | None
    perimetro_abdominal: float | None
    perimetro_cefalico: float | None
    saturacion_o2: float | None
    imc: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CitaTriajeItem(BaseModel):
    """Fila del listado de Triaje — cita confirmada, con o sin triaje ya hecho."""
    cita_id: uuid.UUID
    paciente_nombre: str
    paciente_dni: str | None
    paciente_hc: str | None
    fuente_financiamiento: str | None
    especialidad_nombre: str | None
    servicio_nombre: str | None
    medico_nombre: str
    fecha: date
    hora_inicio: str
    paso_triaje: bool


class TriajeUpdate(TriajeCampos):
    @model_validator(mode="after")
    def conservar_obligatorios(self):
        for campo in ("pulso", "temperatura", "presion_sistolica", "presion_diastolica", "frecuencia_cardiaca", "frecuencia_respiratoria"):
            if campo in self.model_fields_set and getattr(self, campo) is None:
                raise ValueError("No puede borrar una medición obligatoria: " + campo)
        return self



class DiagnosticoCIE10Out(BaseModel):
    id: uuid.UUID
    codigo_cie10: str
    descripcion: str
    model_config = {"from_attributes": True}


class AtencionDiagnosticoCreate(BaseModel):
    diagnostico_cie10_id: uuid.UUID
    tipo: Literal["presuntivo", "definitivo", "repetitivo"] = "definitivo"


class AtencionDiagnosticoOut(BaseModel):
    id: uuid.UUID
    diagnostico_cie10_id: uuid.UUID
    codigo_cie10: str
    descripcion: str
    tipo: str
    model_config = {"from_attributes": True}


class AntecedentesConsulta(BaseModel):
    antecedente_quirurgico: str | None = None
    antecedente_patologico: str | None = None
    antecedente_alergias: str | None = None
    antecedentes_obstetricos: str | None = None
    antecedente_familiares: str | None = None
    antecedente_otros: str | None = None


class AtencionMedicaUpdate(BaseModel):
    motivo_consulta: str | None = Field(default=None, min_length=1)
    enfermedad_actual: str | None = None
    examen_clinico: str | None = None
    plan_tratamiento: str | None = None
    observaciones: str | None = None
    destino_atencion: Literal["ALTA", "HOSPITALIZACION", "REFERENCIA"] | None = None
    indicaciones_alta: str | None = None
    diagnosticos: list[AtencionDiagnosticoCreate] | None = None
    antecedentes: AntecedentesConsulta | None = None
    prestaciones: list[Literal["FARMACIA", "LABORATORIO", "IMAGEN", "INTERCONSULTA"]] | None = None

    @model_validator(mode="before")
    @classmethod
    def normalizar(cls, data):
        if isinstance(data, dict):
            data = {k: (v.strip() if isinstance(v, str) else v) for k, v in data.items()}
            for campo in ("motivo_consulta", "destino_atencion", "diagnosticos", "prestaciones", "antecedentes"):
                if campo in data and data[campo] is None:
                    raise ValueError("No puede borrar el campo " + campo)
        return data


class AtencionMedicaCreate(AtencionMedicaUpdate):
    motivo_consulta: str = Field(min_length=1)
    destino_atencion: Literal["ALTA", "HOSPITALIZACION", "REFERENCIA"] = "ALTA"
    diagnosticos: list[AtencionDiagnosticoCreate] = Field(default_factory=list)
    prestaciones: list[Literal["FARMACIA", "LABORATORIO", "IMAGEN", "INTERCONSULTA"]] = Field(default_factory=list)


class AtencionMedicaResponse(BaseModel):
    id: uuid.UUID
    cita_id: uuid.UUID
    paciente_nombre: str
    paciente_dni: str | None
    paciente_edad: int
    medico_nombre: str
    especialidad_nombre: str | None
    servicio_nombre: str | None
    motivo_consulta: str
    examen_clinico: str | None
    plan_tratamiento: str | None
    observaciones: str | None
    destino_atencion: str
    estado: str
    firmado_at: datetime | None
    diagnosticos: list[AtencionDiagnosticoOut]
    enfermedad_actual: str | None = None
    prestaciones: list[str] = Field(default_factory=list)
    antecedentes_documentados: bool = False
    cierre_evidencia: dict | None = None
    # Antecedentes conservados por consulta
    antecedente_quirurgico: str | None
    antecedente_patologico: str | None
    antecedente_alergias: str | None
    antecedentes_obstetricos: str | None
    antecedente_familiares: str | None
    antecedente_otros: str | None
    # triaje (solo lectura)
    triaje: dict | None
    created_at: datetime
    indicaciones_alta: str | None = None


class AtencionMedicaListItem(BaseModel):
    cita_id: uuid.UUID
    paciente_nombre: str
    paciente_dni: str | None
    medico_nombre: str
    especialidad_nombre: str | None
    servicio_nombre: str | None
    fecha: date
    hora_inicio: str
    destino_atencion: str
    estado: str
    created_at: datetime


class MedicamentoOut(BaseModel):
    id: uuid.UUID
    codigo_interno: str
    nombre_comercial: str
    dci: str | None
    presentacion: str | None
    concentracion: str | None
    model_config = {"from_attributes": True}


class RecetaItemCreate(BaseModel):
    medicamento_id: uuid.UUID
    cantidad: int = Field(ge=1)
    dosis: str | None = None
    frecuencia: str | None = None
    duracion_dias: int | None = Field(default=None, ge=1)
    indicaciones: str | None = None


class RecetaItemOut(BaseModel):
    id: uuid.UUID
    medicamento_id: uuid.UUID
    codigo_interno: str
    nombre_comercial: str
    cantidad: int
    dosis: str | None
    frecuencia: str | None
    duracion_dias: int | None
    indicaciones: str | None


class RecetaCreate(BaseModel):
    items: list[RecetaItemCreate]

    @model_validator(mode="after")
    def validar_items(self):
        if not self.items:
            raise ValueError("La receta debe tener al menos un medicamento")
        return self


class RecetaResponse(BaseModel):
    id: uuid.UUID
    atencion_medica_id: uuid.UUID
    numero_receta: str
    estado: str
    items: list[RecetaItemOut]
    created_at: datetime


class CamaOut(BaseModel):
    id: uuid.UUID
    codigo: str
    nombre: str
    tipo_cama: str | None
    sala_texto: str | None
    piso_texto: str | None
    model_config = {"from_attributes": True}


class HospitalizacionCreate(BaseModel):
    cama_id: uuid.UUID
    especialidad_ingreso_id: uuid.UUID | None = None
    diagnostico_ingreso_id: uuid.UUID | None = None

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


class HospitalizacionResponse(BaseModel):
    id: uuid.UUID
    atencion_medica_id: uuid.UUID
    numero_hospitalizacion: str
    cama_codigo: str
    cama_nombre: str
    especialidad_ingreso_nombre: str | None
    diagnostico_ingreso_codigo: str | None
    diagnostico_ingreso_descripcion: str | None
    fecha_ingreso: datetime
    fecha_alta: datetime | None
    estado: str


class ExamenLaboratorioOut(BaseModel):
    id: uuid.UUID
    codigo: str | None
    nombre: str
    categoria: str | None
    tipo_muestra: str | None
    requiere_ayuno: bool
    model_config = {"from_attributes": True}


class OrdenLaboratorioCreate(BaseModel):
    examen_ids: list[uuid.UUID]
    indicacion_clinica: str | None = None

    @model_validator(mode="after")
    def validar_examenes(self):
        if not self.examen_ids:
            raise ValueError("La orden debe tener al menos un examen")
        return self


class OrdenLaboratorioItemOut(BaseModel):
    id: uuid.UUID
    examen_id: uuid.UUID
    codigo: str | None
    nombre: str
    categoria: str | None
    tipo_muestra: str | None


class OrdenLaboratorioResponse(BaseModel):
    id: uuid.UUID
    atencion_medica_id: uuid.UUID
    numero_orden: str
    indicacion_clinica: str | None
    estado: str
    items: list[OrdenLaboratorioItemOut]
    created_at: datetime


class ExamenImagenOut(BaseModel):
    id: uuid.UUID
    codigo: str | None
    nombre: str
    modalidad: str
    parte_cuerpo: str | None
    requiere_contraste: bool
    model_config = {"from_attributes": True}


class OrdenImagenCreate(BaseModel):
    examen_ids: list[uuid.UUID]
    indicacion_clinica: str | None = None

    @model_validator(mode="after")
    def validar_examenes(self):
        if not self.examen_ids:
            raise ValueError("La orden debe tener al menos un examen")
        return self


class OrdenImagenItemOut(BaseModel):
    id: uuid.UUID
    examen_id: uuid.UUID
    codigo: str | None
    nombre: str
    modalidad: str
    parte_cuerpo: str | None


class OrdenImagenResponse(BaseModel):
    id: uuid.UUID
    atencion_medica_id: uuid.UUID
    numero_orden: str
    indicacion_clinica: str | None
    estado: str
    items: list[OrdenImagenItemOut]
    created_at: datetime


class InterconsultaCreate(BaseModel):
    especialidad_destino_id: uuid.UUID
    diagnostico_id: uuid.UUID | None = None
    motivo: str
    urgente: bool = False

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


class InterconsultaResponse(BaseModel):
    id: uuid.UUID
    atencion_medica_id: uuid.UUID
    paciente_nombre: str
    paciente_dni: str | None
    especialidad_destino_id: uuid.UUID
    especialidad_destino_nombre: str
    diagnostico_codigo: str | None
    diagnostico_descripcion: str | None
    motivo: str
    urgente: bool
    estado: str
    cita_generada_id: uuid.UUID | None
    created_at: datetime


class ProgramarInterconsultaRequest(BaseModel):
    programacion_medica_id: uuid.UUID
    hora_inicio: str
    hora_fin: str

class ReferenciaCreate(BaseModel):
    codigo_renipress_destino: str | None = None
    nombre_ipress_destino: str | None = None
    tenant_destino_id: uuid.UUID | None = None
    especialidad_destino: str | None = None
    diagnostico_id: uuid.UUID | None = None
    motivo: str

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data

    @model_validator(mode="after")
    def validar_destino(self):
        if not self.tenant_destino_id and not self.nombre_ipress_destino:
            raise ValueError("Debe indicar un hospital de destino o el nombre del IPRESS externo")
        return self


class TenantOut(BaseModel):
    id: uuid.UUID
    name: str
    model_config = {"from_attributes": True}


class ReferenciaResponse(BaseModel):
    id: uuid.UUID
    atencion_medica_id: uuid.UUID
    numero_referencia: str
    codigo_renipress_destino: str | None
    nombre_ipress_destino: str | None
    tenant_destino_id: uuid.UUID | None
    tenant_destino_nombre: str | None
    especialidad_destino: str | None
    diagnostico_codigo: str | None
    diagnostico_descripcion: str | None
    motivo: str
    estado: str
    created_at: datetime
