"""SIS (Seguro Integral de Salud). El Formato FUA es el documento que exige
el SIS para reembolsar cada atencion a un asegurado (RM 573-2021/MINSA y
directivas del Pliego SIS) -- registro administrativo propio, distinto de la
atencion clinica que ya existe en Consulta Externa/Emergencia."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, UniqueConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class SisCorrelativo(Base):
    __tablename__ = "sis_correlativos"
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(20), primary_key=True)
    valor: Mapped[int] = mapped_column(Integer, default=0)


class FormatoFua(Base):
    """Un FUA por atencion facturable al SIS -- dualidad de origen igual que
    Hospitalizacion/Referencia/Interconsulta: Consulta Externa o Emergencia."""
    __tablename__ = "sis_formatos_fua"
    __table_args__ = (UniqueConstraint("tenant_id", "numero_fua"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    atencion_medica_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_medicas.id", ondelete="CASCADE"), unique=True, nullable=True)
    atencion_emergencia_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_emergencia.id", ondelete="CASCADE"), unique=True, nullable=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"))
    seguro_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_seguros.id", ondelete="RESTRICT"))

    numero_fua: Mapped[str] = mapped_column(String(40), index=True)
    fecha_atencion: Mapped[datetime] = mapped_column(DateTime)
    estado: Mapped[str] = mapped_column(String(20), default="generado", index=True)  # generado, enviado, observado, pagado, anulado
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    registrado_por: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<FormatoFua {self.numero_fua} ({self.estado})>"
