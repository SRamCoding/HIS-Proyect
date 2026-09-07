import uuid
from datetime import date as date_type
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.consulta_externa.schemas import AtencionMedicaCreate, AtencionMedicaUpdate, AtencionMedicaResponse, DiagnosticoCIE10Out, AtencionMedicaListItem, MedicamentoOut, RecetaCreate, RecetaResponse
from app.hospital.consulta_externa.service import buscar_cie10, create_atencion_medica, get_atencion_medica, update_atencion_medica, firmar_atencion_medica, list_atenciones_medicas, buscar_medicamentos, create_receta, get_receta
from app.core.database import get_db
from app.tenants.entitlements import require_module_jwt
from app.hospital.consulta_externa.schemas import (
    ProgramacionMedicaCreate, ProgramacionMedicaUpdate, ProgramacionMedicaResponse,
    ServicioOut, EspecialidadOut, MedicoOut, CupoOut,
    CitaCreate, CitaUpdate, CitaResponse,
)
from app.hospital.consulta_externa.service import (
    get_servicios, get_especialidades, get_medicos_por_especialidad,
    create_programacion, get_programacion_by_id, list_programaciones, update_programacion,
    get_cupos, create_cita, get_cita_by_id, list_citas, update_cita,
)

from app.hospital.consulta_externa.schemas import TriajeCreate,TriajeUpdate, TriajeResponse, CitaTriajeItem
from app.hospital.consulta_externa.service import confirmar_cita, list_citas_para_triaje, create_triaje, get_triaje_by_cita, update_triaje

router = APIRouter()


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


