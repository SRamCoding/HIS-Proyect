import uuid
from datetime import date, datetime
from sqlalchemy import String, Text, Boolean, Integer, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

"""Hemodiálisis -- programa de terapia de reemplazo renal para pacientes con
Enfermedad Renal Crónica (CIE-10 N18.x). No se duplica la identidad del
paciente ni el catálogo de diagnósticos: PacienteHemodialisis referencia al
Patient y al DiagnosticoCIE10 ya reales de SIGARH/Admisión, igual que hace
el resto de módulos clínicos de esta sesión.

Parámetros clínicos de sesión (peso pre/post, ultrafiltración, acceso
vascular, presión arterial) corresponden a la práctica estándar de
nefrología para el registro de una sesión de hemodiálisis; no se inventa una
taxonomía clínica adicional -- las complicaciones intradiálisis se registran
como texto libre, tal como el propio equipo de enfermería las redacta."""


class PacienteHemodialisis(Base):
    """Inscripción de un paciente en el programa crónico de hemodiálisis del
    establecimiento. No es una atención puntual -- es un estado prolongado
    (meses/años) con un acceso vascular y un peso seco de referencia que se
    actualizan en el tiempo, por eso vive separado de AtencionMedica."""
    __tablename__ = "hemodialisis_pacientes"
    __table_args__ = (UniqueConstraint("tenant_id", "patient_id", name="uq_hd_paciente_tenant_patient"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"))
    diagnostico_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_diagnosticos_cie10.id", ondelete="SET NULL"), nullable=True)
    medico_nefrologo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="SET NULL"), nullable=True)

    fecha_ingreso_programa: Mapped[date] = mapped_column(Date, default=date.today)
    acceso_vascular_tipo: Mapped[str] = mapped_column(String(30))  # FAV, CATETER_VENOSO_CENTRAL, INJERTO
    fecha_creacion_acceso: Mapped[date | None] = mapped_column(Date, nullable=True)
    peso_seco_kg: Mapped[float] = mapped_column(Float)
    turno_habitual: Mapped[str] = mapped_column(String(20), default="MAÑANA")  # MAÑANA, TARDE, NOCHE
    frecuencia_semanal: Mapped[int] = mapped_column(Integer, default=3)

    estado: Mapped[str] = mapped_column(String(20), default="activo", index=True)
    # activo, transferido, trasplantado, fallecido, alta
    fecha_estado: Mapped[date | None] = mapped_column(Date, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PacienteHemodialisis {self.patient_id}>"


class SesionHemodialisis(Base):
    """Una sesión de tratamiento. El peso seco de referencia vive en
    PacienteHemodialisis; aquí se registra lo medido en esta sesión concreta
    (peso pre/post real, presión arterial, ultrafiltración lograda)."""
    __tablename__ = "hemodialisis_sesiones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    paciente_hemodialisis_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("hemodialisis_pacientes.id", ondelete="CASCADE"))

    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    turno: Mapped[str] = mapped_column(String(20))  # MAÑANA, TARDE, NOCHE
    numero_maquina: Mapped[str | None] = mapped_column(String(20), nullable=True)
    hora_inicio: Mapped[str | None] = mapped_column(String(5), nullable=True)
    hora_fin: Mapped[str | None] = mapped_column(String(5), nullable=True)
    tiempo_sesion_horas: Mapped[float | None] = mapped_column(Float, nullable=True)

    peso_pre_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    peso_post_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    ultrafiltracion_litros: Mapped[float | None] = mapped_column(Float, nullable=True)

    presion_pre_sistolica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    presion_pre_diastolica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    presion_post_sistolica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    presion_post_diastolica: Mapped[int | None] = mapped_column(Integer, nullable=True)

    acceso_vascular_utilizado: Mapped[str | None] = mapped_column(String(30), nullable=True)
    heparinizacion: Mapped[bool] = mapped_column(Boolean, default=True)
    complicaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    estado: Mapped[str] = mapped_column(String(20), default="programada", index=True)
    # programada, en_curso, completada, suspendida, no_asistio
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SesionHemodialisis {self.paciente_hemodialisis_id} {self.fecha}>"
