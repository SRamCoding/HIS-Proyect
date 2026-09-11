import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.laboratorio.schemas import ExamenLaboratorioCreate, ExamenLaboratorioUpdate, ExamenLaboratorioResponse
from app.sigarh.laboratorio import service

router = APIRouter()
_MOD = require_module_jwt("sigarh_laboratorio.examenes")


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id")
    if not tid:
        tid = request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(tid)


@router.get("/examenes", response_model=list[ExamenLaboratorioResponse])
async def listar(request: Request, categoria: str | None = None, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await service.listar(db, get_tenant_id(current_user, request), categoria)

@router.post("/examenes", response_model=ExamenLaboratorioResponse, status_code=201)
async def crear(request: Request, data: ExamenLaboratorioCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await service.crear(db, get_tenant_id(current_user, request), data)

@router.get("/examenes/{id}", response_model=ExamenLaboratorioResponse)
async def obtener(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    item = await service.obtener(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="Examen no encontrado")
    return item

@router.patch("/examenes/{id}", response_model=ExamenLaboratorioResponse)
async def actualizar(request: Request, id: uuid.UUID, data: ExamenLaboratorioUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    item = await service.actualizar(db, id, get_tenant_id(current_user, request), data)
    if not item: raise HTTPException(404, detail="Examen no encontrado")
    return item

@router.delete("/examenes/{id}")
async def eliminar(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    ok = await service.eliminar(db, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="Examen no encontrado")
    return {"ok": True}