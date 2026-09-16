"""
Aplica las migraciones pendientes de Alembic a la base fisica de TODOS los
hospitales activos.

Por que existe: run_tenant_migrations() (app/core/tenant_db.py) solo corre
UNA vez, al momento de aprovisionar un hospital nuevo -- no hay ningun
mecanismo que reaplique migraciones agregadas DESPUES a los hospitales que
ya existian. Cada migracion nueva contra la BD central (agregar una
columna a `users`, por ejemplo) deja a esos hospitales desactualizados en
silencio: no falla al migrar, falla despues, la primera vez que alguien
consulta esa tabla desde su base fisica (UndefinedColumnError).

Uso manual, despues de cada `alembic upgrade head` contra la central:
    python -m app.core.migrar_bases_fisicas
"""
import asyncio
import logging

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.tenant_db import run_tenant_migrations
from app.tenants.hospitales.models import Tenant

logger = logging.getLogger(__name__)


async def migrar_todas_las_bases_fisicas() -> dict:
    """Corre alembic upgrade head contra la base fisica de cada hospital
    con database_name propio (activo o no: uno inactivo puede reactivarse
    despues y debe quedar al dia igual). Sigue con el resto si una base
    puntual falla -- un hospital caido no debe bloquear la actualizacion
    de los demas."""
    async with AsyncSessionLocal() as db:
        tenants = (await db.scalars(
            select(Tenant).where(Tenant.database_name.is_not(None))
        )).all()

    migrados, fallidos = [], []
    for tenant in tenants:
        try:
            # command.upgrade() de Alembic es sincrono (usa su propio
            # engine internamente) -- correrlo en un hilo aparte evita
            # bloquear el event loop mientras dura la migracion.
            await asyncio.to_thread(run_tenant_migrations, tenant.database_name)
            migrados.append(tenant.database_name)
        except Exception:
            logger.exception("No se pudo migrar la base fisica de %s (%s)", tenant.name, tenant.database_name)
            fallidos.append(tenant.database_name)

    return {"migrados": migrados, "fallidos": fallidos}


if __name__ == "__main__":
    resultado = asyncio.run(migrar_todas_las_bases_fisicas())
    print(f"Migradas correctamente: {len(resultado['migrados'])}")
    for nombre in resultado["migrados"]:
        print(f"  OK  {nombre}")
    if resultado["fallidos"]:
        print(f"Fallaron: {len(resultado['fallidos'])}")
        for nombre in resultado["fallidos"]:
            print(f"  FALLO  {nombre}")
        raise SystemExit(1)
