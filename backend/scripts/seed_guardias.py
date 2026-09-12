"""Carga idempotente de tarifas y feriados nacionales 2026 por hospital."""
import asyncio
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal, engine
from app.core.tenant_db import get_tenant_sessionmaker, _tenant_engines
from app.tenants.hospitales.models import Tenant
from app.sigarh.mantenimiento.models import GuardiaValorizada
from app.sigarh.mantenimiento.guardias_catalogo import asegurar_guardias

async def main():
    async with AsyncSessionLocal() as db:
        tenants = (await db.scalars(select(Tenant))).all()
        for t in tenants:
            await asegurar_guardias(db, t.id, t.hospital_level)
        await db.commit()
    for t in tenants:
        if t.database_name:
            async with get_tenant_sessionmaker(t.database_name)() as db:
                await asegurar_guardias(db, t.id, t.hospital_level)
                await db.commit()
                print(t.database_name, await db.scalar(select(func.count()).select_from(GuardiaValorizada).where(GuardiaValorizada.tenant_id == t.id)))
    for e in _tenant_engines.values():
        await e.dispose()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
