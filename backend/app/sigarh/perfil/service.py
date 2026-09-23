# backend/app/sigarh/perfil/service.py
import uuid
import bcrypt
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.sigarh.mantenimiento.models import UsuarioSigarh


async def obtener_perfil(db: AsyncSession, user_id: str) -> UsuarioSigarh:
    user = await db.get(UsuarioSigarh, uuid.UUID(user_id))
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    return user


async def actualizar_perfil(db: AsyncSession, user_id: str, data) -> UsuarioSigarh:
    """Mismo criterio que app/admin/perfil/service.py::actualizar_perfil:
    cambiar el correo o la contraseña exige reautenticar con la contraseña
    actual, y cambiar la contraseña invalida cualquier sesion ya emitida
    (session_version) en vez de dejarla viva hasta que expire sola."""
    user = await obtener_perfil(db, user_id)

    if data.email and data.email != user.email:
        if not data.current_password:
            raise HTTPException(400, "Ingresa tu contraseña actual para cambiar el correo")
        if not bcrypt.checkpw(data.current_password.encode(), user.password.encode()):
            raise HTTPException(400, "La contraseña actual no es correcta")
        existente = await db.scalar(
            select(UsuarioSigarh.id).where(UsuarioSigarh.email == data.email, UsuarioSigarh.id != user.id)
        )
        if existente:
            raise HTTPException(400, f"Ya existe un usuario con el correo {data.email}")

    if data.new_password:
        if not data.current_password:
            raise HTTPException(400, "Ingresa tu contraseña actual para cambiarla")
        if not bcrypt.checkpw(data.current_password.encode(), user.password.encode()):
            raise HTTPException(400, "La contraseña actual no es correcta")
        user.password = bcrypt.hashpw(data.new_password.encode(), bcrypt.gensalt()).decode()
        await db.execute(
            update(UsuarioSigarh).where(UsuarioSigarh.id == user.id).values(session_version=UsuarioSigarh.session_version + 1)
        )

    if data.name:
        user.name = data.name
    if data.email:
        user.email = data.email

    await db.commit()
    await db.refresh(user)
    return user
