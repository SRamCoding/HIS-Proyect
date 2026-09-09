"""Lógica compartida de Roles de Turno: armado del detalle + CRUD + builder anidado.

Importado por los routers de creacion_roles, roles_pendientes y roles_aprobados.
"""
import uuid
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.sigarh.creacion_roles.models import (
    Rol, RolEmpleado, RolActividad, RolTurno, SolicitudModificacionRol, MODALIDADES,
)
from app.sigarh.mantenimiento.models import Departamento, Servicio, Actividad, HorarioGuardia
from app.sigarh.rrhh.models import Empleado

EDITABLE = ("draft", "rejected")


class ReglaNegocioError(Exception):
    """Operación bloqueada por regla de negocio -> HTTP 409."""


# ─── Carga ───────────────────────────────────────────────────────────────────

async def _validar_ambito(db, tenant_id, departamento_id, servicio_id) -> None:
    departamento = await db.scalar(select(Departamento).where(
        Departamento.id == departamento_id,
        Departamento.tenant_id == tenant_id,
        Departamento.is_active.is_(True),
    ))
    if not departamento:
        raise ReglaNegocioError("El departamento no existe o está inactivo.")
    servicio = await db.scalar(select(Servicio).where(
        Servicio.id == servicio_id,
        Servicio.tenant_id == tenant_id,
        Servicio.is_active.is_(True),
    ))
    if not servicio:
        raise ReglaNegocioError("El servicio no existe o está inactivo.")
    if servicio.departamento_id != departamento_id:
        raise ReglaNegocioError("El servicio seleccionado no pertenece al departamento.")


def _rol_stmt():
    return select(Rol).options(
        selectinload(Rol.empleados)
        .selectinload(RolEmpleado.actividades)
        .selectinload(RolActividad.turnos)
    )


async def obtener_rol_orm(db: AsyncSession, rol_id: uuid.UUID, tenant_id: uuid.UUID) -> Rol | None:
    res = await db.execute(_rol_stmt().where(Rol.id == rol_id, Rol.tenant_id == tenant_id))
    return res.scalar_one_or_none()


async def _catalogos(db: AsyncSession, tenant_id: uuid.UUID) -> dict:
    deps = dict((await db.execute(
        select(Departamento.id, Departamento.nombre).where(Departamento.tenant_id == tenant_id)
    )).all())
    servs = dict((await db.execute(
        select(Servicio.id, Servicio.nombre).where(Servicio.tenant_id == tenant_id)
    )).all())
    acts = {
        a.id: a for a in (await db.execute(
            select(Actividad).where(Actividad.tenant_id == tenant_id)
        )).scalars().all()
    }
    hors = {
        h.id: h for h in (await db.execute(
            select(HorarioGuardia).where(HorarioGuardia.tenant_id == tenant_id)
        )).scalars().all()
    }
    emps = {
        e.id: e for e in (await db.execute(
            select(Empleado).where(Empleado.tenant_id == tenant_id)
        )).scalars().all()
    }
    return {"deps": deps, "servs": servs, "acts": acts, "hors": hors, "emps": emps}


