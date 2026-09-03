import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Seguro(Base):
    """Compañias o tipos de seguro registrados."""
    __tablename__ = "sigarh_seguros"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tipo_entidad: Mapped[str | None] = mapped_column(String(100), nullable=True)
    requiere_fua: Mapped[bool] = mapped_column(Boolean, default=False)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    planes: Mapped[list["PlanSeguro"]] = relationship(back_populates="seguro", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Seguro {self.nombre}>"


class PlanSeguro(Base):
    """Planes y coberturas de un seguro."""
    __tablename__ = "sigarh_planes_seguro"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seguro_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_seguros.id", ondelete="CASCADE"))
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    precio_referencia: Mapped[float | None] = mapped_column(Float, nullable=True)
    detalle_cobertura: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    seguro: Mapped["Seguro"] = relationship(back_populates="planes")

    def __repr__(self) -> str:
        return f"<PlanSeguro {self.nombre}>"


class Caja(Base):
    """Cajas de cobro del area financiera."""
    __tablename__ = "sigarh_cajas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cajero_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="cerrada")  # abierta, cerrada
    monto_apertura: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Caja {self.nombre} - {self.estado}>"


class Tarifario(Base):
    """Tarifario de servicios y procedimientos."""
    __tablename__ = "sigarh_tarifario"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descripcion_servicio: Mapped[str] = mapped_column(String(255))
    tipo_servicio: Mapped[str | None] = mapped_column(String(100), nullable=True)
    especialidad_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_especialidades.id", ondelete="SET NULL"), nullable=True)
    seguro_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_seguros.id", ondelete="SET NULL"), nullable=True)
    precio: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Tarifario {self.descripcion_servicio} S/. {self.precio}>"