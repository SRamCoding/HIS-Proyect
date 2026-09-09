import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.config_farmacia.schemas import (
    AlmacenCreate, AlmacenUpdate, AlmacenResponse,
    MedicamentoCreate, MedicamentoUpdate, MedicamentoResponse, MedicamentoListItem,
    ProveedorCreate, CatalogoFarmaciaCreate,
)
from app.sigarh.config_farmacia import service as svc

router = APIRouter()
_MOD = require_module_jwt("sigarh_config_farmacia")


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


def _rn(e: svc.ReglaNegocioError):
    return HTTPException(409, detail=str(e))


# ─── Catálogos auxiliares ────────────────────────────────────────────────────

@router.get("/tipos-producto", summary="Catálogo 'tipos_producto' (Infraestructura) para el selector de productos")
async def tipos_producto(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    tid = get_tenant_id(current_user, request)
    try:
        from app.sigarh.infraestructura.models import Catalogo
    except Exception:
        return []
    rows = (await db.execute(
        select(Catalogo.id, Catalogo.nombre).where(
            Catalogo.tenant_id == tid, Catalogo.categoria == "tipos_producto", Catalogo.is_active.is_(True)
        ).order_by(Catalogo.nombre)
    )).all()
    return [{"id": r[0], "nombre": r[1]} for r in rows]


@router.get("/proveedores")
async def proveedores(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await svc.listar_proveedores(db, get_tenant_id(current_user, request))


@router.post("/proveedores", status_code=201)
async def nuevo_proveedor(request: Request, data: ProveedorCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await svc.crear_proveedor(db, get_tenant_id(current_user, request), data)


@router.get("/catalogos/{categoria}")
async def catalogos_farmacia(request: Request, categoria: str, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await svc.listar_catalogo(db, get_tenant_id(current_user, request), categoria)


@router.post("/catalogos", status_code=201)
async def nuevo_catalogo(request: Request, data: CatalogoFarmaciaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await svc.crear_catalogo(db, get_tenant_id(current_user, request), data)


# ─── Almacenes ────────────────────────────────────────────────────────────────

@router.get("/almacenes", response_model=list[AlmacenResponse])
async def listar_alm(
    request: Request, tipo: str | None = None, despacha_recetas: bool | None = None, is_active: bool | None = None,
    db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user),
):
    return await svc.listar_almacenes(db, get_tenant_id(current_user, request), tipo, despacha_recetas, is_active)


@router.post("/almacenes", response_model=AlmacenResponse, status_code=201)
async def crear_alm(request: Request, data: AlmacenCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        return await svc.crear_almacen(db, get_tenant_id(current_user, request), data)
    except svc.ReglaNegocioError as e:
        raise _rn(e)


@router.get("/almacenes/{id}", response_model=AlmacenResponse)
async def obtener_alm(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    item = await svc.obtener_almacen(db, id, get_tenant_id(current_user, request))
    if not item:
        raise HTTPException(404, detail="Almacén no encontrado")
    return item


@router.patch("/almacenes/{id}", response_model=AlmacenResponse)
async def actualizar_alm(request: Request, id: uuid.UUID, data: AlmacenUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        item = await svc.actualizar_almacen(db, id, get_tenant_id(current_user, request), data)
    except svc.ReglaNegocioError as e:
        raise _rn(e)
    if not item:
        raise HTTPException(404, detail="Almacén no encontrado")
    return item


@router.delete("/almacenes/{id}")
async def eliminar_alm(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        ok = await svc.eliminar_almacen(db, id, get_tenant_id(current_user, request))
    except svc.ReglaNegocioError as e:
        raise _rn(e)
    if not ok:
        raise HTTPException(404, detail="Almacén no encontrado")
    return {"ok": True}


# ─── Medicamentos ─────────────────────────────────────────────────────────────

@router.get("/medicamentos", response_model=list[MedicamentoListItem])
async def listar_med(
    request: Request,
    search: str | None = None, is_active: bool | None = None,
    condicion_venta: str | None = None, controlado: bool | None = None,
    fiscalizado_digemid: bool | None = None, reporte_sismed: bool | None = None,
    requiere_cadena_frio: bool | None = None, forma_farmaceutica: str | None = None,
    tipo_producto_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user),
):
    return await svc.listar_medicamentos(
        db, get_tenant_id(current_user, request), search, is_active,
        condicion_venta, controlado, fiscalizado_digemid, reporte_sismed,
        requiere_cadena_frio, forma_farmaceutica, tipo_producto_id,
    )


@router.post("/medicamentos", response_model=MedicamentoResponse, status_code=201)
async def crear_med(request: Request, data: MedicamentoCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        return await svc.crear_medicamento(db, get_tenant_id(current_user, request), data)
    except svc.ReglaNegocioError as e:
        raise _rn(e)


@router.get("/medicamentos/{id}", response_model=MedicamentoResponse)
async def obtener_med(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    item = await svc.obtener_medicamento(db, id, get_tenant_id(current_user, request))
    if not item:
        raise HTTPException(404, detail="Medicamento no encontrado")
    return item


@router.patch("/medicamentos/{id}", response_model=MedicamentoResponse)
async def actualizar_med(request: Request, id: uuid.UUID, data: MedicamentoUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        item = await svc.actualizar_medicamento(db, id, get_tenant_id(current_user, request), data)
    except svc.ReglaNegocioError as e:
        raise _rn(e)
    if not item:
        raise HTTPException(404, detail="Medicamento no encontrado")
    return item


@router.delete("/medicamentos/{id}")
async def eliminar_med(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        ok = await svc.eliminar_medicamento(db, id, get_tenant_id(current_user, request))
    except svc.ReglaNegocioError as e:
        raise _rn(e)
    if not ok:
        raise HTTPException(404, detail="Medicamento no encontrado")
    return {"ok": True}
