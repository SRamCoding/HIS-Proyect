import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt, require_any_module_jwt
from app.hospital.archivo_clinico.schemas import (
    DigitalizarRequest, HistoriaOut, HistoriasPage, MovimientosPage,
)
from app.hospital.archivo_clinico import service

router = APIRouter()

MODULO_CODIGO = "archivo_clinico"

# La dependencia compartida delega en require_module_jwt y exige hospital del JWT.
archivo_user = require_any_module_jwt(MODULO_CODIGO)


@router.get("/historias", response_model=HistoriasPage)
async def listar_historias(
    q: str | None = Query(default=None, max_length=200),
    location: str | None = Query(default=None, max_length=50),
    is_digitized: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(archivo_user),
):
    return await service.list_historias(db, uuid.UUID(current_user["tenant_id"]),
        q, location, is_digitized, page, page_size)


@router.get("/historias/{record_id}/movimientos", response_model=MovimientosPage)
async def listar_movimientos(
    record_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(archivo_user),
):
    result = await service.list_movimientos(db, uuid.UUID(current_user["tenant_id"]),
                                           record_id, page, page_size)
    if result is None:
        raise HTTPException(404, detail="Historia clínica no encontrada")
    return result


@router.patch("/historias/{record_id}/digitalizar", response_model=HistoriaOut)
async def digitalizar_historia(
    record_id: uuid.UUID,
    data: DigitalizarRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(archivo_user),
):
    result = await service.set_digitalizada(db, uuid.UUID(current_user["tenant_id"]),
                                           record_id, data.is_digitized)
    if result is None:
        raise HTTPException(404, detail="Historia clínica no encontrada")
    return result


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


@router.get("/hc-electronica", summary="Estado de HC Electronica (placeholder)")
async def estado_hc_electronica(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "hc-electronica",
        "nombre": "HC Electronica",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


@router.get("/historias-clinicas", summary="Estado de Historias Clinicas (placeholder)")
async def estado_historias_clinicas(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "historias-clinicas",
        "nombre": "Historias Clinicas",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


@router.get("/movimientos-hc", summary="Estado de Movimientos de H.C. (placeholder)")
async def estado_movimientos_hc(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "movimientos-hc",
        "nombre": "Movimientos de H.C.",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


@router.get("/personal-archivo", summary="Estado de Personal de Archivo (placeholder)")
async def estado_personal_archivo(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "personal-archivo",
        "nombre": "Personal de Archivo",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }
