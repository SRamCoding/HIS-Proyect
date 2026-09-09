"""Operación de Laboratorio. Los catálogos y las órdenes existentes se reutilizan."""
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Date, DateTime, Integer, Numeric, Text, ForeignKey, JSON, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class LabCorrelativo(Base):
    __tablename__ = "lab_correlativos"
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(20), primary_key=True)
    valor: Mapped[int] = mapped_column(Integer, default=0)


class LabCupo(Base):
    __tablename__ = "lab_cupos"
    __table_args__ = (
        UniqueConstraint("tenant_id", "fecha"),
        CheckConstraint("cupos >= 0", name="lab_cupos_cupos_check"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    fecha: Mapped[date] = mapped_column(Date)
    cupos: Mapped[int] = mapped_column(Integer)
    registrado_por: Mapped[str] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LabMovimiento(Base):
    __tablename__ = "lab_movimientos"
    __table_args__ = (UniqueConstraint("tenant_id", "numero"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    orden_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ordenes_laboratorio.id", ondelete="RESTRICT"), unique=True)
    numero: Mapped[str] = mapped_column(String(40))
    fecha: Mapped[date] = mapped_column(Date, index=True)
    toma_examen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="RESTRICT"))
    agendamiento_por: Mapped[str] = mapped_column(String(40), default="PACIENTE")
    registrar_por: Mapped[str] = mapped_column(String(30), default="ORDEN")
    cuenta_nueva: Mapped[bool] = mapped_column(default=False)
    comprobante: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="agendado")
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    motivo_anulacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    registrado_por: Mapped[str] = mapped_column(String(255))
    toma_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    validado_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    validado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LabMovimientoItem(Base):
    __tablename__ = "lab_movimiento_items"
    __table_args__ = (
        UniqueConstraint("movimiento_id", "examen_id"),
        CheckConstraint("cantidad > 0", name="lab_movimiento_items_cantidad_check"),
        CheckConstraint("precio >= 0", name="lab_movimiento_items_precio_check"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    movimiento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lab_movimientos.id", ondelete="RESTRICT"))
    examen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_examenes_laboratorio.id", ondelete="RESTRICT"))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nombre: Mapped[str] = mapped_column(String(255))
    tipo_muestra: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cantidad: Mapped[int] = mapped_column(Integer, default=1)
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    unidad: Mapped[str | None] = mapped_column(String(50), nullable=True)
    referencia: Mapped[str | None] = mapped_column(Text, nullable=True)
    resultados: Mapped[list] = mapped_column(JSON, default=list)


class LabFichaCovid(Base):
    __tablename__ = "lab_fichas_covid"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"))
    fecha: Mapped[date] = mapped_column(Date, index=True)
    tipo_prueba: Mapped[str] = mapped_column(String(100))
    muestra: Mapped[str] = mapped_column(String(100))
    resultado: Mapped[str] = mapped_column(String(30), default="pendiente")
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    registrado_por: Mapped[str] = mapped_column(String(255))
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
