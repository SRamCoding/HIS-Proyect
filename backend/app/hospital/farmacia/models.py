"""Operación farmacéutica hospitalaria con trazabilidad por lote."""
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class FarmaciaCorrelativo(Base):
    __tablename__ = "farmacia_correlativos"
    __table_args__ = (UniqueConstraint("tenant_id", "tipo", "anio"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    tipo: Mapped[str] = mapped_column(String(30)); anio: Mapped[int] = mapped_column(Integer); ultimo: Mapped[int] = mapped_column(Integer, default=0)

class FarmaciaLote(Base):
    __tablename__ = "farmacia_lotes"
    __table_args__ = (UniqueConstraint("tenant_id", "almacen_id", "medicamento_id", "numero_lote"), CheckConstraint("stock_actual >= 0"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    almacen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_almacenes.id", ondelete="RESTRICT"), index=True)
    medicamento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_medicamentos.id", ondelete="RESTRICT"), index=True)
    numero_lote: Mapped[str] = mapped_column(String(80)); fecha_vencimiento: Mapped[date] = mapped_column(Date, index=True)
    registro_sanitario: Mapped[str | None] = mapped_column(String(100), nullable=True)
    stock_actual: Mapped[Decimal] = mapped_column(Numeric(14,4), default=0); costo_unitario: Mapped[Decimal] = mapped_column(Numeric(14,4), default=0)
    precio_venta: Mapped[Decimal] = mapped_column(Numeric(14,4), default=0); estado: Mapped[str] = mapped_column(String(20), default="CUARENTENA")
    ubicacion: Mapped[str | None] = mapped_column(String(100), nullable=True); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class FarmaciaMovimiento(Base):
    __tablename__ = "farmacia_movimientos"
    __table_args__ = (UniqueConstraint("tenant_id", "numero"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4); tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    numero: Mapped[str] = mapped_column(String(40), index=True); tipo: Mapped[str] = mapped_column(String(10)); ambito: Mapped[str] = mapped_column(String(15)); concepto: Mapped[str] = mapped_column(String(60))
    almacen_origen_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_almacenes.id", ondelete="RESTRICT"), nullable=True)
    almacen_destino_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_almacenes.id", ondelete="RESTRICT"), nullable=True)
    movimiento_relacionado_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("farmacia_movimientos.id", ondelete="RESTRICT"), nullable=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"), nullable=True)
    numero_cuenta: Mapped[str | None] = mapped_column(String(40), nullable=True); fuente_financiamiento: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tipo_documento: Mapped[str | None] = mapped_column(String(40), nullable=True); numero_documento: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tipo_documento_origen: Mapped[str | None] = mapped_column(String(40), nullable=True); numero_documento_origen: Mapped[str | None] = mapped_column(String(80), nullable=True); fecha_documento_origen: Mapped[date | None] = mapped_column(Date, nullable=True)
    tipo_proceso: Mapped[str | None] = mapped_column(String(50), nullable=True); numero_proceso: Mapped[str | None] = mapped_column(String(80), nullable=True); tipo_compra: Mapped[str | None] = mapped_column(String(50), nullable=True)
    proveedor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_proveedores_farmacia.id", ondelete="RESTRICT"), nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True); total: Mapped[Decimal] = mapped_column(Numeric(14,4), default=0); estado: Mapped[str] = mapped_column(String(20), default="BORRADOR")
    registrado_por: Mapped[str] = mapped_column(String(255)); confirmado_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True); motivo_anulacion: Mapped[str | None] = mapped_column(Text, nullable=True); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

class FarmaciaMovimientoItem(Base):
    __tablename__ = "farmacia_movimiento_items"; __table_args__ = (CheckConstraint("cantidad > 0"), CheckConstraint("precio_unitario >= 0"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4); tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    movimiento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farmacia_movimientos.id", ondelete="RESTRICT"), index=True); medicamento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_medicamentos.id", ondelete="RESTRICT"))
    lote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("farmacia_lotes.id", ondelete="RESTRICT"), nullable=True)
    codigo: Mapped[str] = mapped_column(String(50)); descripcion: Mapped[str] = mapped_column(String(255)); unidad: Mapped[str | None] = mapped_column(String(50), nullable=True); numero_lote: Mapped[str] = mapped_column(String(80)); fecha_vencimiento: Mapped[date] = mapped_column(Date); registro_sanitario: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14,4)); precio_unitario: Mapped[Decimal] = mapped_column(Numeric(14,4), default=0); subtotal: Mapped[Decimal] = mapped_column(Numeric(14,4), default=0)

class FarmaciaDispensacion(Base):
    __tablename__ = "farmacia_dispensaciones"; __table_args__ = (UniqueConstraint("tenant_id", "numero"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4); tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True); numero: Mapped[str] = mapped_column(String(40))
    receta_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recetas.id", ondelete="RESTRICT"), index=True); almacen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_almacenes.id", ondelete="RESTRICT")); movimiento_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("farmacia_movimientos.id", ondelete="RESTRICT"), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="PENDIENTE"); observaciones: Mapped[str | None] = mapped_column(Text, nullable=True); dispensado_por: Mapped[str] = mapped_column(String(255)); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class FarmaciaDispensacionItem(Base):
    __tablename__ = "farmacia_dispensacion_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4); tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True); dispensacion_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farmacia_dispensaciones.id", ondelete="RESTRICT")); receta_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("receta_items.id", ondelete="RESTRICT")); lote_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farmacia_lotes.id", ondelete="RESTRICT")); cantidad: Mapped[Decimal] = mapped_column(Numeric(14,4))

class FarmacotecniaOrden(Base):
    __tablename__ = "farmacotecnia_ordenes"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4); tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True); receta_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("recetas.id", ondelete="RESTRICT"), nullable=True); numero: Mapped[str] = mapped_column(String(40), index=True)
    tipo_requerimiento: Mapped[str] = mapped_column(String(50)); formula: Mapped[str] = mapped_column(Text); cantidad: Mapped[Decimal] = mapped_column(Numeric(14,4), default=1); unidad: Mapped[str] = mapped_column(String(40), default="UNIDAD"); via_administracion: Mapped[str | None] = mapped_column(String(80), nullable=True); estabilidad_horas: Mapped[int | None] = mapped_column(Integer, nullable=True); condiciones_conservacion: Mapped[str | None] = mapped_column(Text, nullable=True); estado: Mapped[str] = mapped_column(String(20), default="PENDIENTE"); responsable: Mapped[str | None] = mapped_column(String(255), nullable=True); control_calidad: Mapped[dict] = mapped_column(JSON, default=dict); observaciones: Mapped[str | None] = mapped_column(Text, nullable=True); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class FarmaciaVenta(Base):
    __tablename__ = "farmacia_ventas"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4); tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True); numero: Mapped[str] = mapped_column(String(40), index=True); almacen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_almacenes.id", ondelete="RESTRICT")); patient_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"), nullable=True); receta_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("recetas.id", ondelete="RESTRICT"), nullable=True); movimiento_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("farmacia_movimientos.id", ondelete="RESTRICT"), nullable=True); tipo_pago: Mapped[str] = mapped_column(String(30), default="CONTADO"); fuente_financiamiento: Mapped[str] = mapped_column(String(60), default="PARTICULAR"); total: Mapped[Decimal] = mapped_column(Numeric(14,4), default=0); estado: Mapped[str] = mapped_column(String(20), default="PENDIENTE"); registrado_por: Mapped[str] = mapped_column(String(255)); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
