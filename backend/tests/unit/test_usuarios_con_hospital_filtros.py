import unittest
import uuid
from datetime import datetime, timedelta
from unittest.mock import ANY, AsyncMock, patch

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


async def _reunir_falso(db, tenant_id, vista=None, q=None, is_active=None, cap=None):
    # Imita el filtrado real de _reunir_todas_las_cuentas, que ahora aplica
    # vista/q/is_active como si fueran WHERE de SQL (antes el router los
    # aplicaba en Python DESPUES de traer todo; ver test_busqueda_por_nombre_
    # o_correo / test_filtro_is_active, que antes no ejercitaban esta
    # funcion en absoluto) y acota con `cap`, igual que la real.
    items = [dict(i) for i in ITEMS]
    if vista == "admin":
        items = [it for it in items if it["panel"] == "admin"]
    elif vista == "hospital":
        items = [it for it in items if it["panel"] != "admin"]
    if is_active is not None:
        items = [it for it in items if it["is_active"] == is_active]
    if q:
        termino = q.strip().lower()
        items = [it for it in items if termino in it["name"].lower() or termino in it["email"].lower()]
    items.sort(key=lambda it: it["_created_at_raw"], reverse=True)
    if cap:
        items = items[:cap]
    return items, []


async def _contar_falso(db, tenant_id, vista, q, is_active):
    # `_contar_todas_las_cuentas` real cuenta con los mismos filtros pero sin
    # `cap` -- aca alcanza con reusar el fake de arriba sin acotar.
    items, _ = await _reunir_falso(db, tenant_id, vista, q=q, is_active=is_active, cap=None)
    return len(items)


class UsuariosConHospitalFiltrosTests(unittest.IsolatedAsyncioTestCase):
    async def _con_hospital(self, **kwargs):
        kwargs.setdefault("limit", 50)
        kwargs.setdefault("offset", 0)
        with patch("app.admin.usuarios.router._reunir_todas_las_cuentas", _reunir_falso), \
             patch("app.admin.usuarios.router._contar_todas_las_cuentas", _contar_falso):
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
    """/usuarios/resumen ya no reune cuentas en Python (ver
    _resumen_todas_las_cuentas, que agrega con COUNT/SUM/DISTINCT en SQL) --
    el router solo reenvia tenant_id/vista y devuelve la respuesta tal cual,
    asi que alcanza con verificar ese reenvio."""
    async def test_resumen_reenvia_tenant_id_y_vista(self):
        resumen_falso = AsyncMock(return_value={
            "total": 3, "activos": 2, "inactivos": 1,
            "roles_unicos": 2, "hospitales_no_disponibles": [], "es_parcial": False,
        })
        tid = uuid.uuid4()
        with patch("app.admin.usuarios.router._resumen_todas_las_cuentas", resumen_falso):
            resp = await usuarios_resumen(tenant_id=tid, vista="hospital", db=AsyncMock(), current_user={})
        resumen_falso.assert_awaited_once_with(ANY, tid, "hospital")
        self.assertEqual(resp["total"], 3)
        self.assertEqual(resp["activos"], 2)
        self.assertEqual(resp["inactivos"], 1)


if __name__ == "__main__":
    unittest.main()
