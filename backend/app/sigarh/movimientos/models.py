import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


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
    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revisado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revisado_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    motivo_rechazo: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CambioTurno {self.solicitante_id}>"


class Papeleta(Base):
    """Papeletas de salida del personal durante la jornada.

    El motivo es una lista fija (no viene de Motivos de Justificación):
    asuntos_particulares, comision, salud, tramite_personal, otro.
    """
    __tablename__ = "sigarh_papeletas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    empleado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    motivo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    numero_documento: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fecha_tramite: Mapped[date] = mapped_column(Date, default=date.today)
    documento_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, aprobado, rechazado
    hora_salida: Mapped[str | None] = mapped_column(String(5), nullable=True)   # se fija al aprobar
    hora_retorno: Mapped[str | None] = mapped_column(String(5), nullable=True)  # se fija al registrar retorno
    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revisado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revisado_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    motivo_rechazo: Mapped[str | None] = mapped_column(Text, nullable=True)
    mes_actual: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Papeleta {self.empleado_id}>"