# backend/app/admin/perfil/service.py
import uuid
import bcrypt
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User


async def obtener_perfil(db: AsyncSession, user_id: str) -> User:
    user = await db.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    return user


async def actualizar_perfil(db: AsyncSession, user_id: str, data) -> User:
    user = await obtener_perfil(db, user_id)

    if data.email and data.email != user.email:
        existente = await db.scalar(select(User.id).where(User.email == data.email, User.id != user.id))
        if existente:
            raise HTTPException(400, f"Ya existe un usuario con el correo {data.email}")

    if data.new_password:
        if not data.current_password:
            raise HTTPException(400, "Ingresa tu contraseña actual para cambiarla")
        if not bcrypt.checkpw(data.current_password.encode(), user.password.encode()):
            raise HTTPException(400, "La contraseña actual no es correcta")
        user.password = bcrypt.hashpw(data.new_password.encode(), bcrypt.gensalt()).decode()
        # Invalida cualquier token que ya se haya emitido con la contraseña
        # anterior -- sin esto, cambiar la contraseña no revocaba sesiones
        # activas (una copia del token seguia sirviendo hasta que expirara).
        # UPDATE atomico en SQL (no "+= 1" en Python) por la misma razon que
        # en el logout: evita perder el incremento si otra operacion sobre
        # la misma cuenta corre en paralelo.
        await db.execute(
            update(User).where(User.id == user.id).values(session_version=User.session_version + 1)
        )

    if data.name:
        user.name = data.name
    if data.email:
        user.email = data.email

    await db.commit()
    await db.refresh(user)
    return user
