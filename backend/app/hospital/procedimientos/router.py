import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.procedimientos import schemas, service

router = APIRouter()
proc_user = require_any_module_jwt("procedimientos")


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/catalogo")
async def catalogo(q: str = "", db: AsyncSession = Depends(get_db), user=Depends(proc_user)):
    return await service.list_catalogo(db, tid(user), q)


@router.get("/catalogos/pacientes")
async def pacientes(q: str = "", db: AsyncSession = Depends(get_db), user=Depends(proc_user)):
    return await service.list_pacientes(db, tid(user), q)


@router.get("/catalogos/empleados")
async def empleados(q: str = "", db: AsyncSession = Depends(get_db), user=Depends(proc_user)):
    return await service.list_empleados(db, tid(user), q)


# ─── Asignaciones ────────────────────────────────────────────────────────

@router.get("/asignaciones")
async def asignaciones(tiempo_procedimiento_id: uuid.UUID | None = None,
                        db: AsyncSession = Depends(get_db), user=Depends(proc_user)):
    return await service.list_asignaciones(db, tid(user), tiempo_procedimiento_id)


@router.post("/asignaciones", status_code=201)
async def crear_asignacion(data: schemas.AsignacionCreateIn, db: AsyncSession = Depends(get_db), user=Depends(proc_user)):
    return await service.crear_asignacion(db, tid(user), user, data)


@router.delete("/asignaciones/{tiempo_procedimiento_id}/{empleado_id}")
async def desasignar(tiempo_procedimiento_id: uuid.UUID, empleado_id: uuid.UUID,
                      db: AsyncSession = Depends(get_db), user=Depends(proc_user)):
    return await service.desasignar(db, tid(user), user, tiempo_procedimiento_id, empleado_id)


# ─── Atenciones ──────────────────────────────────────────────────────────

@router.get("/atenciones")
async def atenciones(estado: str | None = None, patient_id: uuid.UUID | None = None,
                      db: AsyncSession = Depends(get_db), user=Depends(proc_user)):
    return await service.list_atenciones(db, tid(user), estado, patient_id)


@router.post("/atenciones", status_code=201)
async def crear_atencion(data: schemas.AtencionProcedimientoCreateIn, db: AsyncSession = Depends(get_db), user=Depends(proc_user)):
    return await service.crear_atencion(db, tid(user), user, data)


@router.post("/atenciones/{atencion_id}/consentimiento")
async def confirmar_consentimiento(atencion_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(proc_user)):
    return await service.confirmar_consentimiento(db, tid(user), user, atencion_id)


@router.post("/atenciones/{atencion_id}/realizar")
async def realizar_atencion(atencion_id: uuid.UUID, data: schemas.RealizarAtencionIn,
                             db: AsyncSession = Depends(get_db), user=Depends(proc_user)):
    return await service.realizar_atencion(db, tid(user), user, atencion_id, data)


@router.post("/atenciones/{atencion_id}/cancelar")
async def cancelar_atencion(atencion_id: uuid.UUID, data: schemas.CancelarAtencionIn,
                             db: AsyncSession = Depends(get_db), user=Depends(proc_user)):
    return await service.cancelar_atencion(db, tid(user), user, atencion_id, data)
