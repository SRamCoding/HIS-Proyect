from fastapi import HTTPException
from sqlalchemy import select, func, or_
from app.sigarh.mantenimiento.models import Servicio, Departamento
from app.sigarh.infraestructura_hosp.models import Piso
from app.sigarh.general.models import DiagnosticoCIE10, Paquete, PaqueteItem
from app.sigarh.rrhh.models import Especialidad
from app.sigarh.config_farmacia.models import Medicamento


def columns(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


async def _paged(db, q, page, size):
    total = await db.scalar(select(func.count()).select_from(q.order_by(None).subquery()))
    rows = (await db.execute(q.offset((page-1)*size).limit(size))).all()
    return total, rows


# ─── Servicios ───────────────────────────────────────────────────────────────

async def list_servicios(db, tid, q, page=1, size=20):
    query = (select(Servicio, Departamento.nombre)
        .outerjoin(Departamento, Departamento.id == Servicio.departamento_id)
        .where(Servicio.tenant_id == tid, Servicio.is_active.is_(True)))
    if q:
        for term in q.split():
            query = query.where(or_(Servicio.nombre.icontains(term, autoescape=True),
                Servicio.codigo.icontains(term, autoescape=True)))
    total, rows = await _paged(db, query.order_by(Servicio.nombre), page, size)
    items = [dict(columns(s), departamento_nombre=dep) for s, dep in rows]
    return {"items": items, "total": total, "page": page, "page_size": size}


async def servicio_detalle(db, tid, servicio_id):
    row = (await db.execute(select(Servicio, Departamento.nombre, Piso.nombre)
        .outerjoin(Departamento, Departamento.id == Servicio.departamento_id)
        .outerjoin(Piso, Piso.id == Servicio.piso_id)
        .where(Servicio.tenant_id == tid, Servicio.id == servicio_id))).first()
    if not row:
        raise HTTPException(404, detail="Servicio no encontrado en este hospital")
    s, dep, piso = row
    return dict(columns(s), departamento_nombre=dep, piso_nombre=piso)


# ─── Diagnósticos CIE-10 ─────────────────────────────────────────────────────

async def list_diagnosticos(db, tid, q, capitulo, page=1, size=20):
    query = select(DiagnosticoCIE10).where(DiagnosticoCIE10.tenant_id == tid, DiagnosticoCIE10.is_active.is_(True))
    if capitulo:
        query = query.where(DiagnosticoCIE10.capitulo == capitulo)
    if q:
        for term in q.split():
            query = query.where(or_(DiagnosticoCIE10.codigo_cie10.icontains(term, autoescape=True),
                DiagnosticoCIE10.descripcion.icontains(term, autoescape=True)))
    total, rows = await _paged(db, query.order_by(DiagnosticoCIE10.codigo_cie10), page, size)
    return {"items": [columns(row[0]) for row in rows], "total": total, "page": page, "page_size": size}


async def diagnostico_detalle(db, tid, diagnostico_id):
    d = await db.scalar(select(DiagnosticoCIE10).where(DiagnosticoCIE10.tenant_id == tid, DiagnosticoCIE10.id == diagnostico_id))
    if not d:
        raise HTTPException(404, detail="Diagnóstico no encontrado en este hospital")
    return columns(d)


async def catalogo_capitulos(db, tid):
    rows = (await db.scalars(select(DiagnosticoCIE10.capitulo).where(DiagnosticoCIE10.tenant_id == tid,
        DiagnosticoCIE10.is_active.is_(True), DiagnosticoCIE10.capitulo.is_not(None))
        .distinct().order_by(DiagnosticoCIE10.capitulo))).all()
    return list(rows)


# ─── Paquetes ────────────────────────────────────────────────────────────────

async def list_paquetes(db, tid, q, page=1, size=20):
    query = (select(Paquete, Especialidad.nombre)
        .outerjoin(Especialidad, Especialidad.id == Paquete.especialidad_id)
        .where(Paquete.tenant_id == tid, Paquete.is_active.is_(True)))
    if q:
        for term in q.split():
            query = query.where(or_(Paquete.nombre.icontains(term, autoescape=True),
                Paquete.codigo.icontains(term, autoescape=True)))
    total, rows = await _paged(db, query.order_by(Paquete.nombre), page, size)
    items = [dict(columns(p), especialidad_nombre=esp) for p, esp in rows]
    return {"items": items, "total": total, "page": page, "page_size": size}


async def paquete_detalle(db, tid, paquete_id):
    row = (await db.execute(select(Paquete, Especialidad.nombre)
        .outerjoin(Especialidad, Especialidad.id == Paquete.especialidad_id)
        .where(Paquete.tenant_id == tid, Paquete.id == paquete_id))).first()
    if not row:
        raise HTTPException(404, detail="Paquete no encontrado en este hospital")
    paquete, especialidad_nombre = row
    items = (await db.execute(select(PaqueteItem, Medicamento.nombre_comercial, Medicamento.dci, Medicamento.presentacion)
        .outerjoin(Medicamento, Medicamento.id == PaqueteItem.medicamento_id)
        .where(PaqueteItem.paquete_id == paquete.id))).all()
    return dict(columns(paquete), especialidad_nombre=especialidad_nombre,
        items=[dict(columns(i), medicamento_nombre=nombre, dci=dci, presentacion=pres) for i, nombre, dci, pres in items])
