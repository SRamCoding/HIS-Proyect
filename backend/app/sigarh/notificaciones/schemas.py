# backend/app/sigarh/notificaciones/schemas.py
import uuid
from datetime import datetime
from pydantic import BaseModel


class NotificacionSigarhResponse(BaseModel):
    id: uuid.UUID
    titulo: str
    cuerpo: str | None
    nivel: str
    link: str | None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
