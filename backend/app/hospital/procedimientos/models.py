import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

"""Procedimientos -- procedimientos menores/de apoyo al diagnóstico y
tratamiento (curaciones, retiro de puntos, sondaje, canalización de vía,
nebulización, biopsias menores, etc.), realizados fuera del flujo propio de
Laboratorio/Imagenología/Farmacia. No se inventa un catálogo propio de
procedimientos: se reutiliza TiempoProcedimiento, que ya existe y está
seeded en SIGARH > General para estimar tiempos de personal -- aquí se usa
además como catálogo clínico real de qué procedimiento se realizó.

Asignaciones = qué personal está habilitado para realizar cada
procedimiento (igual que TecnologoPrograma en Medicina Física).
Atenciones = la ejecución real sobre un paciente, con origen dual/triple
(Consulta Externa, Emergencia, Hospitalización) o directo, mismo patrón que
el resto de módulos clínicos de esta sesión."""


class ProcedimientosCorrelativo(Base):
    __tablename__ = "procedimientos_correlativos"
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(30), primary_key=True)
    valor: Mapped[int] = mapped_column(Integer, default=0)


class ProcedimientoAsignacion(Base):
    __tablename__ = "procedimientos_asignaciones"
    __table_args__ = (UniqueConstraint("tiempo_procedimiento_id", "empleado_id", name="uq_proc_asignacion"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    tiempo_procedimiento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_tiempos_procedimientos.id", ondelete="CASCADE"))
    empleado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ProcedimientoAsignacion {self.tiempo_procedimiento_id} {self.empleado_id}>"


class AtencionProcedimiento(Base):
    __tablename__ = "procedimientos_atenciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    atencion_medica_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_medicas.id", ondelete="SET NULL"), nullable=True)
    atencion_emergencia_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_emergencia.id", ondelete="SET NULL"), nullable=True)
    hospitalizacion_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("hospitalizaciones.id", ondelete="SET NULL"), nullable=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"))
    tiempo_procedimiento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_tiempos_procedimientos.id", ondelete="RESTRICT"))
    empleado_ejecutor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="RESTRICT"))

    numero_atencion: Mapped[str] = mapped_column(String(30), unique=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    consentimiento_informado: Mapped[bool] = mapped_column(Boolean, default=False)
    hallazgos: Mapped[str | None] = mapped_column(Text, nullable=True)
    complicaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    motivo_cancelacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="programado", index=True)  # programado, realizado, cancelado

    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AtencionProcedimiento {self.numero_atencion}>"
