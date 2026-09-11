import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.sigarh.config_financiera.models import Seguro, PlanSeguro, Caja, Tarifario


# ─── Helper ───────────────────────────────────────────────────────────────────

async def _obtener(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(modelo).where(modelo.id == id, modelo.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


# ─── Seguros ──────────────────────────────────────────────────────────────────

async def listar_seguros(db: AsyncSession, tenant_id: uuid.UUID) -> list[Seguro]:
    result = await db.execute(
        select(Seguro)
        .options(selectinload(Seguro.planes))
        .where(Seguro.tenant_id == tenant_id)
        .order_by(Seguro.nombre)
    )
    return result.scalars().all()


async def obtener_seguro(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Seguro | None:
    result = await db.execute(
        select(Seguro)
        .options(selectinload(Seguro.planes))
        .where(Seguro.id == id, Seguro.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def crear_seguro(db: AsyncSession, tenant_id: uuid.UUID, data) -> Seguro:
    planes_data = data.planes
    seguro_dict = data.model_dump(exclude={"planes"})
    seguro = Seguro(tenant_id=tenant_id, **seguro_dict)
    db.add(seguro)
    await db.flush()

    for plan_data in planes_data:
        plan = PlanSeguro(seguro_id=seguro.id, **plan_data.model_dump())
        db.add(plan)

    await db.commit()
    await db.refresh(seguro)
    return seguro


async def actualizar_seguro(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Seguro | None:
    seguro = await obtener_seguro(db, id, tenant_id)
    if not seguro:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(seguro, field, value)
    await db.commit()
    await db.refresh(seguro)
    return seguro


async def eliminar_seguro(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    seguro = await obtener_seguro(db, id, tenant_id)
    if not seguro:
        return False
    await db.delete(seguro)
    await db.commit()
    return True


# ─── Planes de Seguro ─────────────────────────────────────────────────────────

async def agregar_plan(db: AsyncSession, tenant_id: uuid.UUID, seguro_id: uuid.UUID, data) -> PlanSeguro | None:
    """None si el seguro no existe o no pertenece a este hospital.

    PlanSeguro no tiene tenant_id propio: su aislamiento depende por completo
    de que seguro_id sí sea del hospital que hace la solicitud.
    """
    seguro = await obtener_seguro(db, seguro_id, tenant_id)
    if not seguro:
        return None
    plan = PlanSeguro(seguro_id=seguro_id, **data.model_dump())
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


async def eliminar_plan(db: AsyncSession, tenant_id: uuid.UUID, seguro_id: uuid.UUID, plan_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(PlanSeguro)
        .join(Seguro, Seguro.id == PlanSeguro.seguro_id)
        .where(PlanSeguro.id == plan_id, PlanSeguro.seguro_id == seguro_id, Seguro.tenant_id == tenant_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        return False
    await db.delete(plan)
    await db.commit()
    return True


# ─── Cajas ────────────────────────────────────────────────────────────────────

async def listar_cajas(db: AsyncSession, tenant_id: uuid.UUID) -> list[Caja]:
    result = await db.execute(
        select(Caja)
        .where(Caja.tenant_id == tenant_id)
        .order_by(Caja.nombre)
    )
    return result.scalars().all()


async def obtener_caja(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Caja | None:
    return await _obtener(db, Caja, id, tenant_id)


async def crear_caja(db: AsyncSession, tenant_id: uuid.UUID, data) -> Caja:
    item = Caja(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_caja(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Caja | None:
    item = await obtener_caja(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_caja(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener_caja(db, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True


# ─── Tarifario ────────────────────────────────────────────────────────────────

async def listar_tarifario(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    tipo_servicio: str | None = None,
    seguro_id: uuid.UUID | None = None,
    especialidad_id: uuid.UUID | None = None,
) -> list[Tarifario]:
    query = select(Tarifario).where(Tarifario.tenant_id == tenant_id)
    if tipo_servicio:
        query = query.where(Tarifario.tipo_servicio == tipo_servicio)
    if seguro_id:
        query = query.where(Tarifario.seguro_id == seguro_id)
    if especialidad_id:
        query = query.where(Tarifario.especialidad_id == especialidad_id)
    query = query.order_by(Tarifario.descripcion_servicio)
    result = await db.execute(query)
    return result.scalars().all()


async def obtener_tarifa(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Tarifario | None:
    return await _obtener(db, Tarifario, id, tenant_id)


async def crear_tarifa(db: AsyncSession, tenant_id: uuid.UUID, data) -> Tarifario:
    item = Tarifario(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_tarifa(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Tarifario | None:
    item = await obtener_tarifa(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_tarifa(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener_tarifa(db, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True