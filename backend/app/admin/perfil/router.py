# backend/app/admin/perfil/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.perfil.schemas import PerfilResponse, PerfilUpdate
from app.admin.perfil.service import obtener_perfil, actualizar_perfil

router = APIRouter()

# Actualizar el PROPIO perfil (nombre, preferencias, contraseña propia) se
# deja con get_admin_user: no es una operacion sobre el sistema ni sobre
# otras cuentas, es autoservicio -- una cuenta de solo lectura sigue
# necesitando poder cambiar su propia contraseña.


@router.get("/perfil", response_model=PerfilResponse, summary="Mi perfil")
async def mi_perfil(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await obtener_perfil(db, current_user["sub"])


@router.patch("/perfil", response_model=PerfilResponse, summary="Actualizar mi perfil")
async def actualizar_mi_perfil(
    data: PerfilUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await actualizar_perfil(db, current_user["sub"], data)
