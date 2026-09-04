import uuid
from datetime import datetime
from pydantic import BaseModel


class UserListItem(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: str
    panel: str
    tenant_id: uuid.UUID | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str
    panel: str
    tenant_id: uuid.UUID | None = None
