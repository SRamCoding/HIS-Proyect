"""Caja: ledger interno de cobros (sin facturación electrónica SUNAT).

Los cargos pendientes nacen en los módulos que los generan (Consulta Externa,
Emergencia, Laboratorio, Imagenología) y quedan expuestos por su numero_cuenta;
Farmacia se autocobra en el propio mostrador (FarmaciaVenta ya nace "PAGADA")
por lo que no es un cargo pendiente para Caja.

Caja no muta el estado de esos módulos: registra el cobro en su propio libro
(Cobro/CobroItem) referenciando el origen (origen + origen_id) y neteando
"cobrado" contra "cargo" en tiempo de lectura -- evita invadir las máquinas de
estado ajenas y deja rastro auditable en ambos lados.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, Text, ForeignKey, UniqueConstraint, CheckConstraint, Index, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class CajaCorrelativo(Base):
    __tablename__ = "caja_correlativos"
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(20), primary_key=True)
    valor: Mapped[int] = mapped_column(default=0)


class CajaSesion(Base):
    """Apertura/cierre de turno de una caja física (sigarh_cajas)."""
    __tablename__ = "caja_sesiones"
    __table_args__ = (
        UniqueConstraint("tenant_id", "numero"),
        # Una caja física no puede tener dos turnos abiertos a la vez.
        Index("ux_caja_sesion_abierta", "caja_id", unique=True, postgresql_where=text("estado = 'abierta'")),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    caja_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_cajas.id", ondelete="RESTRICT"), index=True)
    cajero_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="RESTRICT"))
    numero: Mapped[str] = mapped_column(String(40))
    estado: Mapped[str] = mapped_column(String(20), default="abierta")  # abierta, cerrada
    monto_apertura: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    observaciones_apertura: Mapped[str | None] = mapped_column(Text, nullable=True)
    monto_cierre_declarado: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    monto_cierre_sistema: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    diferencia: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    observaciones_cierre: Mapped[str | None] = mapped_column(Text, nullable=True)
    registrado_por: Mapped[str] = mapped_column(String(255))
    abierta_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    cerrada_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Cobro(Base):
    """Un cobro registrado dentro de una sesión de caja abierta."""
    __tablename__ = "caja_cobros"
    __table_args__ = (UniqueConstraint("tenant_id", "numero"), CheckConstraint("monto > 0"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    caja_sesion_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("caja_sesiones.id", ondelete="RESTRICT"), index=True)
    numero: Mapped[str] = mapped_column(String(40))
    numero_cuenta: Mapped[str] = mapped_column(String(50), index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"), nullable=True)
    forma_pago: Mapped[str] = mapped_column(String(20))  # EFECTIVO, TARJETA, TRANSFERENCIA, SEGURO
    fuente_financiamiento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    estado: Mapped[str] = mapped_column(String(20), default="registrado")  # registrado, anulado
    motivo_anulacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    registrado_por: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class CobroItem(Base):
    """Línea de un cobro: qué cargo de qué módulo origen se está pagando.

    origen_id referencia libremente al id del registro origen (Cita,
    AdmisionEmergencia, LabMovimiento, ImagenMovimiento) -- no lleva FK dura
    porque la tabla de origen cambia según `origen`; el service valida su
    existencia antes de guardar."""
    __tablename__ = "caja_cobro_items"
    __table_args__ = (CheckConstraint("monto > 0"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    cobro_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("caja_cobros.id", ondelete="RESTRICT"), index=True)
    origen: Mapped[str] = mapped_column(String(30))  # CONSULTA_EXTERNA, EMERGENCIA, LABORATORIO, IMAGEN
    origen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    descripcion: Mapped[str] = mapped_column(String(255))
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 4))
