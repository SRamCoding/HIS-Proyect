# backend/app/sigarh/mantenimiento/router.py
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
    RolSistema, PerfilUsuario, Dependencia, UsuarioSigarh
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
    DependenciaCreate, DependenciaResponse,
    UsuarioSigarhCreate, UsuarioSigarhUpdate, UsuarioSigarhResponse,
)
from app.sigarh.mantenimiento.service import (
    listar, obtener, eliminar,
    crud_crear, crud_actualizar,
    crear_perfil,
    listar_roles, obtener_rol, crear_rol, actualizar_rol,
    listar_perfiles_usuario, obtener_perfil_usuario, actualizar_perfil_usuario,
    listar_servicios, obtener_servicio,
    crear_servicio, actualizar_servicio,
    listar_dependencias, obtener_dependencia,
    crear_dependencia, actualizar_dependencia,
    listar_horarios_guardia, obtener_horario_guardia,
    crear_horario_guardia, actualizar_horario_guardia,
)

router = APIRouter()


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id")
    if not tid:
        tid = request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(tid)


def make_crud(subrouter, prefix, modelo, schema_create, schema_response, modulo):
    @subrouter.get(f"/{prefix}", response_model=list[schema_response])
    async def listar_items(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt(modulo)), current_user: dict = Depends(get_current_user)):
        return await listar(db, modelo, get_tenant_id(current_user, request))

    @subrouter.post(f"/{prefix}", response_model=schema_response, status_code=201)
    async def crear_item(request: Request, data: schema_create, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt(modulo)), current_user: dict = Depends(get_current_user)):
        return await crud_crear(db, modelo, get_tenant_id(current_user, request), data)

    @subrouter.get(f"/{prefix}/{{id}}", response_model=schema_response)
    async def obtener_item(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt(modulo)), current_user: dict = Depends(get_current_user)):
        item = await obtener(db, modelo, id, get_tenant_id(current_user, request))
        if not item: raise HTTPException(404, detail="No encontrado")
        return item

    @subrouter.patch(f"/{prefix}/{{id}}", response_model=schema_response)
    async def actualizar_item(request: Request, id: uuid.UUID, data: schema_create, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt(modulo)), current_user: dict = Depends(get_current_user)):
        item = await crud_actualizar(db, modelo, id, get_tenant_id(current_user, request), data)
        if not item: raise HTTPException(404, detail="No encontrado")
        return item

    @subrouter.delete(f"/{prefix}/{{id}}")
    async def eliminar_item(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt(modulo)), current_user: dict = Depends(get_current_user)):
        ok = await eliminar(db, modelo, id, get_tenant_id(current_user, request))
        if not ok: raise HTTPException(404, detail="No encontrado")
        return {"ok": True}


