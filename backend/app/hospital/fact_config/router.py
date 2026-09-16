import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.fact_config import service

router = APIRouter()
fc_user = require_any_module_jwt("fact_config")


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/catalogos/tipos-producto")
async def tipos_producto(db: AsyncSession = Depends(get_db), user=Depends(fc_user)):
    return await service.catalogo_tipos_producto(db, tid(user))


@router.get("/bienes-insumos")
async def bienes(q: str | None = Query(None, max_length=200), tipo_id: uuid.UUID | None = None,
                 page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                 db: AsyncSession = Depends(get_db), user=Depends(fc_user)):
    return await service.list_bienes(db, tid(user), q, tipo_id, page, page_size)


@router.get("/bienes-insumos/{bien_id}")
async def bien(bien_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(fc_user)):
    return await service.bien_detalle(db, tid(user), bien_id)


@router.get("/servicios")
async def servicios(q: str | None = Query(None, max_length=200), tipo_servicio: str | None = None,
                    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                    db: AsyncSession = Depends(get_db), user=Depends(fc_user)):
    return await service.list_servicios(db, tid(user), q, tipo_servicio, page, page_size)


@router.get("/servicios/{tarifa_id}")
async def servicio(tarifa_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(fc_user)):
    return await service.servicio_detalle(db, tid(user), tarifa_id)
