from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import bcrypt
import uuid as uuid_lib

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.config import settings
from app.auth.models import User
from app.sigarh.mantenimiento.models import UsuarioSigarh, PerfilUsuario
from app.auth.schemas import LoginRequest, TokenResponse, RefreshRequest

router = APIRouter()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    # --- Panel admin: sigue 100% contra la BD central ---
    if data.panel == "admin":
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.password):
            await _log_audit(db, None, "Sistema", None, "login_failed", "User",
                              f"Intento de inicio de sesión fallido: {data.email}",
                              request.client.host if request.client else None)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales incorrectas")

        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuario inactivo")

        if user.panel != "admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes acceso al panel 'admin'")

        await _log_audit(db, str(user.id), user.name, None, "login", "User",
                          "Inicio de sesión", request.client.host if request.client else None)

        token_data = {
            "sub": str(user.id), "email": user.email, "name": user.name,
            "role": user.role, "panel": user.panel, "tenant_id": None,
            "active_modules": [], "session_version": user.session_version,
        }
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
            user={**token_data, "id": token_data["sub"]},
        )

    # --- Paneles app / sigarh / portal: requieren hospital resuelto por header ---
    from app.core.tenant_db import get_tenant_by_id, tenant_session

    raw_tenant = request.headers.get("X-Tenant-ID")
    if raw_tenant:
        try:
            tenant_id = uuid_lib.UUID(raw_tenant)
        except ValueError:
            raise HTTPException(400, "X-Tenant-ID inválido")
        tenant = await get_tenant_by_id(tenant_id)
    else:
        from app.tenants.hospitales.service import get_tenant_by_domain
        host = (request.headers.get("host") or "").split(":")[0]
        tenant = await get_tenant_by_domain(db, host)

    if not tenant or not tenant.database_name:
        raise HTTPException(404, "Hospital no encontrado")

    async with tenant_session(tenant.database_name) as tdb:
        if data.panel == "sigarh":
            from sqlalchemy import func, or_
            from app.sigarh.mantenimiento.security import contexto_sigarh
            identifier = data.email.strip().lower()
            matches = (await tdb.scalars(select(UsuarioSigarh).where(or_(
                func.lower(UsuarioSigarh.email) == identifier,
                func.lower(UsuarioSigarh.username) == identifier,
            )).limit(2))).all()
            if len(matches) != 1 or not verify_password(data.password, matches[0].password):
                raise HTTPException(401, "Credenciales incorrectas o identificador ambiguo")
            token_data = await contexto_sigarh(tdb, matches[0], hospital=tenant)
            token_data["tenant_id"] = str(tenant.id)
            return _respuesta_sesion(token_data)

        from sqlalchemy import func, or_
        identifier = data.email.strip().lower()
        matches = (await tdb.scalars(select(User).where(or_(func.lower(User.email) == identifier,
            func.lower(User.username) == identifier)).limit(2))).all()
        user = matches[0] if len(matches) == 1 else None

        if not user or not verify_password(data.password, user.password):
            await _log_audit(db, None, "Sistema", str(tenant.id), "login_failed", "User",
                              f"Intento de inicio de sesión fallido: {data.email}",
                              request.client.host if request.client else None)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales incorrectas")

        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuario inactivo")

        if user.panel != data.panel:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"No tienes acceso al panel '{data.panel}'")

        await _log_audit(db, str(user.id), user.name, str(tenant.id), "login", "User",
                          "Inicio de sesión", request.client.host if request.client else None)

        from app.tenants.hospitales.models import TenantModule
        mods_result = await db.execute(
            select(TenantModule).where(
                TenantModule.tenant_id == tenant.id,
                TenantModule.is_active == True
            )
        )
        active_modules = [m.module_code for m in mods_result.scalars().all()]

        if user.panel == "app":
            from app.auth.hospital_access import contexto_hospital, validar_rol_hospital, limitar_por_rol
            if user.perfil_usuario_id:
                return _respuesta_sesion(await contexto_hospital(tdb, user, tenant, set(active_modules)))
            rol = await validar_rol_hospital(db, user.role)
            return _respuesta_sesion(limitar_por_rol(await contexto_hospital(tdb, user, tenant, set(active_modules)), rol))

        token_data = {
            "sub": str(user.id), "email": user.email, "name": user.name,
            "role": user.role, "panel": user.panel, "tenant_id": str(tenant.id),
            "active_modules": active_modules, "session_version": user.session_version,
        }
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
            user={**token_data, "id": token_data["sub"]},
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    payload = verify_token(data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado"
        )

    from app.sigarh.mantenimiento.security import usuario_actual
    token_data = await usuario_actual(db, payload)
    if token_data.get("auth_source") != "sigarh" and token_data.get("panel") != "app":
        from app.tenants.hospitales.models import TenantModule
        active_modules = []
        if token_data.get("tenant_id"):
            import uuid
            active_modules = list((await db.scalars(select(TenantModule.module_code).where(
                TenantModule.tenant_id == uuid.UUID(token_data["tenant_id"]), TenantModule.is_active.is_(True),
            ))).all())
        token_data["active_modules"] = active_modules
    return _respuesta_sesion(token_data)


