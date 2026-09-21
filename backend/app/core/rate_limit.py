"""Limitador de intentos de login en memoria del proceso.

No usa Redis ni almacenamiento compartido: alcanza para el despliegue actual
(un solo proceso Nitro/uvicorn por servicio, ver HANDOFF.md) pero NO protege
si en el futuro se corre mas de una instancia del backend detras de un
balanceador -- ahi cada instancia tendria su propio contador. Moverlo a
Redis con TTL es la solucion correcta para ese caso, no parchear esto.

Se limita por tres combinaciones distintas, no solo IP+correo:
- IP+correo (la mas estricta): frena el reintento directo contra UNA cuenta
  desde UNA IP.
- Solo correo (cualquier IP): sin esto, un atacante rotando de IP podia
  seguir probando contraseñas contra una cuenta puntual sin nunca tocar el
  limite de IP+correo.
- Solo IP (cualquier correo): sin esto, una sola IP podia probar credenciales
  contra muchas cuentas distintas (credential spraying) sin tocar ningun
  limite, porque cada combinacion IP+correo empieza su propio contador en
  cero.
"""
import time
from collections import defaultdict
from fastapi import HTTPException, status

_VENTANA_SEGUNDOS = 15 * 60
_MAX_POR_IP_Y_CORREO = 5
_MAX_POR_CORREO = 10
_MAX_POR_IP = 20

_intentos_ip_correo: dict[str, list[float]] = defaultdict(list)
_intentos_correo: dict[str, list[float]] = defaultdict(list)
_intentos_ip: dict[str, list[float]] = defaultdict(list)


def _normalizar_email(email: str) -> str:
    return email.strip().lower()


def _vigentes(almacen: dict[str, list[float]], clave: str, ahora: float) -> list[float]:
    """Filtra los intentos vencidos y, si la clave queda vacia, la elimina
    del diccionario -- sin esto, cada correo/IP distinto que alguna vez
    probo login queda como clave residual para siempre, aunque ya no tenga
    intentos vigentes."""
    vigentes = [t for t in almacen[clave] if ahora - t < _VENTANA_SEGUNDOS]
    if vigentes:
        almacen[clave] = vigentes
    else:
        almacen.pop(clave, None)
    return vigentes


def verificar_limite_login(ip: str | None, email: str) -> None:
    email = _normalizar_email(email)
    ip = ip or "-"
    ahora = time.monotonic()

    if len(_vigentes(_intentos_ip_correo, f"{ip}|{email}", ahora)) >= _MAX_POR_IP_Y_CORREO:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Demasiados intentos fallidos. Espera unos minutos antes de volver a intentar.",
        )
    if len(_vigentes(_intentos_correo, email, ahora)) >= _MAX_POR_CORREO:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Demasiados intentos fallidos contra esta cuenta. Espera unos minutos.",
        )
    if len(_vigentes(_intentos_ip, ip, ahora)) >= _MAX_POR_IP:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Demasiados intentos fallidos desde esta red. Espera unos minutos.",
        )


def registrar_intento_fallido(ip: str | None, email: str) -> None:
    email = _normalizar_email(email)
    ip = ip or "-"
    ahora = time.monotonic()
    _intentos_ip_correo[f"{ip}|{email}"].append(ahora)
    _intentos_correo[email].append(ahora)
    _intentos_ip[ip].append(ahora)


def limpiar_intentos(ip: str | None, email: str) -> None:
    # Solo se limpia el contador IP+correo (el mas especifico a ESTE login
    # exitoso). Los contadores solo-correo y solo-IP NO se tocan: existen
    # justamente para detectar patrones a traves de otras IPs/cuentas, y un
    # login exitoso puntual no es evidencia de que esos otros intentos
    # (desde otra IP contra esta cuenta, o desde esta IP contra otra cuenta)
    # no sigan siendo un ataque en curso.
    email = _normalizar_email(email)
    ip = ip or "-"
    _intentos_ip_correo.pop(f"{ip}|{email}", None)
