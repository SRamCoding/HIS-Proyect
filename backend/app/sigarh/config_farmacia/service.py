import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.sigarh.config_farmacia.models import Almacen, Medicamento, ProveedorFarmacia, CatalogoFarmacia


class ReglaNegocioError(Exception):
    pass


async def _obtener(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(modelo).where(modelo.id == id, modelo.tenant_id == tenant_id))
    return result.scalar_one_or_none()


async def _lotes_con_stock(db: AsyncSession, tenant_id: uuid.UUID, *, almacen_id=None, medicamento_id=None) -> int:
    """Cuenta lotes de farmacia con stock > 0 asociados a un almacén o medicamento.
    Devuelve -1 si la tabla farmacia_lotes aún no existe en el entorno."""
    try:
        from app.hospital.farmacia.models import FarmaciaLote
    except Exception:
        return 0
    q = select(func.count()).select_from(FarmaciaLote).where(
        FarmaciaLote.tenant_id == tenant_id, FarmaciaLote.stock_actual > 0
    )
    if almacen_id:
        q = q.where(FarmaciaLote.almacen_id == almacen_id)
    if medicamento_id:
        q = q.where(FarmaciaLote.medicamento_id == medicamento_id)
    try:
        return await db.scalar(q) or 0
    except Exception:
        return 0


# ─── Almacenes ────────────────────────────────────────────────────────────────

async def listar_almacenes(
    db: AsyncSession, tenant_id: uuid.UUID,
    tipo: str | None = None, despacha_recetas: bool | None = None, is_active: bool | None = None,
) -> list[Almacen]:
    q = select(Almacen).where(Almacen.tenant_id == tenant_id)
    if tipo:
        q = q.where(Almacen.tipo == tipo)
    if despacha_recetas is not None:
        q = q.where(Almacen.despacha_recetas == despacha_recetas)
    if is_active is not None:
        q = q.where(Almacen.is_active == is_active)
    return (await db.execute(q.order_by(Almacen.nombre))).scalars().all()


