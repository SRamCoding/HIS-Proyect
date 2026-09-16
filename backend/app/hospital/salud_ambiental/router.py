import uuid
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.salud_ambiental import schemas, service

router = APIRouter()
sa_user = require_any_module_jwt("salud_ambiental")


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/defunciones")
async def defunciones(tipo_muerte: str | None = None, estado_envio: str | None = None,
                       db: AsyncSession = Depends(get_db), user=Depends(sa_user)):
    return await service.list_certificados(db, tid(user), tipo_muerte, estado_envio)


@router.post("/defunciones", status_code=201)
async def crear_defuncion(data: schemas.CertificadoDefuncionCreateIn, db: AsyncSession = Depends(get_db), user=Depends(sa_user)):
    return await service.crear_certificado(db, tid(user), user, data)


@router.get("/defunciones/{certificado_id}")
async def obtener_defuncion(certificado_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(sa_user)):
    return await service.get_certificado(db, tid(user), certificado_id)


@router.post("/defunciones/{certificado_id}/marcar-enviado")
async def marcar_enviado(certificado_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(sa_user)):
    return await service.marcar_enviado(db, tid(user), user, certificado_id)


@router.get("/defunciones/{certificado_id}/reporte.pdf")
async def defuncion_pdf(certificado_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(sa_user)):
    pdf = await service.certificado_pdf(db, tid(user), certificado_id)
    return Response(pdf, media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="certificado-defuncion.pdf"', "Cache-Control": "no-store"})
