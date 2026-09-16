import uuid
from datetime import date
from pydantic import BaseModel, model_validator

_TIPOS_FICHA = {"COVID", "CANCER", "DIABETES", "DENGUE", "LEPTOSPIROSIS"}


class DatosCovid(BaseModel):
    fecha_inicio_sintomas: date
    sintomas: list[str] = []
    contacto_caso_confirmado: bool = False
    tipo_prueba: str | None = None  # PCR, ANTIGENA, SEROLOGICA
    resultado_prueba: str = "PENDIENTE"  # POSITIVO, NEGATIVO, PENDIENTE
    fecha_prueba: date | None = None
    condicion: str = "AMBULATORIO"  # AMBULATORIO, HOSPITALIZADO, UCI, FALLECIDO
    requiere_aislamiento: bool = False


class DatosDengue(BaseModel):
    fecha_inicio_sintomas: date
    signos_alarma: list[str] = []  # dolor_abdominal, vomitos_persistentes, sangrado_mucosas, letargia, hepatomegalia...
    clasificacion: str  # SIN_SENALES_ALARMA, CON_SENALES_ALARMA, GRAVE
    prueba_serologica: str | None = None  # NS1, IGM, IGG
    resultado_prueba: str = "PENDIENTE"
    zona_probable_infeccion: str | None = None
    plaquetas: int | None = None
    hematocrito: float | None = None


class DatosLeptospirosis(BaseModel):
    fecha_inicio_sintomas: date
    exposicion_agua_contaminada: bool = False
    exposicion_roedores: bool = False
    ocupacion_riesgo: str | None = None
    sintomas: list[str] = []  # fiebre, mialgias, ictericia, cefalea, conjuntivitis...
    prueba_diagnostica: str | None = None
    resultado_prueba: str = "PENDIENTE"


class DatosDiabetes(BaseModel):
    tipo_diabetes: str  # TIPO_1, TIPO_2, GESTACIONAL
    fecha_diagnostico: date
    glucosa_ayunas: float | None = None
    hba1c: float | None = None
    imc: float | None = None
    complicaciones: list[str] = []  # retinopatia, nefropatia, neuropatia, pie_diabetico
    tratamiento: str | None = None  # INSULINA, METFORMINA, OTROS, DIETA_Y_EJERCICIO


class DatosCancer(BaseModel):
    sitio_primario: str
    estadio: str | None = None  # I, II, III, IV
    fecha_diagnostico: date
    metodo_diagnostico: str  # HISTOPATOLOGICO, CITOLOGICO, CLINICO, IMAGEN
    tratamiento_indicado: list[str] = []  # CIRUGIA, QUIMIOTERAPIA, RADIOTERAPIA, PALIATIVO
    habito_tabaco: bool = False
    antecedente_familiar: bool = False


_SCHEMAS_POR_TIPO = {
    "COVID": DatosCovid, "DENGUE": DatosDengue, "LEPTOSPIROSIS": DatosLeptospirosis,
    "DIABETES": DatosDiabetes, "CANCER": DatosCancer,
}


class FichaCreateIn(BaseModel):
    atencion_medica_id: uuid.UUID | None = None
    atencion_emergencia_id: uuid.UUID | None = None
    patient_id: uuid.UUID | None = None
    diagnostico_cie10_id: uuid.UUID | None = None
    medico_notificante_id: uuid.UUID
    tipo_ficha: str
    fecha_notificacion: date | None = None
    datos_clinicos: dict
    observaciones: str | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.atencion_medica_id and self.atencion_emergencia_id:
            raise ValueError("Indique como máximo un origen: atencion_medica_id o atencion_emergencia_id")
        if not self.atencion_medica_id and not self.atencion_emergencia_id and not self.patient_id:
            raise ValueError("Indique un origen clínico o directamente patient_id")
        if self.tipo_ficha not in _TIPOS_FICHA:
            raise ValueError(f"tipo_ficha debe ser uno de: {', '.join(sorted(_TIPOS_FICHA))}")
        schema = _SCHEMAS_POR_TIPO[self.tipo_ficha]
        try:
            validado = schema.model_validate(self.datos_clinicos)
        except Exception as exc:
            raise ValueError(f"datos_clinicos inválido para ficha {self.tipo_ficha}: {exc}") from exc
        self.datos_clinicos = validado.model_dump(mode="json")
        return self
