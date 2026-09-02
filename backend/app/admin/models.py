import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class SystemRole(Base):
    __tablename__ = "system_roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    label: Mapped[str] = mapped_column(String(255))
    panel: Mapped[str] = mapped_column(String(50))
    required_module: Mapped[str | None] = mapped_column(String(100), nullable=True)
    allowed_modules: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SystemRole {self.name} ({self.panel})>"


class HospitalLevel(Base):
    """
    Niveles hospitalarios MINSA.
    I-1, I-2, I-3, I-4, II-1, II-2, III-1, III-2, IREN
    Equivalente a HospitalLevel en Laravel.
    """
    __tablename__ = "hospital_levels"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(10), unique=True)   # I-1, II-2, etc.
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)  # #EF4444
    default_modules: Mapped[dict | None] = mapped_column(JSON, nullable=True)   # módulos por defecto
    default_roles: Mapped[dict | None] = mapped_column(JSON, nullable=True)     # roles por defecto
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    

    def __repr__(self) -> str:
        return f"<HospitalLevel {self.code}>"


class ModuleDependency(Base):
    """
    Dependencias entre módulos.
    Equivalente a ModuleDependencies en Laravel.
    Ejemplo: laboratorio requiere admision.
    """
    __tablename__ = "module_dependencies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_code: Mapped[str] = mapped_column(String(100))           # módulo que depende
    depends_on_code: Mapped[str] = mapped_column(String(100))       # módulo requerido
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ModuleDependency {self.module_code} → {self.depends_on_code}>"


class AuditLog(Base):
    """
    Log de auditoría global del ERP.
    Equivalente a ActivityLogResource + Spatie Activity Log en Laravel.
    """
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    user_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    tenant_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(100))        # created, updated, deleted, login...
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)   # Tenant, User...
    model_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    old_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by {self.user_name}>"