import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.infraestructura_hosp.schemas import (
    PisoCreate, PisoUpdate, PisoResponse,
    SalaCreate, SalaUpdate, SalaResponse, GenerarCamasRequest,
    CamaCreate, CamaUpdate, CamaResponse, CambiarEstadoRequest,
)
from app.sigarh.infraestructura_hosp.service import (
    ReglaNegocioError,
    listar_pisos, obtener_piso, crear_piso, actualizar_piso, eliminar_piso,
    listar_salas, obtener_sala, crear_sala, actualizar_sala, eliminar_sala, generar_camas,
    listar_camas, obtener_cama, crear_cama, actualizar_cama, eliminar_cama, cambiar_estado_cama,
)

router = APIRouter()

_MOD = require_module_jwt("sigarh_infraestructura_hosp")


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id")
    if not tid:
        tid = request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(tid)


# ─── Pisos ────────────────────────────────────────────────────────────────────

@router.get("/pisos", response_model=list[PisoResponse])
async def listar_p(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await listar_pisos(db, get_tenant_id(current_user, request))

@router.post("/pisos", response_model=PisoResponse, status_code=201)
async def crear_p(request: Request, data: PisoCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await crear_piso(db, get_tenant_id(current_user, request), data)

@router.get("/pisos/{id}", response_model=PisoResponse)
async def obtener_p(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    item = await obtener_piso(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="Piso no encontrado")
    return item

@router.patch("/pisos/{id}", response_model=PisoResponse)
async def actualizar_p(request: Request, id: uuid.UUID, data: PisoUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    item = await actualizar_piso(db, id, get_tenant_id(current_user, request), data)
    if not item: raise HTTPException(404, detail="Piso no encontrado")
    return item

@router.delete("/pisos/{id}")
async def eliminar_p(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        ok = await eliminar_piso(db, id, get_tenant_id(current_user, request))
    except ReglaNegocioError as exc:
        raise HTTPException(409, detail=str(exc)) from exc
    if not ok: raise HTTPException(404, detail="Piso no encontrado")
    return {"ok": True}


# ─── Salas ────────────────────────────────────────────────────────────────────

@router.get("/salas", response_model=list[SalaResponse])
async def listar_s(request: Request, piso_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await listar_salas(db, get_tenant_id(current_user, request), piso_id)

@router.post("/salas", response_model=SalaResponse, status_code=201)
async def crear_s(request: Request, data: SalaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await crear_sala(db, get_tenant_id(current_user, request), data)

@router.get("/salas/{id}", response_model=SalaResponse)
async def obtener_s(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    item = await obtener_sala(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="Sala no encontrada")
    return item

@router.patch("/salas/{id}", response_model=SalaResponse)
async def actualizar_s(request: Request, id: uuid.UUID, data: SalaUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    item = await actualizar_sala(db, id, get_tenant_id(current_user, request), data)
    if not item: raise HTTPException(404, detail="Sala no encontrada")
    return item

@router.delete("/salas/{id}")
async def eliminar_s(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        ok = await eliminar_sala(db, id, get_tenant_id(current_user, request))
    except ReglaNegocioError as exc:
        raise HTTPException(409, detail=str(exc)) from exc
    if not ok: raise HTTPException(404, detail="Sala no encontrada")
    return {"ok": True}

@router.post("/salas/{id}/generar-camas")
async def generar_camas_s(request: Request, id: uuid.UUID, data: GenerarCamasRequest, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    resultado = await generar_camas(db, get_tenant_id(current_user, request), id, data)
    if resultado is None: raise HTTPException(404, detail="Sala no encontrada")
    return resultado


# ─── Camas ────────────────────────────────────────────────────────────────────

@router.get("/camas", response_model=list[CamaResponse])
async def listar_c(
    request: Request,
    sala_id: uuid.UUID | None = None,
    piso_id: uuid.UUID | None = None,
    estado: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD),
    current_user: dict = Depends(get_current_user),
):
    return await listar_camas(db, get_tenant_id(current_user, request), sala_id, piso_id, estado)

@router.post("/camas", response_model=CamaResponse, status_code=201)
async def crear_c(request: Request, data: CamaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        return await crear_cama(db, get_tenant_id(current_user, request), data)
    except ReglaNegocioError as exc:
        raise HTTPException(409, detail=str(exc)) from exc

@router.get("/camas/{id}", response_model=CamaResponse)
async def obtener_c(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    item = await obtener_cama(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="Cama no encontrada")
    return item

@router.patch("/camas/{id}", response_model=CamaResponse)
async def actualizar_c(request: Request, id: uuid.UUID, data: CamaUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        item = await actualizar_cama(db, id, get_tenant_id(current_user, request), data)
    except ReglaNegocioError as exc:
        raise HTTPException(409, detail=str(exc)) from exc
    if not item: raise HTTPException(404, detail="Cama no encontrada")
    return item

@router.post("/camas/{id}/estado", response_model=CamaResponse)
async def cambiar_estado_c(request: Request, id: uuid.UUID, data: CambiarEstadoRequest, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    item = await cambiar_estado_cama(db, id, get_tenant_id(current_user, request), data.estado)
    if not item: raise HTTPException(404, detail="Cama no encontrada")
    return item

@router.delete("/camas/{id}")
async def eliminar_c(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        ok = await eliminar_cama(db, id, get_tenant_id(current_user, request))
    except ReglaNegocioError as exc:
        raise HTTPException(409, detail=str(exc)) from exc
    if not ok: raise HTTPException(404, detail="Cama no encontrada")
    return {"ok": True}
