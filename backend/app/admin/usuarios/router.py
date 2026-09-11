import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.usuarios.schemas import UserListItem, UserCreate, UserUpdate
from app.admin.usuarios.service import (
    get_all_users, get_users_by_tenant, create_user,
    update_user, toggle_user, delete_user,
)

router = APIRouter()


@router.get("/usuarios", response_model=list[UserListItem], summary="Listar todos los usuarios")
async def listar_usuarios(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_all_users(db)


@router.get("/usuarios/con-hospital", summary="Usuarios con datos de hospital")
async def usuarios_con_hospital(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    from app.auth.models import User
    from app.tenants.hospitales.models import Tenant

    result = await db.execute(
        select(User, Tenant.name.label("tenant_name"))
        .outerjoin(Tenant, User.tenant_id == Tenant.id)
        .where(User.email != "admin@erp.local")  # excluir super admin
        .order_by(User.created_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": str(u.id),
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "panel": u.panel,
            "is_active": u.is_active,
            "tenant_name": tenant_name or "—",
            "tenant_id": str(u.tenant_id) if u.tenant_id else None,
            "created_at": u.created_at.strftime("%d/%m/%Y"),
        }
        for u, tenant_name in rows
    ]


@router.get("/usuarios/hospital/{tenant_id}", response_model=list[UserListItem], summary="Usuarios por hospital")
async def usuarios_por_hospital(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_users_by_tenant(db, tenant_id)


@router.post("/usuarios", response_model=UserListItem, status_code=201, summary="Crear usuario")
async def crear_usuario(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await create_user(db, data, current_user)


@router.patch("/usuarios/{user_id}", response_model=UserListItem, summary="Actualizar usuario")
async def actualizar_usuario(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    user = await update_user(db, user_id, data, current_user)
    if not user:
        raise HTTPException(404, detail="Usuario no encontrado")
    return user


@router.patch("/usuarios/{user_id}/toggle", response_model=UserListItem, summary="Activar/desactivar usuario")
async def toggle_usuario(
    user_id: uuid.UUID,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    user = await toggle_user(db, user_id, is_active, current_user)
    if not user:
        raise HTTPException(404, detail="Usuario no encontrado")
    return user


@router.delete("/usuarios/{user_id}", summary="Eliminar usuario")
async def eliminar_usuario(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    ok = await delete_user(db, user_id, current_user)
    if not ok:
        raise HTTPException(404, detail="Usuario no encontrado")
    return {"ok": True}
