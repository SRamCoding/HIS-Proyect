import json
from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from redis.asyncio import Redis

from app.core.config import settings
from app.core.database import get_db, AsyncSessionLocal
from app.core.redis import get_redis, cache_set, cache_get


# ─── Obtener tenant desde el request ──────────────────────────────────────────

def get_tenant_domain(request: Request) -> str:
    """
    Extrae el dominio del request.
    Equivalente a InitializeTenancyByDomainIfTenant de Laravel.
    Ejemplos:
      hospital-tuman.erp.local  → tenant
      erp.local                 → dominio central (Admin ERP)
    """
    host = request.headers.get("host", "").split(":")[0]
    return host


def is_central_domain(domain: str) -> bool:
    """
    Verifica si el dominio es el central (Admin ERP).
    Equivalente a PreventAccessFromTenantDomains de Laravel.
    """
    return domain == settings.CENTRAL_DOMAIN


# ─── Sesión con schema del tenant ─────────────────────────────────────────────

async def get_tenant_session(tenant_schema: str) -> AsyncSession:
    """
    Crea una sesión de BD apuntando al schema del tenant.
    Equivalente a tenancy()->initialize() de Stancl.
    En Laravel usabas BDs separadas — aquí usamos schemas de PostgreSQL,
    que logran el mismo aislamiento pero en una sola BD.
    """
    async with AsyncSessionLocal() as session:
        # Cambia el search_path al schema del tenant
        # Equivalente a SET app.current_tenant en Laravel con RLS
        await session.execute(
            text(f"SET search_path TO {tenant_schema}, public")
        )
        yield session


# ─── Dependency principal — get_current_tenant ────────────────────────────────

async def get_current_tenant(
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Dependency central de FastAPI.
    Uso: tenant = Depends(get_current_tenant)

    Retorna el tenant activo con sus módulos cacheados en Redis.
    Equivalente al middleware EnsureUserBelongsToCurrentTenant de Laravel.
    """
    domain = get_tenant_domain(request)

    if is_central_domain(domain):
        return None  # rutas del Admin ERP no necesitan tenant

    # 1. Buscar en caché Redis primero
    cache_key = f"tenant:{domain}"
    cached = await cache_get(cache_key)

    if cached:
        return json.loads(cached)

    # 2. Si no está en caché, buscar en BD central
    result = await db.execute(
        text("""
            SELECT
                t.id,
                t.name,
                t.domain,
                t.schema_name,
                t.is_active,
                COALESCE(
                    json_agg(tm.module_code) FILTER (WHERE tm.module_code IS NOT NULL),
                    '[]'
                ) AS active_modules
            FROM tenants t
            LEFT JOIN tenant_modules tm ON tm.tenant_id = t.id AND tm.is_active = true
            WHERE t.domain = :domain
            GROUP BY t.id
        """),
        {"domain": domain}
    )
    tenant = result.mappings().first()

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail=f"Hospital no encontrado para el dominio: {domain}"
        )

    if not tenant["is_active"]:
        raise HTTPException(
            status_code=403,
            detail="Este hospital está desactivado en el sistema"
        )

    tenant_data = dict(tenant)

    # 3. Cachear por 5 minutos en Redis
    # Se invalida cuando se activa/desactiva un módulo
    await cache_set(cache_key, json.dumps(tenant_data), expire=300)

    return tenant_data


# ─── Invalidar caché de un tenant ─────────────────────────────────────────────

async def invalidate_tenant_cache(domain: str, redis: Redis) -> None:
    """
    Invalida el caché del tenant en Redis.
    Se llama desde el Admin ERP al activar/desactivar módulos.
    Equivalente a lo que hacías manualmente con Cache::forget() en Laravel.
    """
    await redis.delete(f"tenant:{domain}")