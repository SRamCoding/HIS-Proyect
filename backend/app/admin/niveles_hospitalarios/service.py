import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.admin.niveles_hospitalarios.models import HospitalLevel


async def get_all_hospital_levels(db: AsyncSession) -> list[HospitalLevel]:
    result = await db.execute(
        select(HospitalLevel).order_by(HospitalLevel.sort_order)
    )
    return result.scalars().all()


async def get_hospital_level_by_code(db: AsyncSession, code: str) -> HospitalLevel | None:
    result = await db.execute(
        select(HospitalLevel).where(HospitalLevel.code == code)
    )
    return result.scalar_one_or_none()


async def get_hospital_level_by_id(db: AsyncSession, nivel_id: uuid.UUID) -> HospitalLevel | None:
    result = await db.execute(select(HospitalLevel).where(HospitalLevel.id == nivel_id))
    return result.scalar_one_or_none()


async def create_hospital_level(db: AsyncSession, data) -> HospitalLevel:
    level = HospitalLevel(
        code=data.code,
        name=data.name,
        description=data.description,
        default_modules=data.default_modules,
        default_roles=data.default_roles,
        sort_order=data.sort_order,
    )
    db.add(level)
    await db.commit()
    await db.refresh(level)
    return level


async def update_hospital_level(db: AsyncSession, nivel_id: uuid.UUID, data: dict) -> HospitalLevel | None:
    nivel = await get_hospital_level_by_id(db, nivel_id)
    if not nivel:
        return None
    for field, value in data.items():
        if hasattr(nivel, field):
            setattr(nivel, field, value)
    await db.commit()
    return nivel
