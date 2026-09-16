import unittest
import uuid
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.tenants.hospitales.service import _sigue_siendo_el_intento_vigente

TENANT_ID = uuid.uuid4()


def _ctx(db):
    context = AsyncMock()
    context.__aenter__.return_value = db
    return context


class SigueSiendoElIntentoVigenteTests(unittest.IsolatedAsyncioTestCase):
    """Detectar un 'pendiente' atascado por tiempo no prueba que el worker
    murio -- una tarea lenta puede seguir corriendo de verdad mientras se
    habilita un reintento. Cada ejecucion de aprovisionar_hospital_async
    confirma que sigue siendo SU intento antes de borrar la base fisica o
    de escribir el resultado final."""

    async def test_coincide_con_el_intento_actual(self):
        momento = datetime(2026, 1, 1, 12, 0, 0)
        tenant = SimpleNamespace(provisioning_started_at=momento)
        db = AsyncMock()
        db.get.return_value = tenant
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            self.assertTrue(await _sigue_siendo_el_intento_vigente(TENANT_ID, momento.isoformat()))

    async def test_no_coincide_si_hubo_un_reintento_mas_nuevo(self):
        tenant = SimpleNamespace(provisioning_started_at=datetime(2026, 1, 1, 12, 30, 0))
        db = AsyncMock()
        db.get.return_value = tenant
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            vigente = await _sigue_siendo_el_intento_vigente(TENANT_ID, datetime(2026, 1, 1, 12, 0, 0).isoformat())
        self.assertFalse(vigente)

    async def test_hospital_inexistente_no_es_intento_vigente(self):
        db = AsyncMock()
        db.get.return_value = None
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            self.assertFalse(await _sigue_siendo_el_intento_vigente(TENANT_ID, "algo"))


if __name__ == "__main__":
    unittest.main()
