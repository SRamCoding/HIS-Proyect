"""
Ejecutar con:
python -m app.auth.seeder
"""
import asyncio
import bcrypt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

# Importar TODOS los modelos para que SQLAlchemy resuelva las FK
from app.core.database import Base
from app.tenants.hospitales.models import Tenant, TenantModule
from app.tenants.modulos.models import Module
from app.admin.niveles_hospitalarios.models import HospitalLevel
from app.admin.modulos.models import ModuleDependency
from app.admin.roles.models import SystemRole
from app.admin.auditoria.models import AuditLog
from app.auth.models import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

    async with AsyncSession() as db:
        admin = User(
            name="Administrador ERP",
            email="admin@erp.local",
            password=hash_password("admin123"),
            role="administrador",
            panel="admin",
            tenant_id=None,
            is_active=True,
            is_superadmin=True,
        )
        db.add(admin)
        await db.commit()
        print("✓ Usuario admin creado: admin@erp.local / admin123")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())