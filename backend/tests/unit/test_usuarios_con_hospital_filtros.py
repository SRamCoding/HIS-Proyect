import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from app.admin.usuarios.router import usuarios_con_hospital, usuarios_resumen


def _item(name, email, panel, is_active, dias_atras=0):
    return {
        "id": name, "name": name, "email": email, "role": "administrador" if panel == "admin" else "medico",
        "panel": panel, "is_active": is_active, "tenant_name": "—", "tenant_id": None,
        "created_at": "01/01/2026", "_created_at_raw": datetime.utcnow() - timedelta(days=dias_atras),
        "account_type": "user",
    }


ITEMS = [
    _item("Ana", "ana@x.com", "admin", True, dias_atras=0),
    _item("Beto", "beto@x.com", "app", True, dias_atras=1),
    _item("Carla", "carla@x.com", "app", False, dias_atras=2),
    _item("Diego", "diego@sigarh.com", "sigarh", True, dias_atras=3),
]


async def _reunir_falso(db, tenant_id, vista=None):
    # Imita el filtrado real de _reunir_todas_las_cuentas: vista="admin" ya
    # viene filtrada (nunca toca hospitales), vista="hospital"/None trae
    # todo sin filtrar (el filtro de "hospital" lo aplica el router despues).
    items = [dict(i) for i in ITEMS]
    if vista == "admin":
        items = [it for it in items if it["panel"] == "admin"]
    return items, []


class UsuariosConHospitalFiltrosTests(unittest.IsolatedAsyncioTestCase):
    async def _con_hospital(self, **kwargs):
        kwargs.setdefault("limit", 50)
        kwargs.setdefault("offset", 0)
        with patch("app.admin.usuarios.router._reunir_todas_las_cuentas", _reunir_falso):
            return await usuarios_con_hospital(db=AsyncMock(), current_user={}, **kwargs)

    async def test_vista_admin_solo_devuelve_panel_admin(self):
        resp = await self._con_hospital(vista="admin")
        self.assertEqual(resp["total"], 1)
        self.assertEqual(resp["items"][0]["name"], "Ana")

    async def test_vista_hospital_excluye_admin(self):
        resp = await self._con_hospital(vista="hospital")
        self.assertEqual(resp["total"], 3)
        self.assertTrue(all(it["panel"] in ("app", "sigarh") for it in resp["items"]))

    async def test_filtro_is_active(self):
        resp = await self._con_hospital(is_active=False)
        self.assertEqual(resp["total"], 1)
        self.assertEqual(resp["items"][0]["name"], "Carla")

    async def test_busqueda_por_nombre_o_correo(self):
        resp = await self._con_hospital(q="sigarh")
        self.assertEqual(resp["total"], 1)
        self.assertEqual(resp["items"][0]["name"], "Diego")

    async def test_paginacion_respeta_limit_offset_y_orden(self):
        resp = await self._con_hospital(limit=2, offset=0)
        self.assertEqual(resp["total"], 4)
        self.assertEqual([it["name"] for it in resp["items"]], ["Ana", "Beto"])
        resp2 = await self._con_hospital(limit=2, offset=2)
        self.assertEqual([it["name"] for it in resp2["items"]], ["Carla", "Diego"])

    async def test_los_items_no_filtran_el_campo_interno_created_at_raw(self):
        resp = await self._con_hospital(limit=1)
        self.assertNotIn("_created_at_raw", resp["items"][0])


class UsuariosResumenFiltrosTests(unittest.IsolatedAsyncioTestCase):
    async def test_resumen_respeta_la_vista(self):
        with patch("app.admin.usuarios.router._reunir_todas_las_cuentas",
                   AsyncMock(return_value=([dict(i) for i in ITEMS], []))):
            resp = await usuarios_resumen(vista="hospital", db=AsyncMock(), current_user={})
        self.assertEqual(resp["total"], 3)
        self.assertEqual(resp["activos"], 2)
        self.assertEqual(resp["inactivos"], 1)


if __name__ == "__main__":
    unittest.main()
