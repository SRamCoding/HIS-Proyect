"""Cifrado simetrico para datos sensibles en reposo (hoy: mfa_secret).

No se agrega una variable de entorno nueva -- la clave de Fernet se deriva
de settings.SECRET_KEY via PBKDF2 con un "info" propio ("mfa_secret"), asi
que un secreto TOTP cifrado con esta clave NUNCA es reutilizable para nada
firmado con SECRET_KEY directamente (dominios separados), pero tampoco hace
falta rotar/gestionar una clave adicional en el despliegue. Si SECRET_KEY
rota, los secretos ya cifrados dejan de poder descifrarse -- mismo trade-off
que ya existe hoy con session_version/JWT al rotar SECRET_KEY.
"""
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from app.core.config import settings

_SALT = b"erp-hospitalario-mfa-secret-v1"


def _clave_fernet() -> bytes:
    derivada = hashlib.pbkdf2_hmac("sha256", settings.SECRET_KEY.encode(), _SALT, 200_000, dklen=32)
    return base64.urlsafe_b64encode(derivada)


def cifrar(texto_plano: str) -> str:
    return Fernet(_clave_fernet()).encrypt(texto_plano.encode()).decode()


def descifrar(texto_cifrado: str) -> str:
    try:
        return Fernet(_clave_fernet()).decrypt(texto_cifrado.encode()).decode()
    except InvalidToken:
        raise ValueError("No se pudo descifrar el valor: clave incorrecta o dato corrupto")
