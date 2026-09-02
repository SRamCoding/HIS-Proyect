from redis.asyncio import from_url, Redis
from app.core.config import settings


# Conexión Redis — para cachear entitlements, sesiones y turnero
redis_client: Redis = from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis() -> Redis:
    """
    Dependency de FastAPI.
    Uso: redis: Redis = Depends(get_redis)
    """
    return redis_client


async def cache_set(key: str, value: str, expire: int = 300) -> None:
    """Guarda un valor en caché. expire en segundos (default 5 min)."""
    await redis_client.set(key, value, ex=expire)


async def cache_get(key: str) -> str | None:
    """Obtiene un valor de caché. Retorna None si no existe."""
    return await redis_client.get(key)


async def cache_delete(key: str) -> None:
    """Invalida una clave — se usa al activar/desactivar módulos de un tenant."""
    await redis_client.delete(key)