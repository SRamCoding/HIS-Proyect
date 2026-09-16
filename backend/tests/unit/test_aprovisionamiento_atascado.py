import unittest
import uuid
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.tenants.hospitales.service import revisar_aprovisionamientos_atascados


def _ctx(db):
    context = AsyncMock()
    context.__aenter__.return_value = db
    return context


def _tenant(nombre="Hospital X", minutos_atras=30):
    return SimpleNamespace(
        id=uuid.uuid4(), name=nombre,
        provisioning_status="pendiente",
        provisioning_started_at=datetime.utcnow() - timedelta(minutes=minutos_atras),
    )


class RevisarAprovisionamientosAtascadosTests(unittest.IsolatedAsyncioTestCase):
    """Un hospital que quedo en 'pendiente' sin ninguna tarea real corriendo
    (el proceso murio antes de encolarla, o el worker murio a mitad de
    camino) debe pasar a 'error' para que se pueda reintentar -- de otro
    modo queda atascado para siempre, sin aviso y sin forma de recuperarlo."""

    async def test_marca_como_error_un_pendiente_vencido(self):
        tenant = _tenant(minutos_atras=30)
        db = AsyncMock()
        db.scalars.return_value = SimpleNamespace(all=lambda: [tenant])
        db.execute.return_value = SimpleNamespace(scalar_one_or_none=lambda: tenant.id)  # el FOR UPDATE confirma el claim

        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)), \
             patch("app.admin.notificaciones.service.crear_notificacion", AsyncMock()) as notif_mock:
            marcados = await revisar_aprovisionamientos_atascados()

        self.assertEqual(marcados, ["Hospital X"])
        self.assertEqual(tenant.provisioning_status, "error")
        self.assertIn("no terminó en el tiempo esperado", tenant.provisioning_error)
        notif_mock.assert_awaited_once()

    async def test_no_toca_uno_que_otro_proceso_ya_esta_reclamando(self):
        tenant = _tenant()
        db = AsyncMock()
        db.scalars.return_value = SimpleNamespace(all=lambda: [tenant])
        # SKIP LOCKED: otro proceso ya tiene el lock, no devuelve fila.
        db.execute.return_value = SimpleNamespace(scalar_one_or_none=lambda: None)

        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            marcados = await revisar_aprovisionamientos_atascados()

        self.assertEqual(marcados, [])
        self.assertEqual(tenant.provisioning_status, "pendiente")  # sin tocar

    async def test_sin_candidatos_no_hace_nada(self):
        db = AsyncMock()
        db.scalars.return_value = SimpleNamespace(all=lambda: [])
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            marcados = await revisar_aprovisionamientos_atascados()
        self.assertEqual(marcados, [])
        db.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
