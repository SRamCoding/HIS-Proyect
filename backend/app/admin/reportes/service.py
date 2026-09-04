from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.tenants.hospitales.models import Tenant


async def get_hospitals_modules_report(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Tenant).where(Tenant.is_active == True).order_by(Tenant.name)
    )
    tenants = result.scalars().all()
    return [
        {
            "hospital_name": t.name,
            "domain": t.domain,
            "active_modules": t.active_module_codes,
            "total_modules": len(t.active_module_codes),
        }
        for t in tenants
    ]
