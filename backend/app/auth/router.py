from fastapi import APIRouter, Depends, HTTPException, status, Request
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
    # Si el panel es sigarh, buscar primero en sigarh_usuarios
    if data.panel == "sigarh":
        import json
        sigarh_result = await db.execute(
            select(UsuarioSigarh).where(
                (UsuarioSigarh.email == data.email) | (UsuarioSigarh.username == data.email)
            )
        )
        sigarh_user = sigarh_result.scalar_one_or_none()
        if sigarh_user and verify_password(data.password, sigarh_user.password):
            if not sigarh_user.is_active:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")
            active_modules = []
            if sigarh_user.perfil_id:
                perfil_result = await db.execute(select(PerfilUsuario).where(PerfilUsuario.id == sigarh_user.perfil_id))
                perfil = perfil_result.scalar_one_or_none()
                if perfil and perfil.modulos_acceso:
                    active_modules = json.loads(perfil.modulos_acceso)
            token_data = {
                "sub": str(sigarh_user.id),
                "email": sigarh_user.email,
                "name": sigarh_user.username,
                "role": "sigarh",
                "panel": "sigarh",
                "tenant_id": str(sigarh_user.tenant_id) if sigarh_user.tenant_id else None,
                "active_modules": active_modules,
            }
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token(token_data)
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user={
                    "id": str(sigarh_user.id),
                    "name": sigarh_user.username,
                    "email": sigarh_user.email,
                    "role": "sigarh",
                    "panel": "sigarh",
                    "tenant_id": str(sigarh_user.tenant_id) if sigarh_user.tenant_id else None,
                    "active_modules": active_modules,
                }
            )

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

    result = await db.execute(
        select(User).where(User.id == payload["sub"])
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo"
        )

    # obtener módulos activos del tenant en refresh también
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

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "panel": user.panel,
        "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        "active_modules": active_modules,
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
            "active_modules": active_modules,
        }
    )


@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await _log_audit(
        db=db,
        user_id=None,
        user_name="Admin",
        tenant_id=None,
        action="logout",
        model="User",
        description="Cierre de sesión",
        ip_address=request.client.host if request.client else None,
    )
    return {"ok": True, "message": "Sesión cerrada correctamente"}


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