import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.movimientos.schemas import (
    CambioTurnoCreate, CambioTurnoResponse,
    PapeletaCreate, PapeletaResponse,
    JustificacionCreate, JustificacionUpdate, JustificacionResponse, JustificacionDecision,
)
from app.sigarh.movimientos import service as svc
from app.sigarh.movimientos.service import (
    listar_licencias_unif, crear_licencia_unif, listar_just_vac, crear_just_vac,
)
from app.sigarh.rrhh import service as rrhh_svc

router = APIRouter()
_MOD = require_module_jwt("sigarh_movimientos")


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id")
    if not tid:
        tid = request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(tid)


def _nombre(cu: dict) -> str | None:
    return cu.get("name") or cu.get("email")


# ─── Catálogos auxiliares (para los formularios de trámite) ───────────────────

@router.get("/empleados", summary="Empleados para buscar en los formularios")
async def mov_empleados(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    emps = await rrhh_svc.listar_empleados(db, get_tenant_id(current_user, request))
    return [{"id": e.id, "dni": e.dni, "nombre_completo": e.nombre_completo,
             "cargo_laboral": e.cargo_laboral, "modalidad": e.modalidad, "is_active": e.is_active} for e in emps]


@router.get("/empleados/buscar-dni/{dni}", summary="Buscar un empleado por DNI")
async def mov_buscar_dni(request: Request, dni: str, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    e = await rrhh_svc.obtener_empleado_por_dni(db, dni, get_tenant_id(current_user, request))
    if not e:
        raise HTTPException(404, detail=f"No se encontró un empleado con DNI {dni}")
    return {"id": e.id, "dni": e.dni, "nombre_completo": e.nombre_completo,
            "cargo_laboral": e.cargo_laboral, "modalidad": e.modalidad, "is_active": e.is_active}


@router.get("/motivos", summary="Motivos de justificación activos")
async def mov_motivos(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return [m for m in await rrhh_svc.listar_motivos(db, get_tenant_id(current_user, request)) if m.get("is_active", True)]


@router.get("/servicios", summary="Servicios (para cambio de turno)")
async def mov_servicios(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    from app.sigarh.mantenimiento.service import listar_servicios
    items = await listar_servicios(db, get_tenant_id(current_user, request))
    return [{"id": s.id, "nombre": s.nombre} for s in items if getattr(s, "is_active", True)]


# ─── Justificación y Vacaciones (bandeja) ─────────────────────────────────────

@router.get("/vacaciones", response_model=list[JustificacionResponse])
async def listar_vac(
    request: Request, estado: str | None = None, motivo_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user),
):
    return await listar_just_vac(db, get_tenant_id(current_user, request), estado, motivo_id)


@router.post("/vacaciones", response_model=JustificacionResponse, status_code=201)
async def crear_vac(
    request: Request, data: JustificacionCreate,
    db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user),
):
    return await crear_just_vac(db, get_tenant_id(current_user, request), data, _nombre(current_user))


@router.patch("/vacaciones/{id}", response_model=JustificacionResponse)
async def actualizar_vac(
    request: Request, id: uuid.UUID, data: JustificacionUpdate,
    db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user),
):
    item = await rrhh_svc.actualizar_justificacion(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="No encontrado")
    return item


@router.post("/vacaciones/{id}/aprobar", response_model=JustificacionResponse)
async def aprobar_vac(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await _decidir(db, id, get_tenant_id(current_user, request), True, _nombre(current_user))


@router.post("/vacaciones/{id}/rechazar", response_model=JustificacionResponse)
async def rechazar_vac(request: Request, id: uuid.UUID, data: JustificacionDecision, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await _decidir(db, id, get_tenant_id(current_user, request), False, _nombre(current_user), data.motivo_rechazo)


# ─── Tramitar / Estado Licencia (tipo="licencia") ────────────────────────────

@router.get("/licencias", response_model=list[JustificacionResponse])
async def listar_lic(
    request: Request, estado: str | None = None,
    db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user),
):
    return await listar_licencias_unif(db, get_tenant_id(current_user, request), estado)


@router.post("/licencias", response_model=JustificacionResponse, status_code=201)
async def crear_lic(
    request: Request, data: JustificacionCreate,
    db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user),
):
    return await crear_licencia_unif(db, get_tenant_id(current_user, request), data, _nombre(current_user))


@router.get("/licencias/{id}", response_model=JustificacionResponse)
async def obtener_lic(
    request: Request, id: uuid.UUID,
    db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user),
):
    tid = get_tenant_id(current_user, request)
    j = await rrhh_svc._just_orm(db, id, tid)
    if not j:
        raise HTTPException(404, detail="No encontrado")
    return (await rrhh_svc._serializar_justificaciones(db, tid, [j]))[0]


@router.patch("/licencias/{id}", response_model=JustificacionResponse)
async def actualizar_lic(
    request: Request, id: uuid.UUID, data: JustificacionUpdate,
    db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user),
):
    item = await rrhh_svc.actualizar_justificacion(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="No encontrado")
    return item


