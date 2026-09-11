import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator

from app.sigarh.mantenimiento.schemas import validar_password


class TenantBase(BaseModel):
    name: str
    domain: str
    ruc: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    hospital_level: str | None = None
    mission: str | None = None
    vision: str | None = None
    values: str | None = None
    schedule: dict | None = None
    social_media: dict | None = None


class TenantCreate(TenantBase):
    active_modules: list[str] = []
    admin_name: str | None = None
    admin_email: str | None = None
    admin_password: str | None = None
    sigarh_name: str | None = None
    sigarh_email: str | None = None
    sigarh_password: str | None = None

    @field_validator("admin_password", "sigarh_password")
    @classmethod
    def _v_password(cls, v):
        return validar_password(v) if v else v


class TenantUpdate(TenantBase):
    name: str | None = None
    domain: str | None = None
    active_modules: list[str] | None = None


class TenantResponse(TenantBase):
    id: uuid.UUID
    schema_name: str
    is_active: bool
    active_modules: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}
