"""Siembra el catálogo estándar de Seguros (SIS, EsSalud, FFAA, PNP, EPS, SOAT,
Particular) en cada hospital con BD física provisionada. Idempotente: no
duplica si el hospital ya tiene un seguro con ese código.

Uso:  python -m scripts.seed_seguros_estandar
"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.tenant_db import get_tenant_sessionmaker
from app.tenants.hospitales.models import Tenant
from app.sigarh.config_financiera.seguros_catalogo import asegurar_seguros_estandar


async def main():
    async with AsyncSessionLocal() as db:
        tenants = (await db.scalars(select(Tenant).where(Tenant.is_active.is_(True)))).all()

    for t in tenants:
        if not t.database_name:
            print(f"{t.name}: sin BD física provisionada, se omite")
            continue
        Session = get_tenant_sessionmaker(t.database_name)
        async with Session() as db:
            creados = await asegurar_seguros_estandar(db, t.id)
            await db.commit()
        print(f"{t.name} ({t.database_name}): {creados} seguros creados")


if __name__ == "__main__":
    asyncio.run(main())
