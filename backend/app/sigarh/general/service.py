import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.sigarh.general.models import DiagnosticoCIE10, Paquete, PaqueteItem, TiempoProcedimiento


# ─── Helper ───────────────────────────────────────────────────────────────────

async def _obtener(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(modelo).where(modelo.id == id, modelo.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


# ─── CIE-10 ───────────────────────────────────────────────────────────────────

async def listar_cie10(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    search: str | None = None,
    capitulo: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    query = select(DiagnosticoCIE10).where(DiagnosticoCIE10.tenant_id == tenant_id)
    if capitulo:
        query = query.where(DiagnosticoCIE10.capitulo == capitulo)
    if search:
        term = f"%{search.strip()}%"
        query = query.where(or_(
            DiagnosticoCIE10.codigo_cie10.ilike(term),
            DiagnosticoCIE10.descripcion.ilike(term),
            DiagnosticoCIE10.categoria.ilike(term),
        ))
    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0
    query = query.order_by(DiagnosticoCIE10.codigo_cie10).offset(
        (page - 1) * page_size
    ).limit(page_size)
    result = await db.execute(query)
    return {
        "items": list(result.scalars().all()), "total": total,
        "page": page, "page_size": page_size,
        "pages": max(1, (total + page_size - 1) // page_size),
    }


async def obtener_cie10(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> DiagnosticoCIE10 | None:
    return await _obtener(db, DiagnosticoCIE10, id, tenant_id)


async def crear_cie10(db: AsyncSession, tenant_id: uuid.UUID, data) -> DiagnosticoCIE10:
    item = DiagnosticoCIE10(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_cie10(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> DiagnosticoCIE10 | None:
    item = await obtener_cie10(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_cie10(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener_cie10(db, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True


# ─── Paquetes ─────────────────────────────────────────────────────────────────

async def listar_paquetes(db: AsyncSession, tenant_id: uuid.UUID) -> list[Paquete]:
    result = await db.execute(
        select(Paquete)
        .options(selectinload(Paquete.items))
        .where(Paquete.tenant_id == tenant_id)
        .order_by(Paquete.nombre)
    )
    return result.scalars().all()


async def obtener_paquete(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Paquete | None:
    result = await db.execute(
        select(Paquete)
        .options(selectinload(Paquete.items))
        .where(Paquete.id == id, Paquete.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def crear_paquete(db: AsyncSession, tenant_id: uuid.UUID, data) -> Paquete:
    items_data = data.items
    paquete_dict = data.model_dump(exclude={"items"})
    paquete = Paquete(tenant_id=tenant_id, **paquete_dict)
    db.add(paquete)
    await db.flush()
    for item_data in items_data:
        item = PaqueteItem(paquete_id=paquete.id, **item_data.model_dump())
        db.add(item)
    await db.commit()
    await db.refresh(paquete)
    return paquete


async def actualizar_paquete(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Paquete | None:
    paquete = await obtener_paquete(db, id, tenant_id)
    if not paquete:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(paquete, field, value)
    await db.commit()
    await db.refresh(paquete)
    return paquete


async def eliminar_paquete(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    paquete = await obtener_paquete(db, id, tenant_id)
    if not paquete:
        return False
    await db.delete(paquete)
    await db.commit()
    return True


# ─── Tiempos Procedimientos ───────────────────────────────────────────────────

async def listar_tiempos(db: AsyncSession, tenant_id: uuid.UUID, especialidad_id: uuid.UUID | None = None) -> list[TiempoProcedimiento]:
    query = select(TiempoProcedimiento).where(TiempoProcedimiento.tenant_id == tenant_id)
    if especialidad_id:
        query = query.where(TiempoProcedimiento.especialidad_id == especialidad_id)
    query = query.order_by(TiempoProcedimiento.nombre)
    result = await db.execute(query)
    return result.scalars().all()


async def obtener_tiempo(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> TiempoProcedimiento | None:
    return await _obtener(db, TiempoProcedimiento, id, tenant_id)


async def crear_tiempo(db: AsyncSession, tenant_id: uuid.UUID, data) -> TiempoProcedimiento:
    item = TiempoProcedimiento(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_tiempo(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> TiempoProcedimiento | None:
    item = await obtener_tiempo(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_tiempo(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener_tiempo(db, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True