def _respuesta_sesion(token_data):
    claims = {k: v for k, v in token_data.items() if k not in {"exp", "type", "iat", "nbf"}}
    return TokenResponse(access_token=create_access_token(claims), refresh_token=create_refresh_token(claims),
                         user={"id": claims["sub"], **claims})


async def _revocar_sesion_actual(user: dict) -> bool:
    """Revoca (incrementa session_version) la cuenta de la sesion ACTUAL.

    A diferencia de _cuenta_localizada (pensada para cuando un admin busca
    una cuenta por id sin saber donde vive, y por eso recorre cada hospital
    con base fisica propia), el propio JWT de la sesion YA trae panel,
    tenant_id y auth_source resueltos y validados -- no hay motivo para que
    un logout tenga que barrer TODOS los hospitales, ni para que uno ajeno,
    caido o lento, pueda demorar o afectar el logout de otra cuenta.

    El incremento se hace con un UPDATE ... SET session_version =
    session_version + 1 (calculado en el propio SQL), no leyendo el valor
    en Python y sumando 1 antes de guardar: asi el commit de un logout
    concurrente con un cambio de contraseña o un login no puede "perder"
    el incremento del otro.

    Devuelve True solo si una fila fue efectivamente actualizada."""
    from app.core.database import AsyncSessionLocal

    try:
        uid = uuid_lib.UUID(str(user["sub"]))
    except (ValueError, TypeError, KeyError):
        return False

    panel = user.get("panel")
    tenant_id_str = user.get("tenant_id")

    if panel == "admin" or not tenant_id_str:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                update(User).where(User.id == uid).values(session_version=User.session_version + 1)
            )
            await db.commit()
        return result.rowcount > 0

    try:
        tenant_uuid = uuid_lib.UUID(str(tenant_id_str))
    except (ValueError, TypeError):
        return False

    from app.tenants.hospitales.models import Tenant
    from app.core.tenant_db import get_tenant_sessionmaker
    async with AsyncSessionLocal() as db:
        hospital = await db.get(Tenant, tenant_uuid)
    if not hospital or not hospital.database_name:
        return False

    TenantSession = get_tenant_sessionmaker(hospital.database_name)
    async with TenantSession() as tdb:
        if panel == "sigarh" or user.get("auth_source") == "sigarh":
            result = await tdb.execute(
                update(UsuarioSigarh).where(UsuarioSigarh.id == uid)
                .values(session_version=UsuarioSigarh.session_version + 1)
            )
        else:
            result = await tdb.execute(
                update(User).where(User.id == uid).values(session_version=User.session_version + 1)
            )
        await tdb.commit()
    return result.rowcount > 0


