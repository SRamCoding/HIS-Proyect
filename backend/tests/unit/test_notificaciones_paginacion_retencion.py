import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.admin.notificaciones.service import listar_notificaciones, purgar_notificaciones_antiguas


def _ctx(db):
    context = AsyncMock()
    context.__aenter__.return_value = db
    return context


class ListarNotificacionesPaginacionTests(unittest.IsolatedAsyncioTestCase):
    """Antes solo se podia pedir `limit`, sin `offset`: no habia forma de
    ver nada mas viejo que las ultimas N notificaciones."""

    async def test_devuelve_items_y_total(self):
        db = AsyncMock()
        db.scalar.return_value = 57
        db.execute.return_value = SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: ["n1", "n2"]))

        items, total = await listar_notificaciones(db, limit=20, offset=20)

        self.assertEqual(items, ["n1", "n2"])
        self.assertEqual(total, 57)
        consulta = db.execute.call_args.args[0]
        self.assertIn("OFFSET", str(consulta))


class PurgarNotificacionesAntiguasTests(unittest.IsolatedAsyncioTestCase):
    """Solo debe borrar LEIDAS mas viejas que la retencion; las no leidas
    se conservan sin importar su antiguedad."""

    async def test_borra_solo_leidas_y_vencidas(self):
        db = AsyncMock()
        db.execute.return_value = SimpleNamespace(rowcount=3)
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            borrados = await purgar_notificaciones_antiguas(retencion=timedelta(days=90))

        self.assertEqual(borrados, 3)
        consulta = db.execute.call_args.args[0]
        texto = str(consulta)
        self.assertIn("is_read", texto)
        self.assertIn("created_at", texto)
        db.commit.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
