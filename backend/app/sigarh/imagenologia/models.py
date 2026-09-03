import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ExamenImagenologia(Base):
    """Catalogo de examenes de imagenologia."""
    __tablename__ = "sigarh_examenes_imagenologia"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    modalidad: Mapped[str] = mapped_column(String(100))  # Rayos X, Ecografia, TAC, RMN, etc.
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nombre: Mapped[str] = mapped_column(String(255))
    parte_cuerpo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duracion_min: Mapped[int] = mapped_column(Integer, default=30)
    precio: Mapped[float] = mapped_column(Float, default=0.0)
    requiere_contraste: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ExamenImagenologia {self.codigo} - {self.nombre}>"