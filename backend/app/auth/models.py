import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class User(Base):
    """
    Usuario global del sistema.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(100))       # administrador, medico, enfermera...
    panel: Mapped[str] = mapped_column(String(50))       # admin, app, sigarh, portal
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    empleado_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_empleados.id", ondelete="SET NULL"), nullable=True)
    perfil_hospital_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("hospital_perfiles.id", ondelete="RESTRICT"), nullable=True)
    perfil_usuario_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sigarh_perfiles_usuario.id", ondelete="RESTRICT"), nullable=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
    # Identifica a la cuenta admin fundacional (creada por el seeder), la
    # unica que nunca deberia poder eliminarse/ocultarse por accidente.
    # Antes esa regla se aplicaba comparando el correo contra un texto fijo
    # ("admin@erp.local") en el listado agregado -- si alguien renombraba
    # ese correo, la regla dejaba de aplicar en silencio.
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    session_version: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"


class PerfilHospital(Base):
    __tablename__ = "hospital_perfiles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    role: Mapped[str] = mapped_column(String(100))
    modulos: Mapped[list] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