def _serializa_rol(rol: Rol, cat: dict, detalle: bool) -> dict:
    n_act = sum(len(re.actividades) for re in rol.empleados)
    n_turnos = sum(len(a.turnos) for re in rol.empleados for a in re.actividades)
    completa = bool(rol.empleados) and all(
        re.actividades and all(a.turnos for a in re.actividades) for re in rol.empleados
    )
    base = {
        "id": rol.id,
        "categoria_personal": rol.categoria_personal,
        "tipo_rol": rol.tipo_rol,
        "departamento_id": rol.departamento_id,
        "departamento_nombre": cat["deps"].get(rol.departamento_id),
        "servicio_id": rol.servicio_id,
        "servicio_nombre": cat["servs"].get(rol.servicio_id),
        "mes": rol.mes,
        "anio": rol.anio,
        "status": rol.status,
        "total_empleados": len(rol.empleados),
        "total_actividades": n_act,
        "total_turnos": n_turnos,
        "programacion_completa": completa,
        "created_by": rol.created_by,
        "submitted_at": rol.submitted_at,
        "reviewed_by": rol.reviewed_by,
        "reviewed_at": rol.reviewed_at,
        "rejection_reason": rol.rejection_reason,
        "created_at": rol.created_at,
    }
    if not detalle:
        return base

    empleados = []
    for re_ in rol.empleados:
        emp = cat["emps"].get(re_.empleado_id)
        actividades = []
        for a in re_.actividades:
            act = cat["acts"].get(a.actividad_id)
            turnos = []
            for t in a.turnos:
                hor = cat["hors"].get(t.horario_guardia_id)
                turnos.append({
                    "id": t.id,
                    "horario_guardia_id": t.horario_guardia_id,
                    "horario_nombre": getattr(hor, "nombre", None),
                    "hora_inicio": getattr(hor, "hora_inicio", None),
                    "hora_fin": getattr(hor, "hora_fin", None),
                    "dias_semana": t.dias_semana or [],
                })
            actividades.append({
                "id": a.id,
                "actividad_id": a.actividad_id,
                "actividad_nombre": getattr(act, "nombre", None),
                "requiere_consultorio": bool(getattr(act, "requiere_consultorio", False)),
                "turnos": turnos,
            })
        empleados.append({
            "id": re_.id,
            "empleado_id": re_.empleado_id,
            "empleado_nombre": getattr(emp, "nombre_completo", None),
            "dni": getattr(emp, "dni", None),
            "actividades": actividades,
        })
    base["empleados"] = empleados
    return base


async def serializar(db: AsyncSession, tenant_id: uuid.UUID, roles: list[Rol], detalle: bool = False) -> list[dict]:
    cat = await _catalogos(db, tenant_id)
    return [_serializa_rol(r, cat, detalle) for r in roles]


async def serializar_uno(db: AsyncSession, tenant_id: uuid.UUID, rol: Rol, detalle: bool = True) -> dict:
    cat = await _catalogos(db, tenant_id)
    return _serializa_rol(rol, cat, detalle)


# ─── Listado genérico ────────────────────────────────────────────────────────

async def listar_roles(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    *,
    status_in: list[str] | None = None,
    categoria: str | None = None,
    tipo: str | None = None,
    anio: int | None = None,
    mes: int | None = None,
) -> list[dict]:
    stmt = _rol_stmt().where(Rol.tenant_id == tenant_id)
    if status_in:
        stmt = stmt.where(Rol.status.in_(status_in))
    if categoria:
        stmt = stmt.where(Rol.categoria_personal == categoria)
    if tipo:
        stmt = stmt.where(Rol.tipo_rol == tipo)
    if anio:
        stmt = stmt.where(Rol.anio == anio)
    if mes:
        stmt = stmt.where(Rol.mes == mes)
    stmt = stmt.order_by(Rol.anio.desc(), Rol.mes.desc(), Rol.created_at.desc())
    roles = (await db.execute(stmt)).scalars().unique().all()
    return await serializar(db, tenant_id, roles, detalle=False)


# ─── CRUD cabecera ───────────────────────────────────────────────────────────

async def crear_rol(db: AsyncSession, tenant_id: uuid.UUID, data, usuario: str | None) -> dict:
    await _validar_ambito(db, tenant_id, data.departamento_id, data.servicio_id)
    # Regla de la variante médica ordinaria: no duplicar dep+serv+mes+anio
    if data.categoria_personal == "medicos" and data.tipo_rol == "ordinario":
        dup = await db.scalar(select(func.count()).select_from(Rol).where(
            Rol.tenant_id == tenant_id,
            Rol.categoria_personal == "medicos", Rol.tipo_rol == "ordinario",
            Rol.departamento_id == data.departamento_id, Rol.servicio_id == data.servicio_id,
            Rol.mes == data.mes, Rol.anio == data.anio,
            Rol.status != "rejected",
        ))
        if dup:
            raise ReglaNegocioError("Ya existe un rol médico ordinario para ese departamento, servicio y período.")

    rol = Rol(
        tenant_id=tenant_id,
        categoria_personal=data.categoria_personal,
        tipo_rol=data.tipo_rol,
        departamento_id=data.departamento_id,
        servicio_id=data.servicio_id,
        mes=data.mes,
        anio=data.anio,
        status="draft",
        created_by=usuario,
    )
    db.add(rol)
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, rol.id, tenant_id))


async def actualizar_rol(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID, data) -> dict | None:
    rol = await obtener_rol_orm(db, rol_id, tenant_id)
    if not rol:
        return None
    if rol.status not in EDITABLE:
        raise ReglaNegocioError("Solo se pueden editar roles en borrador o rechazados.")
    cambios = data.model_dump(exclude_unset=True)
    departamento_id = cambios.get("departamento_id", rol.departamento_id)
    servicio_id = cambios.get("servicio_id", rol.servicio_id)
    if departamento_id is None or servicio_id is None:
        raise ReglaNegocioError("El departamento y el servicio son obligatorios.")
    await _validar_ambito(db, tenant_id, departamento_id, servicio_id)
    for f, v in cambios.items():
        setattr(rol, f, v)
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, rol_id, tenant_id))


async def eliminar_rol(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID) -> bool:
    rol = await obtener_rol_orm(db, rol_id, tenant_id)
    if not rol:
        return False
    if rol.status not in EDITABLE:
        raise ReglaNegocioError("Solo se pueden eliminar roles en borrador o rechazados.")
    await db.delete(rol)
    await db.commit()
    return True


async def enviar_rol(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID) -> dict | None:
    rol = await obtener_rol_orm(db, rol_id, tenant_id)
    if not rol:
        return None
    if rol.status not in EDITABLE:
        raise ReglaNegocioError("El rol ya fue enviado.")
    if not rol.empleados or any(not re.actividades or any(not a.turnos for a in re.actividades) for re in rol.empleados):
        raise ReglaNegocioError("La programación está incompleta: cada empleado debe tener actividades y cada actividad al menos un turno.")
    rol.status = "pending"
    rol.submitted_at = datetime.utcnow()
    rol.rejection_reason = None
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, rol_id, tenant_id))


# ─── Builder anidado ─────────────────────────────────────────────────────────

async def _rol_editable(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID) -> Rol:
    rol = await db.scalar(select(Rol).where(Rol.id == rol_id, Rol.tenant_id == tenant_id))
    if not rol:
        raise ReglaNegocioError("Rol no encontrado.")
    if rol.status not in EDITABLE:
        raise ReglaNegocioError("Solo se puede modificar la programación de roles en borrador o rechazados.")
    return rol


async def _rol_empleado(db: AsyncSession, tenant_id: uuid.UUID, rol_empleado_id: uuid.UUID) -> RolEmpleado:
    res = await db.execute(
        select(RolEmpleado).join(Rol, Rol.id == RolEmpleado.rol_id)
        .where(RolEmpleado.id == rol_empleado_id, Rol.tenant_id == tenant_id)
    )
    re_ = res.scalar_one_or_none()
    if not re_:
        raise ReglaNegocioError("Personal del rol no encontrado.")
    return re_


async def _rol_actividad(db: AsyncSession, tenant_id: uuid.UUID, rol_actividad_id: uuid.UUID) -> RolActividad:
    res = await db.execute(
        select(RolActividad)
        .join(RolEmpleado, RolEmpleado.id == RolActividad.rol_empleado_id)
        .join(Rol, Rol.id == RolEmpleado.rol_id)
        .where(RolActividad.id == rol_actividad_id, Rol.tenant_id == tenant_id)
    )
    ra = res.scalar_one_or_none()
    if not ra:
        raise ReglaNegocioError("Actividad del rol no encontrada.")
    return ra


