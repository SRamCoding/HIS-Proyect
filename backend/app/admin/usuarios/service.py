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
    if data.panel != "admin":
        from app.tenants.hospitales.models import Tenant
        from app.core.tenant_db import get_tenant_sessionmaker
        hospital = await db.get(Tenant, data.tenant_id) if data.tenant_id else None
        if not hospital or not hospital.is_active or not hospital.database_name:
            raise HTTPException(400, detail="Seleccione un hospital activo con base de datos")
        async with get_tenant_sessionmaker(hospital.database_name)() as hospital_db:
            if await hospital_db.scalar(select(User.id).where(User.email == data.email)):
                raise HTTPException(400, detail="El correo ya existe en este hospital")
            await validar_empleado_usuario(hospital_db, hospital.id, data.empleado_id, data.panel)
            from app.auth.hospital_access import validar_perfil
            await validar_perfil(hospital_db, hospital.id, data.perfil_hospital_id, data.role, data.empleado_id, data.panel)
            user = User(perfil_hospital_id=data.perfil_hospital_id, empleado_id=data.empleado_id, name=data.name, email=data.email,
                        password=bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode(),
                        role=data.role, panel=data.panel, tenant_id=None, is_active=True)
            hospital_db.add(user)
            await hospital_db.commit()
            await hospital_db.refresh(user)
        from app.admin.auditoria.service import create_audit_log
        await create_audit_log(db, user_id=creador.get("sub"), user_name=creador.get("name"),
                              tenant_id=hospital.id, tenant_name=hospital.name, action="user_created",
                              model="User", model_id=str(user.id), description=f"Usuario creado: {user.email}")
        return user
    if data.tenant_id:
        raise HTTPException(400, detail="Una cuenta admin no pertenece a un hospital")
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


async def _locate_user(db: AsyncSession, user_id: uuid.UUID):
    """Busca un User en la BD central; si no está ahí, lo busca en la BD
    física de cada hospital con base propia (ver create_tenant). Devuelve
    (user, sesion_de_trabajo, sesion_es_de_tenant, "user"). La sesión de
    tenant, si se abre, queda a cargo del llamador (cerrarla cuando termine)."""
    user = await get_user_by_id(db, user_id)
    if user:
        return user, db, False, "user"

    from app.tenants.hospitales.models import Tenant
    from app.core.tenant_db import get_tenant_sessionmaker

    tenants = (await db.scalars(
        select(Tenant).where(Tenant.database_name.is_not(None), Tenant.is_active.is_(True))
    )).all()
    for tenant in tenants:
        TenantSession = get_tenant_sessionmaker(tenant.database_name)
        tdb = TenantSession()
        found = await tdb.scalar(select(User).where(User.id == user_id))
        if found:
            return found, tdb, True, "user"
        await tdb.close()
    return None, None, False, None


async def _locate_cuenta(db: AsyncSession, user_id: uuid.UUID):
    """Como _locate_user, pero además busca en UsuarioSigarh (central y por
    hospital) si no se encontró como User. Devuelve (cuenta, sesion, es_tenant, tipo)
    con tipo en {"user", "sigarh"}."""
    found, work_db, es_tenant, tipo = await _locate_user(db, user_id)
    if found:
        return found, work_db, es_tenant, tipo

    from app.sigarh.mantenimiento.models import UsuarioSigarh
    from app.tenants.hospitales.models import Tenant
    from app.core.tenant_db import get_tenant_sessionmaker

    sigarh_user = await db.scalar(select(UsuarioSigarh).where(UsuarioSigarh.id == user_id))
    if sigarh_user:
        return sigarh_user, db, False, "sigarh"

    tenants = (await db.scalars(
        select(Tenant).where(Tenant.database_name.is_not(None), Tenant.is_active.is_(True))
    )).all()
    for tenant in tenants:
        TenantSession = get_tenant_sessionmaker(tenant.database_name)
        tdb = TenantSession()
        found_sigarh = await tdb.scalar(select(UsuarioSigarh).where(UsuarioSigarh.id == user_id))
        if found_sigarh:
            return found_sigarh, tdb, True, "sigarh"
        await tdb.close()
    return None, None, False, None