# --- Catalogos ---
@router.get("/programacion-medica/servicios", response_model=list[ServicioOut])
async def listar_servicios(request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    return await get_servicios(db, get_tenant_id(current_user, request))


@router.get("/programacion-medica/especialidades", response_model=list[EspecialidadOut])
async def listar_especialidades(request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    return await get_especialidades(db, get_tenant_id(current_user, request))


@router.get("/programacion-medica/medicos/{especialidad_id}", response_model=list[MedicoOut])
async def listar_medicos(especialidad_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    medicos = await get_medicos_por_especialidad(db, get_tenant_id(current_user, request), especialidad_id)
    return [{"id": m.id, "nombre_completo": m.nombre_completo} for m in medicos]


# --- Programaciones ---
@router.get("/programacion-medica", response_model=list[ProgramacionMedicaResponse])
async def listar_programaciones(
    request: Request,
    servicio_id: uuid.UUID | None = None,
    especialidad_id: uuid.UUID | None = None,
    medico_id: uuid.UUID | None = None,
    fecha: date_type | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("consulta_externa")),
):
    tenant_id = get_tenant_id(current_user, request)
    return await list_programaciones(db, tenant_id, servicio_id, especialidad_id, medico_id, fecha)


@router.get("/programacion-medica/{prog_id}", response_model=ProgramacionMedicaResponse)
async def obtener_programacion(prog_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    prog = await get_programacion_by_id(db, get_tenant_id(current_user, request), prog_id)
    if not prog:
        raise HTTPException(404, detail="Programación no encontrada")
    return prog





@router.post("/citas/{cita_id}/confirmar", response_model=CitaResponse)
async def confirmar_cita_endpoint(cita_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    try:
        cita = await confirmar_cita(db, get_tenant_id(current_user, request), cita_id)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    if not cita:
        raise HTTPException(404, detail="Cita no encontrada")
    return cita


@router.get("/triaje/pendientes", response_model=list[CitaTriajeItem])
async def listar_triaje_pendientes(
    request: Request,
    fecha: date_type | None = None,
    especialidad_id: uuid.UUID | None = None,
    servicio_id: uuid.UUID | None = None,
    medico_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("consulta_externa")),
):
    tenant_id = get_tenant_id(current_user, request)
    return await list_citas_para_triaje(db, tenant_id, fecha, especialidad_id, servicio_id, medico_id)


@router.get("/triaje/{cita_id}", response_model=TriajeResponse)
async def obtener_triaje(cita_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    triaje = await get_triaje_by_cita(db, get_tenant_id(current_user, request), cita_id)
    if not triaje:
        raise HTTPException(404, detail="No hay triaje registrado para esta cita")
    return triaje


@router.post("/triaje/{cita_id}", response_model=TriajeResponse, status_code=201)
async def registrar_triaje(cita_id: uuid.UUID, data: TriajeCreate, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    try:
        return await create_triaje(db, get_tenant_id(current_user, request), cita_id, data)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


    
@router.post("/programacion-medica", response_model=ProgramacionMedicaResponse, status_code=201)
async def crear_programacion(data: ProgramacionMedicaCreate, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    return await create_programacion(db, get_tenant_id(current_user, request), data)


@router.patch("/programacion-medica/{prog_id}", response_model=ProgramacionMedicaResponse)
async def actualizar_programacion(prog_id: uuid.UUID, data: ProgramacionMedicaUpdate, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    prog = await update_programacion(db, get_tenant_id(current_user, request), prog_id, data)
    if not prog:
        raise HTTPException(404, detail="Programación no encontrada")
    return prog


# --- Cupos ---
@router.get("/citas/cupos/{programacion_id}", response_model=list[CupoOut])
async def listar_cupos(programacion_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    cupos = await get_cupos(db, get_tenant_id(current_user, request), programacion_id)
    if cupos is None:
        raise HTTPException(404, detail="Programación no encontrada")
    return cupos


# --- Citas ---
@router.get("/citas", response_model=list[CitaResponse])
async def listar_citas_endpoint(
    request: Request,
    programacion_medica_id: uuid.UUID | None = None,
    estado: str | None = None,
    fecha: date_type | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("consulta_externa")),
):
    tenant_id = get_tenant_id(current_user, request)
    return await list_citas(db, tenant_id, programacion_medica_id, estado, fecha)


@router.get("/citas/{cita_id}", response_model=CitaResponse)
async def obtener_cita(cita_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    cita = await get_cita_by_id(db, get_tenant_id(current_user, request), cita_id)
    if not cita:
        raise HTTPException(404, detail="Cita no encontrada")
    return cita


@router.post("/citas", response_model=CitaResponse, status_code=201)
async def crear_cita(data: CitaCreate, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    try:
        return await create_cita(db, get_tenant_id(current_user, request), data)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


@router.patch("/citas/{cita_id}", response_model=CitaResponse)
async def actualizar_cita(cita_id: uuid.UUID, data: CitaUpdate, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    cita = await update_cita(db, get_tenant_id(current_user, request), cita_id, data)
    if not cita:
        raise HTTPException(404, detail="Cita no encontrada")
    return cita

@router.patch("/triaje/{cita_id}", response_model=TriajeResponse)
async def actualizar_triaje(cita_id: uuid.UUID, data: TriajeUpdate, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    triaje = await update_triaje(db, get_tenant_id(current_user, request), cita_id, data)
    if not triaje:
        raise HTTPException(404, detail="No hay triaje registrado para esta cita")
    return triaje




@router.get("/atenciones-medicas/cie10/buscar", response_model=list[DiagnosticoCIE10Out])
async def buscar_cie10_endpoint(q: str, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    if len(q) < 2:
        raise HTTPException(400, detail="Ingresa al menos 2 caracteres")
    return await buscar_cie10(db, get_tenant_id(current_user, request), q)


@router.get("/atenciones-medicas/historial", response_model=list[AtencionMedicaListItem])
async def listar_historial_atenciones(
    request: Request,
    fecha: date_type | None = None,
    especialidad_id: uuid.UUID | None = None,
    medico_id: uuid.UUID | None = None,
    paciente_dni: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("consulta_externa")),
):
    tenant_id = get_tenant_id(current_user, request)
    return await list_atenciones_medicas(db, tenant_id, fecha, especialidad_id, medico_id, paciente_dni)

@router.get("/atenciones-medicas/{cita_id}", response_model=AtencionMedicaResponse)
async def obtener_atencion_medica(cita_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    atencion = await get_atencion_medica(db, get_tenant_id(current_user, request), cita_id)
    if not atencion:
        raise HTTPException(404, detail="No hay atencion medica registrada para esta cita")
    return atencion


@router.post("/atenciones-medicas/{cita_id}", response_model=AtencionMedicaResponse, status_code=201)
async def crear_atencion_medica(cita_id: uuid.UUID, data: AtencionMedicaCreate, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    try:
        return await create_atencion_medica(db, get_tenant_id(current_user, request), cita_id, data)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


@router.patch("/atenciones-medicas/{cita_id}", response_model=AtencionMedicaResponse)
async def actualizar_atencion_medica(cita_id: uuid.UUID, data: AtencionMedicaUpdate, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    try:
        atencion = await update_atencion_medica(db, get_tenant_id(current_user, request), cita_id, data)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    if not atencion:
        raise HTTPException(404, detail="No hay atencion medica registrada para esta cita")
    return atencion


@router.post("/atenciones-medicas/{cita_id}/firmar", response_model=AtencionMedicaResponse)
async def firmar_atencion_endpoint(cita_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    try:
        atencion = await firmar_atencion_medica(db, get_tenant_id(current_user, request), cita_id)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    if not atencion:
        raise HTTPException(404, detail="No hay atencion medica registrada para esta cita")
    return atencion


@router.get("/farmacia/medicamentos/buscar", response_model=list[MedicamentoOut])
async def buscar_medicamentos_endpoint(q: str, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    if len(q) < 2:
        raise HTTPException(400, detail="Ingresa al menos 2 caracteres")
    return await buscar_medicamentos(db, get_tenant_id(current_user, request), q)


@router.get("/farmacia/recetas/{cita_id}", response_model=RecetaResponse)
async def obtener_receta(cita_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    receta = await get_receta(db, get_tenant_id(current_user, request), cita_id)
    if not receta:
        raise HTTPException(404, detail="No hay receta registrada para esta atención")
    return receta


@router.post("/farmacia/recetas/{cita_id}", response_model=RecetaResponse, status_code=201)
async def crear_receta(cita_id: uuid.UUID, data: RecetaCreate, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    try:
        return await create_receta(db, get_tenant_id(current_user, request), cita_id, data)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc



from app.hospital.consulta_externa.schemas import CamaOut, HospitalizacionCreate, HospitalizacionResponse
from app.hospital.consulta_externa.service import get_camas_disponibles, create_hospitalizacion, get_hospitalizacion, dar_alta_hospitalizacion

@router.get("/hospitalizacion/camas-disponibles", response_model=list[CamaOut])
async def listar_camas_disponibles(request: Request, servicio_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    return await get_camas_disponibles(db, get_tenant_id(current_user, request), servicio_id)


@router.get("/hospitalizacion/{cita_id}", response_model=HospitalizacionResponse)
async def obtener_hospitalizacion(cita_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    hosp = await get_hospitalizacion(db, get_tenant_id(current_user, request), cita_id)
    if not hosp:
        raise HTTPException(404, detail="No hay hospitalización registrada para esta atención")
    return hosp


@router.post("/hospitalizacion/{cita_id}", response_model=HospitalizacionResponse, status_code=201)
async def crear_hospitalizacion(cita_id: uuid.UUID, data: HospitalizacionCreate, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    try:
        return await create_hospitalizacion(db, get_tenant_id(current_user, request), cita_id, data)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


@router.post("/hospitalizacion/{cita_id}/alta", response_model=HospitalizacionResponse)
async def dar_alta_endpoint(cita_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_module_jwt("consulta_externa"))):
    try:
        hosp = await dar_alta_hospitalizacion(db, get_tenant_id(current_user, request), cita_id)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    if not hosp:
        raise HTTPException(404, detail="No hay hospitalización registrada")
    return hosp