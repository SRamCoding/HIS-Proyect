import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.sigarh.movimientos.models import Vacacion, Licencia, CambioTurno, Papeleta


# ─── Helper genérico ──────────────────────────────────────────────────────────

async def _obtener(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(modelo).where(modelo.id == id, modelo.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def _eliminar(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await _obtener(db, modelo, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True


# ─── Vacaciones ───────────────────────────────────────────────────────────────

async def listar_vacaciones(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    estado: str | None = None,
    motivo_id: uuid.UUID | None = None,
    mes_actual: bool | None = None,
) -> list[Vacacion]:
    query = select(Vacacion).where(Vacacion.tenant_id == tenant_id)
    if estado:
        query = query.where(Vacacion.estado == estado)
    if motivo_id:
        query = query.where(Vacacion.motivo_id == motivo_id)
    if mes_actual is not None:
        query = query.where(Vacacion.mes_actual == mes_actual)
    query = query.order_by(Vacacion.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def crear_vacacion(db: AsyncSession, tenant_id: uuid.UUID, data) -> Vacacion:
    item = Vacacion(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_vacacion(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data: dict) -> Vacacion | None:
    item = await _obtener(db, Vacacion, id, tenant_id)
    if not item:
        return None
    for field, value in data.items():
        if hasattr(item, field):
            setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


# ─── Licencias ────────────────────────────────────────────────────────────────

async def listar_licencias(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    estado: str | None = None,
) -> list[Licencia]:
    query = select(Licencia).where(Licencia.tenant_id == tenant_id)
    if estado:
        query = query.where(Licencia.estado == estado)
    query = query.order_by(Licencia.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def crear_licencia(db: AsyncSession, tenant_id: uuid.UUID, data) -> Licencia:
    item = Licencia(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_licencia(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data: dict) -> Licencia | None:
    item = await _obtener(db, Licencia, id, tenant_id)
    if not item:
        return None
    for field, value in data.items():
        if hasattr(item, field):
            setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


# ─── Cambio de Turno ──────────────────────────────────────────────────────────

async def listar_cambios_turno(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    estado: str | None = None,
    mes_actual: bool | None = None,
) -> list[CambioTurno]:
    query = select(CambioTurno).where(CambioTurno.tenant_id == tenant_id)
    if estado:
        query = query.where(CambioTurno.estado == estado)
    query = query.order_by(CambioTurno.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def crear_cambio_turno(db: AsyncSession, tenant_id: uuid.UUID, data) -> CambioTurno:
    item = CambioTurno(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_cambio_turno(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data: dict) -> CambioTurno | None:
    item = await _obtener(db, CambioTurno, id, tenant_id)
    if not item:
        return None
    for field, value in data.items():
        if hasattr(item, field):
            setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


# ─── Papeletas ────────────────────────────────────────────────────────────────

async def listar_papeletas(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    estado: str | None = None,
    mes_actual: bool | None = None,
) -> list[Papeleta]:
    query = select(Papeleta).where(Papeleta.tenant_id == tenant_id)
    if estado:
        query = query.where(Papeleta.estado == estado)
    if mes_actual is not None:
        query = query.where(Papeleta.mes_actual == mes_actual)
    query = query.order_by(Papeleta.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def crear_papeleta(db: AsyncSession, tenant_id: uuid.UUID, data) -> Papeleta:
    item = Papeleta(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_papeleta(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data: dict) -> Papeleta | None:
    item = await _obtener(db, Papeleta, id, tenant_id)
    if not item:
        return None
    for field, value in data.items():
        if hasattr(item, field):
            setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item