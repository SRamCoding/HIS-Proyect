import uuid
from datetime import datetime
from pydantic import BaseModel, model_validator


class AcompananteData(BaseModel):
    acompanante_nombre: str | None = None
    acompanante_documento: str | None = None
    acompanante_parentesco: str | None = None
    acompanante_telefono: str | None = None
    acompanante_direccion: str | None = None


class AdmisionEmergenciaCreate(AcompananteData):
    patient_id: uuid.UUID
    servicio_emergencia: str = "Emergencia General"
    fuente_financiamiento: str | None = None
    observaciones: str | None = None

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


class AdmisionEmergenciaResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    paciente_nombre: str
    paciente_dni: str | None
    paciente_edad: int
    paciente_hc: str | None
    numero_cuenta: str
    servicio_emergencia: str
    fuente_financiamiento: str | None
    acompanante_nombre: str | None
    acompanante_parentesco: str | None
    acompanante_telefono: str | None
    observaciones: str | None
    estado: str
    paso_triaje: bool
    created_at: datetime


class TriajeEmergenciaCreate(BaseModel):
    prioridad: str
    pulso: int | None = None
    temperatura: float | None = None
    presion_sistolica: int | None = None
    presion_diastolica: int | None = None
    frecuencia_cardiaca: int | None = None
    frecuencia_respiratoria: int | None = None
    peso: float | None = None
    talla: float | None = None
    saturacion_o2: float | None = None
    observacion: str | None = None

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


class TriajeEmergenciaResponse(TriajeEmergenciaCreate):
    id: uuid.UUID
    admision_id: uuid.UUID
    imc: float | None
    created_at: datetime


class EmergenciaDiagnosticoCreate(BaseModel):
    diagnostico_cie10_id: uuid.UUID
    tipo: str = "definitivo"


class EmergenciaDiagnosticoOut(BaseModel):
    id: uuid.UUID
    diagnostico_cie10_id: uuid.UUID
    codigo_cie10: str
    descripcion: str
    tipo: str


class AtencionEmergenciaCreate(BaseModel):
    motivo_consulta: str
    examen_clinico: str | None = None
    plan_tratamiento: str | None = None
    observaciones: str | None = None
    destino_atencion: str = "AMBULATORIA"
    diagnosticos: list[EmergenciaDiagnosticoCreate] = []

    @model_validator(mode="after")
    def validar_destino(self):
        permitidos = {"AMBULATORIA", "HOSPITALIZACION", "REFERENCIA", "INTERCONSULTA", "ALTA", "FALLECIDO"}
        self.destino_atencion = self.destino_atencion.upper()
        if self.destino_atencion not in permitidos:
            raise ValueError("Destino de atención no válido")
        return self

    @model_validator(mode="before")
    @classmethod
    def vacios_a_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


class AtencionEmergenciaUpdate(BaseModel):
    motivo_consulta: str | None = None
    examen_clinico: str | None = None
    plan_tratamiento: str | None = None
    observaciones: str | None = None
    destino_atencion: str | None = None

    @model_validator(mode="after")
    def validar_destino(self):
        if self.destino_atencion is not None:
            self.destino_atencion = self.destino_atencion.upper()
            if self.destino_atencion not in {"AMBULATORIA", "HOSPITALIZACION", "REFERENCIA", "INTERCONSULTA", "ALTA", "FALLECIDO"}:
                raise ValueError("Destino de atención no válido")
        return self


class DestinoEmergenciaResponse(BaseModel):
    id: uuid.UUID
    atencion_id: uuid.UUID
    admision_id: uuid.UUID
    numero_cuenta: str
    paciente_nombre: str
    paciente_dni: str | None
    destino: str
    estado: str
    observacion: str | None
    created_at: datetime
    resolved_at: datetime | None


class ResolverDestinoRequest(BaseModel):
    observacion: str | None = None


class AtencionEmergenciaResponse(BaseModel):
    id: uuid.UUID
    admision_id: uuid.UUID
    paciente_nombre: str
    paciente_dni: str | None
    motivo_consulta: str
    examen_clinico: str | None
    plan_tratamiento: str | None
    observaciones: str | None
    destino_atencion: str
    estado: str
    firmado_at: datetime | None
    diagnosticos: list[EmergenciaDiagnosticoOut]
    triaje: dict | None
    created_at: datetime
