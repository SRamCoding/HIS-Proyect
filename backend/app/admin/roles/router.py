from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.roles.schemas import SystemRoleCreate, SystemRoleResponse
from app.admin.roles.service import get_all_system_roles, create_system_role

router = APIRouter()


@router.get("/roles", response_model=list[SystemRoleResponse], summary="Listar roles del sistema")
async def listar_roles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_all_system_roles(db)


@router.post("/roles", response_model=SystemRoleResponse, status_code=201)
async def crear_rol(
    data: SystemRoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await create_system_role(db, data)
