import uuid
from datetime import date, datetime
from fastapi import HTTPException
from sqlalchemy import select, func, or_
from app.admin.auditoria.models import AuditLog


def columns(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def _query(tid):
    return select(AuditLog).where(AuditLog.tenant_id == tid)


def _filtrar(q, f):
    if f.get("modelo"):
        q = q.where(AuditLog.model == f["modelo"])
    if f.get("accion"):
        q = q.where(AuditLog.action.icontains(f["accion"], autoescape=True))
    if f.get("usuario"):
        q = q.where(AuditLog.user_name.icontains(f["usuario"], autoescape=True))
    if f.get("desde"):
        q = q.where(AuditLog.created_at >= datetime.combine(f["desde"], datetime.min.time()))
    if f.get("hasta"):
        q = q.where(AuditLog.created_at <= datetime.combine(f["hasta"], datetime.max.time()))
    if f.get("q"):
        for term in f["q"].split():
            q = q.where(or_(AuditLog.model_id.icontains(term, autoescape=True),
                AuditLog.description.icontains(term, autoescape=True)))
    return q


async def list_audit(db, tid, f, page=1, size=20):
    q = _filtrar(_query(tid), f)
    total = await db.scalar(select(func.count()).select_from(q.order_by(None).subquery()))
    rows = (await db.scalars(q.order_by(AuditLog.created_at.desc()).offset((page-1)*size).limit(size))).all()
    return {"items": [columns(r) for r in rows], "total": total, "page": page, "page_size": size}


async def audit_detail(db, tid, audit_id):
    obj = await db.scalar(select(AuditLog).where(AuditLog.id == audit_id, AuditLog.tenant_id == tid))
    if obj is None:
        raise HTTPException(404, detail="Registro de auditoría no encontrado en este hospital")
    return columns(obj)


async def catalogo_modelos(db, tid):
    rows = (await db.scalars(select(AuditLog.model).where(AuditLog.tenant_id == tid,
        AuditLog.model.is_not(None)).distinct().order_by(AuditLog.model))).all()
    return list(rows)


async def _agrupar(db, tid, f, columna, limite=None, orden_por_fecha=False):
    q = (_filtrar(_query(tid), f).with_only_columns(columna, func.count())
        .group_by(columna).order_by(func.count().desc()))
    if limite:
        q = q.limit(limite)
    return (await db.execute(q)).all()


async def resumen(db, tid, desde: date | None, hasta: date | None):
    """Vista agregada para 'Auditoria General': mismo AuditLog de 'Auditoria',
    contado por modelo, acción, usuario y día -- no es un dato distinto, es
    el mismo log visto en agregado en vez de fila por fila."""
    f = {"desde": desde, "hasta": hasta}
    por_modelo = await _agrupar(db, tid, f, AuditLog.model)
    por_accion = await _agrupar(db, tid, f, AuditLog.action)
    por_usuario = await _agrupar(db, tid, f, AuditLog.user_name, limite=15)
    por_dia = (await db.execute(_filtrar(_query(tid), f)
        .with_only_columns(func.date(AuditLog.created_at), func.count())
        .group_by(func.date(AuditLog.created_at)).order_by(func.date(AuditLog.created_at).desc()).limit(30))).all()
    total = await db.scalar(select(func.count()).select_from(_filtrar(_query(tid), f).order_by(None).subquery()))
    return {
        "total": total or 0,
        "por_modelo": [{"modelo": k or "—", "total": v} for k, v in por_modelo],
        "por_accion": [{"accion": k or "—", "total": v} for k, v in por_accion],
        "por_usuario": [{"usuario": k or "—", "total": v} for k, v in por_usuario],
        "por_dia": [{"fecha": d, "total": c} for d, c in por_dia],
    }


async def export_csv(db, tid, f):
    import csv
    from io import StringIO
    result = await list_audit(db, tid, f, 1, 10001)
    if result["total"] > 10000:
        raise HTTPException(422, detail="Acote los filtros: el reporte admite hasta 10000 registros")
    keys = ["created_at", "user_name", "model", "model_id", "action", "description"]
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(keys)
    def safe(v):
        value = str(v) if v is not None else ""
        return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else value
    for row in result["items"]:
        writer.writerow([safe(row.get(k)) for k in keys])
    return ("﻿" + stream.getvalue()).encode("utf-8")
