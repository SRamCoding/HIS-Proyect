import uuid

import bcrypt
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.sigarh.rrhh.models import Empleado, EmpleadoEspecialidad, Especialidad
from app.sigarh.mantenimiento.models import Profesion


async def _empleado_perfil(db: AsyncSession, tid: uuid.UUID, empleado_id: uuid.UUID) -> dict | None:
    empleado = await db.scalar(select(Empleado).where(
        Empleado.id == empleado_id, Empleado.tenant_id == tid))
    if not empleado:
        return None
    profesion = await db.scalar(select(Profesion).where(Profesion.id == empleado.profesion_id)) \
        if empleado.profesion_id else None
    filas = (await db.execute(
        select(EmpleadoEspecialidad, Especialidad)
        .join(Especialidad, Especialidad.id == EmpleadoEspecialidad.especialidad_id)
        .where(EmpleadoEspecialidad.empleado_id == empleado.id)
    )).all()
    return {
        "nombre_completo": empleado.nombre_completo,
        "dni": empleado.dni,
        "celular": empleado.celular,
        "correo": empleado.correo,
        "cargo_laboral": empleado.cargo_laboral,
        "titulo_profesional": empleado.titulo_profesional,
        "profesion_nombre": profesion.nombre if profesion else None,
        "numero_cmp": empleado.numero_cmp,
        "numero_colegiatura": empleado.numero_colegiatura,
        "habilitado_colegio": empleado.habilitado_colegio,
        "especialidades": [
            {"nombre": esp.nombre, "numero_rne": ee.numero_rne, "validado": ee.validado}
            for ee, esp in filas
        ],
    }


async def obtener_perfil(db: AsyncSession, tid: uuid.UUID, current_user: dict) -> dict:
    user = await db.get(User, uuid.UUID(current_user["sub"]))
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    empleado = None
    if current_user.get("empleado_id"):
        empleado = await _empleado_perfil(db, tid, uuid.UUID(current_user["empleado_id"]))
    return {"name": user.name, "email": user.email, "role": user.role, "empleado": empleado}


async def actualizar_perfil(db: AsyncSession, current_user: dict, data) -> dict:
    user = await db.get(User, uuid.UUID(current_user["sub"]))
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

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
        # Invalida cualquier sesión emitida con la contraseña anterior.
        await db.execute(
            update(User).where(User.id == user.id).values(session_version=User.session_version + 1)
        )

    if data.name:
        user.name = data.name
    if data.email:
        user.email = data.email

    await db.commit()
    await db.refresh(user)
    return await obtener_perfil(db, uuid.UUID(current_user["tenant_id"]), current_user)
