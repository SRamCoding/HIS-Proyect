from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.admin.roles.models import SystemRole


async def get_all_system_roles(db: AsyncSession) -> list[SystemRole]:
    result = await db.execute(
        select(SystemRole).order_by(SystemRole.panel, SystemRole.sort_order)
    )
    return result.scalars().all()


async def create_system_role(db: AsyncSession, data) -> SystemRole:
    from fastapi import HTTPException
    from sqlalchemy import func
    if await db.scalar(select(SystemRole.id).where(func.lower(func.trim(SystemRole.name)) == data.name)):
        raise HTTPException(409, 'Ya existe un rol con ese código')
    role = SystemRole(
        name=data.name,
        label=data.label,
        panel=data.panel,
        required_module=data.required_module,
        allowed_modules=data.allowed_modules,
        sort_order=data.sort_order,
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role
