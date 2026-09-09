import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.sigarh.infraestructura.models import Catalogo, Consultorio
from app.sigarh.rrhh.models import Especialidad
from app.sigarh.infraestructura_hosp.models import Piso


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

def _cols(obj) -> dict:
    return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}


async def _enriquecer_consultorios(db: AsyncSession, tenant_id: uuid.UUID, items: list[Consultorio]) -> list[dict]:
    if not items:
        return []
    especialidades = dict((await db.execute(
        select(Especialidad.id, Especialidad.nombre).where(Especialidad.tenant_id == tenant_id)
    )).all())
    pisos = dict((await db.execute(
        select(Piso.id, Piso.nombre).where(Piso.tenant_id == tenant_id)
    )).all())
    return [
        {
            **_cols(c),
            "especialidad_nombre": especialidades.get(c.especialidad_id),
            "piso_nombre": pisos.get(c.piso_id),
        }
        for c in items
    ]


async def listar_consultorios(db: AsyncSession, tenant_id: uuid.UUID) -> list[dict]:
    result = await db.execute(
        select(Consultorio)
        .where(Consultorio.tenant_id == tenant_id)
        .order_by(Consultorio.nombre)
    )
    return await _enriquecer_consultorios(db, tenant_id, result.scalars().all())


async def _obtener_consultorio_orm(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Consultorio | None:
    result = await db.execute(
        select(Consultorio).where(Consultorio.id == id, Consultorio.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def obtener_consultorio(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> dict | None:
    item = await _obtener_consultorio_orm(db, id, tenant_id)
    if not item:
        return None
    return (await _enriquecer_consultorios(db, tenant_id, [item]))[0]


async def crear_consultorio(db: AsyncSession, tenant_id: uuid.UUID, data) -> dict:
    item = Consultorio(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    return await obtener_consultorio(db, item.id, tenant_id)


async def actualizar_consultorio(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> dict | None:
    item = await _obtener_consultorio_orm(db, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    return await obtener_consultorio(db, id, tenant_id)


async def eliminar_consultorio(
    db: AsyncSession,
    id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> bool:
    item = await _obtener_consultorio_orm(db, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True