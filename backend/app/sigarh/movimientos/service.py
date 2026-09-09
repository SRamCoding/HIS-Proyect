import uuid
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.sigarh.movimientos.models import CambioTurno, Papeleta
from app.sigarh.rrhh import service as rrhh_svc

# Nota: "Tramitar Licencia" y "Justificación y Vacaciones" operan sobre la tabla
# unificada sigarh_justificaciones (modelo RRHH). Se distinguen por `tipo`:
#   - licencia   -> Tramitar Licencia / Estado Licencia
#   - vacacion   -> Justificación y Vacaciones (solicitud de vacaciones)
#   - justificacion -> Justificación y Vacaciones (inasistencia) y RRHH


# ─── Licencias (tipo="licencia" en sigarh_justificaciones) ────────────────────

async def listar_licencias_unif(db: AsyncSession, tenant_id: uuid.UUID, estado: str | None = None) -> list[dict]:
    return await rrhh_svc.listar_justificaciones(db, tenant_id, estado=estado, tipo="licencia")


async def crear_licencia_unif(db: AsyncSession, tenant_id: uuid.UUID, data, usuario: str | None = None) -> dict:
    data.tipo = "licencia"
    return await rrhh_svc.crear_justificacion(db, tenant_id, data, usuario)


# ─── Justificación y Vacaciones (tipo in {justificacion, vacacion}) ───────────

async def listar_just_vac(db: AsyncSession, tenant_id: uuid.UUID, estado: str | None = None,
                          motivo_id: uuid.UUID | None = None) -> list[dict]:
    return await rrhh_svc.listar_justificaciones(
        db, tenant_id, estado=estado, motivo_id=motivo_id, tipo=["justificacion", "vacacion"]
    )


async def crear_just_vac(db: AsyncSession, tenant_id: uuid.UUID, data, usuario: str | None = None) -> dict:
    if data.tipo not in {"justificacion", "vacacion"}:
        data.tipo = "justificacion"
    return await rrhh_svc.crear_justificacion(db, tenant_id, data, usuario)


# ─── Helper genérico ──────────────────────────────────────────────────────────