async def _log_audit_seguro(
    user_id: str | None, user_name: str | None, tenant_id: str | None, action: str,
    model: str | None = None, description: str | None = None, ip_address: str | None = None,
) -> None:
    """Como _log_audit, pero en su PROPIA sesion (nunca la que uso la
    operacion que se esta auditando) y sin propagar sus propios errores.

    _revocar_sesion_actual y el registro de auditoria del logout son dos
    resultados independientes: un fallo al escribir el evento de auditoria
    no debe convertir una revocacion ya confirmada en una respuesta de
    error, y si la revocacion fallo porque una sesion quedo en un estado
    invalido tras un commit fallido, reusar esa misma sesion para el
    intento de auditoria solo produce un segundo error que tapa al primero
    y deja sin registrar el evento.

    Si ni siquiera este intento directo funciona, el evento cae a la misma
    cola de recuperacion (audit_log_fallback) que usa la auditoria
    automatica -- antes se quedaba solo en el log tecnico, invisible y sin
    forma de recuperarlo."""
    from app.core.database import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as audit_db:
            await _log_audit(audit_db, user_id, user_name, tenant_id, action,
                             model=model, description=description, ip_address=ip_address)
    except Exception:
        import logging
        logging.getLogger(__name__).exception(
            "No se pudo registrar el evento de auditoria de logout, se guarda en fallback"
        )
        from app.core.audit import guardar_evento_en_fallback
        entrada = {
            "action": action, "model": model, "model_id": None,
            "old_values": None, "new_values": {"description": description} if description else None,
            "tenant_hint": tenant_id, "db_name_hint": None,
        }
        actor = {"user_id": user_id, "user_name": user_name, "tenant_id": tenant_id}
        await guardar_evento_en_fallback(entrada, actor, ip_address)


@router.post("/logout")
async def logout(request: Request, user=Depends(get_current_user)):
    # session_version sube al cerrar sesion para que el token que quedo en el
    # navegador (o una copia filtrada) deje de servir de inmediato -- antes
    # solo pasaba para SIGARH y, ademas, solo si esa cuenta vivia en la BD
    # central: con hospital de base fisica propia (el caso mas comun) la
    # cuenta no se encontraba ahi y la revocacion no hacia nada.
    try:
        revocado = await _revocar_sesion_actual(user)
    except Exception:
        import logging
        logging.getLogger(__name__).exception("No se pudo revocar la sesion de %s", user.get("sub"))
        revocado = False

    modelo = "UsuarioSigarh" if user.get("auth_source") == "sigarh" else "User"
    ip = request.client.host if request.client else None
    if not revocado:
        # No se puede afirmar que la sesion quedo invalidada del lado del
        # servidor -- responder 200 igual (como antes) dejaba creer que el
        # token viejo ya no sirve cuando en realidad puede seguir siendo
        # valido hasta que expire. En un ERP hospitalario eso es
        # inaceptable: se devuelve error explicito para que el cliente lo
        # sepa (aunque de todas formas descarte el token localmente).
        await _log_audit_seguro(user.get("sub"), user.get("name"), user.get("tenant_id"), "logout_fallido",
                                model=modelo,
                                description="No se pudo confirmar la revocación de la sesión en el servidor",
                                ip_address=ip)
        raise HTTPException(500, "No se pudo cerrar la sesión de forma segura en el servidor. Intenta nuevamente.")

    await _log_audit_seguro(user.get("sub"), user.get("name"), user.get("tenant_id"), "logout",
                            model=modelo,
                            description="Cierre de sesión", ip_address=ip)
    return {"ok": True}


async def _log_audit(
    db: AsyncSession,
    user_id: str | None,
    user_name: str | None,
    tenant_id: str | None,
    action: str,
    model: str | None = None,
    description: str | None = None,
    ip_address: str | None = None,
) -> None:
    import uuid
    from app.admin.auditoria.models import AuditLog

    log = AuditLog(
        user_id=uuid.UUID(user_id) if user_id else None,
        user_name=user_name,
        tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
        action=action,
        model=model,
        description=description,
        ip_address=ip_address,
    )
    db.add(log)
    await db.commit()
