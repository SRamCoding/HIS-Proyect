# backend/app/admin/notificaciones/schemas.py
import uuid
from datetime import datetime
from pydantic import BaseModel


class NotificacionResponse(BaseModel):
    id: uuid.UUID
    titulo: str
    cuerpo: str | None
    nivel: str
    link: str | None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
