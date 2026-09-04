import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.sigarh.rrhh.models import Empleado, RegistroAsistencia, Justificacion
from app.sigarh.movimientos.models import Vacacion, Licencia, CambioTurno, Papeleta
from app.sigarh.infraestructura_hosp.models import Cama

router = APIRouter()


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


@router.get("/dashboard")
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = get_tenant_id(current_user, request)
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    hace_7_dias = hoy - timedelta(days=7)

    # ── Empleados ─────────────────────────────────────────────────────────────
    total_empleados = await db.scalar(
        select(func.count(Empleado.id)).where(Empleado.tenant_id == tenant_id)
    )
    empleados_activos = await db.scalar(
        select(func.count(Empleado.id)).where(
            Empleado.tenant_id == tenant_id,
            Empleado.estado == "ACTIVO"
        )
    )

    # ── Asistencia hoy ────────────────────────────────────────────────────────
    asistencia_hoy = await db.scalar(
        select(func.count(RegistroAsistencia.id)).where(
            RegistroAsistencia.tenant_id == tenant_id,
            func.date(RegistroAsistencia.fecha) == hoy,
        )
    )

    # ── Movimientos del mes ───────────────────────────────────────────────────
    vacaciones_mes = await db.scalar(
        select(func.count(Vacacion.id)).where(
            Vacacion.tenant_id == tenant_id,
            Vacacion.fecha_inicio >= inicio_mes,
        )
    )
    licencias_mes = await db.scalar(
        select(func.count(Licencia.id)).where(
            Licencia.tenant_id == tenant_id,
            Licencia.fecha_tramite >= inicio_mes,
        )
    )
    papeletas_mes = await db.scalar(
        select(func.count(Papeleta.id)).where(
            Papeleta.tenant_id == tenant_id,
            Papeleta.fecha_tramite >= inicio_mes,
        )
    )
    cambios_turno_mes = await db.scalar(
        select(func.count(CambioTurno.id)).where(
            CambioTurno.tenant_id == tenant_id,
            CambioTurno.fecha_original >= inicio_mes,
        )
    )

    # ── Movimientos pendientes ────────────────────────────────────────────────
    vacaciones_pendientes = await db.scalar(
        select(func.count(Vacacion.id)).where(
            Vacacion.tenant_id == tenant_id,
            Vacacion.estado == "pendiente",
        )
    )
    licencias_pendientes = await db.scalar(
        select(func.count(Licencia.id)).where(
            Licencia.tenant_id == tenant_id,
            Licencia.estado == "pendiente",
        )
    )
    papeletas_pendientes = await db.scalar(
        select(func.count(Papeleta.id)).where(
            Papeleta.tenant_id == tenant_id,
            Papeleta.estado == "pendiente",
        )
    )

    # ── Camas ─────────────────────────────────────────────────────────────────
    total_camas = await db.scalar(
        select(func.count(Cama.id)).where(Cama.tenant_id == tenant_id)
    )
    camas_disponibles = await db.scalar(
        select(func.count(Cama.id)).where(
            Cama.tenant_id == tenant_id,
            Cama.estado == "DISPONIBLE",
        )
    )
    camas_ocupadas = await db.scalar(
        select(func.count(Cama.id)).where(
            Cama.tenant_id == tenant_id,
            Cama.estado == "OCUPADA",
        )
    )
    camas_mantenimiento = await db.scalar(
        select(func.count(Cama.id)).where(
            Cama.tenant_id == tenant_id,
            Cama.estado == "MANTENIMIENTO",
        )
    )

    # ── Justificaciones pendientes ────────────────────────────────────────────
    justificaciones_pendientes = await db.scalar(
        select(func.count(Justificacion.id)).where(
            Justificacion.tenant_id == tenant_id,
            Justificacion.estado == "pendiente",
        )
    )

    # ── Últimas vacaciones ────────────────────────────────────────────────────
    result = await db.execute(
        select(Vacacion)
        .where(Vacacion.tenant_id == tenant_id)
        .order_by(Vacacion.created_at.desc())
        .limit(5)
    )
    ultimas_vacaciones = result.scalars().all()

    # ── Últimas licencias ─────────────────────────────────────────────────────
    result2 = await db.execute(
        select(Licencia)
        .where(Licencia.tenant_id == tenant_id)
        .order_by(Licencia.created_at.desc())
        .limit(5)
    )
    ultimas_licencias = result2.scalars().all()

    return {
        # KPIs principales
        "total_empleados": total_empleados or 0,
        "empleados_activos": empleados_activos or 0,
        "asistencia_hoy": asistencia_hoy or 0,
        "justificaciones_pendientes": justificaciones_pendientes or 0,

        # Movimientos del mes
        "movimientos_mes": {
            "vacaciones": vacaciones_mes or 0,
            "licencias": licencias_mes or 0,
            "papeletas": papeletas_mes or 0,
            "cambios_turno": cambios_turno_mes or 0,
        },

        # Pendientes (para alertas)
        "pendientes": {
            "vacaciones": vacaciones_pendientes or 0,
            "licencias": licencias_pendientes or 0,
            "papeletas": papeletas_pendientes or 0,
        },

        # Camas
        "camas": {
            "total": total_camas or 0,
            "disponibles": camas_disponibles or 0,
            "ocupadas": camas_ocupadas or 0,
            "mantenimiento": camas_mantenimiento or 0,
        },

        # Actividad reciente
        "ultimas_vacaciones": [
            {
                "id": str(v.id),
                "empleado_nombre": v.empleado_nombre,
                "tipo": v.tipo,
                "fecha_inicio": str(v.fecha_inicio),
                "fecha_fin": str(v.fecha_fin),
                "estado": v.estado,
            }
            for v in ultimas_vacaciones
        ],
        "ultimas_licencias": [
            {
                "id": str(l.id),
                "empleado_nombre": l.empleado_nombre,
                "fecha_tramite": str(l.fecha_tramite),
                "estado": l.estado,
            }
            for l in ultimas_licencias
        ],
    }