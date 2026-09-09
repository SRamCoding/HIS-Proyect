import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.creacion_roles.schemas import (
    RolListItem, RolDetail, RechazoRequest, SolicitudModificacionResponse,
)
from app.sigarh.creacion_roles import service as base_svc
from app.sigarh.roles_pendientes import service as svc

router = APIRouter()
_MOD = require_module_jwt("sigarh_roles_pendientes")


def _tid(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


def _nombre(current_user: dict) -> str | None:
    return current_user.get("name") or current_user.get("email")


# ─── Bandeja de roles pendientes ─────────────────────────────────────────────

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
        status_in=["pending"], categoria=categoria, tipo=tipo, anio=anio, mes=mes,
    )


@router.get("/roles/{rol_id}", response_model=RolDetail)
async def detalle(request: Request, rol_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    tid = _tid(current_user, request)
    rol = await base_svc.obtener_rol_orm(db, rol_id, tid)
    if not rol:
        raise HTTPException(404, detail="Rol no encontrado")
    return await base_svc.serializar_uno(db, tid, rol)


@router.post("/roles/{rol_id}/aprobar", response_model=RolDetail)
async def aprobar(request: Request, rol_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        rol = await svc.aprobar_rol(db, _tid(current_user, request), rol_id, _nombre(current_user))
    except base_svc.ReglaNegocioError as e:
        raise HTTPException(409, detail=str(e)) from e
    if not rol:
        raise HTTPException(404, detail="Rol no encontrado")
    return rol


@router.post("/roles/{rol_id}/rechazar", response_model=RolDetail)
async def rechazar(request: Request, rol_id: uuid.UUID, data: RechazoRequest, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        rol = await svc.rechazar_rol(db, _tid(current_user, request), rol_id, data.motivo, _nombre(current_user))
    except base_svc.ReglaNegocioError as e:
        raise HTTPException(409, detail=str(e)) from e
    if not rol:
        raise HTTPException(404, detail="Rol no encontrado")
    return rol


# ─── Solicitudes de Modificación ─────────────────────────────────────────────

@router.get("/solicitudes-modificacion", response_model=list[SolicitudModificacionResponse])
async def listar_solicitudes(
    request: Request,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD),
    current_user: dict = Depends(get_current_user),
):
    return await svc.listar_solicitudes(db, _tid(current_user, request), status)


@router.get("/solicitudes-modificacion/{sol_id}", response_model=SolicitudModificacionResponse)
async def detalle_solicitud(request: Request, sol_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    sol = await svc.obtener_solicitud(db, _tid(current_user, request), sol_id)
    if not sol:
        raise HTTPException(404, detail="Solicitud no encontrada")
    return sol


@router.post("/solicitudes-modificacion/{sol_id}/aprobar", response_model=SolicitudModificacionResponse)
async def aprobar_solicitud(request: Request, sol_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        sol = await svc.aprobar_solicitud(db, _tid(current_user, request), sol_id, _nombre(current_user))
    except base_svc.ReglaNegocioError as e:
        raise HTTPException(409, detail=str(e)) from e
    if not sol:
        raise HTTPException(404, detail="Solicitud no encontrada")
    return sol


@router.post("/solicitudes-modificacion/{sol_id}/rechazar", response_model=SolicitudModificacionResponse)
async def rechazar_solicitud(request: Request, sol_id: uuid.UUID, data: RechazoRequest, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        sol = await svc.rechazar_solicitud(db, _tid(current_user, request), sol_id, data.motivo, _nombre(current_user))
    except base_svc.ReglaNegocioError as e:
        raise HTTPException(409, detail=str(e)) from e
    if not sol:
        raise HTTPException(404, detail="Solicitud no encontrada")
    return sol
