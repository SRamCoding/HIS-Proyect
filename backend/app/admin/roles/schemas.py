import uuid
from pydantic import BaseModel


class SystemRoleCreate(BaseModel):
    name: str
    label: str
    panel: str
    required_module: str | None = None
    allowed_modules: list[str] = []
    sort_order: int = 0


class SystemRoleResponse(SystemRoleCreate):
    allowed_modules: list[str] | None = None
    id: uuid.UUID
    is_active: bool

    model_config = {"from_attributes": True}
