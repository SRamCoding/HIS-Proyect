import uuid
from datetime import date, datetime
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

"""Defunciones -- certificación del fallecimiento de un paciente, con la
cadena causal en CIE-10 (formato internacional OMS que usa el Certificado de
Defunción peruano) y seguimiento administrativo de su envío al SINADEF
(Sistema Informático Nacional de Defunciones de MINSA) / RENIEC, que es
quien procesa la inscripción civil real -- este ERP no tiene integración con
esos sistemas, solo registra localmente lo certificado y su estado de envío,
igual de honesto que la firma electrónica interna del propio establecimiento.

Origen dual: el fallecimiento puede declararse desde Emergencia
(AtencionEmergencia.destino_atencion='FALLECIDO') o durante una
Hospitalización -- misma dualidad que Hospitalizacion/Referencia/
Interconsulta. Emitir el certificado es lo que fija destino_atencion en el
origen si aún no lo tenía, no al revés."""


class SaludAmbientalCorrelativo(Base):
    __tablename__ = "salud_ambiental_correlativos"
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(30), primary_key=True)
    valor: Mapped[int] = mapped_column(Integer, default=0)


class CertificadoDefuncion(Base):
    __tablename__ = "salud_ambiental_certificados_defuncion"
    __table_args__ = (
        UniqueConstraint("atencion_emergencia_id", name="uq_certdef_atencion_emergencia"),
        UniqueConstraint("hospitalizacion_id", name="uq_certdef_hospitalizacion"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    atencion_emergencia_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_emergencia.id", ondelete="SET NULL"), nullable=True)
    hospitalizacion_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("hospitalizaciones.id", ondelete="SET NULL"), nullable=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"))
    medico_certificador_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="RESTRICT"))

    numero_certificado: Mapped[str] = mapped_column(String(30), unique=True)
    fecha_defuncion: Mapped[datetime] = mapped_column(DateTime)
    lugar_defuncion: Mapped[str] = mapped_column(String(255))
    tipo_muerte: Mapped[str] = mapped_column(String(20))  # NATURAL, VIOLENTA

    # Cadena causal CIE-10 (formato OMS del certificado de defunción): A = causa
    # directa/inmediata, B y C = causas intermedia/básica, D = otro estado
    # patológico contribuyente (opcional). Se reutiliza el catálogo real de
    # DiagnosticoCIE10, no se inventa uno propio.
    causa_a_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_diagnosticos_cie10.id", ondelete="RESTRICT"))
    causa_b_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_diagnosticos_cie10.id", ondelete="SET NULL"), nullable=True)
    causa_c_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_diagnosticos_cie10.id", ondelete="SET NULL"), nullable=True)
    causa_d_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_diagnosticos_cie10.id", ondelete="SET NULL"), nullable=True)

    requiere_necropsia_legal: Mapped[bool] = mapped_column(Boolean, default=False)  # obligatorio si tipo_muerte=VIOLENTA
    estado_envio: Mapped[str] = mapped_column(String(20), default="registrado", index=True)  # registrado, enviado_reniec
    fecha_envio: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CertificadoDefuncion {self.numero_certificado}>"
