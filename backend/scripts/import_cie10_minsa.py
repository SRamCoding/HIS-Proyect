"""Carga el Excel oficial CIE-10 en la base operativa central por hospital."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.tenant_db import get_tenant_sessionmaker
from app.sigarh.general.cie10_import import import_cie10, read_minsa_xlsx
from app.tenants.hospitales.models import Tenant


DEFAULT_FILE = Path(__file__).parents[1] / "data" / "cie10" / "CIE10_MINSA_OFICIAL.xlsx"


async def run(
    path: Path,
    tenant_domains: list[str],
    dry_run: bool,
    include_tenant_databases: bool,
) -> None:
    records = read_minsa_xlsx(path)
    async with AsyncSessionLocal() as db:
        query = select(Tenant).where(Tenant.is_active.is_(True)).order_by(Tenant.name)
        if tenant_domains:
            query = query.where(Tenant.domain.in_(tenant_domains))
        tenants = list((await db.scalars(query)).all())
        if tenant_domains and len(tenants) != len(set(tenant_domains)):
            found = {tenant.domain for tenant in tenants}
            missing = sorted(set(tenant_domains) - found)
            raise ValueError(f"Hospitales activos no encontrados: {', '.join(missing)}")
        if not tenants:
            raise ValueError("No se encontraron hospitales activos")

        for tenant in tenants:
            stats = await import_cie10(db, tenant.id, records, dry_run=dry_run)
            print(json.dumps({
                "almacenamiento": "central", "hospital": tenant.name,
                "domain": tenant.domain, **stats,
            }))

        if include_tenant_databases:
            for tenant in tenants:
                if not tenant.database_name:
                    print(json.dumps({
                        "almacenamiento": "hospital", "hospital": tenant.name,
                        "omitido": "no tiene base física configurada",
                    }))
                    continue
                TenantSession = get_tenant_sessionmaker(tenant.database_name)
                async with TenantSession() as tenant_db:
                    stats = await import_cie10(
                        tenant_db, tenant.id, records, dry_run=dry_run
                    )
                print(json.dumps({
                    "almacenamiento": tenant.database_name,
                    "hospital": tenant.name,
                    "domain": tenant.domain,
                    **stats,
                }))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    parser.add_argument("--tenant-domain", action="append", default=[])
    parser.add_argument("--apply", action="store_true", help="Confirma la escritura; sin esto simula")
    parser.add_argument(
        "--include-tenant-databases",
        action="store_true",
        help="Carga además cada base física hospitalaria configurada",
    )
    args = parser.parse_args()
    asyncio.run(run(
        args.file.resolve(), args.tenant_domain,
        dry_run=not args.apply,
        include_tenant_databases=args.include_tenant_databases,
    ))


if __name__ == "__main__":
    main()
