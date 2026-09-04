import uuid
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Module(Base):
    """
    Catálogo de módulos disponibles en el ERP.
    Equivalente a ModuleResource en el panel Admin de Laravel.
    """
    __tablename__ = "modules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(100), unique=True)   # admision, farmacia...
    name: Mapped[str] = mapped_column(String(255))                 # Admisión, Farmacia...
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50))             # clinico, administrativo, sigarh
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return f"<Module {self.code}>"
