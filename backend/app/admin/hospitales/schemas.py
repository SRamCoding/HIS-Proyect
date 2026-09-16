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
    provisioning_status: str = "listo"
    provisioning_error: str | None = None

    model_config = {"from_attributes": True}


class ModuleToggle(BaseModel):
    tenant_id: uuid.UUID
    module_codes: list[str]


class ActiveToggle(BaseModel):
    is_active: bool
