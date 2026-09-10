from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt

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
    if data.panel == "sigarh":
        from sqlalchemy import func, or_
        from app.sigarh.mantenimiento.security import contexto_sigarh
        identifier = data.email.strip().lower()
        matches = (await db.scalars(select(UsuarioSigarh).where(or_(
            func.lower(UsuarioSigarh.email) == identifier,
            func.lower(UsuarioSigarh.username) == identifier,
        )).limit(2))).all()
        if len(matches) != 1 or not verify_password(data.password, matches[0].password):
            raise HTTPException(401, "Credenciales incorrectas o identificador ambiguo")
        token_data = await contexto_sigarh(db, matches[0])
        return _respuesta_sesion(token_data)

    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password):
        await _log_audit(
            db=db,
            user_id=None,
            user_name="Sistema",
            tenant_id=None,
            action="login_failed",
            model="User",
            description=f"Intento de inicio de sesión fallido: {data.email}",
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    if user.panel != data.panel:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No tienes acceso al panel '{data.panel}'"
        )

    await _log_audit(
        db=db,
        user_id=str(user.id),
        user_name=user.name,
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        action="login",
        model="User",
        description="Inicio de sesión",
        ip_address=request.client.host if request.client else None,
    )

    # ── LÍNEA 67: obtener módulos activos del tenant ──────────────────────────
    active_modules = []
    if user.tenant_id:
        from app.tenants.hospitales.models import TenantModule
        mods_result = await db.execute(
            select(TenantModule).where(
                TenantModule.tenant_id == user.tenant_id,
                TenantModule.is_active == True
            )
        )
        active_modules = [m.module_code for m in mods_result.scalars().all()]
    # ── FIN LÍNEA 67 ──────────────────────────────────────────────────────────

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "panel": user.panel,
        "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        "active_modules": active_modules,  # ← línea 80
    }

    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user={
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "panel": user.panel,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
            "active_modules": active_modules,  # ← línea 91
        }
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