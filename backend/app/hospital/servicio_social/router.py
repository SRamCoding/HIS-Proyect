import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.servicio_social import schemas, service

router = APIRouter()
ss_user = require_any_module_jwt("servicio_social")


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/servicio-social")
async def listar(estado: str | None = None, patient_id: uuid.UUID | None = None,
                  db: AsyncSession = Depends(get_db), user=Depends(ss_user)):
    return await service.list_evaluaciones(db, tid(user), estado, patient_id)


@router.post("/servicio-social", status_code=201)
async def crear(data: schemas.EvaluacionCreateIn, db: AsyncSession = Depends(get_db), user=Depends(ss_user)):
    return await service.crear_evaluacion(db, tid(user), user, data)


@router.get("/servicio-social/{evaluacion_id}")
async def obtener(evaluacion_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(ss_user)):
    return await service.get_evaluacion(db, tid(user), evaluacion_id)


@router.post("/servicio-social/{evaluacion_id}/cerrar")
async def cerrar(evaluacion_id: uuid.UUID, data: schemas.CerrarEvaluacionIn,
                  db: AsyncSession = Depends(get_db), user=Depends(ss_user)):
    return await service.cerrar_evaluacion(db, tid(user), user, evaluacion_id, data)


@router.post("/servicio-social/{evaluacion_id}/gestiones", status_code=201)
async def crear_gestion(evaluacion_id: uuid.UUID, data: schemas.GestionCreateIn,
                         db: AsyncSession = Depends(get_db), user=Depends(ss_user)):
    return await service.crear_gestion(db, tid(user), user, evaluacion_id, data)
