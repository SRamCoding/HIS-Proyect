import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_db_central
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt
from app.sigarh.rrhh.schemas import (
    EmpleadoCreate, EmpleadoUpdate, EmpleadoResponse, EmpleadoListItem,
    EmpleadoEspecialidadCreate, EmpleadoEspecialidadResponse,
    EspecialidadCreate, EspecialidadUpdate, EspecialidadResponse,
    DiasFeriadoCreate, DiasFeriadoUpdate, DiasFeriadoResponse,
    MotivoJustificacionCreate, MotivoJustificacionUpdate, MotivoJustificacionResponse,
    ToleranciaCreate, ToleranciaUpdate, ToleranciaResponse,
    RegistroAsistenciaCreate, RegistroAsistenciaUpdate, RegistroAsistenciaResponse,
    JustificacionCreate, JustificacionUpdate, JustificacionResponse, JustificacionDecision,
)
from app.sigarh.rrhh import service as svc

router = APIRouter()
# Un rol con el código completo "sigarh_recursos_humanos" sigue teniendo acceso
# a todo (ver permiso_incluye en app/tenants/modulos/submodulos.py); un rol más
# fino puede limitarse a uno solo de estos submódulos.
_MOD_EMPLEADOS = require_module_jwt("sigarh_recursos_humanos.empleados")
_MOD_ESPECIALIDADES = require_module_jwt("sigarh_recursos_humanos.especialidades")
_MOD_FERIADOS = require_module_jwt("sigarh_recursos_humanos.feriados")
_MOD_MOTIVOS = require_module_jwt("sigarh_recursos_humanos.motivos_justificacion")
_MOD_TOLERANCIAS = require_module_jwt("sigarh_recursos_humanos.tolerancias")
_MOD_ASISTENCIA = require_module_jwt("sigarh_recursos_humanos.asistencia")
_MOD_JUSTIFICACIONES = require_module_jwt("sigarh_recursos_humanos.justificaciones")


async def _referencia_especialidades(request: Request, current_user=Depends(get_current_user)):
    codes = ("sigarh_recursos_humanos.especialidades", "sigarh_recursos_humanos.empleados",
             "sigarh_mantenimiento.servicios", "sigarh_infraestructura.consultorios")
    for code in codes:
        try:
            return await require_module_jwt(code)(request=request, current_user=current_user)
        except HTTPException as error:
            if error.status_code != 403:
                raise
    raise HTTPException(403, "Su perfil no permite consultar especialidades")


def _tid(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


def _nombre(cu: dict) -> str | None:
    return cu.get("name") or cu.get("email")


def _rn(e: svc.ReglaNegocioError):
    return HTTPException(409, detail=str(e))


# ─── Empleados ────────────────────────────────────────────────────────────────

@router.get("/empleados/catalogos")
async def catalogos_empleado(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_EMPLEADOS)):
    from sqlalchemy import select
    from app.sigarh.mantenimiento.models import TipoTrabajador, NivelRemunerativo, GrupoOcupacional, Departamento, Servicio, Profesion
    tid = _tid(tenant, request)
    result = {}
    for key, model in (("tipos_trabajador", TipoTrabajador), ("niveles_remunerativos", NivelRemunerativo), ("grupos_ocupacionales", GrupoOcupacional), ("departamentos", Departamento), ("servicios", Servicio), ("profesiones", Profesion)):
        items = (await db.scalars(select(model).where(model.tenant_id == tid, model.is_active.is_(True)).order_by(model.nombre))).all()
        result[key] = [svc._cols(i) for i in items]
    return result


@router.get("/vinculos-laborales")
async def vinculos_laborales(db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_EMPLEADOS)):
    from sqlalchemy import select
    from app.sigarh.rrhh.models import VinculoLaboral
    items = (await db.scalars(select(VinculoLaboral).where(VinculoLaboral.is_active.is_(True)).order_by(VinculoLaboral.regimen_codigo, VinculoLaboral.condicion_nombre))).all()
    return [{"codigo": i.codigo, "regimen_codigo": i.regimen_codigo, "regimen_nombre": i.regimen_nombre,
             "condicion_nombre": i.condicion_nombre, "norma": i.norma, "fuente_url": i.fuente_url} for i in items]


@router.get("/empleados", response_model=list[EmpleadoListItem])
async def listar(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_EMPLEADOS), current_user: dict = Depends(get_current_user)):
    return await svc.listar_empleados(db, _tid(current_user, request))


