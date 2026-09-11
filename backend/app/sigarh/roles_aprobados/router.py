import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.creacion_roles.schemas import (
    RolListItem, RolDetail, SolicitudModificacionCreate, SolicitudModificacionResponse,
)
from app.sigarh.creacion_roles import service as base_svc
from app.sigarh.roles_aprobados import service as svc

router = APIRouter()
_MOD = require_module_jwt("sigarh_roles_aprobados.roles_aprobados")


def _tid(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


def _nombre(current_user: dict) -> str | None:
    return current_user.get("name") or current_user.get("email")


@router.get("/roles", response_model=list[RolListItem])
async def listar(
    request: Request,
    categoria: str | None = None,
    tipo: str | None = None,
    anio: int | None = None,
    mes: int | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD),
    current_user: dict = Depends(get_current_user),
):
    return await base_svc.listar_roles(
        db, _tid(current_user, request),
        status_in=["approved"], categoria=categoria, tipo=tipo, anio=anio, mes=mes,
    )


@router.get("/roles/{rol_id}", response_model=RolDetail)
async def detalle(request: Request, rol_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    tid = _tid(current_user, request)
    rol = await base_svc.obtener_rol_orm(db, rol_id, tid)
    if not rol or rol.status != "approved":
        raise HTTPException(404, detail="Rol aprobado no encontrado")
    return await base_svc.serializar_uno(db, tid, rol)


@router.post("/roles/{rol_id}/solicitudes-modificacion", response_model=SolicitudModificacionResponse, status_code=201)
async def solicitar_modificacion(
    request: Request,
    rol_id: uuid.UUID,
    data: SolicitudModificacionCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD),
    current_user: dict = Depends(get_current_user),
):
    try:
        sol = await svc.crear_solicitud(db, _tid(current_user, request), rol_id, data, _nombre(current_user))
    except base_svc.ReglaNegocioError as e:
        raise HTTPException(409, detail=str(e)) from e
    if not sol:
        raise HTTPException(404, detail="Rol no encontrado")
    return sol
