import uuid
from datetime import datetime, date
from pydantic import BaseModel, model_validator


class ProgramacionMedicaCreate(BaseModel):
    medico_id: uuid.UUID
    servicio_id: uuid.UUID
    especialidad_id: uuid.UUID | None = None
    fecha: date
    turno: str
    hora_inicio: str
    hora_fin: str
    tiempo_promedio_atencion: int = 15
    tipo_servicio: str = "CONSULTORIO_EXTERNO"
    mostrar_en_consultorio: bool = False
    descripcion: str | None = None

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


class ProgramacionMedicaUpdate(BaseModel):
    fecha: date | None = None
    turno: str | None = None
    hora_inicio: str | None = None
    hora_fin: str | None = None
    tiempo_promedio_atencion: int | None = None
    mostrar_en_consultorio: bool | None = None
    descripcion: str | None = None
    estado: str | None = None


class ProgramacionMedicaResponse(BaseModel):
    id: uuid.UUID
    medico_id: uuid.UUID
    medico_nombre: str
    servicio_id: uuid.UUID | None
    servicio_nombre: str | None
    especialidad_id: uuid.UUID | None
    especialidad_nombre: str | None
    fecha: date
    turno: str
    hora_inicio: str
    hora_fin: str
    tiempo_promedio_atencion: int
    tipo_servicio: str
    mostrar_en_consultorio: bool
    descripcion: str | None
    estado: str
    created_at: datetime

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


class TriajeCreate(BaseModel):
    pulso: int | None = None
    temperatura: float | None = None
    presion_sistolica: int | None = None
    presion_diastolica: int | None = None
    frecuencia_cardiaca: int | None = None
    frecuencia_respiratoria: int | None = None
    peso: float | None = None
    talla: float | None = None
    perimetro_abdominal: float | None = None
    perimetro_cefalico: float | None = None
    saturacion_o2: float | None = None

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


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


class TriajeUpdate(BaseModel):
    pulso: int | None = None
    temperatura: float | None = None
    presion_sistolica: int | None = None
    presion_diastolica: int | None = None
    frecuencia_cardiaca: int | None = None
    frecuencia_respiratoria: int | None = None
    peso: float | None = None
    talla: float | None = None
    perimetro_abdominal: float | None = None
    perimetro_cefalico: float | None = None
    saturacion_o2: float | None = None



class DiagnosticoCIE10Out(BaseModel):
    id: uuid.UUID
    codigo_cie10: str
    descripcion: str
    model_config = {"from_attributes": True}


class AtencionDiagnosticoCreate(BaseModel):
    diagnostico_cie10_id: uuid.UUID
    tipo: str = "definitivo"


class AtencionDiagnosticoOut(BaseModel):
    id: uuid.UUID
    diagnostico_cie10_id: uuid.UUID
    codigo_cie10: str
    descripcion: str
    tipo: str
    model_config = {"from_attributes": True}


class AtencionMedicaCreate(BaseModel):
    motivo_consulta: str
    examen_clinico: str | None = None
    plan_tratamiento: str | None = None
    observaciones: str | None = None
    destino_atencion: str = "ALTA"
    indicaciones_alta: str | None = None
    diagnosticos: list[AtencionDiagnosticoCreate] = []

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


class AtencionMedicaUpdate(BaseModel):
    motivo_consulta: str | None = None
    examen_clinico: str | None = None
    plan_tratamiento: str | None = None
    observaciones: str | None = None
    destino_atencion: str | None = None
    indicaciones_alta: str | None = None


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
    # antecedentes (leidos desde Patient, solo lectura aqui)
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
    cantidad: int
    dosis: str | None = None
    frecuencia: str | None = None
    duracion_dias: int | None = None
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