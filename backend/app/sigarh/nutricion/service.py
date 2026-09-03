import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.sigarh.nutricion.models import RacionNutricion, CambioTurnoNutricion


# ─── Raciones ─────────────────────────────────────────────────────────────────

async def listar_raciones(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    fecha: date | None = None,
    dependencia: str | None = None,
    entregado: bool | None = None,
) -> list[RacionNutricion]:
    query = select(RacionNutricion).where(RacionNutricion.tenant_id == tenant_id)
    if fecha:
        query = query.where(RacionNutricion.fecha == fecha)
    if dependencia and dependencia != "TODAS":
        query = query.where(RacionNutricion.dependencia == dependencia)
    if entregado is not None:
        query = query.where(RacionNutricion.entregado == entregado)
    query = query.order_by(RacionNutricion.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def buscar_racion_por_dni(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    dni: str,
    fecha: date,
) -> RacionNutricion | None:
    result = await db.execute(
        select(RacionNutricion).where(
            RacionNutricion.tenant_id == tenant_id,
            RacionNutricion.dni == dni,
            RacionNutricion.fecha == fecha,
        )
    )
    return result.scalar_one_or_none()


async def crear_racion(db: AsyncSession, tenant_id: uuid.UUID, data) -> RacionNutricion:
    item = RacionNutricion(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_racion(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> RacionNutricion | None:
    result = await db.execute(
        select(RacionNutricion).where(RacionNutricion.id == id, RacionNutricion.tenant_id == tenant_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


# ─── Cambios de Turno ─────────────────────────────────────────────────────────

async def listar_cambios_turno(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    fecha: date | None = None,
) -> list[CambioTurnoNutricion]:
    query = select(CambioTurnoNutricion).where(CambioTurnoNutricion.tenant_id == tenant_id)
    if fecha:
        query = query.where(CambioTurnoNutricion.fecha == fecha)
    query = query.order_by(CambioTurnoNutricion.fecha.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def crear_cambio_turno(db: AsyncSession, tenant_id: uuid.UUID, data) -> CambioTurnoNutricion:
    item = CambioTurnoNutricion(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item