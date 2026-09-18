import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.hospital.perfil.schemas import PerfilResponse, PerfilUpdate
from app.hospital.perfil.service import obtener_perfil, actualizar_perfil

router = APIRouter()


@router.get("/perfil", response_model=PerfilResponse, summary="Mi perfil")
async def mi_perfil(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return await obtener_perfil(db, uuid.UUID(current_user["tenant_id"]), current_user)


@router.patch("/perfil", response_model=PerfilResponse, summary="Actualizar mi perfil")
async def actualizar_mi_perfil(
    data: PerfilUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await actualizar_perfil(db, current_user, data)
