"""Completa en cada BD fisica de hospital los catalogos que ciertas
migraciones solo siembran cuando corren contra la BD central.

Motivo: profesiones (9b6e3a721c44), UPSS/servicios (7e4b2a109fd3) y la
oferta de especialidades CONAREME (2a91e5c047bf) siembran datos iterando
"SELECT id[, hospital_level] FROM tenants" dentro de la propia migracion.
Esa tabla vive solo en la BD central -- en la fisica de cada hospital existe
vacia (mismo esquema, sin filas), asi que cuando la migracion corre ahi
(via run_tenant_migrations) el paso de siembra no encuentra tenants y no
hace nada, aunque el esquema si quede al dia.

Uso: correr una vez despues de `alembic upgrade head` (central) y de haber
corrido las migraciones contra cada fisica, para backfillear estos 3
catalogos. Es idempotente (ON CONFLICT DO NOTHING / lookup por codigo o
nombre antes de insertar) -- se puede re-ejecutar sin duplicar.
"""
import asyncio
import importlib.util
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select, text

from app.core.database import AsyncSessionLocal
from app.core.tenant_db import get_tenant_engine
from app.tenants.hospitales.models import Tenant
from app.sigarh.rrhh.especialidades_catalogo import (
    ESPECIALIDADES, SUBESPECIALIDADES, RECOMENDADAS_POR_NIVEL,
    catalogo_id, oferta_id, codigo,
)

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations" / "versions"


def _load_migration(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, MIGRATIONS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_ROWS_ESPECIALIDADES = []
for _n, _nombre in enumerate(ESPECIALIDADES, 1):
    _ROWS_ESPECIALIDADES.append({
        "id": catalogo_id("especialidad", _nombre), "codigo": codigo("especialidad", _n),
        "nombre": _nombre, "tipo": "especialidad",
    })
for _n, (_nombre, _parent, _req) in enumerate(SUBESPECIALIDADES, 1):
    _ROWS_ESPECIALIDADES.append({
        "id": catalogo_id("subespecialidad", _nombre), "codigo": codigo("subespecialidad", _n),
        "nombre": _nombre, "tipo": "subespecialidad",
    })


def _seed_especialidades(sync_conn, tenant_id, level):
    recomendadas = RECOMENDADAS_POR_NIVEL.get(level, set())
    ahora = datetime.utcnow()
    for row in _ROWS_ESPECIALIDADES:
        recomendada = row["tipo"] == "especialidad" and row["nombre"] in recomendadas
        sync_conn.execute(text("""
            INSERT INTO sigarh_especialidades
                (id, tenant_id, catalogo_id, nombre, codigo, descripcion, is_active, created_at)
            VALUES (:id, :tenant_id, :catalogo_id, :nombre, :codigo, :descripcion, :active, :created_at)
            ON CONFLICT (tenant_id, catalogo_id) DO NOTHING
        """), {
            "id": oferta_id(tenant_id, row["id"]), "tenant_id": tenant_id, "catalogo_id": row["id"],
            "nombre": row["nombre"], "codigo": row["codigo"],
            "descripcion": "Recomendada por categoría" if recomendada else None,
            "active": recomendada, "created_at": ahora,
        })


async def main():
    mig_profesiones = _load_migration("9b6e3a721c44_profesiones_personal_salud.py", "mig_profesiones")
    mig_upss = _load_migration("7e4b2a109fd3_upss_servicios_nivel.py", "mig_upss")

    async with AsyncSessionLocal() as db:
        tenants = (await db.scalars(select(Tenant))).all()

    for t in tenants:
        if not t.database_name:
            continue
        engine = get_tenant_engine(t.database_name)
        async with engine.begin() as conn:
            await conn.run_sync(lambda c, tid=t.id: mig_profesiones.seed(c, tid))
            await conn.run_sync(lambda c, tid=t.id, lvl=t.hospital_level: mig_upss._seed(c, tid, lvl))
            await conn.run_sync(lambda c, tid=t.id, lvl=t.hospital_level: _seed_especialidades(c, tid, lvl))
        print(f"OK {t.database_name} ({t.name})")


if __name__ == "__main__":
    asyncio.run(main())
