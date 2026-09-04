# backend/app/admin/modulos/router.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.modulos.schemas import ModuleDependencyCreate, ModuleDependencyResponse
from app.admin.modulos.service import get_module_dependencies, create_module_dependency, delete_module_dependency
from app.tenants.modulos.service import get_all_modules

router = APIRouter()


@router.get("/modulos/dependencias", response_model=list[ModuleDependencyResponse])
async def listar_dependencias(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_module_dependencies(db)


@router.post("/modulos/dependencias", response_model=ModuleDependencyResponse, status_code=201)
async def crear_dependencia(
    data: ModuleDependencyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await create_module_dependency(db, data)


@router.delete("/modulos/dependencias/{dep_id}", summary="Eliminar dependencia")
async def eliminar_dependencia(
    dep_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    ok = await delete_module_dependency(db, dep_id)
    if not ok:
        raise HTTPException(404, detail="Dependencia no encontrada")
    return {"ok": True}


@router.get("/modulos/catalogo", summary="Catalogo de modulos")
async def catalogo_modulos(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    modules = await get_all_modules(db)
    return [
        {"id": str(m.id), "code": m.code, "name": m.name, "category": m.category, "is_active": m.is_active}
        for m in modules
    ]