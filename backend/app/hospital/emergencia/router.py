import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.hospital.emergencia.schemas import (
    AdmisionEmergenciaCreate, AdmisionEmergenciaResponse, TriajeEmergenciaCreate, TriajeEmergenciaResponse,
    AtencionEmergenciaCreate, AtencionEmergenciaUpdate, AtencionEmergenciaResponse,
)
from app.hospital.emergencia.service import (
    create_admision, get_admision, list_admisiones, create_triaje_emergencia, get_triaje_emergencia,
    create_atencion_emergencia, get_atencion_emergencia, update_atencion_emergencia, firmar_atencion_emergencia,
)

router = APIRouter()

MODULO_CODIGO = "emergencia"


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


# --- Admisiones (real, ya no placeholder) ---
@router.get("/admisiones", response_model=list[AdmisionEmergenciaResponse], summary="Listar admisiones de emergencia")
async def listar_admisiones(
    request: Request,
    estado: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    return await list_admisiones(db, get_tenant_id(current_user, request), estado)


@router.get("/admisiones/{admision_id}", response_model=AdmisionEmergenciaResponse, summary="Obtener admision de emergencia")
async def obtener_admision(
    admision_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    admision = await get_admision(db, get_tenant_id(current_user, request), admision_id)
    if not admision:
        raise HTTPException(404, detail="Admisión no encontrada")
    return admision


@router.post("/admisiones", response_model=AdmisionEmergenciaResponse, status_code=201, summary="Registrar admision de emergencia")
async def crear_admision(
    data: AdmisionEmergenciaCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    return await create_admision(db, get_tenant_id(current_user, request), data)


# --- Triaje ---
@router.get("/triaje/{admision_id}", response_model=TriajeEmergenciaResponse, summary="Obtener triaje de emergencia")
async def obtener_triaje(
    admision_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    triaje = await get_triaje_emergencia(db, get_tenant_id(current_user, request), admision_id)
    if not triaje:
        raise HTTPException(404, detail="No hay triaje registrado")
    return triaje


@router.post("/triaje/{admision_id}", response_model=TriajeEmergenciaResponse, status_code=201, summary="Registrar triaje de emergencia")
async def registrar_triaje(
    admision_id: uuid.UUID,
    data: TriajeEmergenciaCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    try:
        return await create_triaje_emergencia(db, get_tenant_id(current_user, request), admision_id, data)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


# --- Atenciones ---
@router.get("/atenciones/{admision_id}", response_model=AtencionEmergenciaResponse, summary="Obtener atencion de emergencia")
async def obtener_atencion(
    admision_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    atencion = await get_atencion_emergencia(db, get_tenant_id(current_user, request), admision_id)
    if not atencion:
        raise HTTPException(404, detail="No hay atención registrada")
    return atencion


@router.post("/atenciones/{admision_id}", response_model=AtencionEmergenciaResponse, status_code=201, summary="Registrar atencion de emergencia")
async def crear_atencion(
    admision_id: uuid.UUID,
    data: AtencionEmergenciaCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    try:
        return await create_atencion_emergencia(db, get_tenant_id(current_user, request), admision_id, data)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


@router.patch("/atenciones/{admision_id}", response_model=AtencionEmergenciaResponse, summary="Actualizar atencion de emergencia")
async def actualizar_atencion(
    admision_id: uuid.UUID,
    data: AtencionEmergenciaUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    try:
        atencion = await update_atencion_emergencia(db, get_tenant_id(current_user, request), admision_id, data)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    if not atencion:
        raise HTTPException(404, detail="No hay atención registrada")
    return atencion


@router.post("/atenciones/{admision_id}/firmar", response_model=AtencionEmergenciaResponse, summary="Firmar atencion de emergencia")
async def firmar_atencion(
    admision_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    try:
        atencion = await firmar_atencion_emergencia(db, get_tenant_id(current_user, request), admision_id)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    if not atencion:
        raise HTTPException(404, detail="No hay atención registrada")
    return atencion


# --- Placeholders pendientes ---
@router.get("/observacion", summary="Estado de Observacion (placeholder)")
async def estado_observacion(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "observacion",
        "nombre": "Observacion",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


@router.get("/referencias", summary="Estado de Referencias (placeholder)")
async def estado_referencias(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "referencias",
        "nombre": "Referencias",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }