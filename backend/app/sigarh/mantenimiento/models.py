import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey, Float, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from typing import Optional
from app.sigarh.infraestructura_hosp.models import Piso

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
    """Servicios del hospital – equivalente a Service en Laravel."""
    __tablename__ = "sigarh_servicios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    departamento_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_departamentos.id", ondelete="SET NULL"), nullable=True)
    piso_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_pisos.id", ondelete="SET NULL"), nullable=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Minutos por paciente en consulta externa; usado para calcular cupos al
    # sincronizar la programación médica de App Hospitalario. NULL -> 15 por defecto.
    tiempo_atencion_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    departamento: Mapped["Departamento"] = relationship(back_populates="servicios")
    piso: Mapped[Optional["Piso"]] = relationship()
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
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    es_laborable: Mapped[bool] = mapped_column(Boolean, default=True)
    requiere_epp: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    tipo_guardia_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_tipos_guardia.id", ondelete="SET NULL"), nullable=True)
    horas_totales: Mapped[float | None] = mapped_column(Float, nullable=True)
    duracion_minutos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tipo_guardia: Mapped["TipoGuardia"] = relationship()
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    tipo_grupo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    requiere_consultorio: Mapped[bool] = mapped_column(Boolean, default=False)
    genera_agenda: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    moneda: Mapped[str] = mapped_column(String(3), default="PEN", server_default="PEN")
    vigencia_desde: Mapped[date | None] = mapped_column(Date, nullable=True)
    vigencia_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)
    sustento: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tipo_guardia: Mapped["TipoGuardia"] = relationship()
    grupo_ocupacional: Mapped["GrupoOcupacional"] = relationship()
    nivel_remunerativo: Mapped["NivelRemunerativo"] = relationship()

    def __repr__(self) -> str:
        return f"<GuardiaValorizada {self.valor}>"

class RolSistema(Base):
    """Roles de acceso del sistema SIGARH."""
    __tablename__ = "sigarh_roles_sistema"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    codigo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nombre: Mapped[str] = mapped_column(String(255))
    panel: Mapped[str] = mapped_column(String(50), default="sigarh")  # app, sigarh, portal
    modulo_requerido: Mapped[str | None] = mapped_column(String(100), nullable=True)
    modulos_permitidos: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: lista de codigos
    grupos_ocupacionales_permitidos: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: lista de UUIDs (str)
    # JSON: lista de acciones granulares habilitadas para este rol de acceso,
    # ej. ["aprobar_roles_turno"]. Independiente de modulos_permitidos (ver módulo)
    # porque ver un módulo no implica poder aprobar dentro de él.
    permisos_accion: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Si es True, un permiso de permisos_accion aplica a cualquier servicio/ámbito
    # del hospital (ej. RR. HH., dirección). Si es False, además del permiso se
    # exige que el empleado sea jefe del servicio concreto (Empleado.es_jefe_servicio).
    alcance_global: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PerfilUsuario {self.nombre}>"

class Dependencia(Base):
    """Dependencias organizacionales del hospital."""
    __tablename__ = "sigarh_dependencias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    clasificacion: Mapped[str] = mapped_column(String(50), default="administrativa")  # administrativa, asistencial
    departamento_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_departamentos.id", ondelete="SET NULL"), nullable=True)
    servicio_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_servicios.id", ondelete="SET NULL"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    departamento: Mapped["Departamento"] = relationship()
    servicio: Mapped["Servicio"] = relationship()

    def __repr__(self) -> str:
        return f"<Dependencia {self.nombre}>"

class UsuarioSigarh(Base):
    """
    Usuarios del sistema SIGARH del hospital.
    Se crean a partir de empleados con un perfil asignado.
    """
    __tablename__ = "sigarh_usuarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    empleado_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="SET NULL"), nullable=True
    )
    perfil_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_perfiles_usuario.id", ondelete="SET NULL"), nullable=True)
    username: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
    session_version: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    perfil: Mapped["PerfilUsuario"] = relationship()

    def __repr__(self) -> str:
        return f"<UsuarioSigarh {self.username}>"