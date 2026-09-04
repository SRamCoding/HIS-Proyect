import uuid
from pydantic import BaseModel


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