@router.post("/licencias/{id}/aprobar", response_model=JustificacionResponse)
async def aprobar_lic(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await _decidir(db, id, get_tenant_id(current_user, request), True, _nombre(current_user))


@router.post("/licencias/{id}/rechazar", response_model=JustificacionResponse)
async def rechazar_lic(request: Request, id: uuid.UUID, data: JustificacionDecision, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await _decidir(db, id, get_tenant_id(current_user, request), False, _nombre(current_user), data.motivo_rechazo)


async def _decidir(db, id, tid, aprobar, revisor, motivo_rechazo=None):
    try:
        j = await rrhh_svc.decidir_justificacion(db, id, tid, aprobar, revisor, motivo_rechazo)
    except rrhh_svc.ReglaNegocioError as e:
        raise HTTPException(409, detail=str(e))
    if not j:
        raise HTTPException(404, detail="No encontrado")
    return j


async def _ct_decidir(db, id, tid, aprobar, revisor, motivo_rechazo=None):
    try:
        c = await svc.decidir_cambio_turno(db, id, tid, aprobar, revisor, motivo_rechazo)
    except svc.ReglaNegocioError as e:
        raise HTTPException(409, detail=str(e))
    if not c:
        raise HTTPException(404, detail="No encontrado")
    return c


async def _pap_decidir(db, id, tid, aprobar, revisor, motivo_rechazo=None):
    try:
        p = await svc.decidir_papeleta(db, id, tid, aprobar, revisor, motivo_rechazo)
    except svc.ReglaNegocioError as e:
        raise HTTPException(409, detail=str(e))
    if not p:
        raise HTTPException(404, detail="No encontrado")
    return p


# ─── Cambio de Turno ──────────────────────────────────────────────────────────

@router.get("/cambio-turno", response_model=list[CambioTurnoResponse])
async def listar_ct(request: Request, estado: str | None = None, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await svc.listar_cambios_turno(db, get_tenant_id(current_user, request), estado)


@router.post("/cambio-turno", response_model=CambioTurnoResponse, status_code=201)
async def crear_ct(request: Request, data: CambioTurnoCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        return await svc.crear_cambio_turno(db, get_tenant_id(current_user, request), data, _nombre(current_user))
    except svc.ReglaNegocioError as e:
        raise HTTPException(409, detail=str(e))


@router.post("/cambio-turno/{id}/aprobar", response_model=CambioTurnoResponse)
async def aprobar_ct(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await _ct_decidir(db, id, get_tenant_id(current_user, request), True, _nombre(current_user))


@router.post("/cambio-turno/{id}/rechazar", response_model=CambioTurnoResponse)
async def rechazar_ct(request: Request, id: uuid.UUID, data: JustificacionDecision, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await _ct_decidir(db, id, get_tenant_id(current_user, request), False, _nombre(current_user), data.motivo_rechazo)


# ─── Papeletas ────────────────────────────────────────────────────────────────

@router.get("/papeletas", response_model=list[PapeletaResponse])
async def listar_pap(request: Request, estado: str | None = None, fecha: date | None = None, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await svc.listar_papeletas(db, get_tenant_id(current_user, request), estado, fecha)


@router.post("/papeletas", response_model=PapeletaResponse, status_code=201)
async def crear_pap(request: Request, data: PapeletaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        return await svc.crear_papeleta(db, get_tenant_id(current_user, request), data, _nombre(current_user))
    except svc.ReglaNegocioError as e:
        raise HTTPException(409, detail=str(e))


@router.patch("/papeletas/{id}", response_model=PapeletaResponse)
async def actualizar_pap(request: Request, id: uuid.UUID, data: dict, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    item = await svc.actualizar_papeleta(db, id, get_tenant_id(current_user, request), data)
    if not item:
        raise HTTPException(404, detail="No encontrado")
    return item


@router.post("/papeletas/{id}/aprobar", response_model=PapeletaResponse)
async def aprobar_pap(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await _pap_decidir(db, id, get_tenant_id(current_user, request), True, _nombre(current_user))


@router.post("/papeletas/{id}/rechazar", response_model=PapeletaResponse)
async def rechazar_pap(request: Request, id: uuid.UUID, data: JustificacionDecision, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    return await _pap_decidir(db, id, get_tenant_id(current_user, request), False, _nombre(current_user), data.motivo_rechazo)


@router.post("/papeletas/{id}/registrar-retorno", response_model=PapeletaResponse)
async def retorno_pap(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD), current_user: dict = Depends(get_current_user)):
    try:
        p = await svc.registrar_retorno_papeleta(db, id, get_tenant_id(current_user, request))
    except svc.ReglaNegocioError as e:
        raise HTTPException(409, detail=str(e))
    if not p:
        raise HTTPException(404, detail="No encontrado")
    return p