@router.post("/empleados", response_model=EmpleadoResponse, status_code=201)
async def crear(request: Request, data: EmpleadoCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_EMPLEADOS), current_user: dict = Depends(get_current_user)):
    tid = _tid(current_user, request)
    if await svc.obtener_empleado_por_dni(db, data.dni, tid):
        raise HTTPException(400, detail=f"Ya existe un empleado con DNI {data.dni}")
    try:
        return await svc.crear_empleado(db, tid, data)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e


@router.get("/empleados/buscar-dni/{dni}", response_model=EmpleadoResponse | None)
async def buscar_por_dni(request: Request, dni: str, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_EMPLEADOS), current_user: dict = Depends(get_current_user)):
    return await svc.obtener_empleado_por_dni(db, dni, _tid(current_user, request))


@router.get("/dni-lookup/{dni}", summary="Consultar DNI en el servicio externo (autocompletado)")
async def dni_lookup(dni: str, tenant=Depends(_MOD_EMPLEADOS), current_user: dict = Depends(get_current_user)):
    from app.shared.dni import lookup_dni_externo
    if not dni.isdigit() or len(dni) != 8:
        raise HTTPException(400, detail="El DNI debe tener 8 dígitos numéricos")
    datos = await lookup_dni_externo(dni)
    nombres = (datos or {}).get("nombres", "").strip()
    ap_pat = (datos or {}).get("apellidoPaterno", "").strip()
    ap_mat = (datos or {}).get("apellidoMaterno", "").strip()
    # El proveedor responde 200 con todos los campos vacíos cuando el DNI no existe.
    if not nombres and not ap_pat and not ap_mat:
        raise HTTPException(404, detail="No se encontraron datos para ese DNI en el servicio externo")
    return {"nombres": nombres, "apellido_paterno": ap_pat, "apellido_materno": ap_mat}


@router.get("/ubigeo/departamentos", summary="Catálogo ubigeo: departamentos")
async def ubigeo_departamentos(db: AsyncSession = Depends(get_db_central), tenant=Depends(_MOD_EMPLEADOS), current_user: dict = Depends(get_current_user)):
    from app.shared.ubigeo.service import get_departamentos
    return [{"id": d.id, "nombre": d.nombre} for d in await get_departamentos(db)]


@router.get("/ubigeo/provincias/{departamento_id}", summary="Catálogo ubigeo: provincias de un departamento")
async def ubigeo_provincias(departamento_id: str, db: AsyncSession = Depends(get_db_central), tenant=Depends(_MOD_EMPLEADOS), current_user: dict = Depends(get_current_user)):
    from app.shared.ubigeo.service import get_provincias
    return [{"id": p.id, "nombre": p.nombre} for p in await get_provincias(db, departamento_id)]


@router.get("/ubigeo/distritos/{provincia_id}", summary="Catálogo ubigeo: distritos de una provincia")
async def ubigeo_distritos(provincia_id: str, db: AsyncSession = Depends(get_db_central), tenant=Depends(_MOD_EMPLEADOS), current_user: dict = Depends(get_current_user)):
    from app.shared.ubigeo.service import get_distritos
    return [{"id": d.id, "nombre": d.nombre} for d in await get_distritos(db, provincia_id)]


@router.get("/empleados/{id}", response_model=EmpleadoResponse)
async def obtener(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_EMPLEADOS), current_user: dict = Depends(get_current_user)):
    emp = await svc.obtener_empleado(db, id, _tid(current_user, request))
    if not emp:
        raise HTTPException(404, detail="Empleado no encontrado")
    return emp


@router.patch("/empleados/{id}", response_model=EmpleadoResponse)
async def actualizar(request: Request, id: uuid.UUID, data: EmpleadoUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_EMPLEADOS), current_user: dict = Depends(get_current_user)):
    try:
        emp = await svc.actualizar_empleado(db, id, _tid(current_user, request), data)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e
    if not emp:
        raise HTTPException(404, detail="Empleado no encontrado")
    return emp


@router.delete("/empleados/{id}")
async def eliminar(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_EMPLEADOS), current_user: dict = Depends(get_current_user)):
    ok = await svc.eliminar_empleado(db, id, _tid(current_user, request))
    if not ok:
        raise HTTPException(404, detail="Empleado no encontrado")
    return {"ok": True}


# ─── Especialidades del empleado ──────────────────────────────────────────────

