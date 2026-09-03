import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Text, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Empleado(Base):
    """
    Empleado del hospital.
    Modelo central del SIGARH — base de roles de turno, asistencia y movimientos.
    """
    __tablename__ = "sigarh_empleados"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)

    # ─── Datos Personales ─────────────────────────────────────────────────────
    dni: Mapped[str] = mapped_column(String(8), index=True)
    nombres: Mapped[str] = mapped_column(String(150))
    apellido_paterno: Mapped[str] = mapped_column(String(100))
    apellido_materno: Mapped[str] = mapped_column(String(100))
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    sexo: Mapped[str | None] = mapped_column(String(1), nullable=True)              # M, F
    estado_civil: Mapped[str | None] = mapped_column(String(20), nullable=True)     # soltero, casado, divorciado, viudo, conviviente
    grupo_sanguineo: Mapped[str | None] = mapped_column(String(5), nullable=True)   # A+, A-, B+, B-, AB+, AB-, O+, O-

    # Contacto
    celular: Mapped[str | None] = mapped_column(String(15), nullable=True)
    telefono_fijo: Mapped[str | None] = mapped_column(String(15), nullable=True)
    correo: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ─── Datos Laborales ──────────────────────────────────────────────────────
    tipo_trabajador_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_tipos_trabajador.id", ondelete="SET NULL"), nullable=True)
    nivel_remunerativo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_niveles_remunerativos.id", ondelete="SET NULL"), nullable=True)
    grupo_ocupacional_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_grupos_ocupacionales.id", ondelete="SET NULL"), nullable=True)
    departamento_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_departamentos.id", ondelete="SET NULL"), nullable=True)
    servicio_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_servicios.id", ondelete="SET NULL"), nullable=True)
    cargo_laboral: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modalidad: Mapped[str | None] = mapped_column(String(100), nullable=True)
    codigo_minsa: Mapped[str | None] = mapped_column(String(50), nullable=True)
    numero_cmp: Mapped[str | None] = mapped_column(String(50), nullable=True)      # Colegio Médico del Perú

    # Resoluciones y fechas
    fecha_ingreso: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_nombramiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_cese: Mapped[date | None] = mapped_column(Date, nullable=True)
    resolucion_nombramiento: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolucion_cese: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ─── Datos Bancarios ──────────────────────────────────────────────────────
    banco: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ruc: Mapped[str | None] = mapped_column(String(11), nullable=True)
    numero_cuenta: Mapped[str | None] = mapped_column(String(50), nullable=True)
    numero_cci: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tipo_cuenta: Mapped[str | None] = mapped_column(String(30), nullable=True)     # ahorros, corriente

    # ─── Ubicación ────────────────────────────────────────────────────────────
    departamento_ubigeo: Mapped[str | None] = mapped_column(String(2), nullable=True)
    provincia_ubigeo: Mapped[str | None] = mapped_column(String(4), nullable=True)
    distrito_ubigeo: Mapped[str | None] = mapped_column(String(6), nullable=True)
    direccion: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Estado ───────────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    especialidades: Mapped[list["EmpleadoEspecialidad"]] = relationship(back_populates="empleado", cascade="all, delete-orphan")

    @property
    def nombre_completo(self) -> str:
        return f"{self.apellido_paterno} {self.apellido_materno}, {self.nombres}"

    @property
    def antiguedad(self) -> str | None:
        if not self.fecha_ingreso:
            return None
        delta = date.today() - self.fecha_ingreso
        years = delta.days // 365
        months = (delta.days % 365) // 30
        if years > 0:
            return f"{years} año(s) {months} mes(es)"
        return f"{months} mes(es)"

    def __repr__(self) -> str:
        return f"<Empleado {self.nombre_completo} ({self.dni})>"


class Especialidad(Base):
    """
    Catálogo de especialidades médicas.
    Se configura en Mantenimiento y se asigna a empleados.
    """
    __tablename__ = "sigarh_especialidades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Especialidad {self.nombre}>"


class EmpleadoEspecialidad(Base):
    """
    Especialidades asignadas a un empleado con N° RNE y certificado.
    """
    __tablename__ = "sigarh_empleado_especialidades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empleado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    especialidad_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_especialidades.id", ondelete="CASCADE"))
    numero_rne: Mapped[str | None] = mapped_column(String(50), nullable=True)
    certificado_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    validado: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    empleado: Mapped["Empleado"] = relationship(back_populates="especialidades")
    especialidad: Mapped["Especialidad"] = relationship()

    def __repr__(self) -> str:
        return f"<EmpleadoEspecialidad {self.empleado_id} - {self.especialidad_id}>"


class DiasFeriado(Base):
    """Días feriados del hospital."""
    __tablename__ = "sigarh_dias_feriados"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    fecha: Mapped[date] = mapped_column(Date)
    tipo: Mapped[str] = mapped_column(String(50), default="nacional")   # nacional, regional, local
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<DiasFeriado {self.nombre} ({self.fecha})>"


class MotivoJustificacion(Base):
    """Motivos válidos de justificación de inasistencia."""
    __tablename__ = "sigarh_motivos_justificacion"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<MotivoJustificacion {self.nombre}>"


class Tolerancia(Base):
    """Márgenes de tolerancia para marcaciones de asistencia."""
    __tablename__ = "sigarh_tolerancias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    minutos_entrada: Mapped[int] = mapped_column(Integer, default=0)
    minutos_salida: Mapped[int] = mapped_column(Integer, default=0)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Tolerancia {self.nombre}>"


class RegistroAsistencia(Base):
    """Control de asistencia diaria del personal."""
    __tablename__ = "sigarh_registro_asistencia"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    empleado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    fecha: Mapped[date] = mapped_column(Date)
    hora_entrada: Mapped[str | None] = mapped_column(String(5), nullable=True)   # HH:MM
    hora_salida: Mapped[str | None] = mapped_column(String(5), nullable=True)    # HH:MM
    estado: Mapped[str] = mapped_column(String(20), default="presente")          # presente, ausente, tardanza, justificado
    observacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    empleado: Mapped["Empleado"] = relationship()

    def __repr__(self) -> str:
        return f"<RegistroAsistencia {self.empleado_id} {self.fecha}>"


class Justificacion(Base):
    """Justificaciones e inasistencias del personal."""
    __tablename__ = "sigarh_justificaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    empleado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    motivo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_motivos_justificacion.id", ondelete="SET NULL"), nullable=True)
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date] = mapped_column(Date)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    documento_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")   # pendiente, aprobado, rechazado
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    empleado: Mapped["Empleado"] = relationship()
    motivo: Mapped["MotivoJustificacion"] = relationship()

    def __repr__(self) -> str:
        return f"<Justificacion {self.empleado_id} {self.fecha_inicio}>"