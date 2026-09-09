import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Text, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Almacen(Base):
    """Almacenes y farmacias del hospital."""
    __tablename__ = "sigarh_almacenes"
    __table_args__ = (UniqueConstraint("tenant_id", "codigo"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    codigo: Mapped[str] = mapped_column(String(20))
    nombre: Mapped[str] = mapped_column(String(100))
    tipo: Mapped[str] = mapped_column(String(30), default="farmacia")  # farmacia, almacen_central, laboratorio, dispensacion
    fuente_financiamiento: Mapped[str | None] = mapped_column(String(30), nullable=True)  # sismed, donaciones, mixto
    ubicacion_fisica: Mapped[str | None] = mapped_column(Text, nullable=True)
    despacha_recetas: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Almacen {self.codigo} - {self.nombre}>"


class ProveedorFarmacia(Base):
    """Proveedor habilitado para compras y transferencias SISMED."""
    __tablename__ = "sigarh_proveedores_farmacia"
    __table_args__ = (UniqueConstraint("tenant_id", "ruc"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    ruc: Mapped[str] = mapped_column(String(11)); razon_social: Mapped[str] = mapped_column(String(255))
    direccion: Mapped[str | None] = mapped_column(Text, nullable=True); telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True); registro_digemid: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CatalogoFarmacia(Base):
    """Valores administrables usados en documentos farmacéuticos."""
    __tablename__ = "sigarh_catalogos_farmacia"
    __table_args__ = (UniqueConstraint("tenant_id", "categoria", "codigo"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True); categoria: Mapped[str] = mapped_column(String(50), index=True)
    codigo: Mapped[str] = mapped_column(String(30)); nombre: Mapped[str] = mapped_column(String(150)); is_active: Mapped[bool] = mapped_column(Boolean, default=True); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Medicamento(Base):
    """
    Medicamentos e insumos médicos del hospital.
    Incluye datos DIGEMID según Ley 29459.
    """
    __tablename__ = "sigarh_medicamentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)

    # Identificacion
    codigo_interno: Mapped[str] = mapped_column(String(50))
    nombre_comercial: Mapped[str] = mapped_column(String(255))
    dci: Mapped[str | None] = mapped_column(String(150), nullable=True)         # Denominacion Comun Internacional
    nombre_generico: Mapped[str] = mapped_column(String(255))
    presentacion: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unidad: Mapped[str] = mapped_column(String(20), default="unidad")
    concentracion: Mapped[str | None] = mapped_column(String(100), nullable=True)
    forma_farmaceutica: Mapped[str | None] = mapped_column(String(50), nullable=True)
    via_administracion: Mapped[str | None] = mapped_column(String(30), nullable=True)
    codigo_atc: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Registro DIGEMID
    numero_registro_sanitario: Mapped[str | None] = mapped_column(String(50), nullable=True)
    laboratorio_fabricante: Mapped[str | None] = mapped_column(String(150), nullable=True)
    pais_origen: Mapped[str | None] = mapped_column(String(100), nullable=True)
    condicion_venta: Mapped[str] = mapped_column(String(30), default="sin_receta")  # sin_receta, receta_simple, receta_retenida, control_medico

    # Clasificacion y Control
    tipo_producto_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sigarh_catalogos.id", ondelete="SET NULL"), nullable=True
    )
    precio_referencia: Mapped[float | None] = mapped_column(Float, nullable=True)
    precio_referencia_sismed: Mapped[float | None] = mapped_column(Float, nullable=True)
    requiere_receta: Mapped[bool] = mapped_column(Boolean, default=False)
    controlado: Mapped[bool] = mapped_column(Boolean, default=False)
    fiscalizado_digemid: Mapped[bool] = mapped_column(Boolean, default=False)
    reporte_sismed: Mapped[bool] = mapped_column(Boolean, default=False)
    stock_minimo_alerta: Mapped[int] = mapped_column(Integer, default=10)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Cadena de frio
    requiere_cadena_frio: Mapped[bool] = mapped_column(Boolean, default=False)
    temperatura_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    temperatura_max: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Medicamento {self.codigo_interno} - {self.nombre_comercial}>"
