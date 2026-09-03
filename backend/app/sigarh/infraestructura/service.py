import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.sigarh.infraestructura.models import Catalogo, Consultorio


# ─── Catálogo ─────────────────────────────────────────────────────────────────

async def listar_catalogos(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    categoria: str | None = None,
) -> list[Catalogo]:
    query = select(Catalogo).where(Catalogo.tenant_id == tenant_id)
    if categoria:
        query = query.where(Catalogo.categoria == categoria)
    query = query.order_by(Catalogo.categoria, Catalogo.orden, Catalogo.nombre)
    result = await db.execute(query)
    return result.scalars().all()


async def obtener_catalogo(
    db: AsyncSession,
    id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> Catalogo | None:
    result = await db.execute(
        select(Catalogo).where(Catalogo.id == id, Catalogo.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def crear_catalogo(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    data,
) -> Catalogo:
    item = Catalogo(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_catalogo(
    db: AsyncSession,
    id: uuid.UUID,
    tenant_id: uuid.UUID,
    data,
) -> Catalogo | None:
    item = await obtener_catalogo(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_catalogo(
    db: AsyncSession,
    id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> bool:
    item = await obtener_catalogo(db, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True


# ─── Consultorio ──────────────────────────────────────────────────────────────

async def listar_consultorios(
    db: AsyncSession,
    tenant_id: uuid.UUID,
) -> list[Consultorio]:
    result = await db.execute(
        select(Consultorio)
        .where(Consultorio.tenant_id == tenant_id)
        .order_by(Consultorio.nombre)
    )
    return result.scalars().all()


async def obtener_consultorio(
    db: AsyncSession,
    id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> Consultorio | None:
    result = await db.execute(
        select(Consultorio).where(Consultorio.id == id, Consultorio.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def crear_consultorio(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    data,
) -> Consultorio:
    item = Consultorio(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_consultorio(
    db: AsyncSession,
    id: uuid.UUID,
    tenant_id: uuid.UUID,
    data,
) -> Consultorio | None:
    item = await obtener_consultorio(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_consultorio(
    db: AsyncSession,
    id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> bool:
    item = await obtener_consultorio(db, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True