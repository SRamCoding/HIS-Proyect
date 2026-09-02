import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Departamento(Base):
    """Departamentos del hospital — equivalente a Department en Laravel."""
    __tablename__ = "sigarh_departamentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    servicios: Mapped[list["Servicio"]] = relationship(back_populates="departamento")

    def __repr__(self) -> str:
        return f"<Departamento {self.nombre}>"


class Servicio(Base):
    """Servicios del hospital — equivalente a Service en Laravel."""
    __tablename__ = "sigarh_servicios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    departamento_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_departamentos.id", ondelete="SET NULL"), nullable=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    departamento: Mapped["Departamento"] = relationship(back_populates="servicios")

    def __repr__(self) -> str:
        return f"<Servicio {self.nombre}>"


class TipoTrabajador(Base):
    """Tipos de trabajador — nombrado, contratado, CAS, etc."""
    __tablename__ = "sigarh_tipos_trabajador"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<TipoTrabajador {self.nombre}>"


class TipoGuardia(Base):
    """Tipos de guardia — ordinaria, retén, etc."""
    __tablename__ = "sigarh_tipos_guardia"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    horas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<TipoGuardia {self.nombre}>"


class NivelRemunerativo(Base):
    """Niveles remunerativos del personal."""
    __tablename__ = "sigarh_niveles_remunerativos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<NivelRemunerativo {self.nombre}>"


class HorarioGuardia(Base):
    """Horarios asignables a las guardias."""
    __tablename__ = "sigarh_horarios_guardia"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    hora_inicio: Mapped[str] = mapped_column(String(5))   # HH:MM
    hora_fin: Mapped[str] = mapped_column(String(5))      # HH:MM
    horas_totales: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<HorarioGuardia {self.nombre}>"


class GrupoOcupacional(Base):
    """Grupos ocupacionales del personal."""
    __tablename__ = "sigarh_grupos_ocupacionales"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<GrupoOcupacional {self.nombre}>"


class TipoActividad(Base):
    """Tipos de actividad complementaria."""
    __tablename__ = "sigarh_tipos_actividad"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    actividades: Mapped[list["Actividad"]] = relationship(back_populates="tipo_actividad")

    def __repr__(self) -> str:
        return f"<TipoActividad {self.nombre}>"


class Actividad(Base):
    """Actividades específicas complementarias."""
    __tablename__ = "sigarh_actividades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    tipo_actividad_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_tipos_actividad.id", ondelete="SET NULL"), nullable=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tipo_actividad: Mapped["TipoActividad"] = relationship(back_populates="actividades")

    def __repr__(self) -> str:
        return f"<Actividad {self.nombre}>"


class GuardiaValorizada(Base):
    """Valor monetario por tipo de guardia."""
    __tablename__ = "sigarh_guardias_valorizadas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    tipo_guardia_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_tipos_guardia.id", ondelete="SET NULL"), nullable=True)
    grupo_ocupacional_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_grupos_ocupacionales.id", ondelete="SET NULL"), nullable=True)
    nivel_remunerativo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_niveles_remunerativos.id", ondelete="SET NULL"), nullable=True)
    valor: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<GuardiaValorizada {self.valor}>"


class RolSistema(Base):
    """Roles de acceso del sistema SIGARH."""
    __tablename__ = "sigarh_roles_sistema"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<RolSistema {self.nombre}>"


class PerfilUsuario(Base):
    """Perfiles y permisos de usuario SIGARH."""
    __tablename__ = "sigarh_perfiles_usuario"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    rol_sistema_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_roles_sistema.id", ondelete="SET NULL"), nullable=True)
    modulos_acceso: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON lista de módulos
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PerfilUsuario {self.nombre}>"