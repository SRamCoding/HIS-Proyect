import uuid
from datetime import date, datetime
from sqlalchemy import String, Text, Boolean, Integer, DateTime, Date, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

"""Servicio Social (Trabajo Social hospitalario) -- profesión reconocida y
regulada por la Ley N.° 23808 (Ley del Trabajador Social del Perú) y su
reglamento (D.S. N.° 019-85-PCM). El Servicio de Trabajo Social evalúa la
situación socioeconómica y familiar del paciente (para sustentar
exoneraciones, afiliación SIS, gestión de apoyo) y hace seguimiento del
caso -- no un formulario único, sino un caso social abierto con gestiones
en el tiempo (visitas, llamadas, coordinaciones), igual que un caso clínico.

No se duplica nada de Admisión: EvaluacionSocial referencia al Patient real
y solo agrega lo que Admisión no captura (vivienda, red de apoyo, factores
de riesgo social, clasificación socioeconómica referencial tipo SISFOH,
derivación a MIMP/CEM/INABIF/DEMUNA cuando corresponde)."""


class ServicioSocialCorrelativo(Base):
    __tablename__ = "servicio_social_correlativos"
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(30), primary_key=True)
    valor: Mapped[int] = mapped_column(Integer, default=0)


class EvaluacionSocial(Base):
    """Un caso social abierto por el Trabajador Social para un paciente."""
    __tablename__ = "servicio_social_evaluaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"))
    atencion_medica_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_medicas.id", ondelete="SET NULL"), nullable=True)
    atencion_emergencia_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_emergencia.id", ondelete="SET NULL"), nullable=True)
    hospitalizacion_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("hospitalizaciones.id", ondelete="SET NULL"), nullable=True)
    trabajador_social_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="RESTRICT"))

    numero_ficha: Mapped[str] = mapped_column(String(30), unique=True)
    fecha_evaluacion: Mapped[date] = mapped_column(Date, default=date.today)
    tipo_vivienda: Mapped[str | None] = mapped_column(String(30), nullable=True)  # PROPIA, ALQUILADA, ALOJADA, ASENTAMIENTO_HUMANO, SIN_VIVIENDA
    clasificacion_socioeconomica: Mapped[str | None] = mapped_column(String(20), nullable=True)  # POBRE_EXTREMO, POBRE, NO_POBRE (referencial, tipo SISFOH)
    red_apoyo_familiar: Mapped[str | None] = mapped_column(Text, nullable=True)
    factores_riesgo: Mapped[list | None] = mapped_column(JSON, nullable=True)  # violencia_familiar, abandono, situacion_calle, adulto_mayor_solo, discapacidad_sin_soporte, menor_en_riesgo
    requiere_derivacion_externa: Mapped[bool] = mapped_column(Boolean, default=False)
    entidad_derivacion: Mapped[str | None] = mapped_column(String(20), nullable=True)  # MIMP, CEM, INABIF, DEMUNA, OTRO
    recomendaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    estado: Mapped[str] = mapped_column(String(20), default="abierto", index=True)  # abierto, cerrado
    fecha_cierre: Mapped[date | None] = mapped_column(Date, nullable=True)

    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<EvaluacionSocial {self.numero_ficha}>"


class GestionSocial(Base):
    """Una gestión/actividad de seguimiento dentro de un caso social."""
    __tablename__ = "servicio_social_gestiones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    evaluacion_social_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("servicio_social_evaluaciones.id", ondelete="CASCADE"))

    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    tipo_gestion: Mapped[str] = mapped_column(String(30))  # VISITA_DOMICILIARIA, LLAMADA_TELEFONICA, COORDINACION_INTERINSTITUCIONAL, ENTREVISTA, GESTION_APOYO_SOCIAL, OTRO
    descripcion: Mapped[str] = mapped_column(Text)

    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<GestionSocial {self.tipo_gestion} {self.evaluacion_social_id}>"
