import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt

router = APIRouter()

MODULO_CODIGO = "caja"


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


@router.get("/comprobantes-pago", summary="Estado de Comprobantes de Pago (placeholder)")
async def estado_comprobantes_pago(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "comprobantes-pago",
        "nombre": "Comprobantes de Pago",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


@router.get("/cuentas", summary="Estado de Cuentas (placeholder)")
async def estado_cuentas(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "cuentas",
        "nombre": "Cuentas",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }
