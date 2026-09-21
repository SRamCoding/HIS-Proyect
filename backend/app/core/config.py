from typing import Annotated
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ERP Hospitalario"
    APP_ENV: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:3000", "http://localhost:8000"]

    # Base de datos
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # RabbitMQ
    RABBITMQ_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # Limite absoluto de una sesion, sin importar cuantas veces se refresque
    # el token. Sin esto, cada refresh emite un refresh_token nuevo con sus
    # propios 7 dias de vida (REFRESH_TOKEN_EXPIRE_DAYS), asi que una sesion
    # activa podia extenderse indefinidamente refrescando cada 5 minutos.
    SESSION_MAX_DURATION_HOURS: int = 24

    DNI_API_URL: str = "https://dni-api.prowebsolutions.lat/api/consultar"
    DNI_API_KEY: str = ""

    # Multi-tenant
    CENTRAL_DOMAIN: str = "erp.local"
    TENANT_BASE_DOMAIN: str = "techquk.com"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod"}:
                return False
            if normalized in {"development", "dev"}:
                return True
        return value

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            # Soporta tanto JSON como lista separada por comas
            if v.startswith("["):
                import json
                return json.loads(v)
            return [i.strip() for i in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
