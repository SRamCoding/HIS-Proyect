import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.rrhh.schemas import (
    EmpleadoCreate, EmpleadoUpdate, EmpleadoResponse, EmpleadoListItem,
    EmpleadoEspecialidadCreate, EmpleadoEspecialidadResponse,
    EspecialidadCreate, EspecialidadResponse,
    DiasFeriadoCreate, DiasFeriadoResponse,
    MotivoJustificacionCreate, MotivoJustificacionResponse,
    ToleranciaCreate, ToleranciaResponse,
    RegistroAsistenciaCreate, RegistroAsistenciaResponse,
    JustificacionCreate, JustificacionResponse,
)
from app.sigarh.rrhh.service import (
    listar_empleados, obtener_empleado, obtener_empleado_por_dni,
    crear_empleado, actualizar_empleado, eliminar_empleado,
    agregar_especialidad, eliminar_especialidad,
    listar_especialidades, crear_especialidad,
    actualizar_especialidad, eliminar_especialidad_catalogo,
    listar_feriados, crear_feriado, actualizar_feriado, eliminar_feriado,
    listar_motivos, crear_motivo, actualizar_motivo, eliminar_motivo,
    listar_tolerancias, crear_tolerancia, actualizar_tolerancia, eliminar_tolerancia,
    listar_asistencia, crear_asistencia,
    listar_justificaciones, crear_justificacion, actualizar_justificacion,
)

router = APIRouter()


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id")
    if not tid:
        tid = request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(tid)


# ─── Empleados ────────────────────────────────────────────────────────────────

