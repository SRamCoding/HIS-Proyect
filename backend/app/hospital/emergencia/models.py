import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class AdmisionEmergencia(Base):
    """Admision directa de Emergencia -- sin Cita ni ProgramacionMedica, el paciente llega y se registra."""
    __tablename__ = "admisiones_emergencia"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"))
    numero_cuenta: Mapped[str] = mapped_column(String(30), unique=True)
    servicio_emergencia: Mapped[str] = mapped_column(String(100), default="Emergencia General")  # Emergencia General, Gineco-Obstetricia, etc.
    fuente_financiamiento: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Datos del acompañante -- por admision, no por paciente (puede variar cada visita)
    acompanante_nombre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    acompanante_documento: Mapped[str | None] = mapped_column(String(20), nullable=True)
    acompanante_parentesco: Mapped[str | None] = mapped_column(String(50), nullable=True)
    acompanante_telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    acompanante_direccion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="admitido")  # admitido, en_triaje, en_atencion, atendido
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AdmisionEmergencia {self.numero_cuenta}>"


class TriajeEmergencia(Base):
    """Triaje de emergencia: signos vitales + clasificacion de prioridad (I=grave, II, III=leve)."""
    __tablename__ = "triajes_emergencia"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    admision_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("admisiones_emergencia.id", ondelete="CASCADE"), unique=True)

    prioridad: Mapped[str] = mapped_column(String(5))  # I, II, III

    pulso: Mapped[int | None] = mapped_column(Integer, nullable=True)
    temperatura: Mapped[float | None] = mapped_column(Float, nullable=True)
    presion_sistolica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    presion_diastolica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frecuencia_cardiaca: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frecuencia_respiratoria: Mapped[int | None] = mapped_column(Integer, nullable=True)
    peso: Mapped[float | None] = mapped_column(Float, nullable=True)
    talla: Mapped[float | None] = mapped_column(Float, nullable=True)
    saturacion_o2: Mapped[float | None] = mapped_column(Float, nullable=True)

    observacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @property
    def imc(self) -> float | None:
        if not self.peso or not self.talla:
            return None
        return round(self.peso / ((self.talla / 100) ** 2), 1)

    def __repr__(self) -> str:
        return f"<TriajeEmergencia prioridad={self.prioridad}>"


class AtencionEmergencia(Base):
    """Atencion medica de emergencia -- mismo espiritu que AtencionMedica de Consulta Externa,
    pero con set de destinos propio (incluye AMBULATORIA y FALLECIDO)."""
    __tablename__ = "atenciones_emergencia"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    admision_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("admisiones_emergencia.id", ondelete="CASCADE"), unique=True)
    medico_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="SET NULL"), nullable=True)

    motivo_consulta: Mapped[str] = mapped_column(Text)
    examen_clinico: Mapped[str | None] = mapped_column(Text, nullable=True)
    plan_tratamiento: Mapped[str | None] = mapped_column(Text, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    destino_atencion: Mapped[str] = mapped_column(String(30), default="AMBULATORIA")  # AMBULATORIA, HOSPITALIZACION, REFERENCIA, INTERCONSULTA, ALTA, FALLECIDO

    estado: Mapped[str] = mapped_column(String(20), default="borrador")  # borrador, firmado
    firmado_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    firmado_por_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="SET NULL"), nullable=True)
    cierre_evidencia: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AtencionEmergencia {self.admision_id}>"


class EmergenciaDiagnostico(Base):
    __tablename__ = "emergencia_diagnosticos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    atencion_emergencia_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_emergencia.id", ondelete="CASCADE"))
    diagnostico_cie10_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_diagnosticos_cie10.id", ondelete="CASCADE"))
    tipo: Mapped[str] = mapped_column(String(20), default="definitivo")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DestinoEmergencia(Base):
    """Derivación generada al firmar la atención y consumida por el módulo destino."""
    __tablename__ = "emergencia_destinos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    atencion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("atenciones_emergencia.id", ondelete="CASCADE"), unique=True
    )
    destino: Mapped[str] = mapped_column(String(30), index=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", index=True)
    observacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
