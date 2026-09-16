import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.firma_electronica import schemas, service

router = APIRouter()
fe_user = require_any_module_jwt("firma_electronica")


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/bandeja")
async def bandeja(db: AsyncSession = Depends(get_db), user=Depends(fe_user)):
    return await service.bandeja(db, tid(user), user)


@router.post("/bandeja/firmar")
async def firmar_documento(data: schemas.FirmarDocumentoIn, db: AsyncSession = Depends(get_db), user=Depends(fe_user)):
    return await service.firmar_documento(db, tid(user), user, data)


@router.get("/registros")
async def registros(documento_tipo: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(fe_user)):
    return await service.list_registros(db, tid(user), documento_tipo)
