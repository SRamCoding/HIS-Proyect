# backend/app/admin/auditoria/schemas.py
import uuid
from datetime import datetime
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_name: str | None
    tenant_name: str | None
    action: str
    model: str | None
    model_id: str | None = None
    description: str | None
    old_values: dict | None = None
    new_values: dict | None = None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}