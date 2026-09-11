import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.creacion_roles.models import MODALIDADES, Rol
from app.sigarh.rrhh.models import Empleado
from app.sigarh.creacion_roles.schemas import (
    RolCreate, RolUpdate, RolListItem, RolDetail,
    PersonalRequest, ActividadesRequest, TurnoRequest,
)
from app.sigarh.creacion_roles import service as svc

router = APIRouter()
_MOD = require_module_jwt("sigarh_creacion_roles")


def _tid(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


def _nombre(current_user: dict) -> str | None:
    return current_user.get("name") or current_user.get("email")


def _rn(exc: svc.ReglaNegocioError):
    return HTTPException(409, detail=str(exc))


# ─── Config para el frontend ─────────────────────────────────────────────────

@router.get("/modalidades")
async def modalidades(tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return MODALIDADES


@router.get("/personal-disponible")
async def personal_disponible(
    request: Request,
    servicio_id: uuid.UUID | None = None,
    rol_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD),
    current_user: dict = Depends(get_current_user),
):
    tid = _tid(current_user, request)
    stmt = select(Empleado).where(Empleado.tenant_id == tid, Empleado.is_active.is_(True))
    if servicio_id:
        stmt = stmt.where(Empleado.servicio_id == servicio_id)
    emps = (await db.execute(stmt.order_by(Empleado.apellido_paterno))).scalars().all()

    if rol_id:
        categoria = await db.scalar(select(Rol.categoria_personal).where(Rol.id == rol_id, Rol.tenant_id == tid))
        if categoria:
            categorias = await svc.categorias_de_empleados(db, emps)
            emps = [e for e in emps if categorias.get(e.id) == categoria]

    return [
        {"id": str(e.id), "nombre_completo": e.nombre_completo, "dni": e.dni, "cargo_laboral": e.cargo_laboral}
        for e in emps
    ]


# ─── Roles (borrador / rechazados) ───────────────────────────────────────────

@router.get("/roles", response_model=list[RolListItem])
async def listar(
    request: Request,
    categoria: str | None = None,
    tipo: str | None = None,
    anio: int | None = None,
    mes: int | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(_MOD),
    current_user: dict = Depends(get_current_user),
):
    return await svc.listar_roles(
        db, _tid(current_user, request),
        status_in=["draft", "rejected"], categoria=categoria, tipo=tipo, anio=anio, mes=mes,
    )


@router.post("/roles", response_model=RolDetail, status_code=201)
async def crear(request: Request, data: RolCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        return await svc.crear_rol(db, _tid(current_user, request), data, _nombre(current_user), uuid.UUID(current_user["sub"]))
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e


@router.get("/roles/{rol_id}", response_model=RolDetail)
async def obtener(request: Request, rol_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    tid = _tid(current_user, request)
    rol = await svc.obtener_rol_orm(db, rol_id, tid)
    if not rol:
        raise HTTPException(404, detail="Rol no encontrado")
    return await svc.serializar_uno(db, tid, rol)


@router.get("/roles/{rol_id}/diagnostico")
async def diagnostico(request: Request, rol_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    tid = _tid(current_user, request)
    rol = await svc.obtener_rol_orm(db, rol_id, tid)
    if not rol:
        raise HTTPException(404, detail="Rol no encontrado")
    return await svc.diagnosticar_rol(db, tid, rol)


@router.patch("/roles/{rol_id}", response_model=RolDetail)
async def actualizar(request: Request, rol_id: uuid.UUID, data: RolUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        rol = await svc.actualizar_rol(db, _tid(current_user, request), rol_id, data)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e
    if not rol:
        raise HTTPException(404, detail="Rol no encontrado")
    return rol


@router.delete("/roles/{rol_id}")
async def eliminar(request: Request, rol_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        ok = await svc.eliminar_rol(db, _tid(current_user, request), rol_id)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e
    if not ok:
        raise HTTPException(404, detail="Rol no encontrado")
    return {"ok": True}


@router.post("/roles/{rol_id}/enviar", response_model=RolDetail)
async def enviar(request: Request, rol_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        rol = await svc.enviar_rol(db, _tid(current_user, request), rol_id)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e
    if not rol:
        raise HTTPException(404, detail="Rol no encontrado")
    return rol


# ─── Builder anidado: personal / actividades / turnos ────────────────────────

@router.post("/roles/{rol_id}/personal", response_model=RolDetail)
async def add_personal(request: Request, rol_id: uuid.UUID, data: PersonalRequest, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        return await svc.agregar_personal(db, _tid(current_user, request), rol_id, data.empleado_ids)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e


@router.delete("/roles/personal/{rol_empleado_id}", response_model=RolDetail)
async def del_personal(request: Request, rol_empleado_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        return await svc.quitar_personal(db, _tid(current_user, request), rol_empleado_id)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e


@router.post("/roles/personal/{rol_empleado_id}/actividades", response_model=RolDetail)
async def add_actividades(request: Request, rol_empleado_id: uuid.UUID, data: ActividadesRequest, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        return await svc.agregar_actividades(db, _tid(current_user, request), rol_empleado_id, data.actividad_ids)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e


@router.delete("/roles/actividades/{rol_actividad_id}", response_model=RolDetail)
async def del_actividad(request: Request, rol_actividad_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        return await svc.quitar_actividad(db, _tid(current_user, request), rol_actividad_id)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e


@router.post("/roles/actividades/{rol_actividad_id}/turnos", response_model=RolDetail)
async def add_turno(request: Request, rol_actividad_id: uuid.UUID, data: TurnoRequest, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        return await svc.agregar_turno(db, _tid(current_user, request), rol_actividad_id, data)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e


@router.delete("/roles/turnos/{rol_turno_id}", response_model=RolDetail)
async def del_turno(request: Request, rol_turno_id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        return await svc.quitar_turno(db, _tid(current_user, request), rol_turno_id)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e
