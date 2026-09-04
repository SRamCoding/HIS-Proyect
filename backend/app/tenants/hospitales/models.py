import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Tenant(Base):
    """
    Hospital registrado en el sistema.
    Equivalente al modelo Tenant de Stancl Tenancy en Laravel.
    Cada tenant tiene su propio schema en PostgreSQL.
    """
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255))           # nombre del hospital
    domain: Mapped[str] = mapped_column(String(255), unique=True)  # hospital-tuman.erp.local
    schema_name: Mapped[str] = mapped_column(String(100), unique=True)  # tenant_hospital_tuman
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Datos del hospital
    ruc: Mapped[str | None] = mapped_column(String(11))
    address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    logo_url: Mapped[str | None] = mapped_column(Text)
    hospital_level: Mapped[str | None] = mapped_column(String(10))  # I-1, I-2, II-1, III-1...

    # Landing page del hospital (equivalente al wizard de TenantResource en Laravel)
    mission: Mapped[str | None] = mapped_column(Text)
    vision: Mapped[str | None] = mapped_column(Text)
    values: Mapped[str | None] = mapped_column(Text)
    schedule: Mapped[dict | None] = mapped_column(JSON)      # horarios de atención
    social_media: Mapped[dict | None] = mapped_column(JSON)  # redes sociales

    # Config SUNAT
    sunat_cert: Mapped[str | None] = mapped_column(Text)
    invoice_series: Mapped[str | None] = mapped_column(String(10))
    receipt_series: Mapped[str | None] = mapped_column(String(10))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relaciones
    modules: Mapped[list["TenantModule"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )

    @property
    def active_module_codes(self) -> list[str]:
        """Lista de códigos de módulos activos — equivalente a active_modules en Laravel."""
        return [m.module_code for m in self.modules if m.is_active]

    def __repr__(self) -> str:
        return f"<Tenant {self.name} ({self.domain})>"


class TenantModule(Base):
    """
    Módulos activos por tenant.
    Equivalente a la tabla tenant_modules de Laravel + el CheckboxList de TenantResource.
    """
    __tablename__ = "tenant_modules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE")
    )
    module_code: Mapped[str] = mapped_column(String(100))  # admision, farmacia, laboratorio...
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    activated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    tenant: Mapped["Tenant"] = relationship(back_populates="modules")

    def __repr__(self) -> str:
        return f"<TenantModule {self.module_code} → {self.tenant_id}>"
