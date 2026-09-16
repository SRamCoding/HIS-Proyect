import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


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


class AuditLogFallback(Base):
    """Cola de eventos de auditoría que no se pudieron escribir en AuditLog
    al primer intento. Vive en Postgres (no en un archivo) justamente para
    poder reclamar filas de forma atómica con `SELECT ... FOR UPDATE SKIP
    LOCKED`: eso es lo que permite que el reintento sea seguro con más de
    un worker de Celery corriendo a la vez, algo que un lock en memoria de
    un solo proceso (asyncio.Lock) nunca puede garantizar entre procesos
    distintos.

    `id` se reutiliza como el `id` del AuditLog final cuando se recupera:
    un choque de clave primaria en ese INSERT significa "esta fila ya se
    proceso antes" (un reintento repetido tras una caída a mitad de
    camino), no un error nuevo -- así el reintento es idempotente sin
    necesitar un identificador aparte."""
    __tablename__ = "audit_log_fallback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ocurrido_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    actor: Mapped[dict] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    entrada: Mapped[dict] = mapped_column(JSON)
