import uuid
from datetime import datetime
from pydantic import BaseModel, model_validator


class AsignacionCreateIn(BaseModel):
    tiempo_procedimiento_id: uuid.UUID
    empleado_id: uuid.UUID


class AtencionProcedimientoCreateIn(BaseModel):
    atencion_medica_id: uuid.UUID | None = None
    atencion_emergencia_id: uuid.UUID | None = None
    hospitalizacion_id: uuid.UUID | None = None
    patient_id: uuid.UUID | None = None
    tiempo_procedimiento_id: uuid.UUID
    empleado_ejecutor_id: uuid.UUID
    fecha_hora: datetime | None = None
    consentimiento_informado: bool = False

    @model_validator(mode="after")
    def _v(self):
        origenes = (self.atencion_medica_id, self.atencion_emergencia_id, self.hospitalizacion_id)
        if sum(o is not None for o in origenes) > 1:
            raise ValueError("Indique como máximo un origen clínico")
        if not any(origenes) and not self.patient_id:
            raise ValueError("Indique un origen clínico o directamente patient_id")
        return self


class RealizarAtencionIn(BaseModel):
    hallazgos: str
    complicaciones: str | None = None


class CancelarAtencionIn(BaseModel):
    motivo: str
