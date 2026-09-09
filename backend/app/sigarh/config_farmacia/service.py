import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.sigarh.config_farmacia.models import Almacen, Medicamento, ProveedorFarmacia, CatalogoFarmacia


# ─── Helper ───────────────────────────────────────────────────────────────────

async def _obtener(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(modelo).where(modelo.id == id, modelo.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


# ─── Almacenes ────────────────────────────────────────────────────────────────

async def listar_almacenes(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    tipo: str | None = None,
) -> list[Almacen]:
    query = select(Almacen).where(Almacen.tenant_id == tenant_id)
    if tipo:
        query = query.where(Almacen.tipo == tipo)
    query = query.order_by(Almacen.nombre)
    result = await db.execute(query)
    return result.scalars().all()


async def obtener_almacen(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Almacen | None:
    return await _obtener(db, Almacen, id, tenant_id)


async def crear_almacen(db: AsyncSession, tenant_id: uuid.UUID, data) -> Almacen:
    item = Almacen(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_almacen(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Almacen | None:
    item = await obtener_almacen(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_almacen(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener_almacen(db, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True


# ─── Medicamentos ─────────────────────────────────────────────────────────────

async def listar_medicamentos(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    search: str | None = None,
    is_active: bool | None = None,
) -> list[Medicamento]:
    query = select(Medicamento).where(Medicamento.tenant_id == tenant_id)
    if is_active is not None:
        query = query.where(Medicamento.is_active == is_active)
    if search:
        query = query.where(
            Medicamento.nombre_comercial.ilike(f"%{search}%") |
            Medicamento.codigo_interno.ilike(f"%{search}%") |
            Medicamento.dci.ilike(f"%{search}%")
        )
    query = query.order_by(Medicamento.nombre_comercial)
    result = await db.execute(query)
    return result.scalars().all()


async def obtener_medicamento(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Medicamento | None:
    return await _obtener(db, Medicamento, id, tenant_id)


async def crear_medicamento(db: AsyncSession, tenant_id: uuid.UUID, data) -> Medicamento:
    item = Medicamento(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_medicamento(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Medicamento | None:
    item = await obtener_medicamento(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_medicamento(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener_medicamento(db, id, tenant_id)
    if not item:
        return False
    item.is_active = False
    await db.commit()
    return True

async def listar_proveedores(db, tenant_id):
    return (await db.execute(select(ProveedorFarmacia).where(ProveedorFarmacia.tenant_id==tenant_id).order_by(ProveedorFarmacia.razon_social))).scalars().all()
async def crear_proveedor(db, tenant_id, data):
    row=ProveedorFarmacia(tenant_id=tenant_id,**data.model_dump()); db.add(row); await db.commit(); await db.refresh(row); return row
async def listar_catalogo(db, tenant_id, categoria):
    return (await db.execute(select(CatalogoFarmacia).where(CatalogoFarmacia.tenant_id==tenant_id,CatalogoFarmacia.categoria==categoria,CatalogoFarmacia.is_active==True).order_by(CatalogoFarmacia.nombre))).scalars().all()
async def crear_catalogo(db, tenant_id, data):
    row=CatalogoFarmacia(tenant_id=tenant_id,**data.model_dump()); db.add(row); await db.commit(); await db.refresh(row); return row
