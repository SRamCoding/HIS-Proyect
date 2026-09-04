# backend/app/admin/modulos/service.py
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.admin.modulos.models import ModuleDependency


async def get_module_dependencies(db: AsyncSession) -> list[ModuleDependency]:
    result = await db.execute(
        select(ModuleDependency).order_by(ModuleDependency.module_code)
    )
    return result.scalars().all()


async def create_module_dependency(db: AsyncSession, data) -> ModuleDependency:
    dep = ModuleDependency(
        module_code=data.module_code,
        depends_on_code=data.depends_on_code,
        is_required=data.is_required,
    )
    db.add(dep)
    await db.commit()
    await db.refresh(dep)
    return dep


async def delete_module_dependency(db: AsyncSession, dep_id: uuid.UUID) -> bool:
    result = await db.execute(select(ModuleDependency).where(ModuleDependency.id == dep_id))
    dep = result.scalar_one_or_none()
    if not dep:
        return False
    await db.delete(dep)
    await db.commit()
    return True