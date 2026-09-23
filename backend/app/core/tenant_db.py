"""
Gestión de conexiones y provisión de bases de datos por hospital (tenant).
"""
import re
from urllib.parse import urlparse, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from alembic.config import Config

from alembic import command
from app.core.config import settings

# Cache de engines por hospital, para no abrir uno nuevo en cada request
_tenant_engines: dict[str, "create_async_engine"] = {}


def _slugify_db_name(subdomain: str) -> str:
    """hospital-reque -> his_hospital_reque"""
    clean = re.sub(r"[^a-z0-9_]", "_", subdomain.lower())
    return f"his_{clean}"


def _build_tenant_url(database_name: str) -> str:
    """Reemplaza el nombre de BD en el DATABASE_URL central, conservando host/user/password."""
    parsed = urlparse(settings.DATABASE_URL)
    new_path = f"/{database_name}"
    return urlunparse(parsed._replace(path=new_path))


async def create_tenant_database(database_name: str) -> bool:
    """Crea la base de datos física en Postgres (requiere conexión con CREATE DATABASE).

    Idempotente ante "ya existe": un reintento de aprovisionamiento (hospital
    que quedó en error) puede correr sobre una base que un intento anterior
    alcanzó a crear pero cuya limpieza posterior falló -- fallar de nuevo por
    duplicado en ese caso solo bloquea el reintento sin necesidad.

    Devuelve True solo si ESTA llamada creó la base de verdad, False si ya
    existía. El llamador (aprovisionar_hospital_async) necesita esta
    distinción para decidir si le corresponde borrarla ante un fallo
    posterior: antes se marcaba "creada por mí" sin importar cuál de los
    dos casos era, así que un reintento podía terminar borrando una base
    que en realidad ya existía de un intento anterior (posiblemente ya
    completamente funcional, si lo único que había fallado antes fue
    marcar el estado final como "listo")."""
    import asyncpg

    admin_url = _build_tenant_url("postgres")  # conecta a la BD admin para poder crear otras
    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        async with admin_engine.connect() as conn:
            try:
                await conn.execute(text(f'CREATE DATABASE "{database_name}"'))
                return True
            except Exception as exc:
                # SQLAlchemy async + asyncpg envuelve la excepcion real en un
                # par de wrappers (AsyncAdapt_asyncpg_dbapi.ProgrammingError,
                # etc.) -- comparar solo contra exc.__cause__ nunca matcheaba
                # (la DuplicateDatabaseError real queda uno o mas niveles mas
                # abajo en la cadena), asi que este chequeo de idempotencia
                # nunca se activaba de verdad: cualquier reintento sobre una
                # BD ya creada por un intento anterior volvia a fallar aca
                # mismo, en bucle, sin llegar nunca a revisar si los
                # catalogos/usuarios ya estaban listos.
                causa = exc.__cause__
                while causa is not None:
                    if isinstance(causa, asyncpg.exceptions.DuplicateDatabaseError):
                        return False
                    causa = causa.__cause__
                raise
    finally:
        await admin_engine.dispose()


async def drop_tenant_database(database_name: str) -> None:
    """Elimina exclusivamente una BD recién creada cuya provisión falló."""
    if not re.fullmatch(r"his_[a-z0-9_]+", database_name):
        raise ValueError("Nombre de base hospitalaria inválido")
    admin_engine = create_async_engine(
        _build_tenant_url("postgres"), isolation_level="AUTOCOMMIT"
    )
    try:
        async with admin_engine.connect() as conn:
            await conn.execute(
                text(f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)')
            )
    finally:
        await admin_engine.dispose()


def run_tenant_migrations(database_name: str) -> None:
    """Corre alembic upgrade head contra la BD del tenant nuevo."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.attributes["tenant_database_url"] = _build_tenant_url(database_name)
    command.upgrade(alembic_cfg, "head")


def get_tenant_engine(database_name: str):
    """Devuelve (y cachea) el engine async para la BD de un hospital."""
    if database_name not in _tenant_engines:
        url = _build_tenant_url(database_name)
        _tenant_engines[database_name] = create_async_engine(
            url, pool_size=5, max_overflow=10, pool_pre_ping=True,
        )
    return _tenant_engines[database_name]


def get_tenant_sessionmaker(database_name: str):
    engine = get_tenant_engine(database_name)
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_tenant_by_id(tenant_id):
    """Busca el Tenant en la BD central por su UUID."""
    from app.tenants.hospitales.models import Tenant
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        return await db.get(Tenant, tenant_id)


def tenant_session(database_name: str):
    """Context manager listo para 'async with' sobre la BD de un hospital."""
    return get_tenant_sessionmaker(database_name)()
