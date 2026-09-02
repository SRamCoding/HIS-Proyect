import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module
from app.sigarh.mantenimiento.models import (
    Departamento, Servicio, TipoTrabajador, TipoGuardia,
    NivelRemunerativo, HorarioGuardia, GrupoOcupacional,
    TipoActividad, Actividad, GuardiaValorizada,
    RolSistema, PerfilUsuario
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
    PerfilUsuarioCreate, PerfilUsuarioResponse,
)
from app.sigarh.mantenimiento.service import (
    listar, obtener, eliminar,
    crud_crear, crud_actualizar,
    crear_perfil,
)

router = APIRouter()


def get_tenant_id(current_user: dict) -> uuid.UUID:
    tid = current_user.get("tenant_id")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(tid)


# ─── Macro para generar rutas CRUD de catálogos simples ──────────────────────

def make_crud(
    subrouter: APIRouter,
    prefix: str,
    modelo,
    schema_create,
    schema_response,
    modulo: str,
    tag: str,
):
    @subrouter.get(f"/{prefix}", response_model=list[schema_response], tags=[tag])
    async def listar_items(
        db: AsyncSession = Depends(get_db),
        tenant=Depends(require_module(modulo)),
        current_user: dict = Depends(get_current_user),
    ):
        return await listar(db, modelo, get_tenant_id(current_user))

    @subrouter.post(f"/{prefix}", response_model=schema_response, status_code=201, tags=[tag])
    async def crear_item(
        data: schema_create,
        db: AsyncSession = Depends(get_db),
        tenant=Depends(require_module(modulo)),
        current_user: dict = Depends(get_current_user),
    ):
        return await crud_crear(db, modelo, get_tenant_id(current_user), data)

    @subrouter.get(f"/{prefix}/{{id}}", response_model=schema_response, tags=[tag])
    async def obtener_item(
        id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        tenant=Depends(require_module(modulo)),
        current_user: dict = Depends(get_current_user),
    ):
        item = await obtener(db, modelo, id, get_tenant_id(current_user))
        if not item:
            raise HTTPException(404, detail="No encontrado")
        return item

    @subrouter.patch(f"/{prefix}/{{id}}", response_model=schema_response, tags=[tag])
    async def actualizar_item(
        id: uuid.UUID,
        data: schema_create,
        db: AsyncSession = Depends(get_db),
        tenant=Depends(require_module(modulo)),
        current_user: dict = Depends(get_current_user),
    ):
        item = await crud_actualizar(db, modelo, id, get_tenant_id(current_user), data)
        if not item:
            raise HTTPException(404, detail="No encontrado")
        return item

    @subrouter.delete(f"/{prefix}/{{id}}", tags=[tag])
    async def eliminar_item(
        id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        tenant=Depends(require_module(modulo)),
        current_user: dict = Depends(get_current_user),
    ):
        ok = await eliminar(db, modelo, id, get_tenant_id(current_user))
        if not ok:
            raise HTTPException(404, detail="No encontrado")
        return {"ok": True}


# ─── Registrar todos los CRUDs ───────────────────────────────────────────────

make_crud(router, "departamentos", Departamento, DepartamentoCreate, DepartamentoResponse, "sigarh_mantenimiento", "sigarh-mantenimiento")
make_crud(router, "servicios", Servicio, ServicioCreate, ServicioResponse, "sigarh_mantenimiento", "sigarh-mantenimiento")
make_crud(router, "tipos-trabajador", TipoTrabajador, TipoTrabajadorCreate, TipoTrabajadorResponse, "sigarh_mantenimiento", "sigarh-mantenimiento")
make_crud(router, "tipos-guardia", TipoGuardia, TipoGuardiaCreate, TipoGuardiaResponse, "sigarh_mantenimiento", "sigarh-mantenimiento")
make_crud(router, "niveles-remunerativos", NivelRemunerativo, NivelRemunerativoCreate, NivelRemunerativoResponse, "sigarh_mantenimiento", "sigarh-mantenimiento")
make_crud(router, "horarios-guardia", HorarioGuardia, HorarioGuardiaCreate, HorarioGuardiaResponse, "sigarh_mantenimiento", "sigarh-mantenimiento")
make_crud(router, "grupos-ocupacionales", GrupoOcupacional, GrupoOcupacionalCreate, GrupoOcupacionalResponse, "sigarh_mantenimiento", "sigarh-mantenimiento")
make_crud(router, "tipos-actividad", TipoActividad, TipoActividadCreate, TipoActividadResponse, "sigarh_mantenimiento", "sigarh-mantenimiento")
make_crud(router, "actividades", Actividad, ActividadCreate, ActividadResponse, "sigarh_mantenimiento", "sigarh-mantenimiento")
make_crud(router, "guardias-valorizadas", GuardiaValorizada, GuardiaValorizadaCreate, GuardiaValorizadaResponse, "sigarh_mantenimiento", "sigarh-mantenimiento")
make_crud(router, "roles-sistema", RolSistema, RolSistemaCreate, RolSistemaResponse, "sigarh_mantenimiento", "sigarh-mantenimiento")


# ─── Perfiles (custom por JSON de módulos) ────────────────────────────────────

@router.get("/perfiles-usuario", response_model=list[PerfilUsuarioResponse], tags=["sigarh-mantenimiento"])
async def listar_perfiles(
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module("sigarh_mantenimiento")),
    current_user: dict = Depends(get_current_user),
):
    return await listar(db, PerfilUsuario, get_tenant_id(current_user))


@router.post("/perfiles-usuario", response_model=PerfilUsuarioResponse, status_code=201, tags=["sigarh-mantenimiento"])
async def crear_perfil_usuario(
    data: PerfilUsuarioCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module("sigarh_mantenimiento")),
    current_user: dict = Depends(get_current_user),
):
    return await crear_perfil(db, get_tenant_id(current_user), data)