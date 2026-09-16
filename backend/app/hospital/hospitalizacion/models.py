"""Hospitalizacion: seguimiento del paciente internado.

El ingreso/alta y el propio registro de Hospitalizacion viven en
consulta_externa.models (tabla hospitalizaciones, compartida con el origen
Emergencia) porque Panel de Camas ya se construyó sobre esa tabla. Este
módulo agrega lo que pasa DESPUÉS del ingreso: notas de evolución y
consentimientos informados, además del correlativo propio."""
import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class HospCorrelativo(Base):
    __tablename__ = "hosp_correlativos"
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(20), primary_key=True)
    valor: Mapped[int] = mapped_column(default=0)


class NotaEvolucion(Base):
    """Nota de evolución diaria (médica o de enfermería) de un paciente internado.
    Mismos signos vitales que Triaje de Consulta Externa/Emergencia -- no se
    inventa un set nuevo, es el mismo vocabulario clínico ya usado en el resto
    del sistema."""
    __tablename__ = "hosp_notas_evolucion"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    hospitalizacion_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("hospitalizaciones.id", ondelete="CASCADE"), index=True)
    autor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="RESTRICT"))
    tipo: Mapped[str] = mapped_column(String(20))  # MEDICA, ENFERMERIA

    pulso: Mapped[int | None] = mapped_column(Integer, nullable=True)
    temperatura: Mapped[float | None] = mapped_column(Float, nullable=True)
    presion_sistolica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    presion_diastolica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frecuencia_cardiaca: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frecuencia_respiratoria: Mapped[int | None] = mapped_column(Integer, nullable=True)
    saturacion_o2: Mapped[float | None] = mapped_column(Float, nullable=True)

    contenido: Mapped[str] = mapped_column(Text)
    plan_indicaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    registrado_por: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<NotaEvolucion {self.hospitalizacion_id} {self.tipo}>"


class ConsentimientoInformado(Base):
    """Registro del consentimiento informado firmado en papel para un
    procedimiento durante la hospitalización (Ley General de Salud, Perú).
    El sistema no maneja firma digital ni adjuntos -- solo el registro
    estructurado de que el documento fue explicado y firmado."""
    __tablename__ = "hosp_consentimientos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    hospitalizacion_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("hospitalizaciones.id", ondelete="CASCADE"), index=True)
    medico_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="RESTRICT"))
    numero: Mapped[str] = mapped_column(String(40))

    procedimiento: Mapped[str] = mapped_column(String(255))
    riesgos_beneficios: Mapped[str] = mapped_column(Text)
    firmante_nombre: Mapped[str] = mapped_column(String(255))
    firmante_documento: Mapped[str] = mapped_column(String(20))
    relacion_firmante: Mapped[str] = mapped_column(String(30), default="PACIENTE")  # PACIENTE, REPRESENTANTE
    testigo_nombre: Mapped[str | None] = mapped_column(String(255), nullable=True)

    estado: Mapped[str] = mapped_column(String(20), default="registrado")  # registrado, revocado
    motivo_revocacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha: Mapped[date] = mapped_column(Date)
    registrado_por: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ConsentimientoInformado {self.numero}>"
