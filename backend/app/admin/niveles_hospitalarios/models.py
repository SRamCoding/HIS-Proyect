import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


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
