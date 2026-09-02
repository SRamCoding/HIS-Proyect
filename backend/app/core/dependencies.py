from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import verify_token

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """
    Dependency que verifica el JWT y retorna el usuario actual.
    Equivalente al middleware Authenticate de Laravel.
    """
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_admin_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Solo permite acceso al panel Admin ERP.
    Equivalente al middleware EnsureAdministrativoUser de Laravel.
    """
    if current_user.get("panel") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido al panel de administración"
        )
    return current_user


async def get_hospital_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Panel hospitalario operativo."""
    if current_user.get("panel") != "app":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido al panel hospitalario"
        )
    return current_user


async def get_sigarh_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Panel SIGARH — recursos humanos."""
    if current_user.get("panel") != "sigarh":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido al panel SIGARH"
        )
    return current_user