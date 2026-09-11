import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.admin.niveles_hospitalarios.models import HospitalLevel
from app.admin.auditoria.service import create_audit_log


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
    )
    db.add(level)
    await db.commit()
    await db.refresh(level)
    await create_audit_log(
        db, user_id=actor.get("sub"), user_name=actor.get("name") or actor.get("email"),
        tenant_id=None, tenant_name=None, action="hospital_level_created",
        model="HospitalLevel", model_id=str(level.id),
        description=f"Nivel hospitalario creado: {level.code} — {level.name}",
        new_values=data.model_dump(),
    )
    return level


async def update_hospital_level(db: AsyncSession, nivel_id: uuid.UUID, data, actor: dict) -> HospitalLevel | None:
    nivel = await get_hospital_level_by_id(db, nivel_id)
    if not nivel:
        return None
    cambios = data.model_dump(exclude_unset=True)
    anteriores = {campo: getattr(nivel, campo) for campo in cambios}
    for field, value in cambios.items():
        setattr(nivel, field, value)
    await db.commit()
    await create_audit_log(
        db, user_id=actor.get("sub"), user_name=actor.get("name") or actor.get("email"),
        tenant_id=None, tenant_name=None, action="hospital_level_updated",
        model="HospitalLevel", model_id=str(nivel.id),
        description=f"Nivel hospitalario actualizado: {nivel.code}",
        old_values=anteriores, new_values=cambios,
    )
    return nivel
