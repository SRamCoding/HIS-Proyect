"""Consulta de DNI contra un servicio externo. Compartido por todos los módulos.

`lookup_dni_externo` nunca lanza excepción: si el servicio está apagado, sin
API key o no responde, devuelve None y el registro manual sigue funcionando.
"""
import httpx

from app.core.config import settings


async def lookup_dni_externo(dni: str) -> dict | None:
    """Devuelve {'nombres', 'apellidoPaterno', 'apellidoMaterno'} o None."""
    if not settings.DNI_API_URL or not settings.DNI_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                settings.DNI_API_URL,
                json={"dni": dni},
                headers={"X-API-Key": settings.DNI_API_KEY},
            )
        if resp.status_code != 200:
            return None
        return resp.json()
    except (httpx.TimeoutException, httpx.ConnectError):
        return None
