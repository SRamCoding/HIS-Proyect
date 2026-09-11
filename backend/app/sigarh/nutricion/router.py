import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.nutricion.schemas import (
    RacionNutricionCreate, RacionNutricionUpdate, RacionNutricionResponse,
    BuscarRacionRequest,
    CambioTurnoNutricionCreate, CambioTurnoNutricionResponse,
)
from app.sigarh.nutricion import service

router = APIRouter()
_MOD_RACIONES = require_module_jwt("sigarh_nutricion.raciones")
_MOD_ENTREGA = require_module_jwt("sigarh_nutricion.entrega")
_MOD_REPORTES = require_module_jwt("sigarh_nutricion.reportes")
_MOD_CAMBIO_TURNO = require_module_jwt("sigarh_nutricion.cambio_turno")


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


# ─── Raciones ─────────────────────────────────────────────────────────────────

@router.get("/raciones", response_model=list[RacionNutricionResponse])
async def listar_raciones(
    request: Request, fecha: date | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_RACIONES),
    current_user: dict = Depends(get_current_user),
):
    return await service.listar_raciones(db, get_tenant_id(current_user, request), fecha)


@router.post("/raciones", response_model=RacionNutricionResponse, status_code=201)
async def crear_racion(
    request: Request, data: RacionNutricionCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_RACIONES),
    current_user: dict = Depends(get_current_user),
):
    return await service.crear_racion(db, get_tenant_id(current_user, request), data)


@router.post("/raciones/buscar", response_model=RacionNutricionResponse | None)
async def buscar_racion(
    request: Request, data: BuscarRacionRequest,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_RACIONES),
    current_user: dict = Depends(get_current_user),
):
    return await service.buscar_racion_por_dni(db, get_tenant_id(current_user, request), data.dni, data.fecha)


@router.patch("/raciones/{id}", response_model=RacionNutricionResponse)
async def actualizar_racion(
    request: Request, id: uuid.UUID, data: RacionNutricionUpdate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_RACIONES),
    current_user: dict = Depends(get_current_user),
):
    item = await service.actualizar_racion(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="Ración no encontrada")
    return item


@router.post("/raciones/{id}/entregar", response_model=RacionNutricionResponse)
async def entregar_racion(
    request: Request, id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_ENTREGA),
    current_user: dict = Depends(get_current_user),
):
    item = await service.entregar_racion(db, id, get_tenant_id(current_user, request))
    if not item:
        raise HTTPException(404, detail="Ración no encontrada")
    return item


@router.delete("/raciones/{id}", status_code=204)
async def eliminar_racion(
    request: Request, id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_RACIONES),
    current_user: dict = Depends(get_current_user),
):
    ok = await service.eliminar_racion(db, id, get_tenant_id(current_user, request))
    if not ok:
        raise HTTPException(404, detail="Ración no encontrada")


# ─── Reporte ──────────────────────────────────────────────────────────────────

@router.get("/reportes")
async def reporte_raciones(
    request: Request, fecha: date,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_REPORTES),
    current_user: dict = Depends(get_current_user),
):
    return await service.reporte_por_fecha(db, get_tenant_id(current_user, request), fecha)


# ─── Cambio Turno ─────────────────────────────────────────────────────────────

@router.get("/cambio-turno", response_model=list[CambioTurnoNutricionResponse])
async def listar_cambios_turno(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_CAMBIO_TURNO),
    current_user: dict = Depends(get_current_user),
):
    return await service.listar_cambios_turno(db, get_tenant_id(current_user, request))


@router.post("/cambio-turno", response_model=CambioTurnoNutricionResponse, status_code=201)
async def crear_cambio_turno(
    request: Request, data: CambioTurnoNutricionCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_CAMBIO_TURNO),
    current_user: dict = Depends(get_current_user),
):
    return await service.crear_cambio_turno(db, get_tenant_id(current_user, request), data)


@router.delete("/cambio-turno/{id}", status_code=204)
async def eliminar_cambio_turno(
    request: Request, id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_CAMBIO_TURNO),
    current_user: dict = Depends(get_current_user),
):
    ok = await service.eliminar_cambio_turno(db, id, get_tenant_id(current_user, request))
    if not ok:
        raise HTTPException(404, detail="Cambio de turno no encontrado")