import uuid
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.telesalud import schemas, service

router = APIRouter()
tele_user = require_any_module_jwt("telesalud")


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/resumen-teleconsultas")
async def resumen_teleconsultas(fecha_desde: date, fecha_hasta: date,
                                 db: AsyncSession = Depends(get_db), user=Depends(tele_user)):
    return await service.resumen_teleconsultas(db, tid(user), fecha_desde, fecha_hasta)


@router.get("/guia-rapida-minsa")
async def guia_rapida_minsa(user=Depends(tele_user)):
    return service.guia_rapida()


@router.get("/formulario-solicitud")
async def solicitudes(estado: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(tele_user)):
    return await service.list_solicitudes(db, tid(user), estado)


@router.post("/formulario-solicitud", status_code=201)
async def crear_solicitud(data: schemas.SolicitudCreateIn, db: AsyncSession = Depends(get_db), user=Depends(tele_user)):
    return await service.crear_solicitud(db, tid(user), user, data)


@router.post("/formulario-solicitud/{solicitud_id}/programar")
async def programar_solicitud(solicitud_id: uuid.UUID, data: schemas.ProgramarSolicitudIn,
                               db: AsyncSession = Depends(get_db), user=Depends(tele_user)):
    return await service.programar_solicitud(db, tid(user), user, solicitud_id, data)


@router.post("/formulario-solicitud/{solicitud_id}/rechazar")
async def rechazar_solicitud(solicitud_id: uuid.UUID, data: schemas.RechazarSolicitudIn,
                              db: AsyncSession = Depends(get_db), user=Depends(tele_user)):
    return await service.rechazar_solicitud(db, tid(user), user, solicitud_id, data)


@router.get("/monitor")
async def monitor(db: AsyncSession = Depends(get_db), user=Depends(tele_user)):
    return await service.monitor_hoy(db, tid(user))


@router.get("/medicos")
async def medicos(db: AsyncSession = Depends(get_db), user=Depends(tele_user)):
    return await service.medicos_habilitados(db, tid(user))
