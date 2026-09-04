import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.tenants.hospitales.models import Tenant


async def get_all_hospitals(db: AsyncSession) -> list[Tenant]:
    result = await db.execute(
        select(Tenant)
        .options(selectinload(Tenant.modules))
        .order_by(Tenant.created_at.desc())
    )
    return result.scalars().all()


async def toggle_tenant_active(
    db: AsyncSession, tenant_id: uuid.UUID, is_active: bool
) -> Tenant | None:
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        return None
    tenant.is_active = is_active
    await db.commit()
    await db.refresh(tenant)
    return tenant
