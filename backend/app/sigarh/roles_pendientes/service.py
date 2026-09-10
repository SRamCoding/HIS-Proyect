"""Roles Pendientes: revisión (aprobar / rechazar) y bandeja de Solicitudes de Modificación."""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.sigarh.creacion_roles.models import (
    Rol, RolEmpleado, RolActividad, RolTurno, SolicitudModificacionRol,
)
from app.sigarh.creacion_roles.service import (
    ReglaNegocioError, PermisoError, obtener_rol_orm, serializar_uno,
    diagnosticar_rol, errores_bloqueantes, _empleados_en_otro_rol_ordinario,
    puede_aprobar_roles,
)
from app.sigarh.mantenimiento.models import Servicio, Actividad, HorarioGuardia
from app.sigarh.rrhh.models import Empleado
from app.hospital.consulta_externa.service import sincronizar_programacion_sigarh

MESES = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


# ─── Revisión del rol ────────────────────────────────────────────────────────

async def aprobar_rol(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID, current_user: dict) -> dict | None:
    rol = await obtener_rol_orm(db, rol_id, tenant_id)
    if not rol:
        return None
    if not await puede_aprobar_roles(db, tenant_id, current_user, rol.servicio_id):
        raise PermisoError("No tiene permiso para aprobar roles de turno de este servicio.")
    revisor = current_user.get("name") or current_user.get("email")
    if rol.status != "pending":
        raise ReglaNegocioError("Solo se pueden aprobar roles en estado pendiente.")
    if not rol.created_by_id:
        raise ReglaNegocioError("El rol antiguo requiere identificar a su elaborador antes de aprobarse.")
    if str(rol.created_by_id) == str(current_user.get("sub")):
        raise ReglaNegocioError("Quien elaboró el rol no puede aprobarlo; debe revisarlo otra persona.")
    errores = errores_bloqueantes(await diagnosticar_rol(db, tenant_id, rol))
    if errores:
        raise ReglaNegocioError("No se puede aprobar el rol: " + " · ".join(errores[:8]))
    rol.status = "approved"
    rol.reviewed_by = revisor
    rol.reviewed_at = datetime.utcnow()
    rol.rejection_reason = None
    await db.commit()
    await sincronizar_programacion_sigarh(db, tenant_id, rol.mes, rol.anio)
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, rol_id, tenant_id))


async def rechazar_rol(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID, motivo: str, current_user: dict) -> dict | None:
    rol = await obtener_rol_orm(db, rol_id, tenant_id)
    if not rol:
        return None
    if not await puede_aprobar_roles(db, tenant_id, current_user, rol.servicio_id):
        raise PermisoError("No tiene permiso para revisar roles de turno de este servicio.")
    if rol.status != "pending":
        raise ReglaNegocioError("Solo se pueden rechazar roles en estado pendiente.")
    rol.status = "rejected"
    rol.rejection_reason = motivo
    rol.reviewed_by = current_user.get("name") or current_user.get("email")
    rol.reviewed_at = datetime.utcnow()
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, rol_id, tenant_id))


# ─── Solicitudes de Modificación ─────────────────────────────────────────────

async def _serializa_solicitud(db: AsyncSession, tenant_id: uuid.UUID, sol: SolicitudModificacionRol) -> dict:
    rol = await db.scalar(select(Rol).where(Rol.id == sol.rol_id))
    servicio_nombre = None
    if rol and rol.servicio_id:
        servicio_nombre = await db.scalar(select(Servicio.nombre).where(Servicio.id == rol.servicio_id))
    empleado_nombre = None
    if sol.empleado_id:
        emp = await db.scalar(select(Empleado).where(Empleado.id == sol.empleado_id))
        empleado_nombre = emp.nombre_completo if emp else None
    return {
        "id": sol.id,
        "tenant_id": sol.tenant_id,
        "rol_id": sol.rol_id,
        "role_type": f"{rol.categoria_personal}/{rol.tipo_rol}" if rol else None,
        "rol_periodo": f"{MESES[rol.mes]} {rol.anio}" if rol else None,
        "rol_servicio_nombre": servicio_nombre,
        "empleado_id": sol.empleado_id,
        "empleado_nombre": empleado_nombre,
        "motivo": sol.motivo,
        "schedule_data": sol.schedule_data or {},
        "status": sol.status,
        "requested_by": sol.requested_by,
        "reviewed_by": sol.reviewed_by,
        "reviewed_at": sol.reviewed_at,
        "created_at": sol.created_at,
    }


async def listar_solicitudes(db: AsyncSession, tenant_id: uuid.UUID, status: str | None = None) -> list[dict]:
    stmt = select(SolicitudModificacionRol).where(SolicitudModificacionRol.tenant_id == tenant_id)
    if status:
        stmt = stmt.where(SolicitudModificacionRol.status == status)
    stmt = stmt.order_by(SolicitudModificacionRol.created_at.desc())
    sols = (await db.execute(stmt)).scalars().all()
    return [await _serializa_solicitud(db, tenant_id, s) for s in sols]


async def obtener_solicitud(db: AsyncSession, tenant_id: uuid.UUID, sol_id: uuid.UUID) -> dict | None:
    sol = await db.scalar(select(SolicitudModificacionRol).where(
        SolicitudModificacionRol.id == sol_id, SolicitudModificacionRol.tenant_id == tenant_id
    ))
    if not sol:
        return None
    return await _serializa_solicitud(db, tenant_id, sol)


