import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.seguridad import service

router = APIRouter()
seg_user = require_any_module_jwt("seguridad")


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/resumen")
async def resumen(db: AsyncSession = Depends(get_db), user=Depends(seg_user)):
    return await service.resumen(db, tid(user))


@router.get("/catalogos/roles")
async def roles(db: AsyncSession = Depends(get_db), user=Depends(seg_user)):
    return await service.catalogo_roles(db, tid(user))


@router.get("/empleados")
async def empleados(q: str | None = Query(None, max_length=200), role: str | None = None, estado: str | None = None,
                    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                    db: AsyncSession = Depends(get_db), user=Depends(seg_user)):
    return await service.list_empleados_acceso(db, tid(user), q, role, estado, page, page_size)


@router.get("/empleados/{user_id}")
async def empleado(user_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(seg_user)):
    return await service.empleado_acceso_detalle(db, tid(user), user_id)
