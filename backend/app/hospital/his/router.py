import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.his import schemas, service

router = APIRouter()
his_user = require_any_module_jwt("his")


def tid(user):
    return uuid.UUID(user["tenant_id"])


# --- Formato HIS (reporte de atenciones, no persistido) ---
@router.get("/formato-his")
async def formato_his(fecha_desde: date, fecha_hasta: date, db: AsyncSession = Depends(get_db), user=Depends(his_user)):
    return await service.list_atenciones_his(db, tid(user), fecha_desde, fecha_hasta)


@router.get("/formato-his.csv")
async def formato_his_csv(fecha_desde: date, fecha_hasta: date, db: AsyncSession = Depends(get_db), user=Depends(his_user)):
    return Response(await service.csv_his(db, tid(user), fecha_desde, fecha_hasta), media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="formato-his.csv"', "Cache-Control": "no-store"})


# --- Registro HIS de la MicroRed (envíos por periodo) ---
@router.get("/registro-microred")
async def envios(db: AsyncSession = Depends(get_db), user=Depends(his_user)):
    return await service.list_envios(db, tid(user))


@router.post("/registro-microred", status_code=201)
async def crear_envio(data: schemas.CrearEnvioIn, db: AsyncSession = Depends(get_db), user=Depends(his_user)):
    return await service.crear_envio(db, tid(user), user, data)


@router.post("/registro-microred/{envio_id}/cerrar")
async def cerrar_envio(envio_id: uuid.UUID, data: schemas.CerrarEnvioIn, db: AsyncSession = Depends(get_db), user=Depends(his_user)):
    return await service.cerrar_envio(db, tid(user), user, envio_id, data)
