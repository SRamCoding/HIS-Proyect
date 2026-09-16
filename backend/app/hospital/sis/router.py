import uuid
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.sis import schemas, service

router = APIRouter()
sis_user = require_any_module_jwt("sis")


def tid(user):
    return uuid.UUID(user["tenant_id"])


# --- Formato FUA ---
@router.get("/formato-fua/pendientes")
async def pendientes(db: AsyncSession = Depends(get_db), user=Depends(sis_user)):
    return await service.list_atenciones_pendientes_fua(db, tid(user))


@router.post("/formato-fua", status_code=201)
async def generar(data: schemas.GenerarFuaIn, db: AsyncSession = Depends(get_db), user=Depends(sis_user)):
    return await service.generar_fua(db, tid(user), user, data)


@router.get("/formato-fua")
async def listar(estado: str | None = None, q: str | None = Query(None, max_length=200),
                 page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                 db: AsyncSession = Depends(get_db), user=Depends(sis_user)):
    return await service.list_fua(db, tid(user), estado, q, page, page_size)


@router.get("/formato-fua/{fua_id}")
async def detalle(fua_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(sis_user)):
    return await service.fua_detalle(db, tid(user), fua_id)


@router.post("/formato-fua/{fua_id}/estado")
async def cambiar_estado(fua_id: uuid.UUID, data: schemas.CambiarEstadoFuaIn,
                         db: AsyncSession = Depends(get_db), user=Depends(sis_user)):
    return await service.cambiar_estado_fua(db, tid(user), user, fua_id, data)


@router.get("/formato-fua/{fua_id}/reporte.pdf")
async def pdf(fua_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(sis_user)):
    return Response(await service.fua_pdf(db, tid(user), fua_id), media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="fua.pdf"', "Cache-Control": "no-store"})


# --- Afiliaciones SIS ---
@router.get("/afiliaciones")
async def afiliaciones(q: str | None = Query(None, max_length=200), page: int = Query(1, ge=1),
                       page_size: int = Query(20, ge=1, le=100),
                       db: AsyncSession = Depends(get_db), user=Depends(sis_user)):
    return await service.list_afiliaciones_sis(db, tid(user), q, page, page_size)
