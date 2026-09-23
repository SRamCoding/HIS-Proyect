import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Text, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

# NOTA: los modelos de Citados/Agendamiento/Programacion Medica/Altas de este
# grupo de nav NO viven aqui -- ya existen en consulta_externa (ProgramacionMedica,
# Cita) y se reutilizan tal cual (misma logica que Auditoria/General/Fact-Config/
# Seguridad: sin duplicar tablas). Aqui solo van las 3 tablas nuevas que
# realmente le faltaban a Admision: ListaEspera, Anuncio y Mensaje.


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
    record_number: Mapped[str] = mapped_column(String(64), unique=True)
    previous_record_numbers: Mapped[list] = mapped_column(JSON, default=list, server_default="[]")
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


class ListaEspera(Base):
    """Lista de espera de pacientes sin cupo disponible en la especialidad/servicio
    solicitado. Cuando se libera un cupo (nueva ProgramacionMedica o cancelacion),
    el personal de Admision convierte la espera en una Cita real desde Agendamiento
    y la marca 'atendido' aqui, enlazando el cita_id resultante."""
    __tablename__ = "admision_lista_espera"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"))
    servicio_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_servicios.id", ondelete="SET NULL"), nullable=True)
    especialidad_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_especialidades.id", ondelete="SET NULL"), nullable=True)
    cita_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("citas.id", ondelete="SET NULL"), nullable=True)

    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    prioridad: Mapped[str] = mapped_column(String(20), default="normal")  # normal, urgente
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", index=True)  # pendiente, atendido, cancelado
    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    atendido_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<ListaEspera {self.patient_id} {self.estado}>"


class Anuncio(Base):
    """Tablero de avisos internos de Admision (cambios de horario, consultorios
    cerrados, etc). Herramienta operativa interna -- no corresponde a una norma
    MINSA especifica, igual que el modulo Seguridad."""
    __tablename__ = "admision_anuncios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    titulo: Mapped[str] = mapped_column(String(150))
    contenido: Mapped[str] = mapped_column(Text)
    publicado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Anuncio {self.titulo}>"


class Mensaje(Base):
    """Mensajeria interna corta entre personal del hospital ('Mensajito'). Puede
    dirigirse a un usuario puntual o transmitirse a todo un rol, y opcionalmente
    referenciar a un paciente (ej. 'Paciente en sala de espera hace 2h'). No es
    chat en tiempo real: se consulta por polling desde el panel."""
    __tablename__ = "admision_mensajes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    remitente_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    remitente_nombre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    destinatario_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    destinatario_role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="SET NULL"), nullable=True)

    contenido: Mapped[str] = mapped_column(String(500))
    leido: Mapped[bool] = mapped_column(Boolean, default=False)
    leido_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<Mensaje {self.remitente_user_id} -> {self.destinatario_user_id or self.destinatario_role}>"
