import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, field_validator, model_validator

from app.sigarh.mantenimiento.schemas import validar_password, validar_email

PANELES = ("admin", "app", "sigarh", "portal")

# Roles reales del panel Hospitalario (App) + el rol de administrador del
# panel Admin. Antes solo se exigia que "role" no viniera vacio: cualquier
# texto pasaba, sin garantizar que fuera un rol que el sistema realmente
# reconoce (el frontend ya restringe esta misma lista en un <select>, pero
# la API la aceptaba igual si alguien mandaba otra cosa a mano).
ROLES_VALIDOS = {
    "administrador", "medico", "enfermera", "farmaceutico",
    "laboratorista", "cajero", "tuasis", "sigarh",
}


class UserListItem(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: str
    panel: str
    tenant_id: uuid.UUID | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str
    # "sigarh" no se crea aquí: esas cuentas necesitan un perfil/rol (UsuarioSigarh),
    # que solo se puede asignar desde SIGARH → Mantenimiento → Usuarios. Crear un
    # User con panel="sigarh" desde Admin deja una cuenta fantasma que nunca
    # puede iniciar sesión (el login de SIGARH no lee la tabla User).
    panel: Literal["admin", "app", "portal"]
    tenant_id: uuid.UUID | None = None
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def _v_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("El nombre es requerido")
        return v

    @field_validator("email")
    @classmethod
    def _v_email(cls, v):
        return validar_email(v)

    @field_validator("role")
    @classmethod
    def _v_role(cls, v):
        v = v.strip()
        if v not in ROLES_VALIDOS:
            raise ValueError(f"Rol inválido. Debe ser uno de: {', '.join(sorted(ROLES_VALIDOS))}")
        return v

    @field_validator("password", mode="before")
    @classmethod
    def _v_password(cls, v):
        return validar_password(v)

    @model_validator(mode="after")
    def _v_admin_role(self):
        # Una cuenta del panel admin siempre debe tener el rol real de
        # administrador: es lo único que separa a un superadmin de una
        # cuenta cualquiera (ver get_admin_user en core/dependencies.py).
        if self.panel == "admin" and self.role != "administrador":
            raise ValueError("Las cuentas del panel admin deben tener el rol 'administrador'")
        return self


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    role: str | None = None
    panel: Literal["admin", "app", "portal"] | None = None
    tenant_id: uuid.UUID | None = None
    is_active: bool | None = None

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

    @field_validator("role")
    @classmethod
    def _v_role(cls, v):
        if v is None:
            return v
        v = v.strip()
        if v not in ROLES_VALIDOS:
            raise ValueError(f"Rol inválido. Debe ser uno de: {', '.join(sorted(ROLES_VALIDOS))}")
        return v

    @field_validator("password", mode="before")
    @classmethod
    def _v_password(cls, v):
        return validar_password(v) if v else v
