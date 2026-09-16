import uuid
from datetime import datetime
from pydantic import BaseModel


class ModuleDependencyCreate(BaseModel):
    module_code: str
    depends_on_code: str
    is_required: bool = True


class ModuleDependencyResponse(ModuleDependencyCreate):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ActiveToggle(BaseModel):
    is_active: bool
