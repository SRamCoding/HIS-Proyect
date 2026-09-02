from fastapi import Depends, HTTPException, status
from redis.asyncio import Redis

from app.core.tenancy import get_current_tenant
from app.core.redis import get_redis, cache_set, cache_get
import json


def require_module(module_code: str):
    """
    Dependency factory — verifica que el tenant tenga el módulo activo.
    Equivalente exacto al HasModuleGate + shouldRegisterNavigation() de Laravel.

    Uso en cualquier router:
        @router.get("/stock", dependencies=[Depends(require_module("farmacia"))])
        async def get_stock():
            ...

    O con acceso al tenant:
        @router.get("/stock")
        async def get_stock(tenant=Depends(require_module("farmacia"))):
            ...
    """
    async def dependency(
        tenant: dict = Depends(get_current_tenant),
        redis: Redis = Depends(get_redis),
    ) -> dict:
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Este endpoint requiere un tenant activo"
            )

        active_modules = tenant.get("active_modules", [])

        # active_modules puede venir como string JSON desde Redis
        if isinstance(active_modules, str):
            active_modules = json.loads(active_modules)

        if module_code not in active_modules:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"El módulo '{module_code}' no está activo para este hospital"
            )

        return tenant

    return dependency


def require_any_module(*module_codes: str):
    """
    Verifica que el tenant tenga AL MENOS UNO de los módulos indicados.
    Útil para endpoints compartidos entre módulos (ej: búsqueda de pacientes).
    """
    async def dependency(
        tenant: dict = Depends(get_current_tenant),
    ) -> dict:
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Este endpoint requiere un tenant activo"
            )

        active_modules = tenant.get("active_modules", [])
        if isinstance(active_modules, str):
            active_modules = json.loads(active_modules)

        if not any(code in active_modules for code in module_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere al menos uno de estos módulos: {', '.join(module_codes)}"
            )

        return tenant

    return dependency


def require_all_modules(*module_codes: str):
    """
    Verifica que el tenant tenga TODOS los módulos indicados.
    Útil para endpoints que dependen de varios módulos simultáneamente.
    """
    async def dependency(
        tenant: dict = Depends(get_current_tenant),
    ) -> dict:
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Este endpoint requiere un tenant activo"
            )

        active_modules = tenant.get("active_modules", [])
        if isinstance(active_modules, str):
            active_modules = json.loads(active_modules)

        missing = [code for code in module_codes if code not in active_modules]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Módulos requeridos no activos: {', '.join(missing)}"
            )

        return tenant

    return dependency