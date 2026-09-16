import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.admin.usuarios.service import _cuenta_localizada

TENANT_ID = uuid.uuid4()
USER_ID = uuid.uuid4()


class CuentaLocalizadaDirectaTests(unittest.IsolatedAsyncioTestCase):
    """Cuando el llamador ya sabe en que hospital vive la cuenta
    (editar/activar/eliminar ahora reciben tenant_id, igual que la lectura
    por id), no debe recorrer TODOS los hospitales para encontrarla."""

    async def test_con_tenant_id_va_directo_sin_escanear_otros_hospitales(self):
        tenant = SimpleNamespace(id=TENANT_ID, database_name="his_hospital_x")
        db_central = AsyncMock()
        db_central.get.return_value = tenant

        usuario = SimpleNamespace(id=USER_ID)
        tenant_db = AsyncMock()
        tenant_db.get.return_value = usuario

        with patch("app.core.tenant_db.get_tenant_sessionmaker", return_value=lambda: tenant_db):
            async with _cuenta_localizada(db_central, USER_ID, TENANT_ID) as (cuenta, work_db, es_tenant, tipo):
                self.assertIs(cuenta, usuario)
                self.assertTrue(es_tenant)
                self.assertEqual(tipo, "user")
        # Solo se toco el hospital indicado -- ninguna busqueda de "todos
        # los tenants con base fisica" (eso es lo que hace el escaneo).
        db_central.scalars.assert_not_called()

    async def test_sin_tenant_id_sigue_usando_el_escaneo_de_respaldo(self):
        db_central = AsyncMock()
        db_central.get.return_value = None  # no esta en central
        db_central.scalar.return_value = None  # tampoco es UsuarioSigarh central
        db_central.scalars.return_value = SimpleNamespace(all=lambda: [])  # sin hospitales con BD fisica

        async with _cuenta_localizada(db_central, USER_ID, None) as (cuenta, work_db, es_tenant, tipo):
            self.assertIsNone(cuenta)
        # El escaneo de respaldo SI consulta la lista de tenants.
        db_central.scalars.assert_called()

    async def test_hospital_inexistente_devuelve_cuenta_none(self):
        db_central = AsyncMock()
        db_central.get.return_value = None
        async with _cuenta_localizada(db_central, USER_ID, TENANT_ID) as (cuenta, work_db, es_tenant, tipo):
            self.assertIsNone(cuenta)
            self.assertFalse(es_tenant)


if __name__ == "__main__":
    unittest.main()
