import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.sigarh.infraestructura_hosp.models import Piso, Sala, Cama


# ─── Helper ───────────────────────────────────────────────────────────────────

async def _obtener(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(modelo).where(modelo.id == id, modelo.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


# ─── Pisos ────────────────────────────────────────────────────────────────────

async def listar_pisos(db: AsyncSession, tenant_id: uuid.UUID) -> list[Piso]:
    result = await db.execute(
        select(Piso)
        .where(Piso.tenant_id == tenant_id)
        .order_by(Piso.orden, Piso.nombre)
    )
    return result.scalars().all()


async def obtener_piso(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Piso | None:
    return await _obtener(db, Piso, id, tenant_id)


async def crear_piso(db: AsyncSession, tenant_id: uuid.UUID, data) -> Piso:
    item = Piso(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_piso(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Piso | None:
    item = await obtener_piso(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_piso(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener_piso(db, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True


# ─── Salas ────────────────────────────────────────────────────────────────────

async def listar_salas(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    piso_id: uuid.UUID | None = None,
) -> list[Sala]:
    query = select(Sala).where(Sala.tenant_id == tenant_id)
    if piso_id:
        query = query.where(Sala.piso_id == piso_id)
    query = query.order_by(Sala.nombre)
    result = await db.execute(query)
    return result.scalars().all()


async def obtener_sala(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Sala | None:
    return await _obtener(db, Sala, id, tenant_id)


async def crear_sala(db: AsyncSession, tenant_id: uuid.UUID, data) -> Sala:
    item = Sala(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_sala(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Sala | None:
    item = await obtener_sala(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_sala(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener_sala(db, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True


# ─── Camas ────────────────────────────────────────────────────────────────────

async def listar_camas(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    sala_id: uuid.UUID | None = None,
    piso_id: uuid.UUID | None = None,
    estado: str | None = None,
) -> list[Cama]:
    query = select(Cama).where(Cama.tenant_id == tenant_id)
    if sala_id:
        query = query.where(Cama.sala_id == sala_id)
    if piso_id:
        query = query.where(Cama.piso_id == piso_id)
    if estado:
        query = query.where(Cama.estado == estado)
    query = query.order_by(Cama.codigo)
    result = await db.execute(query)
    return result.scalars().all()


async def obtener_cama(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Cama | None:
    return await _obtener(db, Cama, id, tenant_id)


async def crear_cama(db: AsyncSession, tenant_id: uuid.UUID, data) -> Cama:
    item = Cama(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_cama(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Cama | None:
    item = await obtener_cama(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_cama(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener_cama(db, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True