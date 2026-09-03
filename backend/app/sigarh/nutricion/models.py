import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class RacionNutricion(Base):
    """Registro de raciones de alimentos para pacientes."""
    __tablename__ = "sigarh_raciones_nutricion"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    dni: Mapped[str] = mapped_column(String(8), index=True)
    nombre_completo: Mapped[str] = mapped_column(String(255))
    dependencia: Mapped[str] = mapped_column(String(255))
    tipo_racion: Mapped[str] = mapped_column(String(100))  # desayuno, almuerzo, cena, etc.
    fecha: Mapped[date] = mapped_column(Date)
    entregado: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_entrega: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    observacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<RacionNutricion {self.dni} {self.fecha} {self.tipo_racion}>"


class CambioTurnoNutricion(Base):
    """Registro de cambio de turno del personal de nutricion."""
    __tablename__ = "sigarh_cambios_turno_nutricion"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    fecha: Mapped[date] = mapped_column(Date)
    turno_saliente: Mapped[str] = mapped_column(String(100))
    turno_entrante: Mapped[str] = mapped_column(String(100))
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    raciones_entregadas: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CambioTurnoNutricion {self.fecha}>"