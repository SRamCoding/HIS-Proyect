import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


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
