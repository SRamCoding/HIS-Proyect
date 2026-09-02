import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Any


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
    active_modules: list[str] = []  # códigos de módulos a activar


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


class ModuleBase(BaseModel):
    code: str
    name: str
    description: str | None = None
    category: str
    sort_order: int = 0


class ModuleResponse(ModuleBase):
    id: uuid.UUID
    is_active: bool

    model_config = {"from_attributes": True}