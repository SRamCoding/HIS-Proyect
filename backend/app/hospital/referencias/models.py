"""Referencias: el registro (tabla `referencias`) vive en consulta_externa.models
porque ahí nació, ligado 1:1 a la Atención Médica que lo originaba. Este módulo
agrega lo que faltaba para cerrar el ciclo: admisión desde Emergencia,
resolución (aceptada/rechazada) y registro de la contrarreferencia -- además
del correlativo propio."""
import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ReferenciaCorrelativo(Base):
    __tablename__ = "referencia_correlativos"
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(20), primary_key=True)
    valor: Mapped[int] = mapped_column(default=0)
