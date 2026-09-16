import uuid
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.medicina_fisica import schemas, service

router = APIRouter()
mf_user = require_any_module_jwt("medicina_fisica")


def tid(user):
    return uuid.UUID(user["tenant_id"])


# ─── Programas ───────────────────────────────────────────────────────────

@router.get("/programas")
async def programas(solo_activos: bool = False, db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.list_programas(db, tid(user), solo_activos)


@router.post("/programas", status_code=201)
async def crear_programa(data: schemas.ProgramaCreateIn, db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    p = await service.crear_programa(db, tid(user), user, data)
    return {"id": p.id, "nombre": p.nombre}


@router.patch("/programas/{programa_id}")
async def actualizar_programa(programa_id: uuid.UUID, data: schemas.ProgramaUpdateIn,
                               db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    p = await service.update_programa(db, tid(user), user, programa_id, data)
    return {"id": p.id, "nombre": p.nombre, "is_active": p.is_active}


@router.post("/programas/{programa_id}/tecnologos", status_code=201)
async def asignar_tecnologo(programa_id: uuid.UUID, data: schemas.TecnologoProgramaIn,
                             db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.asignar_tecnologo(db, tid(user), user, programa_id, data)


@router.delete("/programas/{programa_id}/tecnologos/{empleado_id}")
async def desasignar_tecnologo(programa_id: uuid.UUID, empleado_id: uuid.UUID,
                                db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.desasignar_tecnologo(db, tid(user), user, programa_id, empleado_id)


# ─── Programaciones ──────────────────────────────────────────────────────

@router.get("/programaciones")
async def programaciones(fecha: date | None = None, tecnologo_id: uuid.UUID | None = None,
                          programa_id: uuid.UUID | None = None, estado: str | None = None,
                          db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.list_programaciones(db, tid(user), fecha, tecnologo_id, programa_id, estado)


@router.post("/programaciones", status_code=201)
async def crear_programacion(data: schemas.ProgramacionMFCreateIn, db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.crear_programacion(db, tid(user), user, data)


@router.post("/programaciones/{programacion_id}/bloquear")
async def bloquear_programacion(programacion_id: uuid.UUID, data: schemas.BloquearProgramacionIn,
                                 db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.bloquear_programacion(db, tid(user), user, programacion_id, data)


@router.post("/programaciones/{programacion_id}/desbloquear")
async def desbloquear_programacion(programacion_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.desbloquear_programacion(db, tid(user), user, programacion_id)


# ─── Sesiones ────────────────────────────────────────────────────────────

@router.get("/sesiones-m-fisica")
async def sesiones(programacion_mf_id: uuid.UUID | None = None, fecha: date | None = None,
                    estado: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.list_sesiones(db, tid(user), programacion_mf_id, fecha, estado)


@router.post("/sesiones-m-fisica", status_code=201)
async def crear_sesion(data: schemas.SesionCreateIn, db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.crear_sesion(db, tid(user), user, data)


@router.post("/sesiones-m-fisica/{sesion_id}/ejecutar")
async def ejecutar_sesion(sesion_id: uuid.UUID, data: schemas.SesionEjecutarIn,
                           db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.ejecutar_sesion(db, tid(user), user, sesion_id, data)


@router.post("/sesiones-m-fisica/acciones/reprogramar-bloque")
async def reprogramar_bloque(data: schemas.SesionesReprogramarBloqueIn,
                              db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.reprogramar_bloque(db, tid(user), user, data)


# ─── Catálogo ────────────────────────────────────────────────────────────

@router.get("/empleados")
async def empleados(q: str = "", db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.list_empleados(db, tid(user), q)


# ─── Tablero de control ──────────────────────────────────────────────────

@router.get("/tablero-control")
async def tablero_control(fecha: date | None = None, db: AsyncSession = Depends(get_db), user=Depends(mf_user)):
    return await service.tablero_control(db, tid(user), fecha or date.today())
