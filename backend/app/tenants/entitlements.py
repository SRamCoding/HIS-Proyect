# backend/app/tenants/entitlements.py
from fastapi import Depends, HTTPException, status, Request
from redis.asyncio import Redis

from app.core.tenancy import get_current_tenant
from app.core.redis import get_redis, cache_set, cache_get
from app.core.dependencies import get_current_user
import json


def require_module(module_code: str):
    """
    Dependency factory — verifica que el tenant tenga el módulo activo.
    Usa el dominio del request para identificar el tenant.
    Para panel Admin y rutas por subdominio.
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
        if isinstance(active_modules, str):
            active_modules = json.loads(active_modules)

        if module_code not in active_modules:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"El módulo '{module_code}' no está activo para este hospital"
            )

        return tenant

    return dependency


def require_module_jwt(module_code: str):
    """
    Versión de require_module para paneles SIGARH y hospitalario.
    Lee el tenant_id del JWT en vez del dominio del request.
    """
    async def dependency(
        request: Request,
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import text
        from app.tenants.modulos.submodulos import permiso_incluye, modulo_padre

        if current_user.get("panel") == "app":
            from app.auth.hospital_access import permiso_recurso, verificar_ambito_medico
            requerido = permiso_recurso(request.url.path, request.method, module_code)
            if not permiso_incluye(current_user.get("active_modules", []), requerido):
                raise HTTPException(403, detail="Su perfil hospitalario no permite esta operación")
            await verificar_ambito_medico(request, current_user)

        if current_user.get("panel") == "sigarh" and not permiso_incluye(
            current_user.get("active_modules", []), module_code
        ):
            raise HTTPException(403, detail="Su perfil no permite este módulo")

        # Obtener tenant_id del JWT o del header X-Tenant-ID
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sin tenant asignado"
            )

        # tenant_modules solo guarda módulos completos (un hospital contrata el
        # módulo, no cada submódulo por separado): hay que resolver contra el
        # código del módulo padre aunque module_code venga con submódulo.
        modulo_contratado = modulo_padre(module_code)

        # Verificar que el módulo está activo para ese tenant
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                text("""
                    SELECT tm.module_code
                    FROM tenant_modules tm
                    JOIN tenants t ON t.id = tm.tenant_id
                    WHERE t.id = :tenant_id
                    AND tm.module_code = :module_code
                    AND tm.is_active = true
                    AND t.is_active = true
                """),
                {"tenant_id": tenant_id, "module_code": modulo_contratado}
            )
            if not result.first():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"El módulo '{module_code}' no está activo para este hospital"
                )

        return current_user

    return dependency


def require_any_module_jwt(*module_codes: str):
    """Autoriza una operación compartida entre módulos del panel hospitalario.

    El hospital debe proceder del JWT, nunca de un header elegido por el cliente.
    Reutiliza la comprobación de hospital y módulo activos de require_module_jwt.
    """
    checks = [require_module_jwt(code) for code in module_codes]

    async def dependency(
        request: Request,
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        import uuid

        if current_user.get("panel") != "app":
            raise HTTPException(403, detail="Acceso restringido al panel hospitalario")
        try:
            uuid.UUID(str(current_user.get("tenant_id")))
        except (ValueError, TypeError, AttributeError):
            raise HTTPException(403, detail="Sin hospital válido asignado")
        for check in checks:
            try:
                return await check(request=request, current_user=current_user)
            except HTTPException as exc:
                if exc.status_code != 403:
                    raise
        raise HTTPException(403, detail="Ninguno de los módulos requeridos está activo")

    return dependency


def require_any_module(*module_codes: str):
    """
    Verifica que el tenant tenga AL MENOS UNO de los módulos indicados.
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
