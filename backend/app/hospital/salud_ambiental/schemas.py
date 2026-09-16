import uuid
from datetime import datetime
from pydantic import BaseModel, model_validator

_TIPOS_MUERTE = {"NATURAL", "VIOLENTA"}


class CertificadoDefuncionCreateIn(BaseModel):
    atencion_emergencia_id: uuid.UUID | None = None
    hospitalizacion_id: uuid.UUID | None = None
    patient_id: uuid.UUID | None = None
    medico_certificador_id: uuid.UUID
    fecha_defuncion: datetime
    lugar_defuncion: str
    tipo_muerte: str
    causa_a_id: uuid.UUID
    causa_b_id: uuid.UUID | None = None
    causa_c_id: uuid.UUID | None = None
    causa_d_id: uuid.UUID | None = None
    requiere_necropsia_legal: bool | None = None
    observaciones: str | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.atencion_emergencia_id and self.hospitalizacion_id:
            raise ValueError("Indique como máximo un origen: atencion_emergencia_id u hospitalizacion_id")
        if not self.atencion_emergencia_id and not self.hospitalizacion_id and not self.patient_id:
            raise ValueError("Indique un origen clínico (atencion_emergencia_id/hospitalizacion_id) o directamente patient_id")
        if self.tipo_muerte not in _TIPOS_MUERTE:
            raise ValueError("tipo_muerte debe ser NATURAL o VIOLENTA")
        if self.requiere_necropsia_legal is None:
            self.requiere_necropsia_legal = self.tipo_muerte == "VIOLENTA"
        return self
