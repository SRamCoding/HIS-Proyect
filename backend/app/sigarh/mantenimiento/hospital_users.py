"""Cuentas App gestionadas por la misma cadena rol → perfil → usuario."""
import uuid
import bcrypt
from fastapi import HTTPException
from sqlalchemy import select, func, or_
from app.auth.models import User
from app.sigarh.mantenimiento.models import PerfilUsuario, RolSistema
from app.sigarh.mantenimiento.schemas import UsuarioSigarhCreate
from app.sigarh.mantenimiento.security import lista

def salida(user, tid):
    return {'id': user.id, 'tenant_id': tid, 'panel': 'app', 'empleado_id': user.empleado_id,
        'perfil_id': user.perfil_usuario_id, 'username': user.username or user.email,
        'email': user.email, 'is_active': user.is_active, 'created_at': user.created_at}

async def guardar(db, tid, data, actor, item=None):
    from app.sigarh.mantenimiento.service import bloquear_escritura, auditar, referencia
    from app.sigarh.rrhh.models import Empleado
    from app.sigarh.mantenimiento.models import Profesion
    await bloquear_escritura(db, tid)
    supplied = data.model_dump(exclude_unset=True)
    values = salida(item, tid) if item else {}
    values.update(supplied)
    values['panel'] = 'app'
    if item and not supplied.get('password'): values['password'] = 'Placeholder1!'
    entrada = UsuarioSigarhCreate.model_validate({k: v for k,v in values.items() if k in UsuarioSigarhCreate.model_fields})
    perfil = await referencia(db, PerfilUsuario, entrada.perfil_id, tid, 'perfil')
    rol = await referencia(db, RolSistema, perfil.rol_sistema_id, tid, 'rol')
    if rol.panel != 'app' or not rol.tipo_usuario:
        raise HTTPException(422, 'Seleccione un perfil del panel hospitalario')
    empleado = await referencia(db, Empleado, entrada.empleado_id, tid, 'empleado') if entrada.empleado_id else None
    grupos = set(lista(rol.grupos_ocupacionales_permitidos))
    if grupos and (not empleado or str(empleado.grupo_ocupacional_id) not in grupos):
        raise HTTPException(422, 'El empleado no pertenece a los grupos permitidos por el rol')
    if rol.tipo_usuario == 'medico':
        profesion = await db.get(Profesion, empleado.profesion_id) if empleado and empleado.profesion_id else None
        if not profesion or profesion.codigo != 'MED':
            raise HTTPException(422, 'Vincule un empleado con profesión Médico Cirujano')
    query = select(User.id).where(or_(func.lower(User.email).in_([entrada.email,entrada.username]),
        func.lower(User.username).in_([entrada.email,entrada.username])))
    if item: query = query.where(User.id != item.id)
    if await db.scalar(query.limit(1)): raise HTTPException(409, 'El usuario o correo ya existe en el panel hospitalario')
    if not item:
        item = User(id=uuid.uuid4(), name=empleado.nombre_completo if empleado else entrada.username,
            panel='app', tenant_id=None)
        db.add(item)
    item.role, item.username, item.email = rol.tipo_usuario, entrada.username, entrada.email
    item.perfil_usuario_id, item.empleado_id, item.is_active = perfil.id, entrada.empleado_id, entrada.is_active
    if supplied.get('password'):
        item.password = bcrypt.hashpw(entrada.password.encode(), bcrypt.gensalt()).decode()
    await db.commit(); await db.refresh(item)
    await auditar(actor, tid, item, 'hospital_user_saved')
    return salida(item, tid)
