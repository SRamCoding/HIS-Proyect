from fastapi import HTTPException
from sqlalchemy import select, func, or_
from app.sigarh.config_farmacia.models import Medicamento
from app.sigarh.infraestructura.models import Catalogo
from app.sigarh.config_financiera.models import Tarifario, Seguro
from app.sigarh.rrhh.models import Especialidad


def columns(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


async def _paged(db, q, page, size):
    total = await db.scalar(select(func.count()).select_from(q.order_by(None).subquery()))
    rows = (await db.execute(q.offset((page-1)*size).limit(size))).all()
    return total, rows


# ─── Bienes e insumos (Medicamento, SIGARH > Config Farmacia) ──────────────

async def list_bienes(db, tid, q, tipo_id, page=1, size=20):
    query = (select(Medicamento, Catalogo.nombre)
        .outerjoin(Catalogo, Catalogo.id == Medicamento.tipo_producto_id)
        .where(Medicamento.tenant_id == tid, Medicamento.is_active.is_(True)))
    if tipo_id:
        query = query.where(Medicamento.tipo_producto_id == tipo_id)
    if q:
        for term in q.split():
            query = query.where(or_(Medicamento.nombre_comercial.icontains(term, autoescape=True),
                Medicamento.nombre_generico.icontains(term, autoescape=True),
                Medicamento.codigo_interno.icontains(term, autoescape=True),
                Medicamento.dci.icontains(term, autoescape=True)))
    total, rows = await _paged(db, query.order_by(Medicamento.nombre_comercial), page, size)
    items = [dict(columns(m), tipo_producto_nombre=tipo) for m, tipo in rows]
    return {"items": items, "total": total, "page": page, "page_size": size}


async def bien_detalle(db, tid, bien_id):
    row = (await db.execute(select(Medicamento, Catalogo.nombre)
        .outerjoin(Catalogo, Catalogo.id == Medicamento.tipo_producto_id)
        .where(Medicamento.tenant_id == tid, Medicamento.id == bien_id))).first()
    if not row:
        raise HTTPException(404, detail="Bien o insumo no encontrado en este hospital")
    m, tipo = row
    return dict(columns(m), tipo_producto_nombre=tipo)


async def catalogo_tipos_producto(db, tid):
    rows = (await db.execute(select(Catalogo).where(Catalogo.tenant_id == tid, Catalogo.is_active.is_(True),
        Catalogo.categoria == "tipos_producto").order_by(Catalogo.orden, Catalogo.nombre))).scalars().all()
    return [{"id": c.id, "nombre": c.nombre} for c in rows]


# ─── Servicios (Tarifario, SIGARH > Config Financiera) ─────────────────────

async def list_servicios(db, tid, q, tipo_servicio, page=1, size=20):
    query = (select(Tarifario, Especialidad.nombre, Seguro.nombre)
        .outerjoin(Especialidad, Especialidad.id == Tarifario.especialidad_id)
        .outerjoin(Seguro, Seguro.id == Tarifario.seguro_id)
        .where(Tarifario.tenant_id == tid, Tarifario.is_active.is_(True)))
    if tipo_servicio:
        query = query.where(Tarifario.tipo_servicio == tipo_servicio)
    if q:
        for term in q.split():
            query = query.where(or_(Tarifario.descripcion_servicio.icontains(term, autoescape=True),
                Tarifario.codigo.icontains(term, autoescape=True)))
    total, rows = await _paged(db, query.order_by(Tarifario.descripcion_servicio), page, size)
    items = [dict(columns(t), especialidad_nombre=esp, seguro_nombre=seg) for t, esp, seg in rows]
    return {"items": items, "total": total, "page": page, "page_size": size}


async def servicio_detalle(db, tid, tarifa_id):
    row = (await db.execute(select(Tarifario, Especialidad.nombre, Seguro.nombre)
        .outerjoin(Especialidad, Especialidad.id == Tarifario.especialidad_id)
        .outerjoin(Seguro, Seguro.id == Tarifario.seguro_id)
        .where(Tarifario.tenant_id == tid, Tarifario.id == tarifa_id))).first()
    if not row:
        raise HTTPException(404, detail="Tarifa de servicio no encontrada en este hospital")
    t, esp, seg = row
    return dict(columns(t), especialidad_nombre=esp, seguro_nombre=seg)
