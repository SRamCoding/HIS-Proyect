import uuid
from datetime import datetime
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.sigarh.mantenimiento.schemas import validar_password
from app.tenants.hospitales.branding import normalizar_logo


class TenantBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=3, max_length=255)
    logo_url: str | None = None
    domain: str = Field(min_length=4, max_length=255)
    ruc: str | None = Field(default=None, pattern=r"^\d{11}$")
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    hospital_level: str | None = None
    mission: str | None = None
    vision: str | None = None
    values: str | None = None
    schedule: dict | None = None
    social_media: dict | None = None

    @field_validator("domain")
    @classmethod
    def _v_domain(cls, value: str) -> str:
        value = value.lower().rstrip(".")
        if not re.fullmatch(
            r"(?=.{4,253}$)(?!-)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
            r"[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?",
            value,
        ):
            raise ValueError("El dominio no es válido")
        if value.split(".")[0] in {"www", "api", "his-erp", "admin"}:
            raise ValueError("El subdominio está reservado")
        return value


class TenantCreate(TenantBase):
    _logo = field_validator("logo_url")(normalizar_logo)
    active_modules: list[str] = Field(default_factory=list)
    admin_name: str | None = None
    admin_email: str | None = None
    admin_password: str | None = None
    sigarh_name: str | None = None
    sigarh_email: str | None = None
    sigarh_password: str | None = None

    @field_validator("admin_password", "sigarh_password")
    @classmethod
    def _v_password(cls, v):
        return validar_password(v) if v else v

    @field_validator("admin_email", "sigarh_email")
    @classmethod
    def _v_email(cls, value):
        if value is None:
            return value
        value = value.lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("El correo electrónico no es válido")
        return value

    @field_validator("active_modules")
    @classmethod
    def _v_modules(cls, value):
        normalized = [code.strip().lower() for code in value if code.strip()]
        if len(normalized) != len(set(normalized)):
            raise ValueError("La lista de módulos contiene duplicados")
        return normalized

    @model_validator(mode="after")
    def _v_initial_users(self):
        from app.core.config import settings

        admin = (self.admin_name, self.admin_email, self.admin_password)
        sigarh = (self.sigarh_name, self.sigarh_email, self.sigarh_password)
        if not all(admin):
            raise ValueError("Nombre, correo y contraseña del usuario App son obligatorios")
        if not all(sigarh):
            raise ValueError("Nombre, correo y contraseña del usuario SIGARH son obligatorios")
        if self.admin_email == self.sigarh_email:
            raise ValueError("Los usuarios App y SIGARH deben usar correos diferentes")
        suffix = f".{settings.TENANT_BASE_DOMAIN.lower().strip('.')}"
        if not self.domain.endswith(suffix):
            raise ValueError(f"El dominio debe terminar en {suffix}")
        return self


class TenantUpdate(TenantBase):
    _logo = field_validator("logo_url")(normalizar_logo)
    name: str | None = None
    domain: str | None = None
    active_modules: list[str] | None = None
    is_active: bool | None = None


class TenantResponse(TenantBase):
    id: uuid.UUID
    schema_name: str
    is_active: bool
    database_name: str
    active_modules: list[str] = Field(default_factory=list)
    created_at: datetime
    provisioning_status: str = "listo"
    provisioning_error: str | None = None

    model_config = {"from_attributes": True}
