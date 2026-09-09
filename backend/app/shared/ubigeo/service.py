"""Consultas de solo lectura sobre el catálogo nacional de ubigeo.

Compartido por cualquier módulo que necesite selects en cascada
(departamento -> provincia -> distrito).
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.ubigeo.models import UbigeoDepartamento, UbigeoProvincia, UbigeoDistrito


async def get_departamentos(db: AsyncSession) -> list[UbigeoDepartamento]:
    result = await db.execute(select(UbigeoDepartamento).order_by(UbigeoDepartamento.nombre))
    return result.scalars().all()


async def get_provincias(db: AsyncSession, departamento_id: str) -> list[UbigeoProvincia]:
    result = await db.execute(
        select(UbigeoProvincia)
        .where(UbigeoProvincia.departamento_id == departamento_id)
        .order_by(UbigeoProvincia.nombre)
    )
    return result.scalars().all()


async def get_distritos(db: AsyncSession, provincia_id: str) -> list[UbigeoDistrito]:
    result = await db.execute(
        select(UbigeoDistrito)
        .where(UbigeoDistrito.provincia_id == provincia_id)
        .order_by(UbigeoDistrito.nombre)
    )
    return result.scalars().all()
