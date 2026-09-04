import uuid
from datetime import datetime
from pydantic import BaseModel


class HospitalListItem(BaseModel):
    id: uuid.UUID
    name: str
    domain: str
    hospital_level: str | None
    is_active: bool
    active_modules: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ModuleToggle(BaseModel):
    tenant_id: uuid.UUID
    module_codes: list[str]
