import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Patient(Base):
    """NOTA: 'dni' mantiene su nombre por compatibilidad aunque ahora puede contener
    otros tipos de documento (ver document_type). No renombrar la columna."""
    __tablename__ = "patients"
    __table_args__ = (
        UniqueConstraint("tenant_id", "dni", name="ix_patients_tenant_id_dni"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)

    # --- Documento / identificacion ---
    document_type: Mapped[str] = mapped_column(String(20), default="DNI")
    dni: Mapped[str | None] = mapped_column(String(15), nullable=True)
    is_nn: Mapped[bool] = mapped_column(Boolean, default=False)

    # --- Datos personales ---
    first_name: Mapped[str] = mapped_column(String(100))
    second_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name_paterno: Mapped[str] = mapped_column(String(100))
    last_name_materno: Mapped[str] = mapped_column(String(100))
    birth_date: Mapped[date] = mapped_column(Date)
    gender: Mapped[str] = mapped_column(String(1))
    marital_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    education_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ethnicity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # --- Contacto ---
    phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    phone_is_whatsapp: Mapped[bool] = mapped_column(Boolean, default=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # --- Domicilio ---
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    department_id: Mapped[str | None] = mapped_column(String(2), ForeignKey("ubigeo_departamentos.id"), nullable=True)
    province_id: Mapped[str | None] = mapped_column(String(4), ForeignKey("ubigeo_provincias.id"), nullable=True)
    district_id: Mapped[str | None] = mapped_column(String(6), ForeignKey("ubigeo_distritos.id"), nullable=True)
    populated_center: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(50), default="Peru")

    # --- Nacimiento (direccion distinta a domicilio) ---
    birth_same_as_address: Mapped[bool] = mapped_column(Boolean, default=True)
    birth_department_id: Mapped[str | None] = mapped_column(String(2), ForeignKey("ubigeo_departamentos.id"), nullable=True)
    birth_province_id: Mapped[str | None] = mapped_column(String(4), ForeignKey("ubigeo_provincias.id"), nullable=True)
    birth_district_id: Mapped[str | None] = mapped_column(String(6), ForeignKey("ubigeo_distritos.id"), nullable=True)
    birth_populated_center: Mapped[str | None] = mapped_column(String(100), nullable=True)
    birth_country: Mapped[str] = mapped_column(String(50), default="Peru")

       # --- Seguro ---
    insurance_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    insurance_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # --- Antecedentes personales (persisten entre visitas, formato MINSA) ---
    antecedente_quirurgico: Mapped[str | None] = mapped_column(Text, nullable=True)
    antecedente_patologico: Mapped[str | None] = mapped_column(Text, nullable=True)
    antecedente_alergias: Mapped[str | None] = mapped_column(Text, nullable=True)
    antecedentes_obstetricos: Mapped[str | None] = mapped_column(String(50), nullable=True)
    antecedente_familiares: Mapped[str | None] = mapped_column(Text, nullable=True)
    antecedente_otros: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    clinical_record: Mapped["ClinicalRecord"] = relationship(back_populates="patient", uselist=False)

    @property
    def full_name(self) -> str:
        return f"{self.last_name_paterno} {self.last_name_materno}, {self.first_name}"

    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def __repr__(self) -> str:
        return f"<Patient {self.full_name} ({self.dni})>"


class ClinicalRecord(Base):
    __tablename__ = "clinical_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"))
    record_number: Mapped[str] = mapped_column(String(20), unique=True)
    location: Mapped[str] = mapped_column(String(50), default="admision")
    is_digitized: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient: Mapped["Patient"] = relationship(back_populates="clinical_record")
    movements: Mapped[list["ClinicalRecordMovement"]] = relationship(back_populates="clinical_record")

    def __repr__(self) -> str:
        return f"<ClinicalRecord {self.record_number}>"


class ClinicalRecordMovement(Base):
    __tablename__ = "clinical_record_movements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clinical_record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clinical_records.id", ondelete="CASCADE"))
    from_location: Mapped[str] = mapped_column(String(50))
    to_location: Mapped[str] = mapped_column(String(50))
    moved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    clinical_record: Mapped["ClinicalRecord"] = relationship(back_populates="movements")