import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ExamenLaboratorio(Base):
    """Catalogo de examenes de laboratorio."""
    __tablename__ = "sigarh_examenes_laboratorio"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nombre: Mapped[str] = mapped_column(String(255))
    categoria: Mapped[str | None] = mapped_column(String(100), nullable=True)   # Hematologia, Bioquimica, etc.
    tipo_muestra: Mapped[str | None] = mapped_column(String(100), nullable=True) # Sangre, Orina, Heces, etc.
    unidad_medida: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tiempo_resultado_horas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    precio: Mapped[float] = mapped_column(Float, default=0.0)
    valores_referencia: Mapped[str | None] = mapped_column(Text, nullable=True)
    requiere_ayuno: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ExamenLaboratorio {self.codigo} - {self.nombre}>"