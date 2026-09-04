import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.usuarios.schemas import UserListItem, UserCreate
from app.admin.usuarios.service import get_all_users, get_users_by_tenant, create_user

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
    return await create_user(db, data)
