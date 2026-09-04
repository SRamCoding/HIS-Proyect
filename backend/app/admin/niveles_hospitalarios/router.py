import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.niveles_hospitalarios.schemas import HospitalLevelCreate, HospitalLevelResponse
from app.admin.niveles_hospitalarios.service import (
    get_all_hospital_levels, create_hospital_level,
    get_hospital_level_by_code, get_hospital_level_by_id, update_hospital_level,
)

router = APIRouter()


@router.get("/niveles-hospitalarios", response_model=list[HospitalLevelResponse], summary="Niveles MINSA")
async def listar_niveles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_all_hospital_levels(db)


@router.post("/niveles-hospitalarios", response_model=HospitalLevelResponse, status_code=201)
async def crear_nivel(
    data: HospitalLevelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await create_hospital_level(db, data)


@router.get("/niveles-hospitalarios/{code}/modulos", summary="Módulos por defecto de un nivel")
async def modulos_por_nivel(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    """
    Dado un código de nivel (II-2, III-1, etc.), retorna los módulos
    que se activarán automáticamente — equivalente al wizard de Laravel.
    """
    level = await get_hospital_level_by_code(db, code)
    if not level:
        raise HTTPException(404, detail=f"Nivel '{code}' no encontrado")

    return {
        "code": level.code,
        "name": level.name,
        "color": level.color,
        "default_modules": level.default_modules or {"app": [], "sigarh": []},
    }


@router.get("/niveles-hospitalarios/{nivel_id}", summary="Obtener nivel por ID")
async def obtener_nivel(
    nivel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    nivel = await get_hospital_level_by_id(db, nivel_id)
    if not nivel:
        raise HTTPException(404, detail="Nivel no encontrado")
    return {
        "id": str(nivel.id),
        "code": nivel.code,
        "name": nivel.name,
        "description": nivel.description,
        "color": nivel.color,
        "sort_order": nivel.sort_order,
        "is_active": nivel.is_active,
        "default_modules": nivel.default_modules or {"app": [], "sigarh": []},
    }


@router.patch("/niveles-hospitalarios/{nivel_id}", summary="Actualizar nivel")
async def actualizar_nivel(
    nivel_id: uuid.UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    nivel = await update_hospital_level(db, nivel_id, data)
    if not nivel:
        raise HTTPException(404, detail="Nivel no encontrado")
    return {"ok": True}