@router.post("/empleados/{empleado_id}/especialidades", response_model=EmpleadoEspecialidadResponse, status_code=201)
async def agregar_esp(request: Request, empleado_id: uuid.UUID, data: EmpleadoEspecialidadCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_EMPLEADOS), current_user: dict = Depends(get_current_user)):
    if not await svc.obtener_empleado(db, empleado_id, _tid(current_user, request)):
        raise HTTPException(404, detail="Empleado no encontrado")
    try:
        return await svc.agregar_especialidad(db, empleado_id, data)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e


@router.delete("/empleados/{empleado_id}/especialidades/{id}")
async def eliminar_esp(request: Request, empleado_id: uuid.UUID, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_EMPLEADOS), current_user: dict = Depends(get_current_user)):
    if not await svc.eliminar_especialidad(db, id):
        raise HTTPException(404, detail="Especialidad no encontrada")
    return {"ok": True}


# ─── Catálogo de Especialidades ───────────────────────────────────────────────

@router.get("/especialidades", response_model=list[EspecialidadResponse])
async def listar_esp(request: Request, active_only: bool = False, db: AsyncSession = Depends(get_db), tenant=Depends(_referencia_especialidades), current_user: dict = Depends(get_current_user)):
    return await svc.listar_especialidades(db, _tid(current_user, request), active_only)


@router.post("/especialidades", response_model=EspecialidadResponse, status_code=201)
async def crear_esp(request: Request, data: EspecialidadCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_ESPECIALIDADES), current_user: dict = Depends(get_current_user)):
    try:
        return await svc.crear_especialidad(db, _tid(current_user, request), data)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e


@router.get("/especialidades/{id}", response_model=EspecialidadResponse)
async def obtener_esp(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_ESPECIALIDADES), current_user: dict = Depends(get_current_user)):
    tid = _tid(current_user, request)
    items = await svc.listar_especialidades(db, tid)
    esp = next((e for e in items if str(e["id"]) == str(id)), None)
    if not esp:
        raise HTTPException(404, detail="Especialidad no encontrada")
    return esp


@router.patch("/especialidades/{id}", response_model=EspecialidadResponse)
async def actualizar_esp(request: Request, id: uuid.UUID, data: EspecialidadUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_ESPECIALIDADES), current_user: dict = Depends(get_current_user)):
    try:
        esp = await svc.actualizar_especialidad(db, id, _tid(current_user, request), data)
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e
    if not esp:
        raise HTTPException(404, detail="Especialidad no encontrada")
    return esp


@router.delete("/especialidades/{id}")
async def eliminar_esp_cat(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_ESPECIALIDADES), current_user: dict = Depends(get_current_user)):
    try:
        ok = await svc.eliminar_especialidad_catalogo(db, id, _tid(current_user, request))
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e
    if not ok:
        raise HTTPException(404, detail="Especialidad no encontrada")
    return {"ok": True}


# ─── Días Feriados ────────────────────────────────────────────────────────────

@router.get("/feriados", response_model=list[DiasFeriadoResponse])
async def listar_fer(request: Request, anio: int | None = None, mes: int | None = None, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_FERIADOS), current_user: dict = Depends(get_current_user)):
    return await svc.listar_feriados(db, _tid(current_user, request), anio, mes)


@router.post("/feriados", response_model=DiasFeriadoResponse, status_code=201)
async def crear_fer(request: Request, data: DiasFeriadoCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_FERIADOS), current_user: dict = Depends(get_current_user)):
    return await svc.crear_feriado(db, _tid(current_user, request), data)


@router.get("/feriados/{id}", response_model=DiasFeriadoResponse)
async def obtener_fer(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_FERIADOS), current_user: dict = Depends(get_current_user)):
    items = await svc.listar_feriados(db, _tid(current_user, request))
    fer = next((f for f in items if str(f.id) == str(id)), None)
    if not fer:
        raise HTTPException(404, detail="Feriado no encontrado")
    return fer


@router.patch("/feriados/{id}", response_model=DiasFeriadoResponse)
async def actualizar_fer(request: Request, id: uuid.UUID, data: DiasFeriadoUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_FERIADOS), current_user: dict = Depends(get_current_user)):
    fer = await svc.actualizar_feriado(db, id, _tid(current_user, request), data)
    if not fer:
        raise HTTPException(404, detail="Feriado no encontrado")
    return fer


@router.delete("/feriados/{id}")
async def eliminar_fer(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_FERIADOS), current_user: dict = Depends(get_current_user)):
    if not await svc.eliminar_feriado(db, id, _tid(current_user, request)):
        raise HTTPException(404, detail="Feriado no encontrado")
    return {"ok": True}


