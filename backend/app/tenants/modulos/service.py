from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.tenants.modulos.models import Module


async def get_all_modules(db: AsyncSession) -> list[Module]:
    result = await db.execute(
        select(Module).order_by(Module.category, Module.name)
    )
    return result.scalars().all()
