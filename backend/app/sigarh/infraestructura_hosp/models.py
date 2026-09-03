import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Piso(Base):
    """Pisos del hospital."""
    __tablename__ = "sigarh_pisos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    orden: Mapped[int] = mapped_column(Integer, default=0)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    salas: Mapped[list["Sala"]] = relationship(back_populates="piso", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Piso {self.nombre}>"


class Sala(Base):
    """Salas dentro de cada piso del hospital."""
    __tablename__ = "sigarh_salas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    piso_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_pisos.id", ondelete="SET NULL"), nullable=True)
    servicio_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_servicios.id", ondelete="SET NULL"), nullable=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    capacidad: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    piso: Mapped["Piso"] = relationship(back_populates="salas")
    camas: Mapped[list["Cama"]] = relationship(back_populates="sala", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Sala {self.nombre}>"


class Cama(Base):
    """Camas disponibles por sala del hospital."""
    __tablename__ = "sigarh_camas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    sala_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_salas.id", ondelete="SET NULL"), nullable=True)
    piso_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_pisos.id", ondelete="SET NULL"), nullable=True)
    servicio_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_servicios.id", ondelete="SET NULL"), nullable=True)
    codigo: Mapped[str] = mapped_column(String(50))
    nombre: Mapped[str] = mapped_column(String(255))
    sala_texto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    piso_texto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    servicio_texto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tipo_cama: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estado: Mapped[str] = mapped_column(String(30), default="DISPONIBLE")  # DISPONIBLE, OCUPADA, MANTENIMIENTO, RESERVADA
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sala: Mapped["Sala"] = relationship(back_populates="camas")

    def __repr__(self) -> str:
        return f"<Cama {self.codigo} - {self.estado}>"