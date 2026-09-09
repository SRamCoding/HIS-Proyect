import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.sigarh.infraestructura_hosp.models import Piso, Sala, Cama
from app.sigarh.mantenimiento.models import Servicio


class ReglaNegocioError(Exception):
    """Operación bloqueada por una regla de negocio (se traduce a HTTP 409)."""


# ─── Helper ───────────────────────────────────────────────────────────────────

async def _obtener(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(modelo).where(modelo.id == id, modelo.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


def _cols(obj) -> dict:
    return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}


# ─── Pisos ────────────────────────────────────────────────────────────────────

async def _conteos_piso(db: AsyncSession, tenant_id: uuid.UUID):
    salas = dict((await db.execute(
        select(Sala.piso_id, func.count()).where(Sala.tenant_id == tenant_id).group_by(Sala.piso_id)
    )).all())
    servicios = dict((await db.execute(
        select(Servicio.piso_id, func.count()).where(Servicio.tenant_id == tenant_id).group_by(Servicio.piso_id)
    )).all())
    return salas, servicios


async def listar_pisos(db: AsyncSession, tenant_id: uuid.UUID) -> list[dict]:
    result = await db.execute(
        select(Piso).where(Piso.tenant_id == tenant_id).order_by(Piso.orden, Piso.nombre)
    )
    pisos = result.scalars().all()
    salas, servicios = await _conteos_piso(db, tenant_id)
    return [
        {**_cols(p), "total_salas": salas.get(p.id, 0), "total_servicios": servicios.get(p.id, 0)}
        for p in pisos
    ]


async def obtener_piso(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> dict | None:
    p = await _obtener(db, Piso, id, tenant_id)
    if not p:
        return None
    salas, servicios = await _conteos_piso(db, tenant_id)
    return {**_cols(p), "total_salas": salas.get(p.id, 0), "total_servicios": servicios.get(p.id, 0)}


async def crear_piso(db: AsyncSession, tenant_id: uuid.UUID, data) -> dict:
    item = Piso(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {**_cols(item), "total_salas": 0, "total_servicios": 0}


async def actualizar_piso(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> dict | None:
    item = await _obtener(db, Piso, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    return await obtener_piso(db, id, tenant_id)


async def eliminar_piso(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await _obtener(db, Piso, id, tenant_id)
    if not item:
        return False
    n_salas = await db.scalar(
        select(func.count()).select_from(Sala).where(Sala.piso_id == id, Sala.tenant_id == tenant_id)
    )
    n_serv = await db.scalar(
        select(func.count()).select_from(Servicio).where(Servicio.piso_id == id, Servicio.tenant_id == tenant_id)
    )
    if n_salas or n_serv:
        raise ReglaNegocioError(
            f"No se puede eliminar: el piso tiene {n_serv or 0} servicio(s) y {n_salas or 0} sala(s) asociados."
        )
    await db.delete(item)
    await db.commit()
    return True


# ─── Salas ────────────────────────────────────────────────────────────────────

async def _enriquecer_salas(db: AsyncSession, tenant_id: uuid.UUID, salas: list[Sala]) -> list[dict]:
    if not salas:
        return []
    pisos = dict((await db.execute(
        select(Piso.id, Piso.nombre).where(Piso.tenant_id == tenant_id)
    )).all())
    servicios = dict((await db.execute(
        select(Servicio.id, Servicio.nombre).where(Servicio.tenant_id == tenant_id)
    )).all())
    camas = (await db.execute(
        select(Cama.sala_id, Cama.estado, func.count())
        .where(Cama.tenant_id == tenant_id)
        .group_by(Cama.sala_id, Cama.estado)
    )).all()
    total: dict = {}
    disp: dict = {}
    ocup: dict = {}
    for sala_id, estado, n in camas:
        total[sala_id] = total.get(sala_id, 0) + n
        if estado == "DISPONIBLE":
            disp[sala_id] = disp.get(sala_id, 0) + n
        elif estado == "OCUPADA":
            ocup[sala_id] = ocup.get(sala_id, 0) + n
    return [
        {
            **_cols(s),
            "piso_nombre": pisos.get(s.piso_id),
            "servicio_nombre": servicios.get(s.servicio_id),
            "total_camas": total.get(s.id, 0),
            "camas_disponibles": disp.get(s.id, 0),
            "camas_ocupadas": ocup.get(s.id, 0),
        }
        for s in salas
    ]


async def listar_salas(db: AsyncSession, tenant_id: uuid.UUID, piso_id: uuid.UUID | None = None) -> list[dict]:
    query = select(Sala).where(Sala.tenant_id == tenant_id)
    if piso_id:
        query = query.where(Sala.piso_id == piso_id)
    salas = (await db.execute(query.order_by(Sala.nombre))).scalars().all()
    return await _enriquecer_salas(db, tenant_id, salas)


async def obtener_sala(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> dict | None:
    s = await _obtener(db, Sala, id, tenant_id)
    if not s:
        return None
    return (await _enriquecer_salas(db, tenant_id, [s]))[0]


async def crear_sala(db: AsyncSession, tenant_id: uuid.UUID, data) -> dict:
    item = Sala(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    return await obtener_sala(db, item.id, tenant_id)


async def actualizar_sala(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> dict | None:
    item = await _obtener(db, Sala, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    return await obtener_sala(db, id, tenant_id)


async def eliminar_sala(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await _obtener(db, Sala, id, tenant_id)
    if not item:
        return False
    ocupadas = await db.scalar(
        select(func.count()).select_from(Cama).where(
            Cama.sala_id == id, Cama.tenant_id == tenant_id, Cama.estado == "OCUPADA"
        )
    )
    if ocupadas:
        raise ReglaNegocioError(f"No se puede eliminar: la sala tiene {ocupadas} cama(s) ocupada(s).")
    await db.delete(item)
    await db.commit()
    return True


async def generar_camas(db: AsyncSession, tenant_id: uuid.UUID, sala_id: uuid.UUID, data) -> dict:
    sala = await _obtener(db, Sala, sala_id, tenant_id)
    if not sala:
        return None
    existentes = (await db.execute(
        select(Cama).where(Cama.sala_id == sala_id, Cama.tenant_id == tenant_id)
    )).scalars().all()
    faltan = (sala.capacidad or 0) - len(existentes)
    if faltan <= 0:
        return {"creadas": 0, "total": len(existentes), "capacidad": sala.capacidad}

    piso_nombre = None
    servicio_nombre = None
    if sala.piso_id:
        piso_nombre = await db.scalar(select(Piso.nombre).where(Piso.id == sala.piso_id))
    if sala.servicio_id:
        servicio_nombre = await db.scalar(select(Servicio.nombre).where(Servicio.id == sala.servicio_id))

    base = (data.prefijo or sala.codigo or (sala.nombre[:6] if sala.nombre else "C")).upper().strip()
    codigos_usados = {c.codigo for c in existentes}
    creadas = 0
    n = 1
    while creadas < faltan:
        codigo = f"{base}{n:02d}"
        if codigo not in codigos_usados:
            db.add(Cama(
                tenant_id=tenant_id,
                sala_id=sala_id,
                piso_id=sala.piso_id,
                servicio_id=sala.servicio_id,
                codigo=codigo,
                nombre=f"Cama {n:02d} - {sala.nombre}",
                sala_texto=sala.nombre,
                piso_texto=piso_nombre,
                servicio_texto=servicio_nombre,
                tipo_cama=data.tipo_cama,
                estado="DISPONIBLE",
                is_active=True,
            ))
            codigos_usados.add(codigo)
            creadas += 1
        n += 1
    await db.commit()
    return {"creadas": creadas, "total": len(existentes) + creadas, "capacidad": sala.capacidad}


# ─── Camas ────────────────────────────────────────────────────────────────────

async def listar_camas(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    sala_id: uuid.UUID | None = None,
    piso_id: uuid.UUID | None = None,
    estado: str | None = None,
) -> list[Cama]:
    query = select(Cama).where(Cama.tenant_id == tenant_id)
    if sala_id:
        query = query.where(Cama.sala_id == sala_id)
    if piso_id:
        query = query.where(Cama.piso_id == piso_id)
    if estado:
        query = query.where(Cama.estado == estado)
    result = await db.execute(query.order_by(Cama.codigo))
    return result.scalars().all()


async def obtener_cama(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Cama | None:
    return await _obtener(db, Cama, id, tenant_id)


async def _codigo_duplicado(db: AsyncSession, tenant_id: uuid.UUID, codigo: str, excluir: uuid.UUID | None = None) -> bool:
    query = select(func.count()).select_from(Cama).where(
        Cama.tenant_id == tenant_id, func.upper(Cama.codigo) == codigo.upper()
    )
    if excluir:
        query = query.where(Cama.id != excluir)
    return bool(await db.scalar(query))


async def crear_cama(db: AsyncSession, tenant_id: uuid.UUID, data) -> Cama:
    if await _codigo_duplicado(db, tenant_id, data.codigo):
        raise ReglaNegocioError(f"Ya existe una cama con el código {data.codigo}.")
    item = Cama(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_cama(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Cama | None:
    item = await _obtener(db, Cama, id, tenant_id)
    if not item:
        return None
    cambios = data.model_dump(exclude_unset=True)
    if cambios.get("codigo") and await _codigo_duplicado(db, tenant_id, cambios["codigo"], excluir=id):
        raise ReglaNegocioError(f"Ya existe una cama con el código {cambios['codigo']}.")
    for field, value in cambios.items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def cambiar_estado_cama(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, estado: str) -> Cama | None:
    item = await _obtener(db, Cama, id, tenant_id)
    if not item:
        return None
    item.estado = estado
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_cama(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await _obtener(db, Cama, id, tenant_id)
    if not item:
        return False
    if item.estado == "OCUPADA":
        raise ReglaNegocioError("No se puede eliminar una cama ocupada.")
    await db.delete(item)
    await db.commit()
    return True