async def obtener_almacen(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Almacen | None:
    return await _obtener(db, Almacen, id, tenant_id)


async def _codigo_almacen_duplicado(db, tenant_id, codigo, excluir_id=None) -> bool:
    q = select(Almacen.id).where(Almacen.tenant_id == tenant_id, func.upper(Almacen.codigo) == codigo.upper())
    if excluir_id:
        q = q.where(Almacen.id != excluir_id)
    return (await db.execute(q)).first() is not None


async def crear_almacen(db: AsyncSession, tenant_id: uuid.UUID, data) -> Almacen:
    if await _codigo_almacen_duplicado(db, tenant_id, data.codigo):
        raise ReglaNegocioError(f"Ya existe un almacén con el código {data.codigo}")
    item = Almacen(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_almacen(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Almacen | None:
    item = await obtener_almacen(db, id, tenant_id)
    if not item:
        return None
    cambios = data.model_dump(exclude_unset=True)
    if cambios.get("codigo") and await _codigo_almacen_duplicado(db, tenant_id, cambios["codigo"], excluir_id=id):
        raise ReglaNegocioError(f"Ya existe un almacén con el código {cambios['codigo']}")
    for field, value in cambios.items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def eliminar_almacen(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener_almacen(db, id, tenant_id)
    if not item:
        return False
    if await _lotes_con_stock(db, tenant_id, almacen_id=id) > 0:
        raise ReglaNegocioError("No se puede eliminar: el almacén tiene existencias con stock mayor que cero")
    try:
        await db.delete(item)
        await db.commit()
    except Exception:
        await db.rollback()
        raise ReglaNegocioError("No se puede eliminar: el almacén está siendo usado en operaciones de farmacia")
    return True


# ─── Medicamentos ─────────────────────────────────────────────────────────────

async def _tipos_producto(db: AsyncSession, tenant_id: uuid.UUID) -> dict:
    try:
        from app.sigarh.infraestructura.models import Catalogo
    except Exception:
        return {}
    rows = (await db.execute(
        select(Catalogo.id, Catalogo.nombre).where(
            Catalogo.tenant_id == tenant_id, Catalogo.categoria == "tipos_producto"
        )
    )).all()
    return dict(rows)


async def _serializar_medicamentos(db, tenant_id, items: list[Medicamento]) -> list[dict]:
    if not items:
        return []
    tipos = await _tipos_producto(db, tenant_id)
    out = []
    for m in items:
        d = {c.name: getattr(m, c.name) for c in m.__table__.columns}
        d["tipo_producto_nombre"] = tipos.get(m.tipo_producto_id)
        out.append(d)
    return out


async def listar_medicamentos(
    db: AsyncSession, tenant_id: uuid.UUID,
    search: str | None = None, is_active: bool | None = None,
    condicion_venta: str | None = None, controlado: bool | None = None,
    fiscalizado_digemid: bool | None = None, reporte_sismed: bool | None = None,
    requiere_cadena_frio: bool | None = None, forma_farmaceutica: str | None = None,
    tipo_producto_id: uuid.UUID | None = None,
) -> list[dict]:
    q = select(Medicamento).where(Medicamento.tenant_id == tenant_id)
    if is_active is not None:
        q = q.where(Medicamento.is_active == is_active)
    if condicion_venta:
        q = q.where(Medicamento.condicion_venta == condicion_venta)
    if controlado is not None:
        q = q.where(Medicamento.controlado == controlado)
    if fiscalizado_digemid is not None:
        q = q.where(Medicamento.fiscalizado_digemid == fiscalizado_digemid)
    if reporte_sismed is not None:
        q = q.where(Medicamento.reporte_sismed == reporte_sismed)
    if requiere_cadena_frio is not None:
        q = q.where(Medicamento.requiere_cadena_frio == requiere_cadena_frio)
    if forma_farmaceutica:
        q = q.where(Medicamento.forma_farmaceutica == forma_farmaceutica)
    if tipo_producto_id:
        q = q.where(Medicamento.tipo_producto_id == tipo_producto_id)
    if search:
        q = q.where(
            Medicamento.nombre_comercial.ilike(f"%{search}%") |
            Medicamento.codigo_interno.ilike(f"%{search}%") |
            Medicamento.nombre_generico.ilike(f"%{search}%") |
            Medicamento.dci.ilike(f"%{search}%")
        )
    items = (await db.execute(q.order_by(Medicamento.nombre_comercial))).scalars().all()
    return await _serializar_medicamentos(db, tenant_id, items)


async def obtener_medicamento(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> dict | None:
    item = await _obtener(db, Medicamento, id, tenant_id)
    if not item:
        return None
    return (await _serializar_medicamentos(db, tenant_id, [item]))[0]


async def _codigo_med_duplicado(db, tenant_id, codigo, excluir_id=None) -> bool:
    q = select(Medicamento.id).where(Medicamento.tenant_id == tenant_id, Medicamento.codigo_interno == codigo)
    if excluir_id:
        q = q.where(Medicamento.id != excluir_id)
    return (await db.execute(q)).first() is not None


async def crear_medicamento(db: AsyncSession, tenant_id: uuid.UUID, data) -> dict:
    if await _codigo_med_duplicado(db, tenant_id, data.codigo_interno):
        raise ReglaNegocioError(f"Ya existe un producto con el código {data.codigo_interno}")
    item = Medicamento(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    return (await _serializar_medicamentos(db, tenant_id, [await _obtener(db, Medicamento, item.id, tenant_id)]))[0]


async def actualizar_medicamento(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> dict | None:
    item = await _obtener(db, Medicamento, id, tenant_id)
    if not item:
        return None
    cambios = data.model_dump(exclude_unset=True)
    if cambios.get("codigo_interno") and await _codigo_med_duplicado(db, tenant_id, cambios["codigo_interno"], excluir_id=id):
        raise ReglaNegocioError(f"Ya existe un producto con el código {cambios['codigo_interno']}")
    # Coherencia: al cambiar la condición de venta, alinear 'requiere_receta'
    # salvo que el usuario lo haya enviado explícitamente en el mismo PATCH.
    if "condicion_venta" in cambios and "requiere_receta" not in cambios:
        from app.sigarh.config_farmacia.schemas import CONDICIONES_CON_RECETA
        cambios["requiere_receta"] = cambios["condicion_venta"] in CONDICIONES_CON_RECETA
    for field, value in cambios.items():
        setattr(item, field, value)
    await db.commit()
    return (await _serializar_medicamentos(db, tenant_id, [await _obtener(db, Medicamento, id, tenant_id)]))[0]


async def eliminar_medicamento(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await _obtener(db, Medicamento, id, tenant_id)
    if not item:
        return False
    if await _lotes_con_stock(db, tenant_id, medicamento_id=id) > 0:
        raise ReglaNegocioError("No se puede eliminar: el producto tiene existencias con stock mayor que cero")
    item.is_active = False  # baja lógica: conserva historial y no rompe FK RESTRICT
    await db.commit()
    return True


# ─── Proveedores / Catálogos farmacia ────────────────────────────────────────

async def listar_proveedores(db, tenant_id):
    return (await db.execute(
        select(ProveedorFarmacia).where(ProveedorFarmacia.tenant_id == tenant_id).order_by(ProveedorFarmacia.razon_social)
    )).scalars().all()


async def crear_proveedor(db, tenant_id, data):
    row = ProveedorFarmacia(tenant_id=tenant_id, **data.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def listar_catalogo(db, tenant_id, categoria):
    return (await db.execute(
        select(CatalogoFarmacia).where(
            CatalogoFarmacia.tenant_id == tenant_id,
            CatalogoFarmacia.categoria == categoria,
            CatalogoFarmacia.is_active.is_(True),
        ).order_by(CatalogoFarmacia.nombre)
    )).scalars().all()


async def crear_catalogo(db, tenant_id, data):
    row = CatalogoFarmacia(tenant_id=tenant_id, **data.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row
