import uuid
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from redis.asyncio import Redis

from app.tenants.models import Tenant, TenantModule, Module
from app.tenants.schemas import TenantCreate, TenantUpdate
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
    import bcrypt
    from app.auth.models import User

    schema_name = generate_schema_name(data.domain)

    tenant = Tenant(
        name=data.name,
        domain=data.domain,
        schema_name=schema_name,
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

    # Crear schema en PostgreSQL
    await db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))

    # Activar módulos seleccionados
    for module_code in data.active_modules:
        module = TenantModule(
            tenant_id=tenant.id,
            module_code=module_code,
            is_active=True,
        )
        db.add(module)

    # Crear usuario Administrador del hospital
    if data.admin_email and data.admin_password:
        admin_user = User(
            name=data.admin_name or "Administrador",
            email=data.admin_email,
            password=bcrypt.hashpw(
                data.admin_password.encode(), bcrypt.gensalt()
            ).decode(),
            role="administrador",
            panel="app",
            tenant_id=tenant.id,
            is_active=True,
        )
        db.add(admin_user)

    # Crear usuario SIGARH
    if data.sigarh_email and data.sigarh_password:
        sigarh_user = User(
            name=data.sigarh_name or "Usuario SIGARH",
            email=data.sigarh_email,
            password=bcrypt.hashpw(
                data.sigarh_password.encode(), bcrypt.gensalt()
            ).decode(),
            role="sigarh",
            panel="sigarh",
            tenant_id=tenant.id,
            is_active=True,
        )
        db.add(sigarh_user)

    await db.commit()
    await db.refresh(tenant)
    return tenant

from sqlalchemy.orm import selectinload

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
    # Desactivar todos los módulos actuales
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