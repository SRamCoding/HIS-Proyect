import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.banco_sangre import schemas, service

router = APIRouter()
bs_user = require_any_module_jwt("banco_sangre")


def tid(user):
    return uuid.UUID(user["tenant_id"])


# ─── Movimientos: donantes, unidades, tamizaje, fraccionamiento, inventario, kardex ───

@router.get("/donantes")
async def donantes(q: str = "", db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.list_donantes(db, tid(user), q)


@router.post("/donantes", status_code=201)
async def crear_donante(data: schemas.DonanteCreateIn, db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    donante = await service.crear_donante(db, tid(user), user, data)
    return {"id": donante.id, "dni": donante.dni, "nombre_completo": donante.nombre_completo}


@router.get("/unidades")
async def unidades(estado: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.list_unidades(db, tid(user), estado)


@router.post("/unidades", status_code=201)
async def crear_unidad(data: schemas.UnidadCreateIn, db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.crear_unidad(db, tid(user), user, data)


@router.post("/unidades/{unidad_id}/tamizaje")
async def registrar_tamizaje(unidad_id: uuid.UUID, data: schemas.TamizajeIn,
                              db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.registrar_tamizaje(db, tid(user), user, unidad_id, data)


@router.post("/unidades/{unidad_id}/fraccionar")
async def fraccionar_unidad(unidad_id: uuid.UUID, data: schemas.FraccionarIn,
                             db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.fraccionar_unidad(db, tid(user), user, unidad_id, data)


@router.get("/componentes")
async def componentes(estado: str | None = None, tipo: str | None = None,
                       db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.list_componentes(db, tid(user), estado, tipo)


@router.get("/inventario")
async def inventario(db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.inventario_resumen(db, tid(user))


@router.get("/movimientos")
async def movimientos(componente_id: uuid.UUID | None = None, page: int = Query(1, ge=1),
                       page_size: int = Query(20, ge=1, le=100),
                       db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.list_movimientos(db, tid(user), componente_id, page, page_size)


# ─── Solicitud Transfusional ─────────────────────────────────────────────────

@router.get("/solicitud-transfusional")
async def solicitudes(estado: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.list_solicitudes(db, tid(user), estado)


@router.post("/solicitud-transfusional", status_code=201)
async def crear_solicitud(data: schemas.SolicitudCreateIn, db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.crear_solicitud(db, tid(user), user, data)


@router.post("/solicitud-transfusional/{solicitud_id}/asignar-componente")
async def asignar_componente(solicitud_id: uuid.UUID, data: schemas.AsignarComponenteIn,
                              db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.asignar_componente(db, tid(user), user, solicitud_id, data)


@router.post("/solicitud-transfusional/asignaciones/{asignacion_id}/prueba-cruzada")
async def prueba_cruzada(asignacion_id: uuid.UUID, data: schemas.PruebaCruzadaIn,
                          db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.registrar_prueba_cruzada(db, tid(user), user, asignacion_id, data)


@router.post("/solicitud-transfusional/asignaciones/{asignacion_id}/dispensar")
async def dispensar(asignacion_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.dispensar(db, tid(user), user, asignacion_id)


@router.post("/solicitud-transfusional/{solicitud_id}/anular")
async def anular_solicitud(solicitud_id: uuid.UUID, data: schemas.AnularSolicitudIn,
                            db: AsyncSession = Depends(get_db), user=Depends(bs_user)):
    return await service.anular_solicitud(db, tid(user), user, solicitud_id, data)
