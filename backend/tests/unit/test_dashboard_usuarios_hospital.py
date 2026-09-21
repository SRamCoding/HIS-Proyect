import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.admin.dashboard.service import _usuarios_hospital


def _tenant(database_name="his_test_hospital"):
    return SimpleNamespace(id="tid", name="Hospital Test", database_name=database_name)


def _sessionmaker_para(tdb):
    """get_tenant_sessionmaker(name) devuelve un factory SINCRONO (TenantSession)
    que, al llamarlo, produce un context manager ASINCRONO -- por eso el
    factory mismo debe ser un MagicMock normal (no AsyncMock: eso volveria
    la llamada TenantSession() en una corrutina en vez de un contexto)."""
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=tdb)
    ctx.__aexit__ = AsyncMock(return_value=False)
    factory = MagicMock(return_value=ctx)
    return factory


class UsuariosHospitalPorPanelTests(unittest.IsolatedAsyncioTestCase):
    """Cubre el bug real ya corregido en _usuarios_hospital: antes se sumaba
    TODA la tabla User del hospital como si fuera panel="app" (User.panel
    tambien admite "portal", ver auth/models.py). Eso inflaba el conteo de
    "app" y hacia que el desglose users_by_panel del dashboard nunca
    mostrara cuentas "portal" del hospital, aunque existieran."""

    async def test_separa_panel_app_de_panel_portal_en_vez_de_sumarlos_juntos(self):
        tdb = AsyncMock()
        # Simula agrupar por panel en SQL: 3 cuentas app (2 activas) y
        # 5 cuentas portal (4 activas) en la MISMA base fisica.
        tdb.execute.return_value = SimpleNamespace(all=lambda: [
            ("app", 3, 2),
            ("portal", 5, 4),
        ])
        tdb.scalar.side_effect = [0, 0]  # total_sigarh, activos_sigarh

        with patch("app.admin.dashboard.service.get_tenant_sessionmaker", return_value=_sessionmaker_para(tdb)):
            por_panel, total_sigarh, activos_sigarh, disponible = await _usuarios_hospital(_tenant())

        self.assertTrue(disponible)
        self.assertEqual(por_panel, {"app": (3, 2), "portal": (5, 4)},
            "las cuentas portal no deben mezclarse ni desaparecer del desglose por panel")
        # La suma total (para total_users/active_users del dashboard) debe
        # incluir ambos paneles, no solo "app".
        total_hosp = sum(t for t, _ in por_panel.values())
        activos_hosp = sum(a for _, a in por_panel.values())
        self.assertEqual(total_hosp, 8)
        self.assertEqual(activos_hosp, 6)

    async def test_hospital_sin_bd_fisica_no_intenta_conectar(self):
        with patch("app.admin.dashboard.service.get_tenant_sessionmaker") as get_sessionmaker_mock:
            por_panel, total_sigarh, activos_sigarh, disponible = await _usuarios_hospital(_tenant(database_name=None))
        get_sessionmaker_mock.assert_not_called()
        self.assertEqual(por_panel, {})
        self.assertTrue(disponible)

    async def test_bd_no_disponible_se_marca_explicitamente_no_como_cero_silencioso(self):
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(side_effect=Exception("no se pudo conectar"))
        factory = MagicMock(return_value=ctx)

        with patch("app.admin.dashboard.service.get_tenant_sessionmaker", return_value=factory):
            por_panel, total_sigarh, activos_sigarh, disponible = await _usuarios_hospital(_tenant())

        self.assertFalse(disponible,
            "una BD caida debe marcarse como no disponible, no reportar 0 usuarios como si fuera un hospital vacio")
        self.assertEqual(por_panel, {})


if __name__ == "__main__":
    unittest.main()
