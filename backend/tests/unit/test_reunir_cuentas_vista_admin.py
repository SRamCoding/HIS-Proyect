import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.admin.usuarios.router import _reunir_todas_las_cuentas


class ReunirCuentasVistaAdminTests(unittest.IsolatedAsyncioTestCase):
    """vista='admin' no debe tocar ninguna base fisica de hospital: una
    cuenta panel='admin' solo puede vivir en la BD central."""

    async def test_vista_admin_no_consulta_ninguna_bd_de_hospital(self):
        db = AsyncMock()
        db.execute.return_value = SimpleNamespace(all=lambda: [])

        with patch("app.core.tenant_db.get_tenant_sessionmaker") as get_sessionmaker_mock:
            items, no_disponibles = await _reunir_todas_las_cuentas(db, None, vista="admin")

        self.assertEqual(items, [])
        self.assertEqual(no_disponibles, [])
        # Ni siquiera se intento abrir una sesion hacia una base de hospital.
        get_sessionmaker_mock.assert_not_called()
        # No se consulto UsuarioSigarh ni Tenant -- db.execute solo se llamo
        # una vez, para la query central de User.
        self.assertEqual(db.execute.await_count, 1)
        db.scalars.assert_not_called()

    async def test_la_query_central_filtra_por_panel_admin_en_sql(self):
        db = AsyncMock()
        db.execute.return_value = SimpleNamespace(all=lambda: [])
        await _reunir_todas_las_cuentas(db, None, vista="admin")
        consulta = db.execute.call_args.args[0]
        self.assertIn("users.panel", str(consulta))


if __name__ == "__main__":
    unittest.main()
