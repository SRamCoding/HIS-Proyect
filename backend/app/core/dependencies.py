import time
from fastapi import Depends, HTTPException, status, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.config import settings
from app.core.database import get_db_central
from app.core.redis import get_redis
from app.core.security import verify_token

# auto_error=False: si no viene Authorization, no debe cortar aca con un
# 403 generico -- todavia hay que revisar la cookie httpOnly del panel
# correspondiente antes de decidir que no hay sesion. Se acepta cualquiera
# de los dos, no solo uno, porque quitar el header de un dia para el otro
# rompe cualquier cliente que todavia lo use (scripts, tests, un frontend
# no actualizado).
bearer_scheme = HTTPBearer(auto_error=False)

_PREFIJO_A_PANEL = {"/admin": "admin", "/app": "app", "/sigarh": "sigarh"}


def _panel_de_la_ruta(path: str) -> str | None:
    for prefijo, panel in _PREFIJO_A_PANEL.items():
        if path.startswith(prefijo):
            return panel
    return None


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db_central),
    redis: Redis = Depends(get_redis),
    # Las cookies de sesion estan nombradas por panel (access_token_admin,
    # access_token_app, ...) para que un mismo navegador pueda tener varias
    # sesiones simultaneas en pestañas distintas sin que una pise a la
    # otra (ver PANELES_CON_COOKIE en auth/router.py). Para rutas bajo
    # /admin, /app o /sigarh el panel se infiere de la propia URL; para
    # rutas panel-agnosticas (como /auth/logout) el frontend lo manda
    # explicito por query, porque no hay otra forma de saberlo antes de
    # decodificar un token que todavia no se sabe cual cookie contiene.
    panel_hint: str | None = Query(None, alias="panel"),
) -> dict:
    """
    Dependency que verifica el JWT y retorna el usuario actual.
    Equivalente al middleware Authenticate de Laravel.
    """
    if credentials:
        token = credentials.credentials
    else:
        # Orden: query explicito > header X-Panel (el frontend lo manda en
        # toda peticion, ver useApi.ts) > inferido de la URL -- los dos
        # primeros no dependen de que la ruta caiga bajo /admin, /app o
        # /sigarh, asi que cubren cualquier endpoint panel-agnostico sin
        # tener que enumerarlo aca.
        panel = panel_hint or request.headers.get("x-panel") or _panel_de_la_ruta(request.url.path)
        token = request.cookies.get(f"access_token_{panel}") if panel else None
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # El limite absoluto de sesion (session_started_at) antes solo se
    # comprobaba en /auth/refresh -- un access token emitido momentos antes
    # de cumplirse el limite seguia funcionando en CUALQUIER peticion
    # protegida hasta su propia expiracion (hasta 1h mas), sin importar que
    # la sesion ya deberia haber terminado. Se repite el mismo chequeo aca,
    # en el camino que de verdad usa el token en cada peticion.
    inicio = payload.get("session_started_at")
    if inicio and time.time() - inicio > settings.SESSION_MAX_DURATION_HOURS * 3600:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión alcanzó su duración máxima; vuelve a iniciar sesión",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from app.sigarh.mantenimiento.security import usuario_actual
    user = await usuario_actual(db, payload)

    from app.core.audit import set_audit_actor
    set_audit_actor(
        user_id=user.get("sub"),
        user_name=user.get("name"),
        tenant_id=user.get("tenant_id"),
    )
    return user


async def get_admin_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Solo permite acceso al panel Admin ERP.
    Equivalente al middleware EnsureAdministrativoUser de Laravel.

    Antes solo se comprobaba el panel: cualquier cuenta panel="admin",
    sin importar su rol, pasaba este control. Como además nada impedía que
    una cuenta admin creara otra cuenta admin, eso permitía escalar
    privilegios sin límite. Ahora también se exige el rol real de
    administrador.
    """
    if current_user.get("panel") != "admin" or current_user.get("role") != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido al panel de administración"
        )
    return current_user


async def get_admin_user_escritura(
    current_user: dict = Depends(get_admin_user),
) -> dict:
    """Primer corte de permisos administrativos por funcion: lectura vs
    escritura. Antes CUALQUIER cuenta panel="admin" podia hacer cualquier
    operacion (crear/editar/desactivar/eliminar hospitales, usuarios,
    modulos, niveles...) -- no existia forma de dar acceso de solo
    consulta (ej. un Auditor) sin dar tambien acceso total. Se revalida
    en cada request (usuario_actual() relee `admin_solo_lectura` de la
    BD), no solo al login -- si se le quita el flag a una cuenta, el
    cambio aplica de inmediato sin esperar a que expire su token, igual
    que ya pasa con `is_active`/`role`/`session_version`.

    Deliberadamente NO es todavia el sistema de 4 roles funcionales
    completo (Auditor/Operador/Responsable de usuarios/Administrador
    principal) que se discutio -- ese exige un modelo de roles y
    permisos propio. Este es el primer corte, mas grueso pero de mucho
    menor riesgo: separa "puede ver todo" de "puede cambiar algo"."""
    if current_user.get("admin_solo_lectura"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta tiene acceso de solo lectura -- no puedes realizar esta acción",
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
