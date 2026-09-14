import uuid
from pydantic import BaseModel, field_validator
import re


class SystemRoleCreate(BaseModel):
    name: str
    label: str
    panel: str
    required_module: str | None = None
    allowed_modules: list[str] = []
    sort_order: int = 0

    @field_validator('name')
    @classmethod
    def codigo_normalizado(cls, value):
        value = value.strip().lower()
        if not re.fullmatch(r'[a-z][a-z0-9_]{0,99}', value):
            raise ValueError('Use letras, números y guion bajo para el código del rol')
        return value


class SystemRoleResponse(SystemRoleCreate):
    allowed_modules: list[str] | None = None
    id: uuid.UUID
    is_active: bool

    model_config = {"from_attributes": True}
