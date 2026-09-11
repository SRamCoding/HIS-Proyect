import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, field_validator, model_validator

from app.sigarh.mantenimiento.schemas import validar_password

PANELES = ("admin", "app", "sigarh", "portal")


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
    panel: Literal["admin", "app", "sigarh", "portal"]
    tenant_id: uuid.UUID | None = None

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
        return v.strip().lower()

    @field_validator("role")
    @classmethod
    def _v_role(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("El rol es requerido")
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
    panel: Literal["admin", "app", "sigarh", "portal"] | None = None
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
        return v.strip().lower() if v else v

    @field_validator("password", mode="before")
    @classmethod
    def _v_password(cls, v):
        return validar_password(v) if v else v
