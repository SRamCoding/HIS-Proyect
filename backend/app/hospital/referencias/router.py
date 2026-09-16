import uuid
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.referencias import schemas, service

router = APIRouter()
ref_user = require_any_module_jwt("referencias")


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/catalogos/{kind}")
async def catalogos(kind: str, q: str = Query("", max_length=200), db: AsyncSession = Depends(get_db), user=Depends(ref_user)):
    return await service.catalogs(db, tid(user), kind, q)


@router.get("/pacientes")
async def pacientes(q: str = Query(min_length=2, max_length=200), db: AsyncSession = Depends(get_db), user=Depends(ref_user)):
    return await service.patients(db, tid(user), q)


@router.get("/emergencia-pendientes")
async def destinos_pendientes(db: AsyncSession = Depends(get_db), user=Depends(ref_user)):
    return await service.destinos_emergencia_pendientes(db, tid(user))


@router.post("/referencias/admitir-emergencia", status_code=201)
async def admitir_desde_emergencia(data: schemas.AdmisionDesdeEmergencia, db: AsyncSession = Depends(get_db), user=Depends(ref_user)):
    return await service.admitir_desde_emergencia(db, tid(user), user, data)


@router.get("/referencias")
async def referencias(q: str | None = None, estado: str | None = None,
                      page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                      db: AsyncSession = Depends(get_db), user=Depends(ref_user)):
    return await service.list_referencias(db, tid(user), {"q": q, "estado": estado}, page, page_size)


@router.get("/referencias/{referencia_id}")
async def referencia(referencia_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(ref_user)):
    return await service.referencia_detalle(db, tid(user), referencia_id)


@router.post("/referencias/{referencia_id}/resolver")
async def resolver(referencia_id: uuid.UUID, data: schemas.ResolucionEntrada, db: AsyncSession = Depends(get_db), user=Depends(ref_user)):
    return await service.resolver(db, tid(user), user, referencia_id, data)


@router.post("/referencias/{referencia_id}/contrarreferencia")
async def contrarreferencia(referencia_id: uuid.UUID, data: schemas.ContrarreferenciaEntrada, db: AsyncSession = Depends(get_db), user=Depends(ref_user)):
    return await service.registrar_contrarreferencia(db, tid(user), user, referencia_id, data)


@router.get("/referencias/{referencia_id}/comprobante.pdf")
async def comprobante(referencia_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(ref_user)):
    return Response(await service.referencia_pdf(db, tid(user), referencia_id), media_type="application/pdf",
                    headers={"Content-Disposition": 'inline; filename="referencia.pdf"', "Cache-Control": "no-store"})


@router.get("/reportes/referencias.csv")
async def exportar(q: str | None = None, estado: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(ref_user)):
    return Response(await service.export_csv(db, tid(user), {"q": q, "estado": estado}), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="referencias.csv"', "Cache-Control": "no-store"})
