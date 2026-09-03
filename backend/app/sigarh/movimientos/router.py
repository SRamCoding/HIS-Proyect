import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.movimientos.schemas import (
    VacacionCreate, VacacionResponse,
    LicenciaCreate, LicenciaResponse,
    CambioTurnoCreate, CambioTurnoResponse,
    PapeletaCreate, PapeletaResponse,
)
from app.sigarh.movimientos.service import (
    listar_vacaciones, crear_vacacion, actualizar_vacacion,
    listar_licencias, crear_licencia, actualizar_licencia,
    listar_cambios_turno, crear_cambio_turno, actualizar_cambio_turno,
    listar_papeletas, crear_papeleta, actualizar_papeleta,
)

router = APIRouter()


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id")
    if not tid:
        tid = request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(tid)


# ─── Vacaciones ───────────────────────────────────────────────────────────────

@router.get("/vacaciones", response_model=list[VacacionResponse])
async def listar_vac(
    request: Request,
    estado: str | None = None,
    motivo_id: uuid.UUID | None = None,
    mes_actual: bool | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_vacaciones(db, get_tenant_id(current_user, request), estado, motivo_id, mes_actual)


@router.post("/vacaciones", response_model=VacacionResponse, status_code=201)
async def crear_vac(
    request: Request,
    data: VacacionCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    return await crear_vacacion(db, get_tenant_id(current_user, request), data)


@router.patch("/vacaciones/{id}")
async def actualizar_vac(
    request: Request,
    id: uuid.UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    item = await actualizar_vacacion(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="No encontrado")
    return item


# ─── Licencias ────────────────────────────────────────────────────────────────

@router.get("/licencias", response_model=list[LicenciaResponse])
async def listar_lic(
    request: Request,
    estado: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_licencias(db, get_tenant_id(current_user, request), estado)


@router.post("/licencias", response_model=LicenciaResponse, status_code=201)
async def crear_lic(
    request: Request,
    data: LicenciaCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    return await crear_licencia(db, get_tenant_id(current_user, request), data)


@router.get("/licencias/{id}", response_model=LicenciaResponse)
async def obtener_lic(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    from app.sigarh.movimientos.service import _obtener
    from app.sigarh.movimientos.models import Licencia
    item = await _obtener(db, Licencia, id, get_tenant_id(current_user, request))
    if not item:
        raise HTTPException(404, detail="No encontrado")
    return item


@router.patch("/licencias/{id}")
async def actualizar_lic(
    request: Request,
    id: uuid.UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    item = await actualizar_licencia(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="No encontrado")
    return item


# ─── Cambio de Turno ──────────────────────────────────────────────────────────

@router.get("/cambio-turno", response_model=list[CambioTurnoResponse])
async def listar_ct(
    request: Request,
    estado: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_cambios_turno(db, get_tenant_id(current_user, request), estado)


@router.post("/cambio-turno", response_model=CambioTurnoResponse, status_code=201)
async def crear_ct(
    request: Request,
    data: CambioTurnoCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    return await crear_cambio_turno(db, get_tenant_id(current_user, request), data)


@router.patch("/cambio-turno/{id}")
async def actualizar_ct(
    request: Request,
    id: uuid.UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    item = await actualizar_cambio_turno(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="No encontrado")
    return item


# ─── Papeletas ────────────────────────────────────────────────────────────────

@router.get("/papeletas", response_model=list[PapeletaResponse])
async def listar_pap(
    request: Request,
    estado: str | None = None,
    mes_actual: bool | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_papeletas(db, get_tenant_id(current_user, request), estado, mes_actual)


@router.post("/papeletas", response_model=PapeletaResponse, status_code=201)
async def crear_pap(
    request: Request,
    data: PapeletaCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    return await crear_papeleta(db, get_tenant_id(current_user, request), data)


@router.patch("/papeletas/{id}")
async def actualizar_pap(
    request: Request,
    id: uuid.UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_movimientos")),
    current_user: dict = Depends(get_current_user),
):
    item = await actualizar_papeleta(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="No encontrado")
    return item