async def agregar_personal(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID, empleado_ids: list[uuid.UUID]) -> dict:
    await _rol_editable(db, tenant_id, rol_id)
    existentes = set((await db.execute(
        select(RolEmpleado.empleado_id).where(RolEmpleado.rol_id == rol_id)
    )).scalars().all())
    validos = set((await db.execute(
        select(Empleado.id).where(Empleado.tenant_id == tenant_id, Empleado.id.in_(empleado_ids))
    )).scalars().all())
    for eid in empleado_ids:
        if eid in validos and eid not in existentes:
            db.add(RolEmpleado(rol_id=rol_id, empleado_id=eid))
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, rol_id, tenant_id))


async def quitar_personal(db: AsyncSession, tenant_id: uuid.UUID, rol_empleado_id: uuid.UUID) -> dict:
    re_ = await _rol_empleado(db, tenant_id, rol_empleado_id)
    await _rol_editable(db, tenant_id, re_.rol_id)
    rol_id = re_.rol_id
    await db.delete(re_)
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, rol_id, tenant_id))


async def agregar_actividades(db: AsyncSession, tenant_id: uuid.UUID, rol_empleado_id: uuid.UUID, actividad_ids: list[uuid.UUID]) -> dict:
    re_ = await _rol_empleado(db, tenant_id, rol_empleado_id)
    await _rol_editable(db, tenant_id, re_.rol_id)
    existentes = set((await db.execute(
        select(RolActividad.actividad_id).where(RolActividad.rol_empleado_id == rol_empleado_id)
    )).scalars().all())
    validos = set((await db.execute(
        select(Actividad.id).where(Actividad.tenant_id == tenant_id, Actividad.id.in_(actividad_ids))
    )).scalars().all())
    for aid in actividad_ids:
        if aid in validos and aid not in existentes:
            db.add(RolActividad(rol_empleado_id=rol_empleado_id, actividad_id=aid))
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, re_.rol_id, tenant_id))


async def quitar_actividad(db: AsyncSession, tenant_id: uuid.UUID, rol_actividad_id: uuid.UUID) -> dict:
    ra = await _rol_actividad(db, tenant_id, rol_actividad_id)
    re_ = await _rol_empleado(db, tenant_id, ra.rol_empleado_id)
    await _rol_editable(db, tenant_id, re_.rol_id)
    await db.delete(ra)
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, re_.rol_id, tenant_id))


async def agregar_turno(db: AsyncSession, tenant_id: uuid.UUID, rol_actividad_id: uuid.UUID, data) -> dict:
    ra = await _rol_actividad(db, tenant_id, rol_actividad_id)
    re_ = await _rol_empleado(db, tenant_id, ra.rol_empleado_id)
    await _rol_editable(db, tenant_id, re_.rol_id)
    if data.horario_guardia_id:
        ok = await db.scalar(select(func.count()).select_from(HorarioGuardia).where(
            HorarioGuardia.id == data.horario_guardia_id, HorarioGuardia.tenant_id == tenant_id
        ))
        if not ok:
            raise ReglaNegocioError("El horario de guardia no existe.")
    db.add(RolTurno(
        rol_actividad_id=rol_actividad_id,
        horario_guardia_id=data.horario_guardia_id,
        dias_semana=data.dias_semana,
    ))
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, re_.rol_id, tenant_id))


async def quitar_turno(db: AsyncSession, tenant_id: uuid.UUID, rol_turno_id: uuid.UUID) -> dict:
    res = await db.execute(
        select(RolTurno)
        .join(RolActividad, RolActividad.id == RolTurno.rol_actividad_id)
        .join(RolEmpleado, RolEmpleado.id == RolActividad.rol_empleado_id)
        .join(Rol, Rol.id == RolEmpleado.rol_id)
        .where(RolTurno.id == rol_turno_id, Rol.tenant_id == tenant_id)
    )
    t = res.scalar_one_or_none()
    if not t:
        raise ReglaNegocioError("Turno no encontrado.")
    ra = await _rol_actividad(db, tenant_id, t.rol_actividad_id)
    re_ = await _rol_empleado(db, tenant_id, ra.rol_empleado_id)
    await _rol_editable(db, tenant_id, re_.rol_id)
    await db.delete(t)
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, re_.rol_id, tenant_id))
