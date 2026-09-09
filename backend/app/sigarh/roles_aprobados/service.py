"""Roles Aprobados: consulta de la programación autorizada y solicitud de incorporación de personal."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.sigarh.creacion_roles.models import Rol, SolicitudModificacionRol
from app.sigarh.creacion_roles.service import ReglaNegocioError
from app.sigarh.rrhh.models import Empleado


async def crear_solicitud(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID, data, solicitante: str | None) -> dict | None:
    rol = await db.scalar(select(Rol).where(Rol.id == rol_id, Rol.tenant_id == tenant_id))
    if not rol:
        return None
    if rol.status != "approved":
        raise ReglaNegocioError("Solo se pueden solicitar modificaciones sobre roles aprobados.")

    emp = await db.scalar(select(Empleado).where(Empleado.id == data.empleado_id, Empleado.tenant_id == tenant_id))
    if not emp:
        raise ReglaNegocioError("El empleado no existe.")

    # Normaliza schedule_data a la forma esperada.
    schedule = {"actividades": []}
    for act in (data.schedule_data or {}).get("actividades", []):
        turnos = []
        for tno in act.get("turnos", []):
            dias = [d for d in (tno.get("dias_semana") or []) if isinstance(d, int) and 0 <= d <= 6]
            turnos.append({
                "horario_guardia_id": str(tno["horario_guardia_id"]) if tno.get("horario_guardia_id") else None,
                "dias_semana": sorted(set(dias)),
            })
        if act.get("actividad_id"):
            schedule["actividades"].append({"actividad_id": str(act["actividad_id"]), "turnos": turnos})

    sol = SolicitudModificacionRol(
        tenant_id=tenant_id,
        rol_id=rol_id,
        empleado_id=data.empleado_id,
        motivo=data.motivo,
        schedule_data=schedule,
        status="pendiente",
        requested_by=solicitante,
    )
    db.add(sol)
    await db.commit()
    await db.refresh(sol)
    return {
        "id": sol.id,
        "tenant_id": sol.tenant_id,
        "rol_id": sol.rol_id,
        "role_type": f"{rol.categoria_personal}/{rol.tipo_rol}",
        "rol_periodo": f"{rol.mes}/{rol.anio}",
        "rol_servicio_nombre": None,
        "empleado_id": sol.empleado_id,
        "empleado_nombre": emp.nombre_completo,
        "motivo": sol.motivo,
        "schedule_data": sol.schedule_data,
        "status": sol.status,
        "requested_by": sol.requested_by,
        "reviewed_by": None,
        "reviewed_at": None,
        "created_at": sol.created_at,
    }
