import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.infraestructura.models import CATEGORIAS_CATALOGO
from app.sigarh.infraestructura.schemas import (
    CatalogoCreate, CatalogoUpdate, CatalogoResponse,
    ConsultorioCreate, ConsultorioUpdate, ConsultorioResponse,
    CategoriasResponse,
)
from app.sigarh.infraestructura.service import (
    listar_catalogos, obtener_catalogo, crear_catalogo,
    actualizar_catalogo, eliminar_catalogo,
    listar_consultorios, obtener_consultorio, crear_consultorio,
    actualizar_consultorio, eliminar_consultorio,
)

router = APIRouter()


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id")
    if not tid:
        tid = request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(tid)


# ─── Categorías disponibles ───────────────────────────────────────────────────

@router.get("/catalogos/categorias", response_model=CategoriasResponse)
async def obtener_categorias(
    tenant=Depends(require_module_jwt("sigarh_infraestructura")),
    current_user: dict = Depends(get_current_user),
):
    return {"categorias": CATEGORIAS_CATALOGO}


# ─── Catálogos ────────────────────────────────────────────────────────────────

@router.get("/catalogos", response_model=list[CatalogoResponse])
async def listar(
    request: Request,
    categoria: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_infraestructura")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_catalogos(db, get_tenant_id(current_user, request), categoria)


@router.post("/catalogos", response_model=CatalogoResponse, status_code=201)
async def crear(
    request: Request,
    data: CatalogoCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_infraestructura")),
    current_user: dict = Depends(get_current_user),
):
    return await crear_catalogo(db, get_tenant_id(current_user, request), data)


@router.get("/catalogos/{id}", response_model=CatalogoResponse)
async def obtener(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_infraestructura")),
    current_user: dict = Depends(get_current_user),
):
    item = await obtener_catalogo(db, id, get_tenant_id(current_user, request))
    if not item:
        raise HTTPException(404, detail="Catalogo no encontrado")
    return item


@router.patch("/catalogos/{id}", response_model=CatalogoResponse)
async def actualizar(
    request: Request,
    id: uuid.UUID,
    data: CatalogoUpdate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_infraestructura")),
    current_user: dict = Depends(get_current_user),
):
    item = await actualizar_catalogo(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="Catalogo no encontrado")
    return item


@router.delete("/catalogos/{id}")
async def eliminar(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_infraestructura")),
    current_user: dict = Depends(get_current_user),
):
    ok = await eliminar_catalogo(db, id, get_tenant_id(current_user, request))
    if not ok:
        raise HTTPException(404, detail="Catalogo no encontrado")
    return {"ok": True}


# ─── Consultorios ─────────────────────────────────────────────────────────────

@router.get("/consultorios", response_model=list[ConsultorioResponse])
async def listar_cons(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_infraestructura")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_consultorios(db, get_tenant_id(current_user, request))


@router.post("/consultorios", response_model=ConsultorioResponse, status_code=201)
async def crear_cons(
    request: Request,
    data: ConsultorioCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_infraestructura")),
    current_user: dict = Depends(get_current_user),
):
    return await crear_consultorio(db, get_tenant_id(current_user, request), data)


@router.get("/consultorios/{id}", response_model=ConsultorioResponse)
async def obtener_cons(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_infraestructura")),
    current_user: dict = Depends(get_current_user),
):
    item = await obtener_consultorio(db, id, get_tenant_id(current_user, request))
    if not item:
        raise HTTPException(404, detail="Consultorio no encontrado")
    return item


@router.patch("/consultorios/{id}", response_model=ConsultorioResponse)
async def actualizar_cons(
    request: Request,
    id: uuid.UUID,
    data: ConsultorioUpdate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_infraestructura")),
    current_user: dict = Depends(get_current_user),
):
    item = await actualizar_consultorio(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="Consultorio no encontrado")
    return item


@router.delete("/consultorios/{id}")
async def eliminar_cons(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_infraestructura")),
    current_user: dict = Depends(get_current_user),
):
    ok = await eliminar_consultorio(db, id, get_tenant_id(current_user, request))
    if not ok:
        raise HTTPException(404, detail="Consultorio no encontrado")
    return {"ok": True}