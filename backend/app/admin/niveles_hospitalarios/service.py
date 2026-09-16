import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

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


async def create_hospital_level(db: AsyncSession, data, actor: dict) -> HospitalLevel:
    level = HospitalLevel(
        code=data.code,
        name=data.name,
        description=data.description,
        color=data.color,
        default_modules=data.default_modules,
        default_roles=data.default_roles,
        sort_order=data.sort_order,
        is_active=data.is_active,
    )
    db.add(level)
    await db.commit()
    await db.refresh(level)
    return level


async def update_hospital_level(db: AsyncSession, nivel_id: uuid.UUID, data, actor: dict) -> HospitalLevel | None:
    nivel = await get_hospital_level_by_id(db, nivel_id)
    if not nivel:
        return None
    cambios = data.model_dump(exclude_unset=True)
    for field, value in cambios.items():
        setattr(nivel, field, value)
    await db.commit()
    return nivel


async def delete_hospital_level(db: AsyncSession, nivel_id: uuid.UUID) -> bool:
    nivel = await get_hospital_level_by_id(db, nivel_id)
    if not nivel:
        return False
    from app.tenants.hospitales.models import Tenant
    en_uso = await db.scalar(
        select(func.count()).select_from(Tenant).where(Tenant.hospital_level == nivel.code)
    )
    if en_uso:
        raise HTTPException(
            409,
            f"No se puede eliminar: {en_uso} hospital(es) usan el nivel '{nivel.code}'. Desactívalo en su lugar.",
        )
    await db.delete(nivel)
    await db.commit()
    return True
