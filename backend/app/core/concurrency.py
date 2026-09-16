# backend/app/core/concurrency.py
"""Concurrencia acotada para consultas que se disparan en paralelo, una por
hospital (reportes, listado agregado de usuarios). Antes usaban
asyncio.gather directo: con pocos hospitales no se nota, pero con cientos
dispara esa misma cantidad de conexiones simultaneas al motor de Postgres de
cada base fisica de golpe -- saturando el pool de conexiones del servidor."""
import asyncio
from typing import Awaitable, Sequence, TypeVar

T = TypeVar("T")

LIMITE_POR_DEFECTO = 10


async def gather_limitado(coros: Sequence[Awaitable[T]], limite: int = LIMITE_POR_DEFECTO) -> list[T]:
    semaforo = asyncio.Semaphore(limite)

    async def _con_limite(coro: Awaitable[T]) -> T:
        async with semaforo:
            return await coro

    return await asyncio.gather(*(_con_limite(c) for c in coros))
