import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

"""Firma Electrónica -- registro central de trazabilidad de firmas de
documentos clínicos, en la línea de la Ley N.° 30024 (crea el RENHICE --
Registro Nacional de Historias Clínicas Electrónicas) y de la Norma Técnica
de Salud para la Gestión de la Historia Clínica Electrónica (NTS
N.° 139-MINSA/2018/DGAIN). La validación de identidad del firmante (cuenta
médica vinculada a un Empleado activo, profesión MED, colegiatura habilitada
con N.° CMP/colegiatura registrado) se hace en el propio acto de firma de
cada módulo clínico (Consulta Externa y Emergencia) -- este módulo no la
repite, la consume: cada firma real ya deja su propia evidencia con hash
SHA-256 en el documento firmado (AtencionMedica.cierre_evidencia /
AtencionEmergencia.cierre_evidencia); FirmaElectronicaRegistro es la bandeja
de firmas pendientes y el libro de trazabilidad centralizado de esas firmas,
tal como exige la Ley N.° 27269 (Ley de Firmas y Certificados Digitales)
para poder auditar quién firmó qué y cuándo. Se etiqueta honestamente como
firma electrónica interna del establecimiento, sin certificado digital de la
IOFE -- no se simula ni se afirma tener un certificado que este ERP no
emite."""


class FirmaElectronicaRegistro(Base):
    """Un registro por cada firma aplicada desde la Bandeja."""
    __tablename__ = "firma_electronica_registros"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    documento_tipo: Mapped[str] = mapped_column(String(30), index=True)  # ATENCION_MEDICA, ATENCION_EMERGENCIA
    documento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"))
    firmante_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="RESTRICT"))
    firmante_nombre: Mapped[str] = mapped_column(String(255))
    numero_colegiatura: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sha256: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<FirmaElectronicaRegistro {self.documento_tipo} {self.documento_id}>"