async def update_user(db: AsyncSession, user_id: uuid.UUID, data, actor: dict) -> User | None:
    from app.admin.auditoria.service import create_audit_log

    user, work_db, es_tenant, tipo = await _locate_cuenta(db, user_id)
    if not user:
        return None
    if tipo == "sigarh":
        if es_tenant:
            await work_db.close()
        raise HTTPException(400, detail="Las cuentas SIGARH se editan desde SIGARH → Mantenimiento → Usuarios")
    try:
        cambios = data.model_dump(exclude_unset=True, exclude={"password"})
        if es_tenant:
            if cambios.get("panel", user.panel) == "admin":
                raise HTTPException(400, detail="Una cuenta hospitalaria no puede convertirse en admin")
            if "tenant_id" in cambios:
                if cambios["tenant_id"] is not None:
                    from app.tenants.hospitales.models import Tenant
                    hospital = await db.scalar(select(Tenant).where(Tenant.database_name == work_db.bind.url.database))
                    if not hospital or hospital.id != cambios["tenant_id"]:
                        raise HTTPException(400, detail="No se puede trasladar una cuenta a otro hospital")
                cambios.pop("tenant_id")
        if data.email and data.email != user.email:
            existente = await work_db.scalar(select(User.id).where(User.email == data.email, User.id != user_id))
            if existente:
                raise HTTPException(400, detail=f"Ya existe un usuario con el correo {data.email}")
        if cambios.get("tenant_id"):
            from app.tenants.hospitales.models import Tenant
            if not await db.scalar(select(Tenant.id).where(Tenant.id == cambios["tenant_id"])):
                raise HTTPException(400, detail="El hospital indicado no existe")

        panel_final = cambios.get("panel", user.panel)
        await validar_empleado_usuario(work_db, None, cambios.get("empleado_id", user.empleado_id), panel_final)
        role_final = cambios.get("role", user.role)
        from app.auth.hospital_access import validar_perfil
        await validar_perfil(work_db, None, cambios.get("perfil_hospital_id", user.perfil_hospital_id),
            role_final, cambios.get("empleado_id", user.empleado_id), panel_final)
        if panel_final == "admin" and role_final != "administrador":
            raise HTTPException(400, detail="Las cuentas del panel admin deben tener el rol 'administrador'")

        def _serializable(v):
            return str(v) if isinstance(v, uuid.UUID) else v

        anteriores = {campo: _serializable(getattr(user, campo)) for campo in cambios}
        for field, value in cambios.items():
            setattr(user, field, value)
        cambios = {campo: _serializable(valor) for campo, valor in cambios.items()}
        if data.password:
            user.password = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
            cambios["password"] = "••••••••"
            anteriores["password"] = "••••••••"

        await work_db.commit()
        await work_db.refresh(user)
    finally:
        if es_tenant:
            await work_db.close()
    await create_audit_log(
        db, user_id=actor.get("sub"), user_name=actor.get("name") or actor.get("email"),
        tenant_id=None, tenant_name=None, action="user_updated",
        model="User", model_id=str(user.id), description=f"Usuario actualizado: {user.email}",
        old_values=anteriores, new_values=cambios,
    )
    return user


async def toggle_user(db: AsyncSession, user_id: uuid.UUID, is_active: bool, actor: dict):
    from app.admin.auditoria.service import create_audit_log

    user, work_db, es_tenant, tipo = await _locate_cuenta(db, user_id)
    if not user:
        return None
    if str(user.id) == str(actor.get("sub")) and not is_active:
        if es_tenant:
            await work_db.close()
        raise HTTPException(400, detail="No puedes desactivar tu propia cuenta")
    try:
        user.is_active = is_active
        await work_db.commit()
        await work_db.refresh(user)
    finally:
        if es_tenant:
            await work_db.close()
    modelo = "UsuarioSigarh" if tipo == "sigarh" else "User"
    email = user.email
    await create_audit_log(
        db, user_id=actor.get("sub"), user_name=actor.get("name") or actor.get("email"),
        tenant_id=None, tenant_name=None,
        action="user_activated" if is_active else "user_deactivated",
        model=modelo, model_id=str(user.id),
        description=f"Usuario {'activado' if is_active else 'desactivado'}: {email}",
    )
    return user


async def delete_user(db: AsyncSession, user_id: uuid.UUID, actor: dict) -> bool:
    from app.admin.auditoria.service import create_audit_log

    user, work_db, es_tenant, tipo = await _locate_cuenta(db, user_id)
    if not user:
        return False
    if str(user.id) == str(actor.get("sub")):
        if es_tenant:
            await work_db.close()
        raise HTTPException(400, detail="No puedes eliminar tu propia cuenta")
    email = user.email
    panel = "sigarh" if tipo == "sigarh" else user.panel
    try:
        await work_db.delete(user)
        await work_db.commit()
    finally:
        if es_tenant:
            await work_db.close()
    modelo = "UsuarioSigarh" if tipo == "sigarh" else "User"
    await create_audit_log(
        db, user_id=actor.get("sub"), user_name=actor.get("name") or actor.get("email"),
        tenant_id=None, tenant_name=None, action="user_deleted",
        model=modelo, model_id=str(user_id), description=f"Usuario eliminado: {email} ({panel})",
    )
    return True


async def validar_empleado_usuario(db, tid, empleado_id, panel):
    if not empleado_id:
        return
    if panel != "app":
        raise HTTPException(400, detail="Solo el panel hospitalario admite vincular un empleado.")
    from app.sigarh.rrhh.models import Empleado
    query = select(Empleado).where(Empleado.id == empleado_id, Empleado.is_active == True)
    if tid:
        query = query.where(Empleado.tenant_id == tid)
    if not await db.scalar(query):
        raise HTTPException(400, detail="El empleado no pertenece a este hospital o no está activo.")
