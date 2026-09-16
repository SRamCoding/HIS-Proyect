import uuid
from datetime import date, datetime
from sqlalchemy import String, Text, Boolean, Integer, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

"""Medicina Física y Rehabilitación (MFR) -- servicio de apoyo al
tratamiento reconocido en la categorización de establecimientos de salud
(hospitales II-1 y superiores suelen tener un servicio de MFR propio).

No se reutiliza ProgramacionMedica/Cita de Consulta Externa (ese router está
autorizado solo para el módulo 'consulta_externa' vía JWT, y sus campos
-- especialidad_id, consultorio_id -- están pensados para médicos, no para
tecnólogos de terapia física/ocupacional/de lenguaje). Se modela un sistema
de programación propio pero con la misma forma (ProgramacionMF ~
ProgramacionMedica, SesionMF ~ Cita), reutilizando el mismo Patient/Empleado
ya reales de Admisión/SIGARH."""


class ProgramaMedicinaFisica(Base):
    """Catálogo de programas de rehabilitación que ofrece el servicio
    (Fisioterapia, Terapia Ocupacional, Terapia de Lenguaje, Terapia
    Respiratoria, etc). Se configura una sola vez y se reutiliza en cada
    programación."""
    __tablename__ = "medicina_fisica_programas"
    __table_args__ = (UniqueConstraint("tenant_id", "nombre", name="uq_mf_programa_tenant_nombre"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    duracion_sesion_minutos: Mapped[int] = mapped_column(Integer, default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ProgramaMedicinaFisica {self.nombre}>"


class TecnologoPrograma(Base):
    """Tecnólogos médicos habilitados para ejecutar cada programa (relación
    muchos a muchos: un tecnólogo puede cubrir varios programas y un
    programa puede tener varios tecnólogos)."""
    __tablename__ = "medicina_fisica_tecnologo_programa"
    __table_args__ = (UniqueConstraint("programa_id", "empleado_id", name="uq_mf_tecnologo_programa"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    programa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("medicina_fisica_programas.id", ondelete="CASCADE"))
    empleado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<TecnologoPrograma {self.programa_id} {self.empleado_id}>"


class ProgramacionMF(Base):
    """Bloque de horario de un tecnólogo para un programa -- equivalente a
    ProgramacionMedica pero propio de este módulo."""
    __tablename__ = "medicina_fisica_programaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    programa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("medicina_fisica_programas.id", ondelete="RESTRICT"))
    tecnologo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="RESTRICT"))

    fecha: Mapped[date] = mapped_column(Date)
    turno: Mapped[str] = mapped_column(String(20))  # MAÑANA, TARDE, NOCHE
    hora_inicio: Mapped[str] = mapped_column(String(5))
    hora_fin: Mapped[str] = mapped_column(String(5))
    tiempo_sesion_minutos: Mapped[int] = mapped_column(Integer, default=30)

    estado: Mapped[str] = mapped_column(String(20), default="activo", index=True)  # activo, bloqueado, cancelado
    motivo_bloqueo: Mapped[str | None] = mapped_column(Text, nullable=True)

    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ProgramacionMF {self.tecnologo_id} {self.fecha}>"


class SesionMF(Base):
    """Una sesión de terapia agendada dentro de un cupo de ProgramacionMF --
    equivalente a Cita, pero incluye directamente el registro clínico de la
    ejecución (escala de dolor EVA, actividades realizadas, evolución) ya
    que una sesión de rehabilitación es un único paso, a diferencia del
    ciclo triaje->atención->receta de Consulta Externa."""
    __tablename__ = "medicina_fisica_sesiones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    programacion_mf_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("medicina_fisica_programaciones.id", ondelete="CASCADE"))
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"))

    hora_inicio: Mapped[str] = mapped_column(String(5))
    hora_fin: Mapped[str] = mapped_column(String(5))
    estado: Mapped[str] = mapped_column(String(20), default="programada", index=True)
    # programada, atendida, cancelada, no_asistio

    escala_dolor_eva: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-10, Escala Visual Analógica
    actividades_realizadas: Mapped[str | None] = mapped_column(Text, nullable=True)
    evolucion: Mapped[str | None] = mapped_column(Text, nullable=True)

    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SesionMF {self.patient_id} {self.hora_inicio}>"
