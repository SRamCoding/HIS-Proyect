import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class DiagnosticoCIE10(Base):
    """Catalogo de diagnosticos CIE-10."""
    __tablename__ = "sigarh_diagnosticos_cie10"
    __table_args__ = (
        UniqueConstraint("tenant_id", "codigo_cie10", name="uq_cie10_tenant_codigo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    capitulo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    grupo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    categoria: Mapped[str | None] = mapped_column(String(255), nullable=True)
    codigo_cie10: Mapped[str] = mapped_column(String(20), index=True)
    codigo_cie9: Mapped[str | None] = mapped_column(String(20), nullable=True)
    descripcion: Mapped[str] = mapped_column(Text)
    vigencia_desde: Mapped[date | None] = mapped_column(Date, nullable=True)
    vigencia_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)
    sexo: Mapped[str] = mapped_column(String(10), default="ambos")  # ambos, masculino, femenino
    edad_minima: Mapped[int | None] = mapped_column(Integer, nullable=True)
    edad_maxima: Mapped[int | None] = mapped_column(Integer, nullable=True)
    morbilidad: Mapped[bool] = mapped_column(Boolean, default=False)
    intrahospitalario: Mapped[bool] = mapped_column(Boolean, default=False)
    gestacion: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<DiagnosticoCIE10 {self.codigo_cie10} - {self.descripcion[:50]}>"


class Paquete(Base):
    """Paquetes de servicios o procedimientos agrupados."""
    __tablename__ = "sigarh_paquetes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nombre: Mapped[str] = mapped_column(String(255))
    punto_carga: Mapped[str | None] = mapped_column(String(100), nullable=True)
    especialidad_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_especialidades.id", ondelete="SET NULL"), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["PaqueteItem"]] = relationship(back_populates="paquete", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Paquete {self.nombre}>"


class PaqueteItem(Base):
    """Items/productos dentro de un paquete."""
    __tablename__ = "sigarh_paquete_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paquete_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_paquetes.id", ondelete="CASCADE"))
    medicamento_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_medicamentos.id", ondelete="SET NULL"), nullable=True)
    cantidad: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    paquete: Mapped["Paquete"] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return f"<PaqueteItem {self.medicamento_id} x{self.cantidad}>"


class TiempoProcedimiento(Base):
    """Tiempos estandar asignados a cada procedimiento."""
    __tablename__ = "sigarh_tiempos_procedimientos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nombre: Mapped[str] = mapped_column(String(255))
    especialidad_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_especialidades.id", ondelete="SET NULL"), nullable=True)
    duracion_minutos: Mapped[int] = mapped_column(Integer, default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<TiempoProcedimiento {self.nombre} {self.duracion_minutos}min>"
