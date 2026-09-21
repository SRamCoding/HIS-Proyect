"""TOTP (RFC 6238) para MFA de administradores. Sin backup codes todavia:
si un admin pierde el dispositivo con la app de autenticacion, la unica
salida hoy es que otro admin le resetee mfa_secret/mfa_enabled a mano en la
BD -- no hay flujo de recuperacion propio en el producto. Documentado como
limitacion conocida, no un olvido.
"""
import pyotp
import qrcode
import qrcode.image.svg
import io
import base64
import time

EMISOR = "ERP Hospitalario"

# user_id -> (codigo, timestamp de aceptacion). Un codigo TOTP es valido
# ~90s (valid_window=1 = paso actual +/- uno de 30s): sin esto, el MISMO
# codigo interceptado (red, hombro, log) podia reenviarse y aceptarse de
# nuevo mientras siguiera en su ventana de validez -- MFA "de un solo uso"
# de nombre, no de hecho. Mismo criterio en memoria que rate_limit.py /
# refresh_tracking.py: alcanza para un solo proceso backend.
_ULTIMO_CODIGO_ACEPTADO: dict[str, tuple[str, float]] = {}
_VENTANA_REPLAY_SEGUNDOS = 90


def generar_secreto() -> str:
    return pyotp.random_base32()


def uri_otpauth(secreto: str, email: str) -> str:
    return pyotp.totp.TOTP(secreto).provisioning_uri(name=email, issuer_name=EMISOR)


def qr_png_base64(uri: str) -> str:
    img = qrcode.make(uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def verificar_codigo(user_key: str, secreto: str, codigo: str) -> bool:
    if not secreto or not codigo:
        return False
    ahora = time.time()
    anterior = _ULTIMO_CODIGO_ACEPTADO.get(user_key)
    if anterior and anterior[0] == codigo and ahora - anterior[1] < _VENTANA_REPLAY_SEGUNDOS:
        return False
    # valid_window=1: tolera el codigo del intervalo anterior/siguiente (30s
    # cada uno) para no fallar por un pequeño desfase de reloj entre el
    # celular y el servidor -- un problema real y comun con TOTP.
    if not pyotp.totp.TOTP(secreto).verify(codigo, valid_window=1):
        return False
    _ULTIMO_CODIGO_ACEPTADO[user_key] = (codigo, ahora)
    return True
