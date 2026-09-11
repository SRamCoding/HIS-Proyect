from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
            "active_modules": [],
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

        result = await tdb.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

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

        token_data = {
            "sub": str(user.id), "email": user.email, "name": user.name,
            "role": user.role, "panel": user.panel, "tenant_id": str(tenant.id),
            "active_modules": active_modules,
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
    if token_data.get("auth_source") != "sigarh":
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


@router.post("/logout")
async def logout(request: Request, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    if user.get("auth_source") == "sigarh":
        import uuid
        cuenta = await db.scalar(select(UsuarioSigarh).where(UsuarioSigarh.id == uuid.UUID(user["sub"])).with_for_update())
        if cuenta:
            cuenta.session_version += 1
    await _log_audit(db, user["sub"], user.get("name"), user.get("tenant_id"), "logout",
                     model="UsuarioSigarh" if user.get("auth_source") == "sigarh" else "User",
                     description="Cierre de sesión", ip_address=request.client.host if request.client else None)
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