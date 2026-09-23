# backend/app/sigarh/perfil/schemas.py
from pydantic import BaseModel, field_validator

from app.sigarh.mantenimiento.schemas import validar_password, validar_email


class PerfilSigarhResponse(BaseModel):
    name: str | None
    email: str


class PerfilSigarhUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    current_password: str | None = None
    new_password: str | None = None

    @field_validator("name")
    @classmethod
    def _v_name(cls, v):
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El nombre es requerido")
        return v

    @field_validator("email")
    @classmethod
    def _v_email(cls, v):
        return validar_email(v) if v else v

    @field_validator("new_password", mode="before")
    @classmethod
    def _v_new_password(cls, v):
        return validar_password(v) if v else v
