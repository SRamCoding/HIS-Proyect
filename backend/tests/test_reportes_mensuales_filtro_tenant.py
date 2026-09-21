"""Integración PostgreSQL; todos los datos se revierten al terminar.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_reportes_mensuales_filtro_tenant -v

Cubre el bug real ya corregido en get_monthly_report (reportes/service.py):
cuando el reporte se filtraba a UN hospital puntual (tenant_id), dos partes
de la respuesta seguian mezclando datos de TODO el sistema en vez de
respetar ese filtro:

1. hospitales_registrados_periodo ignoraba tenant_id y siempre listaba los
   hospitales registrados en el mes de TODO el sistema, aunque se estuviera
   viendo el reporte de un solo hospital.
2. usuarios_centrales_registrados mostraba el conteo GLOBAL de cuentas
   centrales del mes, sin relacion con el hospital filtrado -- ahora debe
   ser None (no aplica) cuando hay tenant_id, para que el frontend pueda
   distinguir "no aplica a este filtro" de "de verdad no hubo ninguno".

Se prueba con dos hospitales SIN base fisica propia (database_name=None)
para no necesitar simular BDs por hospital: _stats_hospital ya retorna
(0, 0, True) en ese caso sin tocar ninguna BD, y el bug que se cubre vive
enteramente en las consultas contra la BD central (Tenant, User), que es lo
que este test ejercita.
"""
import os
import unittest
import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from main import app  # noqa: F401 -- registra TODOS los modelos en Base.metadata
from app.core.config import settings
from app.tenants.hospitales.models import Tenant
from app.auth.models import User
from app.admin.reportes.service import get_monthly_report


@unittest.skipUnless(os.getenv("RUN_ARCHIVO_DB_TESTS") == "1", "Requiere PostgreSQL explícito")
class ReporteMensualFiltroTenantTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine(settings.DATABASE_URL, echo=False)
        self.connection = await self.engine.connect()
        self.transaction = await self.connection.begin()
        self.addAsyncCleanup(self.cleanup_database)
        self.mes = datetime.utcnow().strftime("%Y-%m")
        ahora = datetime.utcnow()
        self.tenant_a = uuid.uuid4()
        self.tenant_b = uuid.uuid4()

        async with self.session() as db:
            db.add(Tenant(
                id=self.tenant_a, name="TEST Reporte Hospital A", domain=f"{self.tenant_a}.test",
                schema_name=f"test_{self.tenant_a.hex}", database_name=None, is_active=True,
                created_at=ahora,
            ))
            db.add(Tenant(
                id=self.tenant_b, name="TEST Reporte Hospital B", domain=f"{self.tenant_b}.test",
                schema_name=f"test_{self.tenant_b.hex}", database_name=None, is_active=True,
                created_at=ahora,
            ))
            # Cuenta central sin tenant (ej. super-admin), creada este mes.
            db.add(User(
                id=uuid.uuid4(), tenant_id=None, name="Admin Central Test",
                email=f"admin-central-{uuid.uuid4().hex}@test.pe", password="x",
                role="administrador", panel="admin", is_active=True,
                created_at=ahora,
            ))
            await db.commit()

    async def cleanup_database(self):
        await self.transaction.rollback()
        await self.connection.close()
        await self.engine.dispose()

    def session(self):
        return AsyncSession(bind=self.connection, expire_on_commit=False,
                             join_transaction_mode="create_savepoint")

    async def test_hospitales_registrados_periodo_respeta_filtro_de_tenant(self):
        async with self.session() as db:
            reporte = await get_monthly_report(db, self.mes, tenant_id=self.tenant_a)
        nombres = {h["name"] for h in reporte["hospitales_registrados_periodo"]}
        self.assertIn("TEST Reporte Hospital A", nombres)
        self.assertNotIn("TEST Reporte Hospital B", nombres,
            "el reporte filtrado a un hospital no debe incluir el registro de otro hospital")

    async def test_usuarios_centrales_no_aplica_con_filtro_de_tenant(self):
        async with self.session() as db:
            reporte = await get_monthly_report(db, self.mes, tenant_id=self.tenant_a)
        self.assertIsNone(reporte["usuarios_centrales_registrados"],
            "con tenant_id, usuarios_centrales_registrados debe ser None (no aplica), no un conteo global")

    async def test_usuarios_centrales_se_cuenta_sin_filtro_de_tenant(self):
        async with self.session() as db:
            reporte = await get_monthly_report(db, self.mes, tenant_id=None)
        self.assertGreaterEqual(reporte["usuarios_centrales_registrados"], 1,
            "sin filtro de tenant, usuarios_centrales_registrados debe reflejar el conteo real del mes")


if __name__ == "__main__":
    unittest.main()
