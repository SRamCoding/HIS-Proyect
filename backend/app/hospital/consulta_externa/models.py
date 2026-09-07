import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Text, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ProgramacionMedica(Base):
    """Programacion de horarios de atencion — generica para cualquier servicio
    (Consulta Externa, Imagenologia, Laboratorio, etc). especialidad_id es opcional
    porque servicios como Imagenes/Lab no siempre tienen especialidad medica asociada."""
    __tablename__ = "programaciones_medicas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)

    medico_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    servicio_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_servicios.id", ondelete="SET NULL"), nullable=True)
    especialidad_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_especialidades.id", ondelete="SET NULL"), nullable=True)

    fecha: Mapped[date] = mapped_column(Date)
    turno: Mapped[str] = mapped_column(String(20))
    hora_inicio: Mapped[str] = mapped_column(String(5))
    hora_fin: Mapped[str] = mapped_column(String(5))
    tiempo_promedio_atencion: Mapped[int] = mapped_column(Integer, default=15)

    tipo_servicio: Mapped[str] = mapped_column(String(50), default="CONSULTORIO_EXTERNO")
    mostrar_en_consultorio: Mapped[bool] = mapped_column(Boolean, default=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ProgramacionMedica {self.medico_id} {self.fecha} {self.turno}>"


class Cita(Base):
    """Cita agendada dentro de un cupo de una ProgramacionMedica."""
    __tablename__ = "citas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)

    programacion_medica_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("programaciones_medicas.id", ondelete="CASCADE"))
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"))

    hora_inicio: Mapped[str] = mapped_column(String(5))
    hora_fin: Mapped[str] = mapped_column(String(5))

    tipo_consulta: Mapped[str | None] = mapped_column(String(50), nullable=True)
    observacion: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Campos de facturacion -- stub simple, la logica real de vinculacion vive en Caja/Cobros
    numero_cuenta: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cuenta_vinculada: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fuente_financiamiento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    producto_plan: Mapped[str | None] = mapped_column(String(100), nullable=True)

    estado: Mapped[str] = mapped_column(String(20), default="separada")  # separada, atendida, cancelada, no_asistio

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Cita {self.patient_id} {self.hora_inicio}>"


class Triaje(Base):
    """Registro de signos vitales realizado por enfermeria antes de la atencion medica."""
    __tablename__ = "triajes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    cita_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("citas.id", ondelete="CASCADE"), unique=True)
    realizado_por_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="SET NULL"), nullable=True)

    pulso: Mapped[int | None] = mapped_column(Integer, nullable=True)
    temperatura: Mapped[float | None] = mapped_column(Float, nullable=True)
    presion_sistolica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    presion_diastolica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frecuencia_cardiaca: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frecuencia_respiratoria: Mapped[int | None] = mapped_column(Integer, nullable=True)
    peso: Mapped[float | None] = mapped_column(Float, nullable=True)       # kg
    talla: Mapped[float | None] = mapped_column(Float, nullable=True)      # cm
    perimetro_abdominal: Mapped[float | None] = mapped_column(Float, nullable=True)
    perimetro_cefalico: Mapped[float | None] = mapped_column(Float, nullable=True)
    saturacion_o2: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @property
    def imc(self) -> float | None:
        if not self.peso or not self.talla:
            return None
        talla_m = self.talla / 100
        return round(self.peso / (talla_m ** 2), 1)

    def __repr__(self) -> str:
        return f"<Triaje cita={self.cita_id}>"

class AtencionMedica(Base):
    """Atencion medica de consulta externa (formato MINSA). Antecedentes viven en Patient."""
    __tablename__ = "atenciones_medicas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    cita_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("citas.id", ondelete="CASCADE"), unique=True)

    motivo_consulta: Mapped[str] = mapped_column(Text)
    examen_clinico: Mapped[str | None] = mapped_column(Text, nullable=True)
    plan_tratamiento: Mapped[str | None] = mapped_column(Text, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    indicaciones_alta: Mapped[str | None] = mapped_column(Text, nullable=True)
    destino_atencion: Mapped[str] = mapped_column(String(30), default="ALTA")

    estado: Mapped[str] = mapped_column(String(20), default="borrador")  # borrador, firmado
    firmado_por_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="SET NULL"), nullable=True)
    firmado_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AtencionMedica cita={self.cita_id}>"


class AtencionDiagnostico(Base):
    """Diagnosticos CIE-10 asociados a una atencion medica."""
    __tablename__ = "atencion_diagnosticos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    atencion_medica_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_medicas.id", ondelete="CASCADE"))
    diagnostico_cie10_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_diagnosticos_cie10.id", ondelete="CASCADE"))
    tipo: Mapped[str] = mapped_column(String(20), default="definitivo")  # presuntivo, definitivo, repetitivo
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AtencionDiagnostico {self.diagnostico_cie10_id} ({self.tipo})>"


class Receta(Base):
    """Receta medica generada desde una Atencion Medica (destino=FARMACIA).
    Solo la prescripcion; el despacho real lo maneja el modulo Farmacia."""
    __tablename__ = "recetas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    atencion_medica_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_medicas.id", ondelete="CASCADE"), unique=True)
    numero_receta: Mapped[str] = mapped_column(String(30), unique=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, despachada, parcial, anulada
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Receta {self.numero_receta}>"


class RecetaItem(Base):
    """Medicamento prescrito dentro de una receta."""
    __tablename__ = "receta_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receta_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recetas.id", ondelete="CASCADE"))
    medicamento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_medicamentos.id", ondelete="CASCADE"))
    cantidad: Mapped[int] = mapped_column(Integer)
    dosis: Mapped[str | None] = mapped_column(String(100), nullable=True)      # ej "1 tableta"
    frecuencia: Mapped[str | None] = mapped_column(String(100), nullable=True) # ej "cada 8 horas"
    duracion_dias: Mapped[int | None] = mapped_column(Integer, nullable=True)
    indicaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<RecetaItem {self.medicamento_id} x{self.cantidad}>"



class Hospitalizacion(Base):
    """Registro de ingreso a hospitalizacion generado desde una Atencion Medica.
    Al ingresar, la Cama pasa a OCUPADA; al dar de alta, vuelve a DISPONIBLE."""
    __tablename__ = "hospitalizaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    atencion_medica_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_medicas.id", ondelete="CASCADE"), unique=True)
    cama_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_camas.id", ondelete="RESTRICT"))
    especialidad_ingreso_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_especialidades.id", ondelete="SET NULL"), nullable=True)
    diagnostico_ingreso_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_diagnosticos_cie10.id", ondelete="SET NULL"), nullable=True)

    numero_hospitalizacion: Mapped[str] = mapped_column(String(30), unique=True)
    fecha_ingreso: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fecha_alta: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="internado")  # internado, alta

    def __repr__(self) -> str:
        return f"<Hospitalizacion {self.numero_hospitalizacion}>"