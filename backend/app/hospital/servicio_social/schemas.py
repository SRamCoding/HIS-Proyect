import uuid
from datetime import date, datetime
from pydantic import BaseModel, model_validator

_TIPOS_VIVIENDA = {"PROPIA", "ALQUILADA", "ALOJADA", "ASENTAMIENTO_HUMANO", "SIN_VIVIENDA"}
_CLASIFICACIONES = {"POBRE_EXTREMO", "POBRE", "NO_POBRE"}
_FACTORES_RIESGO = {"violencia_familiar", "abandono", "situacion_calle", "adulto_mayor_solo",
                     "discapacidad_sin_soporte", "menor_en_riesgo"}
_ENTIDADES = {"MIMP", "CEM", "INABIF", "DEMUNA", "OTRO"}
_TIPOS_GESTION = {"VISITA_DOMICILIARIA", "LLAMADA_TELEFONICA", "COORDINACION_INTERINSTITUCIONAL",
                   "ENTREVISTA", "GESTION_APOYO_SOCIAL", "OTRO"}


class EvaluacionCreateIn(BaseModel):
    patient_id: uuid.UUID
    atencion_medica_id: uuid.UUID | None = None
    atencion_emergencia_id: uuid.UUID | None = None
    hospitalizacion_id: uuid.UUID | None = None
    trabajador_social_id: uuid.UUID
    fecha_evaluacion: date | None = None
    tipo_vivienda: str | None = None
    clasificacion_socioeconomica: str | None = None
    red_apoyo_familiar: str | None = None
    factores_riesgo: list[str] = []
    requiere_derivacion_externa: bool = False
    entidad_derivacion: str | None = None
    recomendaciones: str | None = None

    @model_validator(mode="after")
    def _v(self):
        if sum(o is not None for o in (self.atencion_medica_id, self.atencion_emergencia_id, self.hospitalizacion_id)) > 1:
            raise ValueError("Indique como máximo un origen clínico")
        if self.tipo_vivienda is not None and self.tipo_vivienda not in _TIPOS_VIVIENDA:
            raise ValueError(f"tipo_vivienda debe ser uno de: {', '.join(sorted(_TIPOS_VIVIENDA))}")
        if self.clasificacion_socioeconomica is not None and self.clasificacion_socioeconomica not in _CLASIFICACIONES:
            raise ValueError(f"clasificacion_socioeconomica debe ser uno de: {', '.join(sorted(_CLASIFICACIONES))}")
        invalidos = set(self.factores_riesgo) - _FACTORES_RIESGO
        if invalidos:
            raise ValueError(f"factores_riesgo inválidos: {', '.join(sorted(invalidos))}")
        if self.requiere_derivacion_externa and not self.entidad_derivacion:
            raise ValueError("Indique la entidad de derivación (MIMP, CEM, INABIF, DEMUNA u OTRO)")
        if self.entidad_derivacion is not None and self.entidad_derivacion not in _ENTIDADES:
            raise ValueError(f"entidad_derivacion debe ser uno de: {', '.join(sorted(_ENTIDADES))}")
        return self


class CerrarEvaluacionIn(BaseModel):
    recomendaciones: str | None = None


class GestionCreateIn(BaseModel):
    tipo_gestion: str
    descripcion: str
    fecha: datetime | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.tipo_gestion not in _TIPOS_GESTION:
            raise ValueError(f"tipo_gestion debe ser uno de: {', '.join(sorted(_TIPOS_GESTION))}")
        return self
