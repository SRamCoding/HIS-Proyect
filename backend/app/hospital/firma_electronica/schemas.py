import uuid
from pydantic import BaseModel, model_validator

_TIPOS_DOCUMENTO = {"ATENCION_MEDICA", "ATENCION_EMERGENCIA"}


class FirmarDocumentoIn(BaseModel):
    documento_tipo: str
    documento_id: uuid.UUID

    @model_validator(mode="after")
    def _v(self):
        if self.documento_tipo not in _TIPOS_DOCUMENTO:
            raise ValueError("documento_tipo debe ser ATENCION_MEDICA o ATENCION_EMERGENCIA")
        return self