# ─── CRUDs simples ────────────────────────────────────────────────────────────
make_crud(router, "departamentos", Departamento, DepartamentoCreate, DepartamentoResponse, "sigarh_mantenimiento")
# Servicios (endpoints propios para incluir piso)
@router.get("/servicios", response_model=list[ServicioResponse])
async def listar_servicios_endpoint(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    items = await listar_servicios(db, get_tenant_id(current_user, request))
    return [ServicioResponse(
        **{k: v for k, v in item.__dict__.items() if not k.startswith("_")},
        departamento_nombre=item.departamento.nombre if item.departamento else None,
        piso_nombre=item.piso.nombre if item.piso else None,
    ) for item in items]

@router.post("/servicios", response_model=ServicioResponse, status_code=201)
async def crear_servicio_endpoint(request: Request, data: ServicioCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    return await crear_servicio(db, get_tenant_id(current_user, request), data)

@router.get("/servicios/{id}", response_model=ServicioResponse)
async def obtener_servicio_endpoint(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    item = await obtener_servicio(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="No encontrado")
    return ServicioResponse(
        **{k: v for k, v in item.__dict__.items() if not k.startswith("_")},
        departamento_nombre=item.departamento.nombre if item.departamento else None,
        piso_nombre=item.piso.nombre if item.piso else None,
    )

@router.patch("/servicios/{id}", response_model=ServicioResponse)
async def actualizar_servicio_endpoint(request: Request, id: uuid.UUID, data: ServicioCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    item = await actualizar_servicio(db, id, get_tenant_id(current_user, request), data)
    if not item: raise HTTPException(404, detail="No encontrado")
    item = await obtener_servicio(db, id, get_tenant_id(current_user, request))
    return ServicioResponse(
        **{k: v for k, v in item.__dict__.items() if not k.startswith("_")},
        departamento_nombre=item.departamento.nombre if item.departamento else None,
        piso_nombre=item.piso.nombre if item.piso else None,
    )

@router.delete("/servicios/{id}")
async def eliminar_servicio_endpoint(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar(db, Servicio, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="No encontrado")
    return {"ok": True}
# Dependencias (endpoints propios para incluir departamento y servicio)
@router.get("/dependencias", response_model=list[DependenciaResponse])
async def listar_dependencias_endpoint(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    items = await listar_dependencias(db, get_tenant_id(current_user, request))
    return [DependenciaResponse(
        **{k: v for k, v in item.__dict__.items() if not k.startswith("_")},
        departamento_nombre=item.departamento.nombre if item.departamento else None,
        servicio_nombre=item.servicio.nombre if item.servicio else None,
    ) for item in items]

@router.post("/dependencias", response_model=DependenciaResponse, status_code=201)
async def crear_dependencia_endpoint(request: Request, data: DependenciaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    return await crear_dependencia(db, get_tenant_id(current_user, request), data)

@router.get("/dependencias/{id}", response_model=DependenciaResponse)
async def obtener_dependencia_endpoint(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    item = await obtener_dependencia(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="No encontrado")
    return DependenciaResponse(
        **{k: v for k, v in item.__dict__.items() if not k.startswith("_")},
        departamento_nombre=item.departamento.nombre if item.departamento else None,
        servicio_nombre=item.servicio.nombre if item.servicio else None,
    )

@router.patch("/dependencias/{id}", response_model=DependenciaResponse)
async def actualizar_dependencia_endpoint(request: Request, id: uuid.UUID, data: DependenciaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    item = await actualizar_dependencia(db, id, get_tenant_id(current_user, request), data)
    if not item: raise HTTPException(404, detail="No encontrado")
    item = await obtener_dependencia(db, id, get_tenant_id(current_user, request))
    return DependenciaResponse(
        **{k: v for k, v in item.__dict__.items() if not k.startswith("_")},
        departamento_nombre=item.departamento.nombre if item.departamento else None,
        servicio_nombre=item.servicio.nombre if item.servicio else None,
    )

@router.delete("/dependencias/{id}")
async def eliminar_dependencia_endpoint(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar(db, Dependencia, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="No encontrado")
    return {"ok": True}
make_crud(router, "tipos-trabajador", TipoTrabajador, TipoTrabajadorCreate, TipoTrabajadorResponse, "sigarh_mantenimiento")
make_crud(router, "tipos-guardia", TipoGuardia, TipoGuardiaCreate, TipoGuardiaResponse, "sigarh_mantenimiento")
make_crud(router, "niveles-remunerativos", NivelRemunerativo, NivelRemunerativoCreate, NivelRemunerativoResponse, "sigarh_mantenimiento")
# Horarios Guardia (endpoints propios para incluir tipo_guardia)
@router.get("/horarios-guardia", response_model=list[HorarioGuardiaResponse])
async def listar_horarios_endpoint(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    items = await listar_horarios_guardia(db, get_tenant_id(current_user, request))
    return [HorarioGuardiaResponse(
        **{k: v for k, v in item.__dict__.items() if not k.startswith("_")},
        tipo_guardia_nombre=item.tipo_guardia.nombre if item.tipo_guardia else None,
    ) for item in items]

@router.post("/horarios-guardia", response_model=HorarioGuardiaResponse, status_code=201)
async def crear_horario_endpoint(request: Request, data: HorarioGuardiaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    return await crear_horario_guardia(db, get_tenant_id(current_user, request), data)

@router.get("/horarios-guardia/{id}", response_model=HorarioGuardiaResponse)
async def obtener_horario_endpoint(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    item = await obtener_horario_guardia(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="No encontrado")
    return HorarioGuardiaResponse(
        **{k: v for k, v in item.__dict__.items() if not k.startswith("_")},
        tipo_guardia_nombre=item.tipo_guardia.nombre if item.tipo_guardia else None,
    )

@router.patch("/horarios-guardia/{id}", response_model=HorarioGuardiaResponse)
async def actualizar_horario_endpoint(request: Request, id: uuid.UUID, data: HorarioGuardiaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    item = await actualizar_horario_guardia(db, id, get_tenant_id(current_user, request), data)
    if not item: raise HTTPException(404, detail="No encontrado")
    item = await obtener_horario_guardia(db, id, get_tenant_id(current_user, request))
    return HorarioGuardiaResponse(
        **{k: v for k, v in item.__dict__.items() if not k.startswith("_")},
        tipo_guardia_nombre=item.tipo_guardia.nombre if item.tipo_guardia else None,
    )

@router.delete("/horarios-guardia/{id}")
async def eliminar_horario_endpoint(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar(db, HorarioGuardia, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="No encontrado")
    return {"ok": True}
make_crud(router, "grupos-ocupacionales", GrupoOcupacional, GrupoOcupacionalCreate, GrupoOcupacionalResponse, "sigarh_mantenimiento")
make_crud(router, "tipos-actividad", TipoActividad, TipoActividadCreate, TipoActividadResponse, "sigarh_mantenimiento")
make_crud(router, "actividades", Actividad, ActividadCreate, ActividadResponse, "sigarh_mantenimiento")
make_crud(router, "guardias-valorizadas", GuardiaValorizada, GuardiaValorizadaCreate, GuardiaValorizadaResponse, "sigarh_mantenimiento")

# ─── Roles del Sistema ─────────────────────────────────────────────────────

@router.get("/roles-sistema", response_model=list[RolSistemaResponse])
async def listar_roles_sistema(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    return await listar_roles(db, get_tenant_id(current_user, request))


@router.post("/roles-sistema", response_model=RolSistemaResponse, status_code=201)
async def crear_rol_sistema(request: Request, data: RolSistemaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    return await crear_rol(db, get_tenant_id(current_user, request), data)


@router.get("/roles-sistema/{id}", response_model=RolSistemaResponse)
async def obtener_rol_sistema(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    item = await obtener_rol(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="No encontrado")
    return item


@router.patch("/roles-sistema/{id}", response_model=RolSistemaResponse)
async def actualizar_rol_sistema(request: Request, id: uuid.UUID, data: RolSistemaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    item = await actualizar_rol(db, id, get_tenant_id(current_user, request), data)
    if not item: raise HTTPException(404, detail="No encontrado")
    return item


@router.delete("/roles-sistema/{id}")
async def eliminar_rol_sistema(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar(db, RolSistema, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="No encontrado")
    return {"ok": True}


@router.get("/modulos-catalogo", summary="Catálogo de módulos (para checkboxes de roles)")
async def catalogo_modulos_sigarh(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_mantenimiento")),
    current_user: dict = Depends(get_current_user),
):
    from app.tenants.modulos.service import get_all_modules
    modules = await get_all_modules(db)
    return [
        {"id": str(m.id), "code": m.code, "name": m.name, "category": m.category, "is_active": m.is_active}
        for m in modules
    ]


# ─── Perfiles ─────────────────────────────────────────────────────────────────

@router.get("/perfiles-usuario", response_model=list[PerfilUsuarioResponse])
async def listar_perfiles(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    return await listar_perfiles_usuario(db, get_tenant_id(current_user, request))

@router.post("/perfiles-usuario", response_model=PerfilUsuarioResponse, status_code=201)
async def crear_perfil_usuario(request: Request, data: PerfilUsuarioCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    try:
        return await crear_perfil(db, get_tenant_id(current_user, request), data)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc

@router.get("/perfiles-usuario/{id}", response_model=PerfilUsuarioResponse)
async def obtener_perfil(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    item = await obtener_perfil_usuario(db, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="No encontrado")
    return item

@router.patch("/perfiles-usuario/{id}", response_model=PerfilUsuarioResponse)
async def actualizar_perfil(request: Request, id: uuid.UUID, data: PerfilUsuarioCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    try:
        item = await actualizar_perfil_usuario(db, id, get_tenant_id(current_user, request), data)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    if not item: raise HTTPException(404, detail="No encontrado")
    return item

@router.delete("/perfiles-usuario/{id}")
async def eliminar_perfil(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar(db, PerfilUsuario, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="No encontrado")
    return {"ok": True}

# ─── Usuarios SIGARH ──────────────────────────────────────────────────────────

@router.get("/usuarios", response_model=list[UsuarioSigarhResponse])
async def listar_usuarios(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    return await listar(db, UsuarioSigarh, get_tenant_id(current_user, request))

@router.post("/usuarios", response_model=UsuarioSigarhResponse, status_code=201)
async def crear_usuario(request: Request, data: UsuarioSigarhCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    import bcrypt
    hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
    usuario = UsuarioSigarh(
        tenant_id=get_tenant_id(current_user, request),
        empleado_id=data.empleado_id,
        perfil_id=data.perfil_id,
        username=data.username,
        email=data.email,
        password=hashed,
        is_active=data.is_active,
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario

@router.get("/usuarios/{id}", response_model=UsuarioSigarhResponse)
async def obtener_usuario(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    item = await obtener(db, UsuarioSigarh, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="No encontrado")
    return item

@router.patch("/usuarios/{id}", response_model=UsuarioSigarhResponse)
async def actualizar_usuario(request: Request, id: uuid.UUID, data: UsuarioSigarhUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    import bcrypt
    item = await obtener(db, UsuarioSigarh, id, get_tenant_id(current_user, request))
    if not item: raise HTTPException(404, detail="No encontrado")
    cambios = data.model_dump(exclude_unset=True)
    if cambios.get("password"):
        cambios["password"] = bcrypt.hashpw(cambios["password"].encode(), bcrypt.gensalt()).decode()
    else:
        cambios.pop("password", None)
    for field, value in cambios.items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/usuarios/{id}")
async def eliminar_usuario(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_mantenimiento")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar(db, UsuarioSigarh, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="No encontrado")
    return {"ok": True}
