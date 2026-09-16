import uuid
from datetime import date
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.informes import service

router = APIRouter()
informes_user = require_any_module_jwt("informes")


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/reporte-medico")
async def reporte_medico(fecha_desde: date, fecha_hasta: date, medico_id: uuid.UUID | None = None,
                          db: AsyncSession = Depends(get_db), user=Depends(informes_user)):
    return await service.reporte_medico(db, tid(user), fecha_desde, fecha_hasta, medico_id)


@router.get("/reporte-medico.csv")
async def reporte_medico_csv(fecha_desde: date, fecha_hasta: date, medico_id: uuid.UUID | None = None,
                              db: AsyncSession = Depends(get_db), user=Depends(informes_user)):
    return Response(await service.csv_reporte_medico(db, tid(user), fecha_desde, fecha_hasta, medico_id),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="reporte-medico.csv"', "Cache-Control": "no-store"})


@router.get("/reportes-hospitalizacion")
async def reportes_hospitalizacion(fecha_desde: date, fecha_hasta: date,
                                    db: AsyncSession = Depends(get_db), user=Depends(informes_user)):
    return await service.reportes_hospitalizacion(db, tid(user), fecha_desde, fecha_hasta)


@router.get("/gestion-cupos")
async def gestion_cupos(fecha_desde: date, fecha_hasta: date, medico_id: uuid.UUID | None = None,
                         servicio_id: uuid.UUID | None = None,
                         db: AsyncSession = Depends(get_db), user=Depends(informes_user)):
    return await service.gestion_cupos(db, tid(user), fecha_desde, fecha_hasta, medico_id, servicio_id)


@router.get("/gestion-cupos.csv")
async def gestion_cupos_csv(fecha_desde: date, fecha_hasta: date, medico_id: uuid.UUID | None = None,
                             servicio_id: uuid.UUID | None = None,
                             db: AsyncSession = Depends(get_db), user=Depends(informes_user)):
    return Response(await service.csv_gestion_cupos(db, tid(user), fecha_desde, fecha_hasta, medico_id, servicio_id),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="gestion-cupos.csv"', "Cache-Control": "no-store"})


@router.get("/gestion-tickets")
async def gestion_tickets(fecha_desde: date, fecha_hasta: date,
                           db: AsyncSession = Depends(get_db), user=Depends(informes_user)):
    return await service.gestion_tickets(db, tid(user), fecha_desde, fecha_hasta)


@router.get("/visor-colas")
async def visor_colas(db: AsyncSession = Depends(get_db), user=Depends(informes_user)):
    return await service.visor_colas(db, tid(user))


@router.get("/externos")
async def externos(fecha_desde: date, fecha_hasta: date,
                    db: AsyncSession = Depends(get_db), user=Depends(informes_user)):
    return await service.externos(db, tid(user), fecha_desde, fecha_hasta)


@router.get("/externos.csv")
async def externos_csv(fecha_desde: date, fecha_hasta: date,
                        db: AsyncSession = Depends(get_db), user=Depends(informes_user)):
    return Response(await service.csv_externos(db, tid(user), fecha_desde, fecha_hasta), media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="externos.csv"', "Cache-Control": "no-store"})
