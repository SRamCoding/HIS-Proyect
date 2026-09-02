import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.mantenimiento.models import (
    Departamento, Servicio, TipoTrabajador, TipoGuardia,
    NivelRemunerativo, HorarioGuardia, GrupoOcupacional,
    TipoActividad, Actividad, GuardiaValorizada,
    RolSistema, PerfilUsuario,Dependencia
)
from app.sigarh.mantenimiento.schemas import (
    DepartamentoCreate, DepartamentoResponse,
    ServicioCreate, ServicioResponse,
    TipoTrabajadorCreate, TipoTrabajadorResponse,
    TipoGuardiaCreate, TipoGuardiaResponse,
    NivelRemunerativoCreate, NivelRemunerativoResponse,
    HorarioGuardiaCreate, HorarioGuardiaResponse,
    GrupoOcupacionalCreate, GrupoOcupacionalResponse,
    TipoActividadCreate, TipoActividadResponse,
    ActividadCreate, ActividadResponse,
    GuardiaValorizadaCreate, GuardiaValorizadaResponse,
    RolSistemaCreate, RolSistemaResponse,
    PerfilUsuarioCreate, PerfilUsuarioResponse,DependenciaCreate, DependenciaResponse,
)
from app.sigarh.mantenimiento.service import (
    listar, obtener, eliminar,
    crud_crear, crud_actualizar,
    crear_perfil,
)

router = APIRouter()


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id")
    if not tid:
        tid = request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(tid)


def make_crud(
    subrouter: APIRouter,
    prefix: str,
    modelo,
    schema_create,
    schema_response,
    modulo: str,
):
    @subrouter.get(f"/{prefix}", response_model=list[schema_response])
    async def listar_items(
        request: Request,
        db: AsyncSession = Depends(get_db),
        tenant=Depends(require_module_jwt(modulo)),
        current_user: dict = Depends(get_current_user),
    ):
        return await listar(db, modelo, get_tenant_id(current_user, request))

    @subrouter.post(f"/{prefix}", response_model=schema_response, status_code=201)
    async def crear_item(
        request: Request,
        data: schema_create,
        db: AsyncSession = Depends(get_db),
        tenant=Depends(require_module_jwt(modulo)),
        current_user: dict = Depends(get_current_user),
    ):
        return await crud_crear(db, modelo, get_tenant_id(current_user, request), data)

    @subrouter.get(f"/{prefix}/{{id}}", response_model=schema_response)
    async def obtener_item(
        request: Request,
        id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        tenant=Depends(require_module_jwt(modulo)),
        current_user: dict = Depends(get_current_user),
    ):
        item = await obtener(db, modelo, id, get_tenant_id(current_user, request))
        if not item:
            raise HTTPException(404, detail="No encontrado")
        return item

    @subrouter.patch(f"/{prefix}/{{id}}", response_model=schema_response)
    async def actualizar_item(
        request: Request,
        id: uuid.UUID,
        data: schema_create,
        db: AsyncSession = Depends(get_db),
        tenant=Depends(require_module_jwt(modulo)),
        current_user: dict = Depends(get_current_user),
    ):
        item = await crud_actualizar(db, modelo, id, get_tenant_id(current_user, request), data)
        if not item:
            raise HTTPException(404, detail="No encontrado")
        return item

    @subrouter.delete(f"/{prefix}/{{id}}")
    async def eliminar_item(
        request: Request,
        id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        tenant=Depends(require_module_jwt(modulo)),
        current_user: dict = Depends(get_current_user),
    ):
        ok = await eliminar(db, modelo, id, get_tenant_id(current_user, request))
        if not ok:
            raise HTTPException(404, detail="No encontrado")
        return {"ok": True}


# ─── Registrar CRUDs ──────────────────────────────────────────────────────────
make_crud(router, "departamentos", Departamento, DepartamentoCreate, DepartamentoResponse, "sigarh_mantenimiento")
make_crud(router, "servicios", Servicio, ServicioCreate, ServicioResponse, "sigarh_mantenimiento")
make_crud(router, "tipos-trabajador", TipoTrabajador, TipoTrabajadorCreate, TipoTrabajadorResponse, "sigarh_mantenimiento")
make_crud(router, "tipos-guardia", TipoGuardia, TipoGuardiaCreate, TipoGuardiaResponse, "sigarh_mantenimiento")
make_crud(router, "niveles-remunerativos", NivelRemunerativo, NivelRemunerativoCreate, NivelRemunerativoResponse, "sigarh_mantenimiento")
make_crud(router, "horarios-guardia", HorarioGuardia, HorarioGuardiaCreate, HorarioGuardiaResponse, "sigarh_mantenimiento")
make_crud(router, "grupos-ocupacionales", GrupoOcupacional, GrupoOcupacionalCreate, GrupoOcupacionalResponse, "sigarh_mantenimiento")
make_crud(router, "tipos-actividad", TipoActividad, TipoActividadCreate, TipoActividadResponse, "sigarh_mantenimiento")
make_crud(router, "actividades", Actividad, ActividadCreate, ActividadResponse, "sigarh_mantenimiento")
make_crud(router, "guardias-valorizadas", GuardiaValorizada, GuardiaValorizadaCreate, GuardiaValorizadaResponse, "sigarh_mantenimiento")
make_crud(router, "roles-sistema", RolSistema, RolSistemaCreate, RolSistemaResponse, "sigarh_mantenimiento")
make_crud(router, "dependencias", Dependencia, DependenciaCreate, DependenciaResponse, "sigarh_mantenimiento")


# ─── Perfiles ─────────────────────────────────────────────────────────────────

@router.get("/perfiles-usuario", response_model=list[PerfilUsuarioResponse])
async def listar_perfiles(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_mantenimiento")),
    current_user: dict = Depends(get_current_user),
):
    return await listar(db, PerfilUsuario, get_tenant_id(current_user, request))


@router.post("/perfiles-usuario", response_model=PerfilUsuarioResponse, status_code=201)
async def crear_perfil_usuario(
    request: Request,
    data: PerfilUsuarioCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_mantenimiento")),
    current_user: dict = Depends(get_current_user),
):
    return await crear_perfil(db, get_tenant_id(current_user, request), data)