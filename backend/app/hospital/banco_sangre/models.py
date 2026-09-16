import uuid
from datetime import date, datetime
from sqlalchemy import String, Text, Boolean, Integer, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

"""Banco de Sangre -- Ley N.° 26454 (declara de orden público e interés
nacional la obtención, donación, conservación, transfusión y suministro de
sangre humana; crea el PRONAHEBAS -- Programa Nacional de Hemoterapia y
Bancos de Sangre) y su reglamento, D.S. N.° 03-95-SA.

Flujo real modelado:
  Donante -> UnidadSangre (extracción + tamizaje serológico obligatorio) ->
  ComponenteSanguineo (fraccionamiento) -> inventario disponible.
  SolicitudTransfusional (origen dual/triple: Consulta Externa, Emergencia u
  Hospitalización, igual que Interconsulta/Referencia) -> asignación de
  componentes + prueba cruzada -> dispensación.
  MovimientoSangre es el kardex/trazabilidad de cada componente (ingreso por
  fraccionamiento, salida por transfusión, descarte, vencimiento) -- exigencia
  central de PRONAHEBAS: toda unidad debe poder rastrearse del donante al
  receptor."""


class BancoSangreCorrelativo(Base):
    """Numeración atómica por tenant (numero_unidad, numero_solicitud, codigo_componente)."""
    __tablename__ = "banco_sangre_correlativos"
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(30), primary_key=True)
    valor: Mapped[int] = mapped_column(Integer, default=0)


class Donante(Base):
    """Registro de donante de sangre. No siempre es un Patient del hospital --
    la donación es un proceso propio (campañas, donantes de reposición para un
    familiar, donantes voluntarios) que no siempre pasa por Admisión."""
    __tablename__ = "banco_sangre_donantes"
    __table_args__ = (UniqueConstraint("tenant_id", "dni", name="uq_donante_tenant_dni"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    dni: Mapped[str] = mapped_column(String(15))
    nombres: Mapped[str] = mapped_column(String(150))
    apellido_paterno: Mapped[str] = mapped_column(String(100))
    apellido_materno: Mapped[str] = mapped_column(String(100))
    fecha_nacimiento: Mapped[date] = mapped_column(Date)
    sexo: Mapped[str] = mapped_column(String(1))  # M, F
    celular: Mapped[str | None] = mapped_column(String(15), nullable=True)
    correo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    direccion: Mapped[str | None] = mapped_column(Text, nullable=True)

    grupo_sanguineo: Mapped[str | None] = mapped_column(String(2), nullable=True)  # A, B, AB, O (se confirma en la 1a donación)
    factor_rh: Mapped[str | None] = mapped_column(String(1), nullable=True)        # +, -
    fecha_ultima_donacion: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # false = diferido permanente

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @property
    def nombre_completo(self) -> str:
        return f"{self.apellido_paterno} {self.apellido_materno}, {self.nombres}"

    def __repr__(self) -> str:
        return f"<Donante {self.dni}>"


class UnidadSangre(Base):
    """Una unidad de sangre total extraída a un donante en un acto de donación.
    El tamizaje serológico de las 5 pruebas obligatorias en Perú (VIH, Hepatitis
    B, Hepatitis C, Sífilis, Chagas) se registra aquí; si alguna resulta
    reactiva la unidad queda DESCARTADA y no se fracciona."""
    __tablename__ = "banco_sangre_unidades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    donante_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("banco_sangre_donantes.id", ondelete="RESTRICT"))
    numero_unidad: Mapped[str] = mapped_column(String(30), unique=True)

    fecha_extraccion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    peso_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    hemoglobina_g_dl: Mapped[float | None] = mapped_column(Float, nullable=True)
    presion_sistolica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    presion_diastolica: Mapped[int | None] = mapped_column(Integer, nullable=True)

    grupo_sanguineo: Mapped[str] = mapped_column(String(2))  # A, B, AB, O
    factor_rh: Mapped[str] = mapped_column(String(1))        # +, -

    # Tamizaje serológico obligatorio (PRONAHEBAS) -- null = aún no procesado
    vih_reactivo: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    hbsag_reactivo: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    hcv_reactivo: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    sifilis_reactivo: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    chagas_reactivo: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tamizaje_registrado_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    apto: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # lo confirma el responsable tras ver el tamizaje
    motivo_diferido: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="extraida", index=True)  # extraida, descartada, fraccionada

    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<UnidadSangre {self.numero_unidad}>"


class ComponenteSanguineo(Base):
    """Hemocomponente obtenido al fraccionar una UnidadSangre apta. Vida útil de
    referencia estándar de medicina transfusional (varía según el sistema
    anticoagulante/conservación real del banco):
    Paquete Globular 35 d · Plasma Fresco Congelado 365 d · Plaquetas 5 d ·
    Crioprecipitado 365 d · Sangre Total (sin fraccionar) 35 d."""
    __tablename__ = "banco_sangre_componentes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    unidad_sangre_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("banco_sangre_unidades.id", ondelete="RESTRICT"))
    codigo: Mapped[str] = mapped_column(String(30), unique=True)

    tipo: Mapped[str] = mapped_column(String(30))  # PAQUETE_GLOBULAR, PLASMA_FRESCO_CONGELADO, PLAQUETAS, CRIOPRECIPITADO, SANGRE_TOTAL
    grupo_sanguineo: Mapped[str] = mapped_column(String(2))
    factor_rh: Mapped[str] = mapped_column(String(1))

    fecha_produccion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fecha_vencimiento: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(20), default="disponible", index=True)  # disponible, reservado, transfundido, descartado, vencido

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ComponenteSanguineo {self.codigo} {self.tipo}>"


