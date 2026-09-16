import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.auditoria import service

router = APIRouter()
aud_user = require_any_module_jwt("auditoria")


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/catalogos/modelos")
async def catalogo_modelos(db: AsyncSession = Depends(get_db), user=Depends(aud_user)):
    return await service.catalogo_modelos(db, tid(user))


@router.get("/auditoria")
async def auditoria(modelo: str | None = None, accion: str | None = None, usuario: str | None = None,
                    desde: date | None = None, hasta: date | None = None, q: str | None = Query(None, max_length=200),
                    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                    db: AsyncSession = Depends(get_db), user=Depends(aud_user)):
    f = {"modelo": modelo, "accion": accion, "usuario": usuario, "desde": desde, "hasta": hasta, "q": q}
    return await service.list_audit(db, tid(user), f, page, page_size)


@router.get("/auditoria/{audit_id}")
async def auditoria_detalle(audit_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(aud_user)):
    return await service.audit_detail(db, tid(user), audit_id)


@router.get("/auditoria-general/resumen")
async def resumen(desde: date | None = None, hasta: date | None = None, db: AsyncSession = Depends(get_db), user=Depends(aud_user)):
    return await service.resumen(db, tid(user), desde, hasta)


@router.get("/reportes/auditoria.csv")
async def exportar(modelo: str | None = None, accion: str | None = None, usuario: str | None = None,
                   desde: date | None = None, hasta: date | None = None, q: str | None = Query(None, max_length=200),
                   db: AsyncSession = Depends(get_db), user=Depends(aud_user)):
    f = {"modelo": modelo, "accion": accion, "usuario": usuario, "desde": desde, "hasta": hasta, "q": q}
    return Response(await service.export_csv(db, tid(user), f), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="auditoria.csv"', "Cache-Control": "no-store"})
