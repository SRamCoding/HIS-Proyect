import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.sigarh.imagenologia.models import ExamenImagenologia


async def listar(db: AsyncSession, tenant_id: uuid.UUID, modalidad: str | None = None) -> list[ExamenImagenologia]:
    query = select(ExamenImagenologia).where(ExamenImagenologia.tenant_id == tenant_id)
    if modalidad:
        query = query.where(ExamenImagenologia.modalidad == modalidad)
    query = query.order_by(ExamenImagenologia.modalidad, ExamenImagenologia.nombre)
    result = await db.execute(query)
    return result.scalars().all()


async def obtener(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> ExamenImagenologia | None:
    result = await db.execute(
        select(ExamenImagenologia).where(ExamenImagenologia.id == id, ExamenImagenologia.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def crear(db: AsyncSession, tenant_id: uuid.UUID, data) -> ExamenImagenologia:
    item = ExamenImagenologia(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> ExamenImagenologia | None:
    item = await obtener(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener(db, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True