import uuid
from datetime import datetime
from pydantic import BaseModel


class HospitalLevelCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    color: str | None = None
    default_modules: list[str] = []
    default_roles: list[str] = []
    sort_order: int = 0


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
