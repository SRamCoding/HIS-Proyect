import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.general.schemas import (
    DiagnosticoCIE10Create, DiagnosticoCIE10Update, DiagnosticoCIE10Response,
    PaqueteCreate, PaqueteUpdate, PaqueteResponse,
    TiempoProcedimientoCreate, TiempoProcedimientoUpdate, TiempoProcedimientoResponse,
)
from app.sigarh.general import service

router = APIRouter()
# Un rol con el código completo "sigarh_general" sigue teniendo acceso a todo
# (ver permiso_incluye en app/tenants/modulos/submodulos.py).
_MOD_CIE10 = require_module_jwt("sigarh_general.cie10")
_MOD_PAQUETES = require_module_jwt("sigarh_general.paquetes")
_MOD_TIEMPOS = require_module_jwt("sigarh_general.tiempos")


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


# ─── CIE-10 ───────────────────────────────────────────────────────────────────

@router.get("/cie10", response_model=list[DiagnosticoCIE10Response])
async def listar_cie10(
    request: Request, q: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_CIE10),
    current_user: dict = Depends(get_current_user),
):
    return await service.listar_cie10(db, get_tenant_id(current_user, request), q)


@router.post("/cie10", response_model=DiagnosticoCIE10Response, status_code=201)
async def crear_cie10(
    request: Request, data: DiagnosticoCIE10Create,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_CIE10),
    current_user: dict = Depends(get_current_user),
):
    return await service.crear_cie10(db, get_tenant_id(current_user, request), data)


@router.get("/cie10/{id}", response_model=DiagnosticoCIE10Response)
async def obtener_cie10(
    request: Request, id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_CIE10),
    current_user: dict = Depends(get_current_user),
):
    item = await service.obtener_cie10(db, id, get_tenant_id(current_user, request))
    if not item:
        raise HTTPException(404, detail="Diagnóstico no encontrado")
    return item


@router.patch("/cie10/{id}", response_model=DiagnosticoCIE10Response)
async def actualizar_cie10(
    request: Request, id: uuid.UUID, data: DiagnosticoCIE10Update,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_CIE10),
    current_user: dict = Depends(get_current_user),
):
    item = await service.actualizar_cie10(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="Diagnóstico no encontrado")
    return item


@router.delete("/cie10/{id}", status_code=204)
async def eliminar_cie10(
    request: Request, id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_CIE10),
    current_user: dict = Depends(get_current_user),
):
    ok = await service.eliminar_cie10(db, id, get_tenant_id(current_user, request))
    if not ok:
        raise HTTPException(404, detail="Diagnóstico no encontrado")


# ─── Paquetes ─────────────────────────────────────────────────────────────────

@router.get("/paquetes", response_model=list[PaqueteResponse])
async def listar_paquetes(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_PAQUETES),
    current_user: dict = Depends(get_current_user),
):
    return await service.listar_paquetes(db, get_tenant_id(current_user, request))


@router.post("/paquetes", response_model=PaqueteResponse, status_code=201)
async def crear_paquete(
    request: Request, data: PaqueteCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_PAQUETES),
    current_user: dict = Depends(get_current_user),
):
    return await service.crear_paquete(db, get_tenant_id(current_user, request), data)


@router.get("/paquetes/{id}", response_model=PaqueteResponse)
async def obtener_paquete(
    request: Request, id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_PAQUETES),
    current_user: dict = Depends(get_current_user),
):
    item = await service.obtener_paquete(db, id, get_tenant_id(current_user, request))
    if not item:
        raise HTTPException(404, detail="Paquete no encontrado")
    return item


@router.patch("/paquetes/{id}", response_model=PaqueteResponse)
async def actualizar_paquete(
    request: Request, id: uuid.UUID, data: PaqueteUpdate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_PAQUETES),
    current_user: dict = Depends(get_current_user),
):
    item = await service.actualizar_paquete(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="Paquete no encontrado")
    return item


@router.delete("/paquetes/{id}", status_code=204)
async def eliminar_paquete(
    request: Request, id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_PAQUETES),
    current_user: dict = Depends(get_current_user),
):
    ok = await service.eliminar_paquete(db, id, get_tenant_id(current_user, request))
    if not ok:
        raise HTTPException(404, detail="Paquete no encontrado")


# ─── Tiempos Procedimientos ───────────────────────────────────────────────────

@router.get("/tiempos", response_model=list[TiempoProcedimientoResponse])
async def listar_tiempos(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_TIEMPOS),
    current_user: dict = Depends(get_current_user),
):
    return await service.listar_tiempos(db, get_tenant_id(current_user, request))


@router.post("/tiempos", response_model=TiempoProcedimientoResponse, status_code=201)
async def crear_tiempo(
    request: Request, data: TiempoProcedimientoCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_TIEMPOS),
    current_user: dict = Depends(get_current_user),
):
    return await service.crear_tiempo(db, get_tenant_id(current_user, request), data)


@router.get("/tiempos/{id}", response_model=TiempoProcedimientoResponse)
async def obtener_tiempo(
    request: Request, id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_TIEMPOS),
    current_user: dict = Depends(get_current_user),
):
    item = await service.obtener_tiempo(db, id, get_tenant_id(current_user, request))
    if not item:
        raise HTTPException(404, detail="Tiempo de procedimiento no encontrado")
    return item


@router.patch("/tiempos/{id}", response_model=TiempoProcedimientoResponse)
async def actualizar_tiempo(
    request: Request, id: uuid.UUID, data: TiempoProcedimientoUpdate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_TIEMPOS),
    current_user: dict = Depends(get_current_user),
):
    item = await service.actualizar_tiempo(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="Tiempo de procedimiento no encontrado")
    return item


@router.delete("/tiempos/{id}", status_code=204)
async def eliminar_tiempo(
    request: Request, id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD_TIEMPOS),
    current_user: dict = Depends(get_current_user),
):
    ok = await service.eliminar_tiempo(db, id, get_tenant_id(current_user, request))
    if not ok:
        raise HTTPException(404, detail="Tiempo de procedimiento no encontrado")