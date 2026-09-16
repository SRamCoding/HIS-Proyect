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
    # code es unique a nivel de columna; sin este chequeo, un duplicado
    # revienta como IntegrityError sin controlar (500) en vez de un 409
    # legible -- mismo criterio que ya se usa para el dominio de un hospital
    # al crearlo.
    if await db.scalar(select(HospitalLevel.id).where(HospitalLevel.code == data.code)):
        raise HTTPException(409, f"Ya existe un nivel con el código '{data.code}'")
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
    if "code" in cambios and cambios["code"] != nivel.code:
        # Tenant.hospital_level guarda el CODIGO como texto libre, no una
        # FK -- cambiar el codigo de un nivel en uso deja a esos hospitales
        # apuntando a un codigo que ya no existe en ningun lado (huerfanos),
        # sin ningun error visible hasta que algo intente resolverlo. Se
        # bloquea igual que ya se bloquea el borrado de un nivel en uso, en
        # vez de migrar las referencias: reescribir Tenant.hospital_level en
        # cada hospital que lo usa es una operacion de mas riesgo (toca N
        # filas, posiblemente inconsistente si falla a mitad de camino) que
        # no se justifica frente a simplemente pedir crear un nivel nuevo.
        from app.tenants.hospitales.models import Tenant
        en_uso = await db.scalar(
            select(func.count()).select_from(Tenant).where(Tenant.hospital_level == nivel.code)
        )
        if en_uso:
            raise HTTPException(
                409,
                f"No se puede cambiar el código: {en_uso} hospital(es) usan el código '{nivel.code}'. "
                "Crea un nivel nuevo en su lugar.",
            )
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
