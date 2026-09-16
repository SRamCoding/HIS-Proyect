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


async def contexto_sigarh(db, usuario, hospital=None):
    from app.sigarh.mantenimiento.models import PerfilUsuario, RolSistema
    from app.sigarh.rrhh.models import Empleado
    from app.tenants.hospitales.models import Tenant, TenantModule
    from app.tenants.modulos.models import Module
    from app.core.database import AsyncSessionLocal as CentralSession

    async with CentralSession() as central_db:
        if hospital is None:
            hospital = await central_db.scalar(select(Tenant).where(
                Tenant.id == usuario.tenant_id, Tenant.is_active.is_(True)
            ))
        if not usuario.is_active or not hospital:
            raise HTTPException(401, "Usuario u hospital inactivo")

        habilitados = set((await central_db.scalars(select(TenantModule.module_code).join(
            Module, Module.code == TenantModule.module_code,
        ).where(
            TenantModule.tenant_id == usuario.tenant_id,
            TenantModule.is_active.is_(True),
            Module.is_active.is_(True),
        ))).all())

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
    if rol.modulo_requerido and rol.modulo_requerido not in habilitados:
        raise HTTPException(403, "El módulo requerido por el rol no está habilitado")
    # tenant_modules (habilitados) solo guarda módulos completos: un código de
    # submódulo (ej. "sigarh_recursos_humanos.empleados") cuenta como habilitado
    # si el hospital contrató su módulo padre, aunque el string exacto no calce.
    #
    # El cruce Perfil×Rol tampoco puede ser una interseccion exacta de strings:
    # si el Rol tiene un submódulo puntual ("...empleados") y el Perfil tiene
    # el módulo padre completo ("sigarh_recursos_humanos"), un "&" de sets
    # entre esos dos códigos distintos da vacío y el permiso desaparece en
    # silencio. permiso_incluye() ya sabe que el código padre cubre a sus
    # hijos; se usa para verificar, código por código, que AMBOS lados (rol y
    # perfil) —cada uno leído como conjunto de wildcards— cubren ese código.
    from app.tenants.modulos.submodulos import modulo_padre, permiso_incluye
    concedidos_perfil = set(lista(perfil.modulos_acceso))
    concedidos_rol = set(lista(rol.modulos_permitidos))
    candidatos = concedidos_perfil | concedidos_rol
    modulos = sorted(
        c for c in candidatos
        if permiso_incluye(concedidos_rol, c) and permiso_incluye(concedidos_perfil, c)
        and modulo_padre(c) in habilitados
    )
    return {
        "sub": str(usuario.id), "email": usuario.email, "name": usuario.name or usuario.username,
        "role": "sigarh", "panel": "sigarh", "tenant_id": str(usuario.tenant_id),
        "active_modules": modulos, "perfil_id": str(perfil.id),
        "empleado_id": str(empleado.id) if empleado else None,
        "permisos_accion": lista(rol.permisos_accion), "alcance_global": rol.alcance_global,
        "auth_source": "sigarh", "session_version": usuario.session_version,
    }


async def usuario_actual(db, payload):
    from app.auth.models import User
    from app.sigarh.mantenimiento.models import UsuarioSigarh
    from app.tenants.hospitales.models import Tenant
    from app.core.tenant_db import get_tenant_sessionmaker

    try:
        uid = uuid.UUID(str(payload.get("sub")))
    except (ValueError, TypeError):
        raise HTTPException(401, "Sesión inválida")

    panel = payload.get("panel")
    tenant_id_str = payload.get("tenant_id")

    # Panel admin: siempre en la BD central, sin hospital asociado.
    if panel == "admin" or not tenant_id_str:
        usuario = await db.scalar(select(User).where(User.id == uid, User.is_active.is_(True)))
        if not usuario or usuario.panel != panel:
            raise HTTPException(401, "Usuario no encontrado o inactivo")
        if payload.get("session_version", 0) != usuario.session_version:
            raise HTTPException(401, "La sesión fue revocada; vuelva a ingresar")
        result = dict(payload)
        result.update(name=usuario.name, email=usuario.email, role=usuario.role, tenant_id=None)
        return result

    # Resto de paneles (app, sigarh, portal): resolver el hospital y su BD propia.
    try:
        tenant_uuid = uuid.UUID(tenant_id_str)
    except (ValueError, TypeError):
        raise HTTPException(401, "Sesión inválida")

    hospital = await db.scalar(select(Tenant).where(Tenant.id == tenant_uuid, Tenant.is_active.is_(True)))
    if not hospital or not hospital.database_name:
        raise HTTPException(401, "Hospital no encontrado o inactivo")

    TenantSession = get_tenant_sessionmaker(hospital.database_name)
    async with TenantSession() as tdb:
        if panel == "sigarh" or payload.get("auth_source") == "sigarh":
            usuario = await tdb.scalar(select(UsuarioSigarh).where(UsuarioSigarh.id == uid))
            if not usuario:
                raise HTTPException(401, "Usuario no encontrado")
            if payload.get("session_version", 0) != usuario.session_version:
                raise HTTPException(401, "La sesión fue revocada; vuelva a ingresar")
            return await contexto_sigarh(tdb, usuario, hospital=hospital)

        usuario = await tdb.scalar(select(User).where(User.id == uid, User.is_active.is_(True)))
        if not usuario or usuario.panel != panel:
            raise HTTPException(401, "Usuario no encontrado o inactivo")
        if payload.get("session_version", 0) != usuario.session_version:
            raise HTTPException(401, "La sesión fue revocada; vuelva a ingresar")
        result = dict(payload)
        result.update(name=usuario.name, email=usuario.email, role=usuario.role, tenant_id=str(hospital.id))
        return result


def es_admin_erp(user):
    return user.get("panel") == "admin" and user.get("role") == "administrador"


def exigir_permiso(user, permiso):
    if es_admin_erp(user):
        return
    if user.get("panel") != "sigarh" or permiso not in user.get("permisos_accion", []):
        raise HTTPException(403, f"Se requiere el permiso: {permiso}")