# ─── Motivos Justificación ────────────────────────────────────────────────────

@router.get("/motivos-justificacion", response_model=list[MotivoJustificacionResponse])
async def listar_mot(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_MOTIVOS), current_user: dict = Depends(get_current_user)):
    return await svc.listar_motivos(db, _tid(current_user, request))


@router.post("/motivos-justificacion", response_model=MotivoJustificacionResponse, status_code=201)
async def crear_mot(request: Request, data: MotivoJustificacionCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_MOTIVOS), current_user: dict = Depends(get_current_user)):
    return await svc.crear_motivo(db, _tid(current_user, request), data)


@router.get("/motivos-justificacion/{id}", response_model=MotivoJustificacionResponse)
async def obtener_mot(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_MOTIVOS), current_user: dict = Depends(get_current_user)):
    items = await svc.listar_motivos(db, _tid(current_user, request))
    mot = next((m for m in items if str(m["id"]) == str(id)), None)
    if not mot:
        raise HTTPException(404, detail="Motivo no encontrado")
    return mot


@router.patch("/motivos-justificacion/{id}", response_model=MotivoJustificacionResponse)
async def actualizar_mot(request: Request, id: uuid.UUID, data: MotivoJustificacionUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_MOTIVOS), current_user: dict = Depends(get_current_user)):
    mot = await svc.actualizar_motivo(db, id, _tid(current_user, request), data)
    if not mot:
        raise HTTPException(404, detail="Motivo no encontrado")
    return mot


@router.delete("/motivos-justificacion/{id}")
async def eliminar_mot(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_MOTIVOS), current_user: dict = Depends(get_current_user)):
    try:
        ok = await svc.eliminar_motivo(db, id, _tid(current_user, request))
    except svc.ReglaNegocioError as e:
        raise _rn(e) from e
    if not ok:
        raise HTTPException(404, detail="Motivo no encontrado")
    return {"ok": True}


# ─── Tolerancias ──────────────────────────────────────────────────────────────

@router.get("/tolerancias", response_model=list[ToleranciaResponse])
async def listar_tol(request: Request, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_TOLERANCIAS), current_user: dict = Depends(get_current_user)):
    return await svc.listar_tolerancias(db, _tid(current_user, request))


@router.post("/tolerancias", response_model=ToleranciaResponse, status_code=201)
async def crear_tol(request: Request, data: ToleranciaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_TOLERANCIAS), current_user: dict = Depends(get_current_user)):
    return await svc.crear_tolerancia(db, _tid(current_user, request), data)


@router.get("/tolerancias/{id}", response_model=ToleranciaResponse)
async def obtener_tol(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_TOLERANCIAS), current_user: dict = Depends(get_current_user)):
    items = await svc.listar_tolerancias(db, _tid(current_user, request))
    tol = next((t for t in items if str(t["id"]) == str(id)), None)
    if not tol:
        raise HTTPException(404, detail="Tolerancia no encontrada")
    return tol


@router.patch("/tolerancias/{id}", response_model=ToleranciaResponse)
async def actualizar_tol(request: Request, id: uuid.UUID, data: ToleranciaUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_TOLERANCIAS), current_user: dict = Depends(get_current_user)):
    tol = await svc.actualizar_tolerancia(db, id, _tid(current_user, request), data)
    if not tol:
        raise HTTPException(404, detail="Tolerancia no encontrada")
    return tol


@router.delete("/tolerancias/{id}")
async def eliminar_tol(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_TOLERANCIAS), current_user: dict = Depends(get_current_user)):
    if not await svc.eliminar_tolerancia(db, id, _tid(current_user, request)):
        raise HTTPException(404, detail="Tolerancia no encontrada")
    return {"ok": True}


# ─── Registro Asistencia ──────────────────────────────────────────────────────

@router.get("/asistencia", response_model=list[RegistroAsistenciaResponse])
async def listar_asis(
    request: Request,
    fecha: date | None = None,
    empleado_id: uuid.UUID | None = None,
    grupo_ocupacional_id: uuid.UUID | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    solo_tardanza: bool = False,
    db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_ASISTENCIA), current_user: dict = Depends(get_current_user),
):
    return await svc.listar_asistencia(
        db, _tid(current_user, request), fecha, empleado_id, grupo_ocupacional_id, desde, hasta, solo_tardanza,
    )


