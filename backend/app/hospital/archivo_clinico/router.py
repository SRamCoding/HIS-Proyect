import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt

router = APIRouter()

MODULO_CODIGO = "archivo_clinico"


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
