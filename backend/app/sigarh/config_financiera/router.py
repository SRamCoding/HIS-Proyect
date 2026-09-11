import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.config_financiera.schemas import (
    SeguroCreate, SeguroUpdate, SeguroResponse, SeguroListItem,
    PlanSeguroCreate, PlanSeguroResponse,
    CajaCreate, CajaUpdate, CajaResponse,
    TarifarioCreate, TarifarioUpdate, TarifarioResponse,
)
from app.sigarh.config_financiera.service import (
    listar_seguros, obtener_seguro, crear_seguro, actualizar_seguro, eliminar_seguro,
    agregar_plan, eliminar_plan,
    listar_cajas, obtener_caja, crear_caja, actualizar_caja, eliminar_caja,
    listar_tarifario, obtener_tarifa, crear_tarifa, actualizar_tarifa, eliminar_tarifa,
)

router = APIRouter()


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id")
    if not tid:
        tid = request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(tid)


# ─── Seguros ──────────────────────────────────────────────────────────────────

@router.get("/seguros", response_model=list[SeguroListItem])
async def listar_seg(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    return await listar_seguros(db, get_tenant_id(current_user, request))

@router.post("/seguros", response_model=SeguroResponse, status_code=201)
async def crear_seg(request: Request, data: SeguroCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    return await crear_seguro(db, get_tenant_id(current_user, request), data)

@router.get("/seguros/{id}", response_model=SeguroResponse)
async def obtener_seg(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    item = await obtener_seguro(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="Seguro no encontrado")
    return item

@router.patch("/seguros/{id}", response_model=SeguroResponse)
async def actualizar_seg(request: Request, id: uuid.UUID, data: SeguroUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    item = await actualizar_seguro(db, id, get_tenant_id(current_user, request), data)
    if not item: raise HTTPException(404, detail="Seguro no encontrado")
    return item

@router.delete("/seguros/{id}")
async def eliminar_seg(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar_seguro(db, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="Seguro no encontrado")
    return {"ok": True}


# ─── Planes de Seguro ─────────────────────────────────────────────────────────

@router.post("/seguros/{seguro_id}/planes", response_model=PlanSeguroResponse, status_code=201)
async def agregar_plan_seg(request: Request, seguro_id: uuid.UUID, data: PlanSeguroCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    plan = await agregar_plan(db, get_tenant_id(current_user, request), seguro_id, data)
    if not plan: raise HTTPException(404, detail="Seguro no encontrado")
    return plan

@router.delete("/seguros/{seguro_id}/planes/{plan_id}")
async def eliminar_plan_seg(request: Request, seguro_id: uuid.UUID, plan_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar_plan(db, get_tenant_id(current_user, request), seguro_id, plan_id)
    if not ok: raise HTTPException(404, detail="Plan no encontrado")
    return {"ok": True}


# ─── Cajas ────────────────────────────────────────────────────────────────────

@router.get("/cajas", response_model=list[CajaResponse])
async def listar_caj(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    return await listar_cajas(db, get_tenant_id(current_user, request))

@router.post("/cajas", response_model=CajaResponse, status_code=201)
async def crear_caj(request: Request, data: CajaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    return await crear_caja(db, get_tenant_id(current_user, request), data)

@router.get("/cajas/{id}", response_model=CajaResponse)
async def obtener_caj(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    item = await obtener_caja(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="Caja no encontrada")
    return item

@router.patch("/cajas/{id}", response_model=CajaResponse)
async def actualizar_caj(request: Request, id: uuid.UUID, data: CajaUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    item = await actualizar_caja(db, id, get_tenant_id(current_user, request), data)
    if not item: raise HTTPException(404, detail="Caja no encontrada")
    return item

@router.delete("/cajas/{id}")
async def eliminar_caj(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar_caja(db, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="Caja no encontrada")
    return {"ok": True}


# ─── Tarifario ────────────────────────────────────────────────────────────────

@router.get("/tarifario", response_model=list[TarifarioResponse])
async def listar_tar(
    request: Request,
    tipo_servicio: str | None = None,
    seguro_id: uuid.UUID | None = None,
    especialidad_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_config_financiera")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_tarifario(db, get_tenant_id(current_user, request), tipo_servicio, seguro_id, especialidad_id)

@router.post("/tarifario", response_model=TarifarioResponse, status_code=201)
async def crear_tar(request: Request, data: TarifarioCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    return await crear_tarifa(db, get_tenant_id(current_user, request), data)

@router.get("/tarifario/{id}", response_model=TarifarioResponse)
async def obtener_tar(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    item = await obtener_tarifa(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="Tarifa no encontrada")
    return item

@router.patch("/tarifario/{id}", response_model=TarifarioResponse)
async def actualizar_tar(request: Request, id: uuid.UUID, data: TarifarioUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    item = await actualizar_tarifa(db, id, get_tenant_id(current_user, request), data)
    if not item: raise HTTPException(404, detail="Tarifa no encontrada")
    return item

@router.delete("/tarifario/{id}")
async def eliminar_tar(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_config_financiera")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar_tarifa(db, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="Tarifa no encontrada")
    return {"ok": True}