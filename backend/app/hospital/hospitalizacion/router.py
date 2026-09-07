import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.hospital.hospitalizacion.schemas import PisoOut, CamaConPacienteOut
from app.hospital.hospitalizacion.service import get_pisos, get_panel_camas

router = APIRouter()

MODULO_CODIGO = "hospitalizacion"


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


@router.get("/hospitalizaciones", summary="Estado de Hospitalizaciones (placeholder)")
async def estado_hospitalizaciones(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "hospitalizaciones",
        "nombre": "Hospitalizaciones",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


# --- Panel de Camas (real, ya no placeholder) ---
@router.get("/pisos", response_model=list[PisoOut], summary="Listar pisos del hospital")
async def listar_pisos(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    return await get_pisos(db, get_tenant_id(current_user, request))


@router.get("/panel-camas", response_model=list[CamaConPacienteOut], summary="Panel de Camas en tiempo real")
async def panel_camas(
    request: Request,
    piso_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    return await get_panel_camas(db, get_tenant_id(current_user, request), piso_id)


@router.get("/seguimiento-paciente", summary="Estado de Seguimiento Paciente (placeholder)")
async def estado_seguimiento_paciente(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "seguimiento-paciente",
        "nombre": "Seguimiento Paciente",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


@router.get("/censo-diario", summary="Estado de Censo Diario (placeholder)")
async def estado_censo_diario(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "censo-diario",
        "nombre": "Censo Diario",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


@router.get("/interconsultas", summary="Estado de Interconsultas (placeholder)")
async def estado_interconsultas(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "interconsultas",
        "nombre": "Interconsultas",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


@router.get("/consentimientos", summary="Estado de Consentimientos Informados (placeholder)")
async def estado_consentimientos(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "consentimientos",
        "nombre": "Consentimientos Informados",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }