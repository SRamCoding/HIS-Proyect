from fastapi import Request
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# Motor principal — BD central (tenants, módulos, usuarios globales)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,       # muestra las queries en consola en desarrollo
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,        # verifica conexión antes de usarla
)

# Sesión async — equivalente al DB facade de Laravel
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Base para todos los modelos SQLAlchemy."""
    pass


async def _bd_fisica_sigarh(request: Request) -> str | None:
    """Resuelve el nombre de la BD física del hospital para una petición /sigarh/*.

    El JWT ya trae tenant_id resuelto (usuario_actual/contexto_sigarh); se lee
    ahí directamente para evitar depender de get_current_user (que a su vez
    depende de get_db) y así no crear una dependencia circular. El panel admin
    no tiene tenant_id en su JWT y usa el header X-Tenant-ID como excepción
    (mismo criterio que get_tenant_id() en sigarh/mantenimiento/router.py).
    """
    import uuid as _uuid
    from app.core.security import verify_token

    tenant_id_raw = None
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        payload = verify_token(auth.removeprefix("Bearer ").strip())
        if payload:
            tenant_id_raw = payload.get("tenant_id")
    if not tenant_id_raw:
        tenant_id_raw = request.headers.get("X-Tenant-ID")
    if not tenant_id_raw:
        return None
    try:
        tenant_id = _uuid.UUID(str(tenant_id_raw))
    except (ValueError, TypeError):
        return None

    from app.tenants.hospitales.models import Tenant
    async with AsyncSessionLocal() as central:
        tenant = await central.get(Tenant, tenant_id)
    return tenant.database_name if tenant else None


async def get_db_central() -> AsyncSession:
    """Siempre la BD central. Uso exclusivo de get_current_user (necesita
    resolver Tenant/User centrales antes de saber a qué hospital pertenece
    la petición); nunca la use un router de negocio."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db(request: Request) -> AsyncSession:
    """
    Dependency de FastAPI — equivalente al DB::transaction de Laravel.
    Uso: db: AsyncSession = Depends(get_db)

    Los módulos SIGARH viven en la BD física del hospital cuando este la
    tiene (mismo criterio que el login: auth/router.py y
    sigarh/mantenimiento/security.py::usuario_actual). Todo lo demás (admin,
    app, auth) sigue igual, siempre contra la BD central.
    """
    session_factory = AsyncSessionLocal
    if request.url.path.startswith("/sigarh/"):
        database_name = await _bd_fisica_sigarh(request)
        if database_name:
            from app.core.tenant_db import get_tenant_sessionmaker
            session_factory = get_tenant_sessionmaker(database_name)

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()