class SolicitudTransfusional(Base):
    """Solicitud de transfusión desde un servicio clínico. Origen dual/triple --
    misma dualidad de Hospitalizacion/Interconsulta/Referencia -- pero SIN
    unicidad por atención: una atención larga (hospitalización) puede requerir
    varias solicitudes en el tiempo, a diferencia de una orden de laboratorio."""
    __tablename__ = "banco_sangre_solicitudes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    atencion_medica_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_medicas.id", ondelete="CASCADE"), nullable=True)
    atencion_emergencia_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("atenciones_emergencia.id", ondelete="CASCADE"), nullable=True)
    hospitalizacion_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("hospitalizaciones.id", ondelete="CASCADE"), nullable=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"))
    medico_solicitante_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="SET NULL"), nullable=True)

    numero_solicitud: Mapped[str] = mapped_column(String(30), unique=True)
    tipo_componente: Mapped[str] = mapped_column(String(30))
    cantidad_unidades: Mapped[int] = mapped_column(Integer, default=1)
    grupo_sanguineo_paciente: Mapped[str] = mapped_column(String(2))
    factor_rh_paciente: Mapped[str] = mapped_column(String(1))
    urgencia: Mapped[str] = mapped_column(String(20), default="RUTINA")  # RUTINA, URGENTE, EMERGENCIA
    motivo_clinico: Mapped[str] = mapped_column(Text)

    estado: Mapped[str] = mapped_column(String(30), default="pendiente", index=True)
    # pendiente, en_pruebas_cruzadas, lista_para_dispensar, dispensada, anulada

    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SolicitudTransfusional {self.numero_solicitud}>"


class SolicitudComponenteAsignado(Base):
    """Componente concreto asignado a una solicitud: prueba cruzada de
    compatibilidad y, tras confirmarse compatible, su dispensación. Un
    componente solo puede asignarse a una solicitud a la vez (unique)."""
    __tablename__ = "banco_sangre_solicitud_componentes"
    __table_args__ = (UniqueConstraint("componente_id", name="uq_componente_una_asignacion"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    solicitud_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("banco_sangre_solicitudes.id", ondelete="CASCADE"))
    componente_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("banco_sangre_componentes.id", ondelete="RESTRICT"))

    resultado_prueba_cruzada: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, compatible, incompatible
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    prueba_cruzada_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    prueba_cruzada_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    dispensado: Mapped[bool] = mapped_column(Boolean, default=False)
    dispensado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dispensado_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SolicitudComponenteAsignado {self.componente_id}>"


class MovimientoSangre(Base):
    """Kardex/trazabilidad de cada componente -- exigencia PRONAHEBAS de poder
    rastrear toda unidad del donante al receptor final."""
    __tablename__ = "banco_sangre_movimientos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    componente_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("banco_sangre_componentes.id", ondelete="CASCADE"))
    solicitud_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("banco_sangre_solicitudes.id", ondelete="SET NULL"), nullable=True)

    tipo: Mapped[str] = mapped_column(String(30))
    # ingreso_fraccionamiento, reserva, liberacion_reserva, salida_transfusion, descarte, vencimiento
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<MovimientoSangre {self.tipo} {self.componente_id}>"
