import uuid
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload
from redis.asyncio import Redis

from app.tenants.hospitales.models import Tenant, TenantModule
from app.tenants.hospitales.schemas import TenantCreate, TenantUpdate
from app.core.tenancy import invalidate_tenant_cache


def generate_schema_name(domain: str) -> str:
    """
    Genera el nombre del schema PostgreSQL desde el dominio.
    Equivalente a Tenant::getDatabaseName() de Laravel.
    Ejemplo: hospital-tuman.erp.local → tenant_hospital_tuman_erp_local
    """
    clean = re.sub(r"[.\-]", "_", domain)
    return f"tenant_{clean}"


async def create_tenant(
    db: AsyncSession,
    data: TenantCreate,
) -> Tenant:
    import asyncio
    import json
    import bcrypt
    from app.auth.models import User
    from app.sigarh.mantenimiento.models import RolSistema, PerfilUsuario, UsuarioSigarh
    from app.core.tenant_db import (
        create_tenant_database,
        run_tenant_migrations,
        get_tenant_sessionmaker,
        _slugify_db_name,
    )

    schema_name = generate_schema_name(data.domain)
    subdomain = data.domain.split(".")[0]
    database_name = _slugify_db_name(subdomain)

    tenant = Tenant(
        name=data.name,
        domain=data.domain,
        schema_name=schema_name,
        database_name=database_name,
        ruc=data.ruc,
        address=data.address,
        phone=data.phone,
        email=data.email,
        hospital_level=data.hospital_level,
        mission=data.mission,
        vision=data.vision,
    )
    db.add(tenant)
    await db.flush()

    for module_code in data.active_modules:
        module = TenantModule(
            tenant_id=tenant.id,
            module_code=module_code,
            is_active=True,
        )
        db.add(module)

    await db.commit()
    await db.refresh(tenant)

    # --- Provisión de la BD física del hospital (100% independiente) ---
    await create_tenant_database(database_name)
    await asyncio.to_thread(run_tenant_migrations, database_name)

    # --- Crear usuarios DENTRO de la BD del hospital, no en la central ---
    TenantSession = get_tenant_sessionmaker(database_name)
    async with TenantSession() as tenant_db:
        if data.admin_email and data.admin_password:
            admin_user = User(
                name=data.admin_name or "Administrador",
                email=data.admin_email,
                password=bcrypt.hashpw(
                    data.admin_password.encode(), bcrypt.gensalt()
                ).decode(),
                role="administrador",
                panel="app",
                tenant_id=None,
                is_active=True,
            )
            tenant_db.add(admin_user)

        if data.sigarh_email and data.sigarh_password:
            rol = RolSistema(
                tenant_id=tenant.id,
                nombre="Administrador SIGARH",
                panel="sigarh",
                modulos_permitidos=json.dumps(data.active_modules),
                # El rol Administrador SIGARH debe poder gestionar Mantenimiento,
                # Seguridad (usuarios/perfiles/roles) y aprobar roles de turno
                # desde el primer momento; sin esto, la propia cuenta que crea
                # el hospital queda sin acceso a Mantenimiento → Roles del Sistema.
                permisos_accion=json.dumps([
                    "administrar_mantenimiento", "administrar_seguridad", "aprobar_roles_turno",
                ]),
                alcance_global=True,
                is_active=True,
            )
            tenant_db.add(rol)
            await tenant_db.flush()

            perfil = PerfilUsuario(
                tenant_id=tenant.id,
                nombre="Administrador SIGARH",
                rol_sistema_id=rol.id,
                modulos_acceso=json.dumps(data.active_modules),
                is_active=True,
            )
            tenant_db.add(perfil)
            await tenant_db.flush()

            sigarh_user = UsuarioSigarh(
                tenant_id=tenant.id,
                perfil_id=perfil.id,
                username=data.sigarh_email.split("@")[0],
                email=data.sigarh_email,
                password=bcrypt.hashpw(
                    data.sigarh_password.encode(), bcrypt.gensalt()
                ).decode(),
                is_active=True,
            )
            tenant_db.add(sigarh_user)

        await tenant_db.commit()

    return tenant


async def get_tenant_by_domain(db: AsyncSession, domain: str) -> Tenant | None:
    result = await db.execute(
        select(Tenant)
        .options(selectinload(Tenant.modules))
        .where(Tenant.domain == domain)
    )
    return result.scalar_one_or_none()


async def update_tenant_modules(
    db: AsyncSession,
    redis: Redis,
    tenant_id: uuid.UUID,
    module_codes: list[str],
) -> None:
    """
    Actualiza los módulos activos de un tenant e invalida el caché.
    Equivalente a activar/desactivar módulos desde ModulesCatalog en Laravel.
    """
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        return

    # Eliminar módulos actuales
    await db.execute(
        text("DELETE FROM tenant_modules WHERE tenant_id = :tid"),
        {"tid": str(tenant_id)}
    )

    # Insertar los nuevos
    for code in module_codes:
        module = TenantModule(
            tenant_id=tenant_id,
            module_code=code,
            is_active=True,
        )
        db.add(module)

    await db.commit()

    # Invalidar caché Redis — igual que Cache::forget() en Laravel
    await invalidate_tenant_cache(tenant.domain, redis)