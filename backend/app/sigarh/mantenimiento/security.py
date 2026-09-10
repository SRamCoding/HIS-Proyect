"""Permisos actuales de SIGARH, consultados en BD en cada solicitud."""
import json
import uuid
from fastapi import HTTPException
from sqlalchemy import select


def lista(value):
    try:
        parsed = json.loads(value) if isinstance(value, str) else value
        return parsed if isinstance(parsed, list) else []
    except (TypeError, ValueError):
        return []


async def contexto_sigarh(db, usuario):
    from app.sigarh.mantenimiento.models import PerfilUsuario, RolSistema
    from app.sigarh.rrhh.models import Empleado
    from app.tenants.hospitales.models import Tenant, TenantModule
    from app.tenants.modulos.models import Module
    hospital = await db.scalar(select(Tenant).where(Tenant.id == usuario.tenant_id, Tenant.is_active.is_(True)))
    if not usuario.is_active or not hospital:
        raise HTTPException(401, "Usuario u hospital inactivo")
    perfil = await db.scalar(select(PerfilUsuario).where(
        PerfilUsuario.id == usuario.perfil_id, PerfilUsuario.tenant_id == usuario.tenant_id,
        PerfilUsuario.is_active.is_(True),
    ))
    rol = await db.scalar(select(RolSistema).where(
        RolSistema.id == perfil.rol_sistema_id, RolSistema.tenant_id == usuario.tenant_id,
        RolSistema.is_active.is_(True), RolSistema.panel == "sigarh",
    )) if perfil else None
    if not perfil or not rol:
        raise HTTPException(401, "El usuario requiere un perfil y rol activos")
    grupos = set(lista(rol.grupos_ocupacionales_permitidos))
    empleado = None
    if usuario.empleado_id:
        empleado = await db.scalar(select(Empleado).where(
            Empleado.id == usuario.empleado_id, Empleado.tenant_id == usuario.tenant_id,
            Empleado.is_active.is_(True),
        ))
        if not empleado:
            raise HTTPException(401, "Empleado inactivo o ajeno al hospital")
    if grupos and (not empleado or str(empleado.grupo_ocupacional_id) not in grupos):
        raise HTTPException(403, "El grupo ocupacional no está autorizado por el rol")
    habilitados = set((await db.scalars(select(TenantModule.module_code).join(
        Module, Module.code == TenantModule.module_code,
    ).where(TenantModule.tenant_id == usuario.tenant_id, TenantModule.is_active.is_(True), Module.is_active.is_(True)))).all())
    if rol.modulo_requerido and rol.modulo_requerido not in habilitados:
        raise HTTPException(403, "El módulo requerido por el rol no está habilitado")
    modulos = sorted(set(lista(perfil.modulos_acceso)) & set(lista(rol.modulos_permitidos)) & habilitados)
    return {
        "sub": str(usuario.id), "email": usuario.email, "name": usuario.username,
        "role": "sigarh", "panel": "sigarh", "tenant_id": str(usuario.tenant_id),
        "active_modules": modulos, "perfil_id": str(perfil.id),
        "empleado_id": str(empleado.id) if empleado else None,
        "permisos_accion": lista(rol.permisos_accion), "alcance_global": rol.alcance_global,
        "auth_source": "sigarh", "session_version": usuario.session_version,
    }


async def usuario_actual(db, payload):
    from app.auth.models import User
    from app.sigarh.mantenimiento.models import UsuarioSigarh
    try:
        uid = uuid.UUID(str(payload.get("sub")))
    except (ValueError, TypeError):
        raise HTTPException(401, "Sesión inválida")
    # Tokens anteriores del panel SIGARH se verifican contra la cuenta real.
    if payload.get("auth_source") == "sigarh" or payload.get("panel") == "sigarh":
        usuario = await db.scalar(select(UsuarioSigarh).where(UsuarioSigarh.id == uid))
        if usuario:
            if payload.get("session_version", 0) != usuario.session_version:
                raise HTTPException(401, "La sesión fue revocada; vuelva a ingresar")
            return await contexto_sigarh(db, usuario)
        if payload.get("auth_source") == "sigarh":
            raise HTTPException(401, "Usuario no encontrado")
    usuario = await db.scalar(select(User).where(User.id == uid, User.is_active.is_(True)))
    if not usuario or usuario.panel != payload.get("panel"):
        raise HTTPException(401, "Usuario no encontrado o inactivo")
    result = dict(payload)
    result.update(name=usuario.name, email=usuario.email, role=usuario.role,
                  tenant_id=str(usuario.tenant_id) if usuario.tenant_id else None)
    # Las cuentas globales no reciben permisos SIGARH implícitos.
    if usuario.panel == "sigarh":
        result.update(active_modules=[], permisos_accion=[], perfil_id=None, empleado_id=None)
    return result


def es_admin_erp(user):
    return user.get("panel") == "admin" and user.get("role") == "administrador"


def exigir_permiso(user, permiso):
    if es_admin_erp(user):
        return
    if user.get("panel") != "sigarh" or permiso not in user.get("permisos_accion", []):
        raise HTTPException(403, f"Se requiere el permiso: {permiso}")
