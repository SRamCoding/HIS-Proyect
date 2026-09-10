"""Modelo unificado de Roles de Turno.

Una sola familia de tablas cubre las 15 modalidades (combinaciones de
`categoria_personal` x `tipo_rol`) y las 3 etapas del flujo mediante `status`:

    draft/rejected -> Creación de Roles
    pending        -> Roles Pendientes
    approved       -> Roles Aprobados

Jerarquía:  Rol -> RolEmpleado -> RolActividad -> RolTurno
"""
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


CATEGORIAS_PERSONAL = ("medicos", "otros_profesionales", "residentes", "tecnicos", "internos")
TIPOS_ROL = (
    "ordinario", "complementario", "reten", "ordinario_sin_actividad",
    "ordinario_con_actividad", "complementario_con_actividad", "turnos",
)
ESTADOS_ROL = ("draft", "pending", "approved", "rejected")
ESTADOS_SOLICITUD = ("pendiente", "aprobado", "rechazado")

# Combinaciones válidas (categoria -> tipos permitidos). Total: 15 modalidades.
MODALIDADES: dict[str, list[str]] = {
    "medicos": ["ordinario", "complementario", "reten", "ordinario_sin_actividad"],
    "otros_profesionales": ["ordinario", "complementario", "reten", "ordinario_con_actividad", "complementario_con_actividad"],
    "residentes": ["ordinario"],
    "tecnicos": ["ordinario", "complementario", "reten", "ordinario_con_actividad"],
    "internos": ["turnos"],
}

# Tipo de trabajador esperado por categoría (para filtrar personal).
TIPO_TRABAJADOR_POR_CATEGORIA = {
    "medicos": "medico",
    "otros_profesionales": "otro_profesional",
    "residentes": "residente",
    "tecnicos": "tecnico",
    "internos": "interno",
}


class Rol(Base):
    __tablename__ = "sigarh_roles_turno"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)

    categoria_personal: Mapped[str] = mapped_column(String(30), index=True)
    tipo_rol: Mapped[str] = mapped_column(String(40), index=True)

    departamento_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sigarh_departamentos.id", ondelete="SET NULL"), nullable=True
    )
    servicio_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sigarh_servicios.id", ondelete="SET NULL"), nullable=True
    )
    mes: Mapped[int] = mapped_column(Integer)
    anio: Mapped[int] = mapped_column(Integer, index=True)

    status: Mapped[str] = mapped_column(String(15), default="draft", index=True)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    empleados: Mapped[list["RolEmpleado"]] = relationship(
        back_populates="rol", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Rol {self.categoria_personal}/{self.tipo_rol} {self.mes}/{self.anio} [{self.status}]>"


class RolEmpleado(Base):
    __tablename__ = "sigarh_roles_turno_empleados"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rol_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_roles_turno.id", ondelete="CASCADE"), index=True)
    empleado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    rol: Mapped["Rol"] = relationship(back_populates="empleados")
    actividades: Mapped[list["RolActividad"]] = relationship(
        back_populates="rol_empleado", cascade="all, delete-orphan"
    )


class RolActividad(Base):
    __tablename__ = "sigarh_roles_turno_actividades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rol_empleado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_roles_turno_empleados.id", ondelete="CASCADE"), index=True)
    actividad_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_actividades.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    rol_empleado: Mapped["RolEmpleado"] = relationship(back_populates="actividades")
    turnos: Mapped[list["RolTurno"]] = relationship(
        back_populates="rol_actividad", cascade="all, delete-orphan"
    )


class RolTurno(Base):
    __tablename__ = "sigarh_roles_turno_turnos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rol_actividad_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_roles_turno_actividades.id", ondelete="CASCADE"), index=True)
    horario_guardia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sigarh_horarios_guardia.id", ondelete="SET NULL"), nullable=True
    )
    dias_semana: Mapped[list] = mapped_column(JSONB, default=list)  # 0=domingo ... 6=sabado
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    rol_actividad: Mapped["RolActividad"] = relationship(back_populates="turnos")


class SolicitudModificacionRol(Base):
    __tablename__ = "sigarh_roles_turno_solicitudes_mod"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    rol_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_roles_turno.id", ondelete="CASCADE"), index=True)
    empleado_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="SET NULL"), nullable=True
    )
    motivo: Mapped[str] = mapped_column(Text)
    # {"actividades": [{"actividad_id": "..", "turnos": [{"horario_guardia_id": "..", "dias_semana": [..]}]}]}
    schedule_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(15), default="pendiente", index=True)
    requested_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SolicitudModificacionRol rol={self.rol_id} [{self.status}]>"
