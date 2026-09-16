import uuid
from datetime import date
from pydantic import BaseModel, model_validator

_GRUPOS = {"A", "B", "AB", "O"}
_RH = {"+", "-"}
_TIPOS_COMPONENTE = {"PAQUETE_GLOBULAR", "PLASMA_FRESCO_CONGELADO", "PLAQUETAS", "CRIOPRECIPITADO", "SANGRE_TOTAL"}
_URGENCIAS = {"RUTINA", "URGENTE", "EMERGENCIA"}


class DonanteCreateIn(BaseModel):
    dni: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: date
    sexo: str
    celular: str | None = None
    correo: str | None = None
    direccion: str | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.sexo not in {"M", "F"}:
            raise ValueError("sexo debe ser M o F")
        return self


class UnidadCreateIn(BaseModel):
    donante_id: uuid.UUID
    peso_kg: float | None = None
    hemoglobina_g_dl: float | None = None
    presion_sistolica: int | None = None
    presion_diastolica: int | None = None
    grupo_sanguineo: str
    factor_rh: str

    @model_validator(mode="after")
    def _v(self):
        if self.grupo_sanguineo not in _GRUPOS:
            raise ValueError("grupo_sanguineo debe ser A, B, AB u O")
        if self.factor_rh not in _RH:
            raise ValueError("factor_rh debe ser + o -")
        return self


class TamizajeIn(BaseModel):
    vih_reactivo: bool
    hbsag_reactivo: bool
    hcv_reactivo: bool
    sifilis_reactivo: bool
    chagas_reactivo: bool
    motivo_diferido: str | None = None  # para diferir por criterio clínico aun con tamizaje no reactivo


class FraccionarIn(BaseModel):
    tipos: list[str]

    @model_validator(mode="after")
    def _v(self):
        if not self.tipos:
            raise ValueError("Debe indicar al menos un tipo de componente a producir")
        for t in self.tipos:
            if t not in _TIPOS_COMPONENTE:
                raise ValueError(f"Tipo de componente inválido: {t}")
        return self


class SolicitudCreateIn(BaseModel):
    atencion_medica_id: uuid.UUID | None = None
    atencion_emergencia_id: uuid.UUID | None = None
    hospitalizacion_id: uuid.UUID | None = None
    medico_solicitante_id: uuid.UUID | None = None
    tipo_componente: str
    cantidad_unidades: int = 1
    grupo_sanguineo_paciente: str
    factor_rh_paciente: str
    urgencia: str = "RUTINA"
    motivo_clinico: str

    @model_validator(mode="after")
    def _v(self):
        origenes = [self.atencion_medica_id, self.atencion_emergencia_id, self.hospitalizacion_id]
        if sum(o is not None for o in origenes) != 1:
            raise ValueError("Debe indicar exactamente un origen: atencion_medica_id, atencion_emergencia_id u hospitalizacion_id")
        if self.tipo_componente not in _TIPOS_COMPONENTE:
            raise ValueError("tipo_componente inválido")
        if self.grupo_sanguineo_paciente not in _GRUPOS:
            raise ValueError("grupo_sanguineo_paciente debe ser A, B, AB u O")
        if self.factor_rh_paciente not in _RH:
            raise ValueError("factor_rh_paciente debe ser + o -")
        if self.urgencia not in _URGENCIAS:
            raise ValueError("urgencia debe ser RUTINA, URGENTE o EMERGENCIA")
        if self.cantidad_unidades < 1:
            raise ValueError("cantidad_unidades debe ser al menos 1")
        return self


class AsignarComponenteIn(BaseModel):
    componente_id: uuid.UUID


class PruebaCruzadaIn(BaseModel):
    resultado: str
    observaciones: str | None = None

    @model_validator(mode="after")
    def _v(self):
        if self.resultado not in {"compatible", "incompatible"}:
            raise ValueError("resultado debe ser compatible o incompatible")
        return self


class AnularSolicitudIn(BaseModel):
    motivo: str
