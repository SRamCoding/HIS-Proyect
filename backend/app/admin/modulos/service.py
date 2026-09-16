# backend/app/admin/modulos/service.py
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.admin.modulos.models import ModuleDependency


async def get_module_dependencies(db: AsyncSession) -> list[ModuleDependency]:
    result = await db.execute(
        select(ModuleDependency).order_by(ModuleDependency.module_code)
    )
    return result.scalars().all()


async def _existe_ciclo(db: AsyncSession, origen: str, destino: str) -> bool:
    """True si agregar `origen depende de destino` cerraria un ciclo, es
    decir, si `origen` ya es (transitivamente) una dependencia de `destino`."""
    visitados: set[str] = set()
    pendientes = [destino]
    while pendientes:
        actual = pendientes.pop()
        if actual == origen:
            return True
        if actual in visitados:
            continue
        visitados.add(actual)
        siguientes = (await db.scalars(
            select(ModuleDependency.depends_on_code).where(ModuleDependency.module_code == actual)
        )).all()
        pendientes.extend(siguientes)
    return False


async def create_module_dependency(db: AsyncSession, data) -> ModuleDependency:
    from app.tenants.modulos.models import Module

    if data.module_code == data.depends_on_code:
        raise HTTPException(409, "Un módulo no puede depender de sí mismo")

    codigos_validos = set((await db.scalars(
        select(Module.code).where(Module.code.in_([data.module_code, data.depends_on_code]))
    )).all())
    faltantes = {data.module_code, data.depends_on_code} - codigos_validos
    if faltantes:
        raise HTTPException(422, f"Módulo(s) inexistente(s): {', '.join(sorted(faltantes))}")

    existente = await db.scalar(
        select(ModuleDependency.id).where(
            ModuleDependency.module_code == data.module_code,
            ModuleDependency.depends_on_code == data.depends_on_code,
        )
    )
    if existente:
        raise HTTPException(409, "Esa dependencia ya existe")

    if await _existe_ciclo(db, data.module_code, data.depends_on_code):
        raise HTTPException(409, "Esa dependencia crearía un ciclo entre módulos")

    dep = ModuleDependency(
        module_code=data.module_code,
        depends_on_code=data.depends_on_code,
        is_required=data.is_required,
    )
    db.add(dep)
    await db.commit()
    await db.refresh(dep)
    return dep


async def delete_module_dependency(db: AsyncSession, dep_id: uuid.UUID) -> bool:
    result = await db.execute(select(ModuleDependency).where(ModuleDependency.id == dep_id))
    dep = result.scalar_one_or_none()
    if not dep:
        return False
    await db.delete(dep)
    await db.commit()
    return True


async def toggle_module(db: AsyncSession, module_id: uuid.UUID, is_active: bool):
    from app.tenants.modulos.models import Module
    module = await db.get(Module, module_id)
    if not module:
        return None
    module.is_active = is_active
    await db.commit()
    return module