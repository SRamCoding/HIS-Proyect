# backend/app/admin/notificaciones/models.py
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Notificacion(Base):
    """Notificaciones del panel Admin (campana del header). Es una bandeja
    compartida por todos los administradores -- con pocas cuentas admin en
    la practica, no hace falta un estado de lectura por usuario."""
    __tablename__ = "notificaciones_admin"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo: Mapped[str] = mapped_column(String(255))
    cuerpo: Mapped[str | None] = mapped_column(Text, nullable=True)
    nivel: Mapped[str] = mapped_column(String(20), default="info")  # info, exito, alerta, error
    link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
