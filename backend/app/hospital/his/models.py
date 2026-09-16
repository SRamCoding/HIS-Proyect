"""HIS (Sistema de Información en Salud - MINSA). A diferencia de SIS/FUA
(reembolso, solo asegurados SIS), el Formato HIS es un reporte estadístico
obligatorio de TODA atención, sin importar el financiador, que cada
establecimiento remite periódicamente a su MicroRed/Red de Salud (Anexo 4B,
Norma Técnica del Sistema HIS-MINSA). Aquí solo se persiste el envío
(cierre administrativo del periodo); el detalle de atenciones se calcula al
vuelo desde los datos clínicos reales, igual que un reporte de Laboratorio o
Farmacia -- no se duplica esa información en una tabla aparte."""
import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Text, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class HisEnvio(Base):
    __tablename__ = "his_envios"
    __table_args__ = (UniqueConstraint("tenant_id", "periodo"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    periodo: Mapped[str] = mapped_column(String(7))  # "AAAA-MM"
    fecha_desde: Mapped[date] = mapped_column(Date)
    fecha_hasta: Mapped[date] = mapped_column(Date)
    total_registros: Mapped[int] = mapped_column(Integer, default=0)
    estado: Mapped[str] = mapped_column(String(20), default="borrador", index=True)  # borrador, enviado
    fecha_envio: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    registrado_por: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<HisEnvio {self.periodo} ({self.estado})>"
