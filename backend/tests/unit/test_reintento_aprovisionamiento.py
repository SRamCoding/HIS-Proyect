import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from app.admin.hospitales.router import reintentar_aprovisionamiento
from app.admin.hospitales.schemas import ReintentarAprovisionamiento

TENANT_ID = uuid.uuid4()


def _payload():
    return ReintentarAprovisionamiento(
        admin_name="Admin App", admin_email="admin@hospital.test", admin_password="Clave-Segura1",
        sigarh_name="Resp RRHH", sigarh_email="rrhh@hospital.test", sigarh_password="Otra-Clave2",
    )


class ReintentarAprovisionamientoTests(unittest.IsolatedAsyncioTestCase):
    """El cambio de estado 'error' -> 'pendiente' debe ser un UPDATE
    condicionado (no leer-decidir-escribir): dos solicitudes de reintento
    simultaneas no pueden pasar ambas la comprobacion."""

    def _tenant(self):
        return SimpleNamespace(id=TENANT_ID, database_name="his_x", hospital_level="II-1", name="Hospital X")

    async def test_transicion_atomica_rechaza_si_ya_no_esta_en_error(self):
        db = AsyncMock()
        db.get.return_value = self._tenant()
        db.scalars.return_value = SimpleNamespace(all=lambda: [])
        db.execute.return_value = SimpleNamespace(rowcount=0)  # el WHERE provisioning_status='error' no matcheo nada

        with self.assertRaises(HTTPException) as err:
            await reintentar_aprovisionamiento(TENANT_ID, _payload(), db=db, current_user={})
        self.assertEqual(err.exception.status_code, 400)
        db.commit.assert_awaited()

    async def test_transicion_atomica_encola_si_rowcount_es_uno(self):
        db = AsyncMock()
        db.get.return_value = self._tenant()
        db.scalars.return_value = SimpleNamespace(all=lambda: ["admision"])
        db.execute.return_value = SimpleNamespace(rowcount=1)

        with patch("app.admin.hospitales.router._encolar_aprovisionamiento", AsyncMock(return_value=True)) as encolar_mock:
            resultado = await reintentar_aprovisionamiento(TENANT_ID, _payload(), db=db, current_user={})

        self.assertEqual(resultado, {"ok": True})
        encolar_mock.assert_awaited_once()

    async def test_hospital_inexistente_da_404(self):
        db = AsyncMock()
        db.get.return_value = None
        with self.assertRaises(HTTPException) as err:
            await reintentar_aprovisionamiento(TENANT_ID, _payload(), db=db, current_user={})
        self.assertEqual(err.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
