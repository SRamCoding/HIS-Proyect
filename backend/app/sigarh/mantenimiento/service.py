import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.sigarh.mantenimiento.models import (
    Departamento, Servicio, TipoTrabajador, TipoGuardia,
    NivelRemunerativo, HorarioGuardia, GrupoOcupacional,
    TipoActividad, Actividad, GuardiaValorizada,
    RolSistema, PerfilUsuario
)


# ─── Helper genérico CRUD ────────────────────────────────────────────────────

async def listar(db: AsyncSession, modelo, tenant_id: uuid.UUID):
    result = await db.execute(
        select(modelo)
        .where(modelo.tenant_id == tenant_id)
        .order_by(modelo.created_at.desc())
    )
    return result.scalars().all()


async def obtener(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(modelo)
        .where(modelo.id == id, modelo.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def eliminar(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener(db, modelo, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True


# ─── Departamentos ────────────────────────────────────────────────────────────

async def crear_departamento(db: AsyncSession, tenant_id: uuid.UUID, data) -> Departamento:
    item = Departamento(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_departamento(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Departamento | None:
    item = await obtener(db, Departamento, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


# ─── Servicios ────────────────────────────────────────────────────────────────

async def crear_servicio(db: AsyncSession, tenant_id: uuid.UUID, data) -> Servicio:
    item = Servicio(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_servicio(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Servicio | None:
    item = await obtener(db, Servicio, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


# ─── Helper para catálogos simples ───────────────────────────────────────────

async def crud_crear(db: AsyncSession, modelo, tenant_id: uuid.UUID, data) -> any:
    item = modelo(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def crud_actualizar(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID, data) -> any:
    item = await obtener(db, modelo, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


# ─── Perfil Usuario (con JSON de módulos) ────────────────────────────────────

async def crear_perfil(db: AsyncSession, tenant_id: uuid.UUID, data) -> PerfilUsuario:
    data_dict = data.model_dump()
    modulos = data_dict.pop('modulos_acceso', [])
    perfil = PerfilUsuario(
        tenant_id=tenant_id,
        modulos_acceso=json.dumps(modulos),
        **data_dict
    )
    db.add(perfil)
    await db.commit()
    await db.refresh(perfil)
    return perfil