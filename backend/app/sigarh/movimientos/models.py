import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Vacacion(Base):
    """Justificaciones y vacaciones del personal."""
    __tablename__ = "sigarh_vacaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    empleado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    motivo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_motivos_justificacion.id", ondelete="SET NULL"), nullable=True)
    tipo: Mapped[str] = mapped_column(String(30), default="vacacion")  # vacacion, justificacion
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date] = mapped_column(Date)
    dias: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
    documento_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, aprobado, rechazado
    mes_actual: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Vacacion {self.empleado_id} {self.fecha_inicio}>"


class Licencia(Base):
    """Tramite de licencias del personal."""
    __tablename__ = "sigarh_licencias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    empleado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    motivo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_motivos_justificacion.id", ondelete="SET NULL"), nullable=True)
    fecha_tramite: Mapped[date] = mapped_column(Date, default=date.today)
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date] = mapped_column(Date)
    dias: Mapped[int | None] = mapped_column(Integer, nullable=True)
    documento_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, aprobado, rechazado
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Licencia {self.empleado_id} {self.fecha_inicio}>"


class CambioTurno(Base):
    """Cambio de turno entre empleados."""
    __tablename__ = "sigarh_cambios_turno"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    servicio_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_servicios.id", ondelete="SET NULL"), nullable=True)
    numero_documento: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Solicitante
    solicitante_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    fecha_original: Mapped[date] = mapped_column(Date)
    modalidad_solicitante: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Aceptante
    aceptante_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="SET NULL"), nullable=True)
    fecha_reemplazo: Mapped[date] = mapped_column(Date)
    modalidad_aceptante: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CambioTurno {self.solicitante_id}>"


class Papeleta(Base):
    """Papeletas de permiso del personal."""
    __tablename__ = "sigarh_papeletas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    empleado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    motivo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_motivos_justificacion.id", ondelete="SET NULL"), nullable=True)
    fecha_tramite: Mapped[date] = mapped_column(Date, default=date.today)
    documento_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    mes_actual: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Papeleta {self.empleado_id}>"