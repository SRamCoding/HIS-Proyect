# backend/app/sigarh/perfil/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.sigarh.perfil.schemas import PerfilSigarhResponse, PerfilSigarhUpdate
from app.sigarh.perfil.service import obtener_perfil, actualizar_perfil

router = APIRouter()


@router.get("/perfil", response_model=PerfilSigarhResponse, summary="Mi perfil SIGARH")
async def mi_perfil(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await obtener_perfil(db, current_user["sub"])


@router.patch("/perfil", response_model=PerfilSigarhResponse, summary="Actualizar mi perfil SIGARH")
async def actualizar_mi_perfil(
    data: PerfilSigarhUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await actualizar_perfil(db, current_user["sub"], data)
