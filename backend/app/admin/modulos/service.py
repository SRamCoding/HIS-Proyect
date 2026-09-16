# backend/app/admin/modulos/service.py
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.admin.modulos.models import ModuleDependency

# Clave arbitraria (constante) para el advisory lock que serializa la
# creacion de dependencias entre modulos -- ver create_module_dependency.
_LOCK_GRAFO_DEPENDENCIAS = 837_412_665


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

    # Advisory lock de transaccion: serializa TODA creacion de dependencias
    # entre si. Sin esto, dos peticiones concurrentes pueden cada una
    # recorrer el grafo (BFS de _existe_ciclo), ver "sin ciclo" con el
    # estado de ANTES de la otra, e insertar las dos -- juntas, sin que
    # ninguna lo haya detectado, si cierran un ciclo. Bloquear filas
    # puntuales no alcanza aca porque el ciclo se forma por la COMBINACION
    # de dos inserts, no por chocar sobre la misma fila; se serializa la
    # operacion completa en su lugar. Se libera solo al terminar la
    # transaccion (commit o rollback), automaticamente.
    await db.execute(text("SELECT pg_advisory_xact_lock(:clave)"), {"clave": _LOCK_GRAFO_DEPENDENCIAS})

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
    if not is_active:
        # Mismo criterio que ya se usa para un nivel hospitalario o un
        # codigo en uso: bloquear en vez de dejar el catalogo en un estado
        # inconsistente. Sin esto, se podia apagar un modulo del que otro
        # modulo ACTIVO depende obligatoriamente, sin ningun aviso -- el
        # dependiente quedaba con una dependencia rota y silenciosa.
        dependientes = (await db.scalars(
            select(ModuleDependency.module_code)
            .join(Module, Module.code == ModuleDependency.module_code)
            .where(
                ModuleDependency.depends_on_code == module.code,
                ModuleDependency.is_required.is_(True),
                Module.is_active.is_(True),
            )
        )).all()
        if dependientes:
            raise HTTPException(
                409,
                f"No se puede desactivar: {', '.join(sorted(dependientes))} "
                f"depende{'n' if len(dependientes) > 1 else ''} obligatoriamente de este módulo. "
                "Desactívalos primero.",
            )
    module.is_active = is_active
    await db.commit()
    return module