async def _sol_orm(db: AsyncSession, tenant_id: uuid.UUID, sol_id: uuid.UUID) -> SolicitudModificacionRol | None:
    return await db.scalar(select(SolicitudModificacionRol).where(
        SolicitudModificacionRol.id == sol_id, SolicitudModificacionRol.tenant_id == tenant_id
    ))


async def aprobar_solicitud(db: AsyncSession, tenant_id: uuid.UUID, sol_id: uuid.UUID, current_user: dict) -> dict | None:
    sol = await _sol_orm(db, tenant_id, sol_id)
    if not sol:
        return None
    if sol.status != "pendiente":
        raise ReglaNegocioError("La solicitud ya fue revisada.")
    rol_previo = await db.scalar(select(Rol).where(Rol.id == sol.rol_id, Rol.tenant_id == tenant_id))
    if not await puede_aprobar_roles(db, tenant_id, current_user, rol_previo.servicio_id if rol_previo else None):
        raise PermisoError("No tiene permiso para aprobar modificaciones de roles de este servicio.")
    revisor = current_user.get("name") or current_user.get("email")
    if revisor and sol.requested_by and revisor == sol.requested_by:
        raise ReglaNegocioError("Quien solicitó la modificación no puede aprobarla; debe revisarla otra persona.")
    rol = rol_previo
    if not rol or rol.status != "approved":
        raise ReglaNegocioError("El rol asociado ya no está aprobado.")
    if not sol.empleado_id:
        raise ReglaNegocioError("La solicitud no indica un empleado.")
    if await _empleados_en_otro_rol_ordinario(db, tenant_id, rol, [sol.empleado_id]):
        raise ReglaNegocioError("El empleado ya pertenece a otro rol ordinario de este servicio y período.")

    # Incorporar empleado + su programación propuesta, de forma atómica.
    re_ = await db.scalar(select(RolEmpleado).where(
        RolEmpleado.rol_id == rol.id, RolEmpleado.empleado_id == sol.empleado_id
    ))
    if not re_:
        re_ = RolEmpleado(rol_id=rol.id, empleado_id=sol.empleado_id)
        db.add(re_)
        await db.flush()

    validas_act = set((await db.execute(
        select(Actividad.id).where(Actividad.tenant_id == tenant_id)
    )).scalars().all())
    validos_hor = set((await db.execute(
        select(HorarioGuardia.id).where(HorarioGuardia.tenant_id == tenant_id)
    )).scalars().all())

    for act in (sol.schedule_data or {}).get("actividades", []):
        try:
            act_id = uuid.UUID(str(act.get("actividad_id")))
        except (ValueError, TypeError):
            continue
        if act_id not in validas_act:
            continue
        ra = RolActividad(rol_empleado_id=re_.id, actividad_id=act_id)
        db.add(ra)
        await db.flush()
        for tno in act.get("turnos", []):
            hg = tno.get("horario_guardia_id")
            try:
                hg_id = uuid.UUID(str(hg)) if hg else None
            except (ValueError, TypeError):
                hg_id = None
            if hg_id and hg_id not in validos_hor:
                hg_id = None
            dias = [d for d in (tno.get("dias_semana") or []) if isinstance(d, int) and 0 <= d <= 6]
            db.add(RolTurno(rol_actividad_id=ra.id, horario_guardia_id=hg_id, dias_semana=sorted(set(dias))))

    # Mismo diagnóstico que se exige para enviar/aprobar el rol original: la
    # modificación no puede introducir turnos que no generarían cupos válidos.
    await db.flush()
    rol_actualizado = await obtener_rol_orm(db, rol.id, tenant_id)
    errores = errores_bloqueantes(await diagnosticar_rol(db, tenant_id, rol_actualizado))
    if errores:
        await db.rollback()
        raise ReglaNegocioError("No se puede aprobar la modificación: " + " · ".join(errores[:8]))

    sol.status = "aprobado"
    sol.reviewed_by = revisor
    sol.reviewed_at = datetime.utcnow()
    await db.commit()
    await sincronizar_programacion_sigarh(db, tenant_id, rol.mes, rol.anio)
    return await _serializa_solicitud(db, tenant_id, await _sol_orm(db, tenant_id, sol_id))


async def rechazar_solicitud(db: AsyncSession, tenant_id: uuid.UUID, sol_id: uuid.UUID, motivo: str, current_user: dict) -> dict | None:
    sol = await _sol_orm(db, tenant_id, sol_id)
    if not sol:
        return None
    if sol.status != "pendiente":
        raise ReglaNegocioError("La solicitud ya fue revisada.")
    rol = await db.scalar(select(Rol).where(Rol.id == sol.rol_id, Rol.tenant_id == tenant_id))
    if not await puede_aprobar_roles(db, tenant_id, current_user, rol.servicio_id if rol else None):
        raise PermisoError("No tiene permiso para revisar modificaciones de roles de este servicio.")
    sol.status = "rechazado"
    sol.motivo = f"{sol.motivo}\n\n[Rechazo] {motivo}" if motivo else sol.motivo
    sol.reviewed_by = current_user.get("name") or current_user.get("email")
    sol.reviewed_at = datetime.utcnow()
    await db.commit()
    return await _serializa_solicitud(db, tenant_id, await _sol_orm(db, tenant_id, sol_id))
