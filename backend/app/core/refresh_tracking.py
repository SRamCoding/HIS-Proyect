"""Rotacion de refresh tokens con deteccion de reuso, en memoria del proceso.

Mismo criterio y misma limitacion que app/core/rate_limit.py: alcanza para
un solo proceso backend (ver HANDOFF.md); si en el futuro hay mas de una
instancia detras de un balanceador, esto necesita moverse a Redis. Se
documenta aca en vez de repetirlo. Tambien hereda la misma limitacion de
"sin historial persistente": si el proceso se reinicia, un refresh token
todavia vigente (firmado y no expirado) de una sesion que ya se habia
rotado ANTES del reinicio vuelve a aceptarse, porque no hay memoria previa
de esa sesion. Ampliar esto requeriria un almacen persistente (Redis/BD),
que es un cambio de infraestructura aparte, no un ajuste de este archivo.

Se trackea por `sid` (session id, un uuid generado UNA vez en el login
original y que viaja igual en cada token de esa cadena de renovaciones -- ver
_emitir_tokens en auth/router.py), NO por user_id: antes, con un solo jti
vigente por CUENTA, loguearse en un segundo dispositivo/navegador (sesion B)
pisaba el registro de la sesion A, y el siguiente refresh legitimo de A se
trataba como reuso -- revocando TODAS las sesiones del usuario por el simple
hecho de tener dos sesiones simultaneas validas. Con un jti vigente POR sid,
cada sesion tiene su propia cadena de rotacion independiente.
"""
from collections import defaultdict

# sid (str) -> jti del refresh token vigente para ESA sesion. Si un sid no
# aparece aca, es porque el proceso se reinicio o es su primer refresh: se
# acepta el jti presentado y se empieza a trackear desde ahi, en vez de
# invalidar sesiones legitimas solo porque el proceso se reinicio.
_jti_vigente: dict[str, str] = {}


def emitir_jti(sid: str, jti: str) -> None:
    """Registra `jti` como el refresh token vigente para `sid` (login o
    rotacion exitosa). Idempotente frente a reservar_rotacion: si ya se
    reservo este mismo valor, esto solo lo reafirma."""
    _jti_vigente[sid] = jti


def reservar_rotacion(sid: str, jti_presentado: str | None, jti_nuevo: str) -> bool:
    """Chequea Y reserva en una sola operacion sincrona (sin ningun `await`
    de por medio, ver el llamador en auth/router.py) -- si se separara en
    "verificar" y luego "registrar" mas adelante (despues de consultas a la
    BD), dos renovaciones concurrentes con el MISMO refresh token viejo
    podrian pasar el chequeo ambas antes de que cualquiera registrara nada,
    y la que registra al final "pisa" silenciosamente a la otra sin que
    nadie detecte el reuso. Con esto, la segunda peticion concurrente
    encuentra el jti ya cambiado por la primera y se rechaza de inmediato.

    True si `jti_presentado` es el vigente (o no habia ninguno trackeado
    todavia) -- en ese caso queda reservado `jti_nuevo` como vigente ya
    mismo. False si se presento un jti DISTINTO al vigente -- reuso
    detectado, no se modifica nada."""
    vigente = _jti_vigente.get(sid)
    if vigente is not None and jti_presentado != vigente:
        return False
    _jti_vigente[sid] = jti_nuevo
    return True


def olvidar(sid: str) -> None:
    """Deja de trackear esa sesion (logout, cambio de contraseña o
    cualquier otro punto que ya revoque por su cuenta vía session_version)."""
    _jti_vigente.pop(sid, None)
