import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Text, Integer, Float, ForeignKey, UniqueConstraint, Index, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ProgramacionMedica(Base):
    """Programacion de horarios de atencion — generica para cualquier servicio
    (Consulta Externa, Imagenologia, Laboratorio, etc). especialidad_id es opcional
    porque servicios como Imagenes/Lab no siempre tienen especialidad medica asociada."""
    __tablename__ = "programaciones_medicas"
    __table_args__ = (
        UniqueConstraint("tenant_id", "origen_sigarh_turno_id", "fecha", name="uq_programacion_sigarh_turno_fecha"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)

    medico_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    servicio_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_servicios.id", ondelete="SET NULL"), nullable=True)
    especialidad_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_especialidades.id", ondelete="SET NULL"), nullable=True)
    origen_sigarh_turno_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sigarh_roles_turno_turnos.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Correlativo legible; lo asigna la secuencia en cualquier inserción (sync o manual).
    codigo: Mapped[str] = mapped_column(
        String(20), index=True,
        server_default=text("nextval('programacion_medica_codigo_seq')::text"),
    )
    consultorio_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sigarh_consultorios.id", ondelete="SET NULL"), nullable=True
    )

    fecha: Mapped[date] = mapped_column(Date)
    turno: Mapped[str] = mapped_column(String(20))
    hora_inicio: Mapped[str] = mapped_column(String(5))
    hora_fin: Mapped[str] = mapped_column(String(5))
    tiempo_promedio_atencion: Mapped[int] = mapped_column(Integer, default=15)

    tipo_servicio: Mapped[str] = mapped_column(String(50), default="CONSULTORIO_EXTERNO")
    modalidad: Mapped[str] = mapped_column(String(20), default="PRESENCIAL", server_default="PRESENCIAL")
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
    __table_args__ = (
        # Evita doble reserva del mismo cupo bajo concurrencia (dos operadores
        # reservando el mismo horario a la vez); las canceladas no cuentan.
        Index(
            "ux_citas_cupo_activo", "programacion_medica_id", "hora_inicio",
            unique=True, postgresql_where=text("estado <> 'cancelada'"),
        ),
    )

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
    

class OrdenLaboratorio(Base):
    """Orden de examenes de laboratorio generada desde una Atencion Medica (destino=LABORATORIO).
    Solo la solicitud; la toma de muestra y resultados los maneja el modulo Laboratorio."""
    __tablename__ = "ordenes_laboratorio"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    atencion_medica_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_medicas.id", ondelete="CASCADE"), unique=True, nullable=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"), nullable=True)
    emergencia_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("admisiones_emergencia.id", ondelete="RESTRICT"), nullable=True)
    tipo_servicio: Mapped[str] = mapped_column(String(30), default="CONSULTA_EXTERNA", server_default="CONSULTA_EXTERNA")
    servicio_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_servicios.id", ondelete="RESTRICT"), nullable=True)
    especialidad_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_especialidades.id", ondelete="RESTRICT"), nullable=True)
    medico_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="RESTRICT"), nullable=True)
    numero_cuenta: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fuente_financiamiento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    numero_orden: Mapped[str] = mapped_column(String(30), unique=True)
    indicacion_clinica: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, en_proceso, completada, anulada
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<OrdenLaboratorio {self.numero_orden}>"


class OrdenLaboratorioItem(Base):
    """Examen solicitado dentro de una orden de laboratorio."""
    __tablename__ = "orden_laboratorio_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    orden_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ordenes_laboratorio.id", ondelete="CASCADE"))
    examen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_examenes_laboratorio.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<OrdenLaboratorioItem {self.examen_id}>"


class Interconsulta(Base):
    """Solicitud de interconsulta a otra especialidad desde Consulta Externa.
    Queda pendiente para que Admision la programe como una Cita nueva."""
    __tablename__ = "interconsultas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    atencion_medica_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_medicas.id", ondelete="CASCADE"), unique=True)
    especialidad_destino_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_especialidades.id", ondelete="CASCADE"))
    diagnostico_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_diagnosticos_cie10.id", ondelete="SET NULL"), nullable=True)
    motivo: Mapped[str] = mapped_column(Text)
    urgente: Mapped[bool] = mapped_column(Boolean, default=False)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, programada, atendida
    cita_generada_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("citas.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Interconsulta {self.especialidad_destino_id}>"


class OrdenImagen(Base):
    """Orden de examenes de imagenologia generada desde una Atencion Medica (destino=IMAGEN)."""
    __tablename__ = "ordenes_imagen"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    atencion_medica_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_medicas.id", ondelete="CASCADE"), unique=True)
    numero_orden: Mapped[str] = mapped_column(String(30), unique=True)
    indicacion_clinica: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<OrdenImagen {self.numero_orden}>"


class OrdenImagenItem(Base):
    __tablename__ = "orden_imagen_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    orden_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ordenes_imagen.id", ondelete="CASCADE"))
    examen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_examenes_imagenologia.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<OrdenImagenItem {self.examen_id}>"


class Referencia(Base):
    """Referencia de paciente a otro establecimiento (Norma Tecnica N 018-MINSA/DGSP-V.01).
    Puede ser a un IPRESS externo (texto libre) o a otro tenant de nuestro propio sistema."""
    __tablename__ = "referencias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    atencion_medica_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_medicas.id", ondelete="CASCADE"), unique=True)

    # Destino externo (fuera de nuestro sistema) -- texto libre, formato oficial RENIPRESS
    codigo_renipress_destino: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nombre_ipress_destino: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Destino interno (otro hospital que usa nuestro mismo ERP)
    tenant_destino_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True)

    especialidad_destino: Mapped[str | None] = mapped_column(String(150), nullable=True)
    diagnostico_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_diagnosticos_cie10.id", ondelete="SET NULL"), nullable=True)
    motivo: Mapped[str] = mapped_column(Text)
    numero_referencia: Mapped[str] = mapped_column(String(30), unique=True)
    estado: Mapped[str] = mapped_column(String(20), default="enviada")  # enviada, aceptada, rechazada, contrarreferida
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Referencia {self.numero_referencia}>"



