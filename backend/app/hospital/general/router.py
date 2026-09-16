import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.general import service

router = APIRouter()
gen_user = require_any_module_jwt("general")


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/servicios")
async def servicios(q: str | None = Query(None, max_length=200), page: int = Query(1, ge=1),
                    page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), user=Depends(gen_user)):
    return await service.list_servicios(db, tid(user), q, page, page_size)


@router.get("/servicios/{servicio_id}")
async def servicio(servicio_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(gen_user)):
    return await service.servicio_detalle(db, tid(user), servicio_id)


@router.get("/diagnosticos/capitulos")
async def capitulos(db: AsyncSession = Depends(get_db), user=Depends(gen_user)):
    return await service.catalogo_capitulos(db, tid(user))


@router.get("/diagnosticos")
async def diagnosticos(q: str | None = Query(None, max_length=200), capitulo: str | None = None,
                       page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                       db: AsyncSession = Depends(get_db), user=Depends(gen_user)):
    return await service.list_diagnosticos(db, tid(user), q, capitulo, page, page_size)


@router.get("/diagnosticos/{diagnostico_id}")
async def diagnostico(diagnostico_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(gen_user)):
    return await service.diagnostico_detalle(db, tid(user), diagnostico_id)


@router.get("/paquetes")
async def paquetes(q: str | None = Query(None, max_length=200), page: int = Query(1, ge=1),
                   page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), user=Depends(gen_user)):
    return await service.list_paquetes(db, tid(user), q, page, page_size)


@router.get("/paquetes/{paquete_id}")
async def paquete(paquete_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(gen_user)):
    return await service.paquete_detalle(db, tid(user), paquete_id)