@router.post("/asistencia", response_model=RegistroAsistenciaResponse, status_code=201)
async def crear_asis(request: Request, data: RegistroAsistenciaCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_ASISTENCIA), current_user: dict = Depends(get_current_user)):
    return await svc.crear_asistencia(db, _tid(current_user, request), data, _nombre(current_user))


@router.get("/asistencia/{id}", response_model=RegistroAsistenciaResponse)
async def obtener_asis(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_ASISTENCIA), current_user: dict = Depends(get_current_user)):
    tid = _tid(current_user, request)
    r = await svc._asis_orm(db, id, tid)
    if not r:
        raise HTTPException(404, detail="Registro no encontrado")
    return (await svc._serializar_asistencia(db, tid, [r]))[0]


@router.patch("/asistencia/{id}", response_model=RegistroAsistenciaResponse)
async def actualizar_asis(request: Request, id: uuid.UUID, data: RegistroAsistenciaUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_ASISTENCIA), current_user: dict = Depends(get_current_user)):
    r = await svc.actualizar_asistencia(db, id, _tid(current_user, request), data)
    if not r:
        raise HTTPException(404, detail="Registro no encontrado")
    return r


@router.delete("/asistencia/{id}")
async def eliminar_asis(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_ASISTENCIA), current_user: dict = Depends(get_current_user)):
    if not await svc.eliminar_asistencia(db, id, _tid(current_user, request)):
        raise HTTPException(404, detail="Registro no encontrado")
    return {"ok": True}


# ─── Justificaciones ──────────────────────────────────────────────────────────

@router.get("/justificaciones", response_model=list[JustificacionResponse])
async def listar_just(
    request: Request,
    empleado_id: uuid.UUID | None = None,
    estado: str | None = None,
    motivo_id: uuid.UUID | None = None,
    tipo: str | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_JUSTIFICACIONES), current_user: dict = Depends(get_current_user),
):
    return await svc.listar_justificaciones(db, _tid(current_user, request), empleado_id, estado, motivo_id, tipo, desde, hasta)


@router.post("/justificaciones", response_model=JustificacionResponse, status_code=201)
async def crear_just(request: Request, data: JustificacionCreate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_JUSTIFICACIONES), current_user: dict = Depends(get_current_user)):
    return await svc.crear_justificacion(db, _tid(current_user, request), data, _nombre(current_user))


@router.post("/justificaciones/{id}/aprobar", response_model=JustificacionResponse)
async def aprobar_just(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_JUSTIFICACIONES), current_user: dict = Depends(get_current_user)):
    try:
        j = await svc.decidir_justificacion(db, id, _tid(current_user, request), True, _nombre(current_user))
    except svc.ReglaNegocioError as e:
        raise _rn(e)
    if not j:
        raise HTTPException(404, detail="Justificación no encontrada")
    return j


@router.post("/justificaciones/{id}/rechazar", response_model=JustificacionResponse)
async def rechazar_just(request: Request, id: uuid.UUID, data: JustificacionDecision, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_JUSTIFICACIONES), current_user: dict = Depends(get_current_user)):
    try:
        j = await svc.decidir_justificacion(db, id, _tid(current_user, request), False, _nombre(current_user), data.motivo_rechazo)
    except svc.ReglaNegocioError as e:
        raise _rn(e)
    if not j:
        raise HTTPException(404, detail="Justificación no encontrada")
    return j


@router.get("/justificaciones/{id}", response_model=JustificacionResponse)
async def obtener_just(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_JUSTIFICACIONES), current_user: dict = Depends(get_current_user)):
    tid = _tid(current_user, request)
    j = await svc._just_orm(db, id, tid)
    if not j:
        raise HTTPException(404, detail="Justificación no encontrada")
    return (await svc._serializar_justificaciones(db, tid, [j]))[0]


@router.patch("/justificaciones/{id}", response_model=JustificacionResponse)
async def actualizar_just(request: Request, id: uuid.UUID, data: JustificacionUpdate, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_JUSTIFICACIONES), current_user: dict = Depends(get_current_user)):
    j = await svc.actualizar_justificacion(db, id, _tid(current_user, request), data)
    if not j:
        raise HTTPException(404, detail="Justificación no encontrada")
    return j


@router.delete("/justificaciones/{id}")
async def eliminar_just(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), tenant=Depends(_MOD_JUSTIFICACIONES), current_user: dict = Depends(get_current_user)):
    if not await svc.eliminar_justificacion(db, id, _tid(current_user, request)):
        raise HTTPException(404, detail="Justificación no encontrada")
    return {"ok": True}