@router.get("/empleados", response_model=list[EmpleadoListItem])
async def listar(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_empleados(db, get_tenant_id(current_user, request))


@router.post("/empleados", response_model=EmpleadoResponse, status_code=201)
async def crear(
    request: Request,
    data: EmpleadoCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    existente = await obtener_empleado_por_dni(db, data.dni, get_tenant_id(current_user, request))
    if existente:
        raise HTTPException(400, detail=f"Ya existe un empleado con DNI {data.dni}")
    return await crear_empleado(db, get_tenant_id(current_user, request), data)


@router.get("/empleados/buscar-dni/{dni}", response_model=EmpleadoResponse | None)
async def buscar_por_dni(
    request: Request,
    dni: str,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    return await obtener_empleado_por_dni(db, dni, get_tenant_id(current_user, request))


@router.get("/empleados/{id}", response_model=EmpleadoResponse)
async def obtener(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    empleado = await obtener_empleado(db, id, get_tenant_id(current_user, request))
    if not empleado:
        raise HTTPException(404, detail="Empleado no encontrado")
    return empleado


@router.patch("/empleados/{id}", response_model=EmpleadoResponse)
async def actualizar(
    request: Request,
    id: uuid.UUID,
    data: EmpleadoUpdate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    empleado = await actualizar_empleado(db, id, get_tenant_id(current_user, request), data)
    if not empleado:
        raise HTTPException(404, detail="Empleado no encontrado")
    return empleado


@router.delete("/empleados/{id}")
async def eliminar(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    ok = await eliminar_empleado(db, id, get_tenant_id(current_user, request))
    if not ok:
        raise HTTPException(404, detail="Empleado no encontrado")
    return {"ok": True}


# ─── Especialidades del empleado ──────────────────────────────────────────────

@router.post("/empleados/{empleado_id}/especialidades", response_model=EmpleadoEspecialidadResponse, status_code=201)
async def agregar_esp(
    request: Request,
    empleado_id: uuid.UUID,
    data: EmpleadoEspecialidadCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    return await agregar_especialidad(db, empleado_id, data)


@router.delete("/empleados/{empleado_id}/especialidades/{id}")
async def eliminar_esp(
    request: Request,
    empleado_id: uuid.UUID,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    ok = await eliminar_especialidad(db, id)
    if not ok:
        raise HTTPException(404, detail="Especialidad no encontrada")
    return {"ok": True}


# ─── Catálogo de Especialidades ───────────────────────────────────────────────

@router.get("/especialidades", response_model=list[EspecialidadResponse])
async def listar_esp_catalogo(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_especialidades(db, get_tenant_id(current_user, request))


@router.post("/especialidades", response_model=EspecialidadResponse, status_code=201)
async def crear_esp_catalogo(
    request: Request,
    data: EspecialidadCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    return await crear_especialidad(db, get_tenant_id(current_user, request), data)


@router.patch("/especialidades/{id}", response_model=EspecialidadResponse)
async def actualizar_esp_catalogo(
    request: Request,
    id: uuid.UUID,
    data: EspecialidadCreate,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    esp = await actualizar_especialidad(db, id, get_tenant_id(current_user, request), data)
    if not esp:
        raise HTTPException(404, detail="Especialidad no encontrada")
    return esp


@router.delete("/especialidades/{id}")
async def eliminar_esp_catalogo(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    ok = await eliminar_especialidad_catalogo(db, id, get_tenant_id(current_user, request))
    if not ok:
        raise HTTPException(404, detail="Especialidad no encontrada")
    return {"ok": True}


# ─── Días Feriados ────────────────────────────────────────────────────────────

@router.get("/feriados", response_model=list[DiasFeriadoResponse])
async def listar_fer(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    return await listar_feriados(db, get_tenant_id(current_user, request))

@router.post("/feriados", response_model=DiasFeriadoResponse, status_code=201)
async def crear_fer(request: Request, data: DiasFeriadoCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    return await crear_feriado(db, get_tenant_id(current_user, request), data)

@router.patch("/feriados/{id}", response_model=DiasFeriadoResponse)
async def actualizar_fer(request: Request, id: uuid.UUID, data: DiasFeriadoCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    feriado = await actualizar_feriado(db, id, get_tenant_id(current_user, request), data)
    if not feriado: raise HTTPException(404, detail="Feriado no encontrado")
    return feriado

@router.delete("/feriados/{id}")
async def eliminar_fer(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar_feriado(db, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="Feriado no encontrado")
    return {"ok": True}


# ─── Motivos Justificación ────────────────────────────────────────────────────

@router.get("/motivos-justificacion", response_model=list[MotivoJustificacionResponse])
async def listar_mot(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    return await listar_motivos(db, get_tenant_id(current_user, request))

@router.post("/motivos-justificacion", response_model=MotivoJustificacionResponse, status_code=201)
async def crear_mot(request: Request, data: MotivoJustificacionCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    return await crear_motivo(db, get_tenant_id(current_user, request), data)

@router.patch("/motivos-justificacion/{id}", response_model=MotivoJustificacionResponse)
async def actualizar_mot(request: Request, id: uuid.UUID, data: MotivoJustificacionCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    motivo = await actualizar_motivo(db, id, get_tenant_id(current_user, request), data)
    if not motivo: raise HTTPException(404, detail="Motivo no encontrado")
    return motivo

@router.delete("/motivos-justificacion/{id}")
async def eliminar_mot(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar_motivo(db, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="Motivo no encontrado")
    return {"ok": True}


# ─── Tolerancias ──────────────────────────────────────────────────────────────

@router.get("/tolerancias", response_model=list[ToleranciaResponse])
async def listar_tol(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    return await listar_tolerancias(db, get_tenant_id(current_user, request))

@router.post("/tolerancias", response_model=ToleranciaResponse, status_code=201)
async def crear_tol(request: Request, data: ToleranciaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    return await crear_tolerancia(db, get_tenant_id(current_user, request), data)

@router.patch("/tolerancias/{id}", response_model=ToleranciaResponse)
async def actualizar_tol(request: Request, id: uuid.UUID, data: ToleranciaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    tol = await actualizar_tolerancia(db, id, get_tenant_id(current_user, request), data)
    if not tol: raise HTTPException(404, detail="Tolerancia no encontrada")
    return tol

@router.delete("/tolerancias/{id}")
async def eliminar_tol(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    ok = await eliminar_tolerancia(db, id, get_tenant_id(current_user, request))
    if not ok: raise HTTPException(404, detail="Tolerancia no encontrada")
    return {"ok": True}


# ─── Registro Asistencia ──────────────────────────────────────────────────────

@router.get("/asistencia", response_model=list[RegistroAsistenciaResponse])
async def listar_asis(
    request: Request,
    fecha: date | None = None,
    empleado_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_asistencia(db, get_tenant_id(current_user, request), fecha, empleado_id)

@router.post("/asistencia", response_model=RegistroAsistenciaResponse, status_code=201)
async def crear_asis(request: Request, data: RegistroAsistenciaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    return await crear_asistencia(db, get_tenant_id(current_user, request), data)


# ─── Justificaciones ──────────────────────────────────────────────────────────

@router.get("/justificaciones", response_model=list[JustificacionResponse])
async def listar_just(
    request: Request,
    empleado_id: uuid.UUID | None = None,
    estado: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt("sigarh_recursos_humanos")),
    current_user: dict = Depends(get_current_user),
):
    return await listar_justificaciones(db, get_tenant_id(current_user, request), empleado_id, estado)

@router.post("/justificaciones", response_model=JustificacionResponse, status_code=201)
async def crear_just(request: Request, data: JustificacionCreate, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    return await crear_justificacion(db, get_tenant_id(current_user, request), data)

@router.patch("/justificaciones/{id}")
async def actualizar_just(request: Request, id: uuid.UUID, data: dict, db: AsyncSession = Depends(get_db), tenant=Depends(require_module_jwt("sigarh_recursos_humanos")), current_user: dict = Depends(get_current_user)):
    just = await actualizar_justificacion(db, id, get_tenant_id(current_user, request), data)
    if not just: raise HTTPException(404, detail="Justificacion no encontrada")
    return just