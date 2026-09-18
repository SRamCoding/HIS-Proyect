"""Mi perfil (panel hospitalario). Datos propios de la cuenta y, si está
vinculada a un empleado, su ficha profesional (RRHH) de solo lectura.
"""
from pydantic import BaseModel, field_validator

from app.sigarh.mantenimiento.schemas import validar_password, validar_email


class EspecialidadPerfil(BaseModel):
    nombre: str
    numero_rne: str | None
    validado: bool


class EmpleadoPerfil(BaseModel):
    nombre_completo: str
    dni: str
    celular: str | None
    correo: str | None
    cargo_laboral: str | None
    titulo_profesional: str | None
    profesion_nombre: str | None
    numero_cmp: str | None
    numero_colegiatura: str | None
    habilitado_colegio: bool
    especialidades: list[EspecialidadPerfil]


class PerfilResponse(BaseModel):
    name: str
    email: str
    role: str
    empleado: EmpleadoPerfil | None = None


class PerfilUpdate(BaseModel):
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
