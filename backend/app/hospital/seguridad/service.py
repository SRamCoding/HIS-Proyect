from fastapi import HTTPException
from sqlalchemy import select, func, or_
from app.auth.models import User, PerfilHospital
from app.sigarh.rrhh.models import Empleado
from app.sigarh.mantenimiento.models import PerfilUsuario, RolSistema
import json


def columns(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


async def _paged(db, q, page, size):
    total = await db.scalar(select(func.count()).select_from(q.order_by(None).subquery()))
    rows = (await db.execute(q.offset((page-1)*size).limit(size))).all()
    return total, rows


def _query(tid):
    # User.tenant_id no se llena para cuentas panel='app': SIGARH > Mantenimiento
    # > Usuarios las crea directo en la BD física del hospital sin setearlo, porque
    # ahí es redundante (el aislamiento ya lo da la BD, no esa columna). Filtrar
    # por tenant_id aquí dejaría la lista siempre vacía -- confirmado contra las
    # cuentas reales de Reque. `tid` se mantiene en la firma por consistencia con
    # el resto del módulo, aunque esta consulta no lo necesite.
    return (select(User, Empleado, PerfilUsuario, RolSistema, PerfilHospital)
        .outerjoin(Empleado, Empleado.id == User.empleado_id)
        .outerjoin(PerfilUsuario, PerfilUsuario.id == User.perfil_usuario_id)
        .outerjoin(RolSistema, RolSistema.id == PerfilUsuario.rol_sistema_id)
        .outerjoin(PerfilHospital, PerfilHospital.id == User.perfil_hospital_id)
        .where(User.panel == "app"))


def _out(row):
    u, empleado, perfil, rol, perfil_legacy = row
    perfil_actual = perfil or perfil_legacy
    if perfil:
        try:
            modulos = json.loads(perfil.modulos_acceso or "[]")
        except (TypeError, ValueError):
            modulos = []
        if not modulos and rol:
            try:
                modulos = json.loads(rol.modulos_permitidos or "[]")
            except (TypeError, ValueError):
                modulos = []
    else:
        modulos = (perfil_legacy.modulos if perfil_legacy else []) or []
    return {
        "id": u.id, "name": u.name, "email": u.email, "username": u.username,
        "role": u.role, "is_active": u.is_active, "created_at": u.created_at,
        "empleado_id": empleado.id if empleado else None,
        "empleado_nombre": empleado.nombre_completo if empleado else None,
        "empleado_dni": empleado.dni if empleado else None,
        "perfil_id": perfil_actual.id if perfil_actual else None,
        "perfil_nombre": perfil_actual.nombre if perfil_actual else None,
        "perfil_activo": perfil_actual.is_active if perfil_actual else None,
        "modulos": modulos,
    }


async def list_empleados_acceso(db, tid, q, role, estado, page=1, size=20):
    query = _query(tid)
    if role:
        query = query.where(User.role == role)
    if estado == "activo":
        query = query.where(User.is_active.is_(True))
    elif estado == "inactivo":
        query = query.where(User.is_active.is_(False))
    if q:
        for term in q.split():
            query = query.where(or_(User.name.icontains(term, autoescape=True),
                User.email.icontains(term, autoescape=True),
                Empleado.dni.icontains(term, autoescape=True)))
    total, rows = await _paged(db, query.order_by(User.name), page, size)
    return {"items": [_out(r) for r in rows], "total": total, "page": page, "page_size": size}


async def empleado_acceso_detalle(db, tid, user_id):
    row = (await db.execute(_query(tid).where(User.id == user_id))).first()
    if not row:
        raise HTTPException(404, detail="Cuenta no encontrada en este hospital")
    u, empleado, perfil, rol, perfil_legacy = row
    detalle = _out(row)
    if empleado:
        detalle["empleado_profesion_id"] = str(empleado.profesion_id) if empleado.profesion_id else None
        detalle["empleado_grupo_ocupacional_id"] = str(empleado.grupo_ocupacional_id) if empleado.grupo_ocupacional_id else None
        detalle["empleado_activo"] = empleado.is_active
    return detalle


async def catalogo_roles(db, tid):
    # Mismo motivo que en _query(): sin filtro por tenant_id, aislado por BD física.
    rows = (await db.scalars(select(User.role).where(User.panel == "app")
        .distinct().order_by(User.role))).all()
    return list(rows)


async def resumen(db, tid):
    total = await db.scalar(select(func.count()).select_from(_query(tid).order_by(None).subquery()))
    activos = await db.scalar(select(func.count()).select_from(
        _query(tid).where(User.is_active.is_(True)).order_by(None).subquery()))
    sin_perfil = await db.scalar(select(func.count()).select_from(
        _query(tid).where(User.perfil_usuario_id.is_(None), User.perfil_hospital_id.is_(None)).order_by(None).subquery()))
    sin_empleado = await db.scalar(select(func.count()).select_from(
        _query(tid).where(User.empleado_id.is_(None)).order_by(None).subquery()))
    por_rol = (await db.execute(_query(tid).with_only_columns(User.role, func.count())
        .group_by(User.role).order_by(func.count().desc()))).all()
    return {
        "total": total or 0, "activos": activos or 0, "inactivos": (total or 0) - (activos or 0),
        "sin_perfil_hospitalario": sin_perfil or 0, "sin_empleado_vinculado": sin_empleado or 0,
        "por_rol": [{"role": r, "total": c} for r, c in por_rol],
    }
