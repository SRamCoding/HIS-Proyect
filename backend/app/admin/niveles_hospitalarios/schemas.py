import uuid
from datetime import datetime
from pydantic import BaseModel


class HospitalLevelCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    color: str | None = None
    default_modules: dict = {}
    default_roles: dict = {}
    sort_order: int = 0


class HospitalLevelUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    description: str | None = None
    color: str | None = None
    default_modules: dict | None = None
    default_roles: dict | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class HospitalLevelResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    description: str | None = None
    color: str | None = None
    default_modules: dict | None = None
    sort_order: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
