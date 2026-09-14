"""Aplica la migración revisada y crea el perfil médico sin crear cuentas."""
import asyncio
import uuid
from sqlalchemy import select, text
from alembic import command
from alembic.config import Config
from app.core.database import AsyncSessionLocal, engine
from app.core.tenant_db import get_tenant_sessionmaker, run_tenant_migrations, _tenant_engines
from app.tenants.hospitales.models import Tenant
from app.auth.models import PerfilHospital
from app.auth.hospital_access import MEDICO_MODULOS


async def hospitales():
    async with AsyncSessionLocal() as db:
        nombres = set((await db.scalars(text("SELECT datname FROM pg_database"))).all())
        rows = (await db.scalars(select(Tenant).where(Tenant.is_active.is_(True), Tenant.database_name.is_not(None)))).all()
        resultado = [(t.id, t.database_name) for t in rows if t.database_name in nombres]
    await engine.dispose()
    return resultado


async def crear_perfiles(rows):
    try:
        from app.admin.roles.models import SystemRole
        async with AsyncSessionLocal() as central:
            for codigo, etiqueta in [('administrador', 'Administrador hospitalario'), ('medico', 'Médico'),
                ('enfermera', 'Enfermería'), ('farmaceutico', 'Farmacéutico'), ('laboratorista', 'Laboratorista'),
                ('cajero', 'Cajero'), ('tuasis', 'TUASIS')]:
                if not await central.scalar(select(SystemRole.id).where(SystemRole.name == codigo)):
                    central.add(SystemRole(name=codigo, label=etiqueta, panel='app',
                        allowed_modules=sorted(MEDICO_MODULOS) if codigo == 'medico' else None, is_active=True))
            await central.commit()
        for tid, nombre in rows:
            async with get_tenant_sessionmaker(nombre)() as db:
                perfil = await db.scalar(select(PerfilHospital).where(PerfilHospital.tenant_id == tid, PerfilHospital.role == "medico"))
                if not perfil:
                    db.add(PerfilHospital(id=uuid.uuid4(), tenant_id=tid, nombre="Médico de consulta externa",
                        role="medico", modulos=sorted(MEDICO_MODULOS), is_active=True))
                    await db.commit()
                print(nombre, "migrado; perfil medico disponible")
    finally:
        await engine.dispose()
        for tenant_engine in _tenant_engines.values():
            await tenant_engine.dispose()


if __name__ == "__main__":
    cfg = Config("alembic.ini")
    heads = __import__('alembic.script', fromlist=['ScriptDirectory']).ScriptDirectory.from_config(cfg).get_heads()
    if heads != ["e83b12a5cd40"]:
        raise RuntimeError("Revise las cabezas antes de migrar")
    rows = asyncio.run(hospitales())
    command.upgrade(cfg, "head")
    for _, nombre in rows:
        run_tenant_migrations(nombre)
    asyncio.run(crear_perfiles(rows))
