"""Integración PostgreSQL; todos los datos se revierten al terminar.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_usuarios_panel_paginacion -v

Cubre el bug real reportado sobre /usuarios/con-hospital con vista="hospital":
el filtro de panel (solo app/sigarh, nunca admin NI portal -- User.panel
admite "admin"/"app"/"portal", ver auth/models.py) se aplicaba en Python
DESPUES de que la consulta ya habia sido acotada por `cap` (LIMIT/ORDER BY
created_at). Si las primeras `cap` filas por fecha eran todas panel="portal",
las cuentas app/sigarh reales -- mas atras en la misma tabla -- nunca
llegaban a fetchearse: la pagina salia vacia (o incompleta) aunque existieran
cuentas validas. La correccion empuja `User.panel == "app"` al WHERE, antes
del LIMIT, tanto al listar (_reunir_todas_las_cuentas) como al contar
(_contar_todas_las_cuentas/_resumen_todas_las_cuentas).

Se prueba sobre un hospital SIN base fisica propia (database_name=None) para
que las cuentas vivan en la tabla `users` CENTRAL sin necesitar simular una
segunda base de datos por hospital -- el codigo que arma la consulta
(_usuarios_de, en el camino "hospital con base fisica") aplica exactamente
el mismo patron (`.where(User.panel == "app")` antes de `.limit(cap)`) sobre
una sesion distinta; este test cubre esa misma logica de filtrado en el
camino central, que es donde se puede verificar con Postgres real sin esa
infraestructura adicional.
"""
import os
import unittest
import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from main import app  # noqa: F401 -- registra TODOS los modelos en Base.metadata
                       # (User.empleado_id apunta a sigarh_empleados, que si no se
                       # importa en algun punto, SQLAlchemy no puede resolver esa FK)
from app.core.config import settings
from app.tenants.hospitales.models import Tenant
from app.auth.models import User
from app.admin.usuarios.router import (
    _reunir_todas_las_cuentas, _contar_todas_las_cuentas, _resumen_todas_las_cuentas,
)


@unittest.skipUnless(os.getenv("RUN_ARCHIVO_DB_TESTS") == "1", "Requiere PostgreSQL explícito")
class PanelAntesDeCapTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine(settings.DATABASE_URL, echo=False)
        self.connection = await self.engine.connect()
        self.transaction = await self.connection.begin()
        self.addAsyncCleanup(self.cleanup_database)
        self.tenant_id = uuid.uuid4()

        ahora = datetime.utcnow()
        async with self.session() as db:
            # Sin database_name: hospital sin base fisica propia -- sus
            # cuentas viven en la tabla `users` CENTRAL con este tenant_id.
            db.add(Tenant(
                id=self.tenant_id, name="TEST Panel Paginacion", domain=f"{self.tenant_id}.test",
                schema_name=f"test_{self.tenant_id.hex}", database_name=None, is_active=True,
            ))
            await db.flush()
            # 3 cuentas "portal" MAS RECIENTES que la unica cuenta "app" real
            # -- con cap=1, un LIMIT sin filtro de panel devolveria solo
            # portal y perderia la cuenta app de vista=hospital.
            for i in range(3):
                db.add(User(
                    id=uuid.uuid4(), tenant_id=self.tenant_id, name=f"Portal {i}",
                    email=f"portal{i}-{self.tenant_id.hex}@test.pe", password="x",
                    role="paciente", panel="portal", is_active=True,
                    created_at=ahora - timedelta(minutes=i),
                ))
            db.add(User(
                id=uuid.uuid4(), tenant_id=self.tenant_id, name="Medico App",
                email=f"medico-app-{self.tenant_id.hex}@test.pe", password="x",
                role="medico", panel="app", is_active=True,
                created_at=ahora - timedelta(days=1),
            ))
            await db.commit()

    async def cleanup_database(self):
        await self.transaction.rollback()
        await self.connection.close()
        await self.engine.dispose()

    def session(self):
        return AsyncSession(bind=self.connection, expire_on_commit=False,
                             join_transaction_mode="create_savepoint")

    async def test_listado_con_cap_no_pierde_cuenta_app_detras_de_portal(self):
        async with self.session() as db:
            items, no_disponibles = await _reunir_todas_las_cuentas(
                db, self.tenant_id, vista="hospital", cap=1,
            )
        self.assertEqual(no_disponibles, [])
        nombres = {it["name"] for it in items}
        self.assertIn("Medico App", nombres, "la cuenta app se perdio detras del cap de cuentas portal")
        self.assertNotIn("Portal 0", nombres, "vista=hospital no debe incluir panel=portal")

    async def test_conteo_con_vista_hospital_excluye_portal(self):
        async with self.session() as db:
            total = await _contar_todas_las_cuentas(db, self.tenant_id, "hospital", None, None)
        self.assertEqual(total, 1, "el conteo de vista=hospital no debe contar las 3 cuentas portal")

    async def test_resumen_con_vista_hospital_excluye_portal(self):
        async with self.session() as db:
            resumen = await _resumen_todas_las_cuentas(db, self.tenant_id, "hospital")
        self.assertEqual(resumen["total"], 1)
        self.assertEqual(resumen["activos"], 1)
        self.assertEqual(resumen["roles_unicos"], 1)


if __name__ == "__main__":
    unittest.main()
