import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.config_farmacia.schemas import (
    AlmacenCreate, AlmacenUpdate, AlmacenResponse,
    MedicamentoCreate, MedicamentoUpdate, MedicamentoResponse, MedicamentoListItem,
)
from app.sigarh.config_farmacia.service import (
    listar_almacenes, obtener_almacen, crear_almacen, actualizar_almacen, eliminar_almacen,
    listar_medicamentos, obtener_medicamento, crear_medicamento, actualizar_medicamento, eliminar_medicamento,
)

router = APIRouter()


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id")
    if not tid:
        tid = request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(tid)


# ─── Almacenes ────────────────────────────────────────────────────────────────

@router.get("/almacenes", response_model=list[AlmacenResponse])
async def listar_alm(
    request: Request,
    tipo: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_config_farmacia")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_almacenes(db, get_tenant_id(current_user, request), tipo)


@router.post("/almacenes", response_model=AlmacenResponse, status_code=201)
async def crear_alm(
    request: Request,
    data: AlmacenCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_config_farmacia")),
    current_user: dict = Depends(get_current_user),
):
    return await crear_almacen(db, get_tenant_id(current_user, request), data)


@router.get("/almacenes/{id}", response_model=AlmacenResponse)
async def obtener_alm(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_config_farmacia")),
    current_user: dict = Depends(get_current_user),
):
    item = await obtener_almacen(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="Almacen no encontrado")
    return item


@router.patch("/almacenes/{id}", response_model=AlmacenResponse)
async def actualizar_alm(
    request: Request,
    id: uuid.UUID,
    data: AlmacenUpdate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_config_farmacia")),
    current_user: dict = Depends(get_current_user),
):
    item = await actualizar_almacen(db, id, get_tenant_id(current_user, request), data)
    if not item: raise HTTPException(404, detail="Almacen no encontrado")
    return item


@router.delete("/almacenes/{id}")
async def eliminar_alm(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_config_farmacia")),
    current_user: dict = Depends(get_current_user),
):
    ok = await eliminar_almacen(db, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="Almacen no encontrado")
    return {"ok": True}


# ─── Medicamentos ─────────────────────────────────────────────────────────────

@router.get("/medicamentos", response_model=list[MedicamentoListItem])
async def listar_med(
    request: Request,
    search: str | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_config_farmacia")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_medicamentos(db, get_tenant_id(current_user, request), search, is_active)


@router.post("/medicamentos", response_model=MedicamentoResponse, status_code=201)
async def crear_med(
    request: Request,
    data: MedicamentoCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_config_farmacia")),
    current_user: dict = Depends(get_current_user),
):
    return await crear_medicamento(db, get_tenant_id(current_user, request), data)


@router.get("/medicamentos/{id}", response_model=MedicamentoResponse)
async def obtener_med(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_config_farmacia")),
    current_user: dict = Depends(get_current_user),
):
    item = await obtener_medicamento(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="Medicamento no encontrado")
    return item


@router.patch("/medicamentos/{id}", response_model=MedicamentoResponse)
async def actualizar_med(
    request: Request,
    id: uuid.UUID,
    data: MedicamentoUpdate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_config_farmacia")),
    current_user: dict = Depends(get_current_user),
):
    item = await actualizar_medicamento(db, id, get_tenant_id(current_user, request), data)
    if not item: raise HTTPException(404, detail="Medicamento no encontrado")
    return item


@router.delete("/medicamentos/{id}")
async def eliminar_med(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_config_farmacia")),
    current_user: dict = Depends(get_current_user),
):
    ok = await eliminar_medicamento(db, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="Medicamento no encontrado")
    return {"ok": True}