async def _obtener(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(modelo).where(modelo.id == id, modelo.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def _eliminar(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await _obtener(db, modelo, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True


class ReglaNegocioError(Exception):
    pass


def _cols(obj) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


async def _emp_map(db: AsyncSession, tenant_id: uuid.UUID) -> dict:
    from app.sigarh.rrhh.models import Empleado
    return {e.id: e for e in (await db.execute(
        select(Empleado).where(Empleado.tenant_id == tenant_id)
    )).scalars().all()}


async def _empleado_activo(db: AsyncSession, tenant_id: uuid.UUID, empleado_id: uuid.UUID) -> bool:
    from app.sigarh.rrhh.models import Empleado
    e = await db.scalar(select(Empleado).where(Empleado.id == empleado_id, Empleado.tenant_id == tenant_id))
    return bool(e and e.is_active)


async def _marcar_asistencia(db: AsyncSession, tenant_id: uuid.UUID, empleado_id: uuid.UUID, fecha, observacion: str) -> None:
    """Crea o marca como 'justificado' la asistencia de un empleado en una fecha."""
    from app.sigarh.rrhh.models import RegistroAsistencia
    a = await db.scalar(select(RegistroAsistencia).where(
        RegistroAsistencia.tenant_id == tenant_id,
        RegistroAsistencia.empleado_id == empleado_id,
        RegistroAsistencia.fecha == fecha,
    ))
    if a:
        a.estado = "justificado"
        if not a.observacion:
            a.observacion = observacion
    else:
        db.add(RegistroAsistencia(
            tenant_id=tenant_id, empleado_id=empleado_id, fecha=fecha,
            estado="justificado", observacion=observacion,
        ))


# ─── Cambio de Turno ──────────────────────────────────────────────────────────

async def _serializar_cambios_turno(db, tenant_id, items: list) -> list[dict]:
    if not items:
        return []
    emps = await _emp_map(db, tenant_id)
    from app.sigarh.mantenimiento.models import Servicio
    servicios = dict((await db.execute(
        select(Servicio.id, Servicio.nombre).where(Servicio.tenant_id == tenant_id)
    )).all())
    out = []
    for c in items:
        s = emps.get(c.solicitante_id)
        a = emps.get(c.aceptante_id)
        out.append({
            **_cols(c),
            "solicitante_nombre": s.nombre_completo if s else None,
            "solicitante_dni": s.dni if s else None,
            "aceptante_nombre": a.nombre_completo if a else None,
            "aceptante_dni": a.dni if a else None,
            "servicio_nombre": servicios.get(c.servicio_id),
        })
    return out


async def listar_cambios_turno(db: AsyncSession, tenant_id: uuid.UUID, estado: str | None = None) -> list[dict]:
    q = select(CambioTurno).where(CambioTurno.tenant_id == tenant_id)
    if estado:
        q = q.where(CambioTurno.estado == estado)
    items = (await db.execute(q.order_by(CambioTurno.created_at.desc()))).scalars().all()
    return await _serializar_cambios_turno(db, tenant_id, items)


async def crear_cambio_turno(db: AsyncSession, tenant_id: uuid.UUID, data, usuario: str | None = None) -> dict:
    if not await _empleado_activo(db, tenant_id, data.solicitante_id):
        raise ReglaNegocioError("El solicitante no existe o no está activo")
    if not await _empleado_activo(db, tenant_id, data.aceptante_id):
        raise ReglaNegocioError("El aceptante no existe o no está activo")
    dup = await db.scalar(select(CambioTurno).where(
        CambioTurno.tenant_id == tenant_id,
        CambioTurno.solicitante_id == data.solicitante_id,
        CambioTurno.fecha_original == data.fecha_original,
        CambioTurno.estado.in_(["pendiente", "aprobado"]),
    ))
    if dup:
        raise ReglaNegocioError("Ya existe un cambio de turno pendiente o aprobado para ese solicitante y esa fecha")
    item = CambioTurno(tenant_id=tenant_id, registrado_por=usuario, **data.model_dump())
    db.add(item)
    await db.commit()
    return (await _serializar_cambios_turno(db, tenant_id, [item]))[0]


async def decidir_cambio_turno(db, id, tenant_id, aprobar: bool, revisor: str | None = None, motivo_rechazo: str | None = None) -> dict | None:
    item = await _obtener(db, CambioTurno, id, tenant_id)
    if not item:
        return None
    if item.estado != "pendiente":
        raise ReglaNegocioError(f"El cambio de turno ya fue {item.estado}")
    item.estado = "aprobado" if aprobar else "rechazado"
    item.revisado_por = revisor
    item.revisado_at = datetime.utcnow()
    item.motivo_rechazo = None if aprobar else motivo_rechazo
    await db.commit()
    if aprobar:
        emps = await _emp_map(db, tenant_id)
        s = emps.get(item.solicitante_id)
        a = emps.get(item.aceptante_id)
        await _marcar_asistencia(db, tenant_id, item.solicitante_id, item.fecha_original,
                                 f"Cambio de turno: cubierto por {a.nombre_completo if a else 'otro'}")
        if item.aceptante_id:
            await _marcar_asistencia(db, tenant_id, item.aceptante_id, item.fecha_reemplazo,
                                     f"Cambio de turno: cubierto por {s.nombre_completo if s else 'otro'}")
        await db.commit()
    return (await _serializar_cambios_turno(db, tenant_id, [await _obtener(db, CambioTurno, id, tenant_id)]))[0]


# ─── Papeletas ────────────────────────────────────────────────────────────────

async def _serializar_papeletas(db, tenant_id, items: list) -> list[dict]:
    if not items:
        return []
    emps = await _emp_map(db, tenant_id)
    out = []
    for p in items:
        e = emps.get(p.empleado_id)
        out.append({
            **_cols(p),
            "empleado_nombre": e.nombre_completo if e else None,
            "empleado_cargo": e.cargo_laboral if e else None,
        })
    return out


async def listar_papeletas(db: AsyncSession, tenant_id: uuid.UUID, estado: str | None = None, fecha: date | None = None) -> list[dict]:
    q = select(Papeleta).where(Papeleta.tenant_id == tenant_id)
    if estado:
        q = q.where(Papeleta.estado == estado)
    if fecha:
        q = q.where(Papeleta.fecha_tramite == fecha)
    items = (await db.execute(q.order_by(Papeleta.created_at.desc()))).scalars().all()
    return await _serializar_papeletas(db, tenant_id, items)


async def crear_papeleta(db: AsyncSession, tenant_id: uuid.UUID, data, usuario: str | None = None) -> dict:
    if not await _empleado_activo(db, tenant_id, data.empleado_id):
        raise ReglaNegocioError("El empleado no existe o no está activo")
    fecha_tramite = data.fecha_tramite or date.today()
    dup = await db.scalar(select(Papeleta).where(
        Papeleta.tenant_id == tenant_id,
        Papeleta.empleado_id == data.empleado_id,
        Papeleta.fecha_tramite == fecha_tramite,
        Papeleta.estado.in_(["pendiente", "aprobado"]),
    ))
    if dup:
        raise ReglaNegocioError("El empleado ya tiene una papeleta pendiente o aprobada para ese día")
    payload = data.model_dump()
    payload["fecha_tramite"] = fecha_tramite
    item = Papeleta(tenant_id=tenant_id, registrado_por=usuario, **payload)
    db.add(item)
    await db.commit()
    return (await _serializar_papeletas(db, tenant_id, [item]))[0]


async def actualizar_papeleta(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data: dict) -> dict | None:
    item = await _obtener(db, Papeleta, id, tenant_id)
    if not item:
        return None
    for f, v in data.items():
        if hasattr(item, f) and f not in {"id", "tenant_id", "estado", "hora_salida", "hora_retorno", "revisado_por", "revisado_at"}:
            setattr(item, f, v)
    await db.commit()
    return (await _serializar_papeletas(db, tenant_id, [item]))[0]


async def decidir_papeleta(db, id, tenant_id, aprobar: bool, revisor: str | None = None, motivo_rechazo: str | None = None) -> dict | None:
    item = await _obtener(db, Papeleta, id, tenant_id)
    if not item:
        return None
    if item.estado != "pendiente":
        raise ReglaNegocioError(f"La papeleta ya fue {item.estado}")
    item.estado = "aprobado" if aprobar else "rechazado"
    item.revisado_por = revisor
    item.revisado_at = datetime.utcnow()
    if aprobar:
        item.hora_salida = datetime.now().strftime("%H:%M")
    else:
        item.motivo_rechazo = motivo_rechazo
    await db.commit()
    return (await _serializar_papeletas(db, tenant_id, [item]))[0]


async def registrar_retorno_papeleta(db, id, tenant_id) -> dict | None:
    item = await _obtener(db, Papeleta, id, tenant_id)
    if not item:
        return None
    if item.estado != "aprobado":
        raise ReglaNegocioError("Solo se puede registrar el retorno de una papeleta aprobada")
    if item.hora_retorno:
        raise ReglaNegocioError("El retorno ya fue registrado")
    item.hora_retorno = datetime.now().strftime("%H:%M")
    await db.commit()
    return (await _serializar_papeletas(db, tenant_id, [item]))[0]