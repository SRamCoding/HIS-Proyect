import uuid
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.core.config import settings


def create_access_token(data: dict) -> str:
    """
    Genera el JWT de acceso.
    El payload incluye: user_id, tenant_id, role, panel, active_modules
    Equivalente a Auth::login() de Laravel pero con claims custom.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict, jti: str | None = None) -> str:
    """Token de refresco de larga duración.

    `jti` es un id unico por token, nuevo en CADA llamada (incluso si
    `data` trae uno heredado del token anterior -- se pisa siempre) para
    que app/core/refresh_tracking pueda distinguir "el ultimo refresh token
    emitido" de cualquier copia previa ya rotada. Se puede pasar un `jti`
    explicito (en vez de generarlo aca) cuando el llamador ya reservo ese
    valor de forma atomica ANTES de este punto -- ver refresh_token() en
    auth/router.py, donde la reserva tiene que pasar antes de cualquier
    `await` para cerrar una condicion de carrera real entre dos renovaciones
    concurrentes con el mismo token viejo.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload.update({"exp": expire, "type": "refresh", "jti": jti or str(uuid.uuid4())})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_mfa_pending_token(sub: str, purpose: str) -> str:
    """Token corto que prueba "ya pasaste la contraseña, falta el codigo
    TOTP" -- separado de access/refresh a proposito: nunca debe servir para
    acceder a ningun endpoint protegido por get_current_user, solo para
    /auth/mfa/verify. `purpose` es "setup" (primera vez, todavia sin
    confirmar un codigo) o "verify" (login normal con MFA ya activo).

    Duracion distinta por proposito: "setup" exige instalar una app de
    autenticacion (si el usuario no la tiene) y escanear el QR antes de
    poder generar el primer codigo -- 5 min resultaba insuficiente para
    eso y dejaba al usuario sin poder entrar ("token vencido") en su
    primer login con MFA. "verify" (ya tiene la app lista, solo lee y
    escribe el codigo) se mantiene corto por seguridad: limita la ventana
    util de una contraseña robada.
    """
    minutos = 15 if purpose == "setup" else 5
    payload = {"sub": sub, "type": "mfa_pending", "purpose": purpose}
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=minutos)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> dict | None:
    """
    Verifica y decodifica un JWT.
    Retorna el payload o None si es inválido/expirado.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None