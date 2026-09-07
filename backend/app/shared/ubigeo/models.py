from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class UbigeoDepartamento(Base):
    """Catalogo nacional de ubigeo. Compartido por todos los tenants — NO lleva tenant_id.
    Nombrado 'UbigeoDepartamento' (no 'Departamento') para no chocar con
    app.sigarh.mantenimiento.models.Departamento en el registro de SQLAlchemy."""
    __tablename__ = "ubigeo_departamentos"

    id: Mapped[str] = mapped_column(String(2), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))

    provincias: Mapped[list["UbigeoProvincia"]] = relationship(back_populates="departamento")


class UbigeoProvincia(Base):
    __tablename__ = "ubigeo_provincias"

    id: Mapped[str] = mapped_column(String(4), primary_key=True)
    departamento_id: Mapped[str] = mapped_column(String(2), ForeignKey("ubigeo_departamentos.id"))
    nombre: Mapped[str] = mapped_column(String(100))

    departamento: Mapped["UbigeoDepartamento"] = relationship(back_populates="provincias")
    distritos: Mapped[list["UbigeoDistrito"]] = relationship(back_populates="provincia")


class UbigeoDistrito(Base):
    __tablename__ = "ubigeo_distritos"

    id: Mapped[str] = mapped_column(String(6), primary_key=True)
    provincia_id: Mapped[str] = mapped_column(String(4), ForeignKey("ubigeo_provincias.id"))
    nombre: Mapped[str] = mapped_column(String(100))

    provincia: Mapped["UbigeoProvincia"] = relationship(back_populates="distritos")