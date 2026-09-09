import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Catalogo(Base):
    """
    Catálogo genérico del sistema.
    Una sola tabla agrupa múltiples tipos de catálogos mediante el campo 'categoria'.
    Ej: Tipos de Documento, Tipos de Servicio, Modalidades de Atención, etc.
    """
    __tablename__ = "sigarh_catalogos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    categoria: Mapped[str] = mapped_column(String(100), index=True)
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nombre: Mapped[str] = mapped_column(String(255))
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Catalogo {self.categoria}: {self.nombre}>"


class Consultorio(Base):
    """
    Consultorios médicos del hospital.
    Se configura en SIGARH y se usa en Consulta Externa para programación médica.
    """
    __tablename__ = "sigarh_consultorios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    especialidad_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sigarh_especialidades.id", ondelete="SET NULL"),
        nullable=True
    )
    piso_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    capacidad: Mapped[int] = mapped_column(Integer, default=1)
    equipamiento: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    especialidad: Mapped["sigarh_especialidades"] = relationship(
        "Especialidad",
        foreign_keys=[especialidad_id],
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Consultorio {self.nombre}>"


# ─── Categorías predefinidas del catálogo ─────────────────────────────────────
CATEGORIAS_CATALOGO = [
    "tipos_documento",
    "tipos_servicio",
    "modalidades_atencion",
    "estados_cita",
    "tipos_diagnostico",
    "tipos_alta",
    "procedencia_emergencia",
    "tipos_grupo_ocupacional",
    "metodos_pago",
    "tipos_producto",
    "estados_emergencia",
    "estados_comprobante",
    "destino_atencion",
    "tipos_comprobante",
    "tipos_cama",
    "tipos_cupo_cita",
    "puntos_llamado",
]