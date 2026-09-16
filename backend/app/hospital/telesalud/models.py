import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class TelesaludSolicitud(Base):
    """Solicitud de teleconsulta (Ley N.° 30421 -- Ley Marco de Telesalud, modificada
    por la Ley N.° 31166 -- Ley de Telesalud, que reconoce la teleconsulta como
    modalidad sincrónica de telesalud). Es la intención/intake antes de tener un
    cupo real asignado -- igual que ListaEspera en Admisión, pero para modalidad
    virtual. Cuando el personal la programa, se enlaza a una Cita real generada
    sobre una ProgramacionMedica con modalidad='VIRTUAL' (misma tabla que usa
    Consulta Externa) -- no se duplica la agenda ni la atención clínica."""
    __tablename__ = "telesalud_solicitudes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"))
    especialidad_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_especialidades.id", ondelete="SET NULL"), nullable=True)
    cita_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("citas.id", ondelete="SET NULL"), unique=True, nullable=True)

    motivo: Mapped[str] = mapped_column(Text)
    medio_preferido: Mapped[str] = mapped_column(String(20), default="LLAMADA")  # LLAMADA, WHATSAPP, VIDEOLLAMADA
    contacto: Mapped[str | None] = mapped_column(String(100), nullable=True)  # override opcional del telefono/correo del paciente
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", index=True)  # pendiente, programada, rechazada
    motivo_rechazo: Mapped[str | None] = mapped_column(Text, nullable=True)
    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    atendido_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<TelesaludSolicitud {self.patient_id} {self.estado}>"
