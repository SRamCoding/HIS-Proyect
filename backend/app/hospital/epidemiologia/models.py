import uuid
from datetime import date, datetime
from sqlalchemy import String, Text, Integer, DateTime, Date, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

"""Epidemiología -- notificación de Enfermedades de Notificación Obligatoria
(ENO) y daños no transmisibles bajo vigilancia, al Centro Nacional de
Epidemiología, Prevención y Control de Enfermedades (CDC-MINSA), vía el
Registro Nacional de Epidemiología (RENACE). Este ERP no tiene integración
real con RENACE -- registra localmente la ficha y su estado de envío a la
Red de Salud, igual de honesto que Firma Electrónica/Defunciones.

Una sola tabla, FichaEpidemiologica, con datos_clinicos en JSON: cada tipo
de ficha (COVID, Cáncer, Diabetes, Dengue, Leptospirosis) tiene campos
clínicos genuinamente distintos entre sí (signos de alarma en dengue,
estadio en cáncer, HbA1c en diabetes...), así que forzarlos a una tabla
ancha con decenas de columnas nulas sería peor que un JSON validado por un
schema específico por tipo -- mismo criterio que AtencionMedica.prestaciones
y AtencionMedica.antecedentes_snapshot ya usan en este mismo código base."""


class EpidemiologiaCorrelativo(Base):
    __tablename__ = "epidemiologia_correlativos"
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(30), primary_key=True)
    valor: Mapped[int] = mapped_column(Integer, default=0)


class FichaEpidemiologica(Base):
    __tablename__ = "epidemiologia_fichas"
    __table_args__ = (
        UniqueConstraint("atencion_medica_id", "tipo_ficha", name="uq_ficha_epi_atencion_medica_tipo"),
        UniqueConstraint("atencion_emergencia_id", "tipo_ficha", name="uq_ficha_epi_atencion_emergencia_tipo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    atencion_medica_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_medicas.id", ondelete="CASCADE"), nullable=True)
    atencion_emergencia_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_emergencia.id", ondelete="CASCADE"), nullable=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"))
    diagnostico_cie10_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_diagnosticos_cie10.id", ondelete="SET NULL"), nullable=True)
    medico_notificante_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="RESTRICT"))

    numero_ficha: Mapped[str] = mapped_column(String(30), unique=True)
    tipo_ficha: Mapped[str] = mapped_column(String(20), index=True)  # COVID, CANCER, DIABETES, DENGUE, LEPTOSPIROSIS
    fecha_notificacion: Mapped[date] = mapped_column(Date, default=date.today)
    datos_clinicos: Mapped[dict] = mapped_column(JSON)

    estado_envio: Mapped[str] = mapped_column(String(20), default="registrada", index=True)  # registrada, enviada_red_salud
    fecha_envio: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<FichaEpidemiologica {self.tipo_ficha} {self.numero_ficha}>"
