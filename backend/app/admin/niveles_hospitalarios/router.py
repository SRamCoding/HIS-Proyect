import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user, get_admin_user_escritura
from app.admin.niveles_hospitalarios.schemas import HospitalLevelCreate, HospitalLevelUpdate, HospitalLevelResponse
from app.admin.niveles_hospitalarios.service import (
    get_all_hospital_levels, create_hospital_level,
    get_hospital_level_by_code, get_hospital_level_by_id, update_hospital_level,
    delete_hospital_level,
)

router = APIRouter()


@router.get("/niveles-hospitalarios", response_model=list[HospitalLevelResponse], summary="Niveles MINSA")
async def listar_niveles(
    activos: bool = Query(False, description="Si es true, solo devuelve niveles con is_active=true"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_all_hospital_levels(db, solo_activos=activos)


@router.post("/niveles-hospitalarios", response_model=HospitalLevelResponse, status_code=201)
async def crear_nivel(
    data: HospitalLevelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user_escritura),
):
    return await create_hospital_level(db, data, current_user)


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
    data: HospitalLevelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user_escritura),
):
    nivel = await update_hospital_level(db, nivel_id, data, current_user)
    if not nivel:
        raise HTTPException(404, detail="Nivel no encontrado")
    return {"ok": True}


@router.delete("/niveles-hospitalarios/{nivel_id}", summary="Eliminar nivel")
async def eliminar_nivel(
    nivel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user_escritura),
):
    ok = await delete_hospital_level(db, nivel_id)
    if not ok:
        raise HTTPException(404, detail="Nivel no encontrado")
    return {"ok": True}
