import uuid
import bcrypt
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.models import User


async def get_all_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


async def get_users_by_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> list[User]:
    result = await db.execute(
        select(User).where(User.tenant_id == tenant_id).order_by(User.name)
    )
    return result.scalars().all()


async def create_user(db: AsyncSession, data, creador: dict) -> User:
    existente = await db.scalar(select(User.id).where(User.email == data.email))
    if existente:
        raise HTTPException(400, detail=f"Ya existe un usuario con el correo {data.email}")

    if data.tenant_id:
        from app.tenants.hospitales.models import Tenant
        if not await db.scalar(select(Tenant.id).where(Tenant.id == data.tenant_id)):
            raise HTTPException(400, detail="El hospital indicado no existe")

    hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
    user = User(
        name=data.name,
        email=data.email,
        password=hashed,
        role=data.role,
        panel=data.panel,
        tenant_id=data.tenant_id,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    if data.panel == "admin":
        # Crear otra cuenta con acceso total al ERP es la acción más sensible
        # de este panel: se audita explícitamente, aunque el resto de acciones
        # de Admin todavía no pasen por auditoría (ver admin/auditoria).
        from app.admin.auditoria.models import AuditLog
        db.add(AuditLog(
            user_id=uuid.UUID(str(creador.get("sub"))) if creador.get("sub") else None,
            user_name=creador.get("name") or creador.get("email"),
            action="admin_user_created",
            model="User",
            model_id=str(user.id),
            description=f"Cuenta admin creada: {user.email}",
        ))

    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await db.scalar(select(User).where(User.id == user_id))


async def update_user(db: AsyncSession, user_id: uuid.UUID, data, actor: dict) -> User | None:
    from app.admin.auditoria.service import create_audit_log

    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    cambios = data.model_dump(exclude_unset=True, exclude={"password"})
    if data.email and data.email != user.email:
        existente = await db.scalar(select(User.id).where(User.email == data.email, User.id != user_id))
        if existente:
            raise HTTPException(400, detail=f"Ya existe un usuario con el correo {data.email}")
    if cambios.get("tenant_id"):
        from app.tenants.hospitales.models import Tenant
        if not await db.scalar(select(Tenant.id).where(Tenant.id == cambios["tenant_id"])):
            raise HTTPException(400, detail="El hospital indicado no existe")

    panel_final = cambios.get("panel", user.panel)
    role_final = cambios.get("role", user.role)
    if panel_final == "admin" and role_final != "administrador":
        raise HTTPException(400, detail="Las cuentas del panel admin deben tener el rol 'administrador'")

    anteriores = {campo: getattr(user, campo) for campo in cambios}
    for field, value in cambios.items():
        setattr(user, field, value)
    if data.password:
        user.password = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
        cambios["password"] = "••••••••"
        anteriores["password"] = "••••••••"

    await db.commit()
    await db.refresh(user)
    await create_audit_log(
        db, user_id=actor.get("sub"), user_name=actor.get("name") or actor.get("email"),
        tenant_id=None, tenant_name=None, action="user_updated",
        model="User", model_id=str(user.id), description=f"Usuario actualizado: {user.email}",
        old_values=anteriores, new_values=cambios,
    )
    return user


async def toggle_user(db: AsyncSession, user_id: uuid.UUID, is_active: bool, actor: dict) -> User | None:
    from app.admin.auditoria.service import create_audit_log

    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    if str(user.id) == str(actor.get("sub")) and not is_active:
        raise HTTPException(400, detail="No puedes desactivar tu propia cuenta")
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)
    await create_audit_log(
        db, user_id=actor.get("sub"), user_name=actor.get("name") or actor.get("email"),
        tenant_id=None, tenant_name=None,
        action="user_activated" if is_active else "user_deactivated",
        model="User", model_id=str(user.id),
        description=f"Usuario {'activado' if is_active else 'desactivado'}: {user.email}",
    )
    return user


async def delete_user(db: AsyncSession, user_id: uuid.UUID, actor: dict) -> bool:
    from app.admin.auditoria.service import create_audit_log

    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    if str(user.id) == str(actor.get("sub")):
        raise HTTPException(400, detail="No puedes eliminar tu propia cuenta")
    email, panel = user.email, user.panel
    await db.delete(user)
    await db.commit()
    await create_audit_log(
        db, user_id=actor.get("sub"), user_name=actor.get("name") or actor.get("email"),
        tenant_id=None, tenant_name=None, action="user_deleted",
        model="User", model_id=str(user_id), description=f"Usuario eliminado: {email} ({panel})",
    )
    return True
