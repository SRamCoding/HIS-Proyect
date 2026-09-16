"""Operación de Imagenología. Los catálogos y las órdenes existentes se reutilizan
(ExamenImagenologia en SIGARH, OrdenImagen/OrdenImagenItem en consulta_externa)."""
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Date, DateTime, Integer, Numeric, Text, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ImagenCorrelativo(Base):
    __tablename__ = "imagen_correlativos"
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(20), primary_key=True)
    valor: Mapped[int] = mapped_column(Integer, default=0)


class ImagenMovimiento(Base):
    """El estudio de imagenología en sí: agendamiento, toma del estudio e informe.
    Análogo a LabMovimiento; sin cupos porque Imagenología no los maneja hoy."""
    __tablename__ = "imagen_movimientos"
    __table_args__ = (UniqueConstraint("tenant_id", "numero"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    orden_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ordenes_imagen.id", ondelete="RESTRICT"), unique=True)
    numero: Mapped[str] = mapped_column(String(40))
    fecha: Mapped[date] = mapped_column(Date, index=True)
    tecnico_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="RESTRICT"))
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


class ImagenMovimientoItem(Base):
    """Estudio solicitado dentro de un movimiento, con su informe radiológico.
    El informe usa los tres campos estándar de un reporte de imagenología
    (técnica, hallazgos, impresión diagnóstica) en vez de la lista libre de
    parámetro/valor de Laboratorio, porque así se documenta un estudio de
    imagen: no son valores de referencia sino un reporte narrativo."""
    __tablename__ = "imagen_movimiento_items"
    __table_args__ = (
        UniqueConstraint("movimiento_id", "examen_id"),
        CheckConstraint("cantidad > 0", name="imagen_movimiento_items_cantidad_check"),
        CheckConstraint("precio >= 0", name="imagen_movimiento_items_precio_check"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    movimiento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("imagen_movimientos.id", ondelete="RESTRICT"))
    examen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_examenes_imagenologia.id", ondelete="RESTRICT"))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nombre: Mapped[str] = mapped_column(String(255))
    modalidad: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parte_cuerpo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cantidad: Mapped[int] = mapped_column(Integer, default=1)
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    tecnica: Mapped[str | None] = mapped_column(Text, nullable=True)
    hallazgos: Mapped[str | None] = mapped_column(Text, nullable=True)
    impresion_diagnostica: Mapped[str | None] = mapped_column(Text, nullable=True)
