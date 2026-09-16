import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from app.admin.modulos.service import toggle_module

MODULE_ID = uuid.uuid4()


def _modulo(code="laboratorio", is_active=True):
    return SimpleNamespace(id=MODULE_ID, code=code, is_active=is_active)


class ToggleModuleDependientesTests(unittest.IsolatedAsyncioTestCase):
    """Apagar un modulo del catalogo del que otro modulo ACTIVO depende
    obligatoriamente dejaba al dependiente con una dependencia rota, sin
    ningun aviso. Mismo criterio que ya bloquea borrar un nivel en uso."""

    async def test_bloquea_si_hay_dependientes_activos_y_obligatorios(self):
        db = AsyncMock()
        db.get.return_value = _modulo()
        db.scalars.return_value = SimpleNamespace(all=lambda: ["imagenologia"])

        with self.assertRaises(HTTPException) as err:
            await toggle_module(db, MODULE_ID, False)
        self.assertEqual(err.exception.status_code, 409)
        db.commit.assert_not_awaited()

    async def test_permite_desactivar_sin_dependientes(self):
        modulo = _modulo()
        db = AsyncMock()
        db.get.return_value = modulo
        db.scalars.return_value = SimpleNamespace(all=lambda: [])

        resultado = await toggle_module(db, MODULE_ID, False)
        self.assertFalse(resultado.is_active)
        db.commit.assert_awaited_once()

    async def test_activar_no_revisa_dependientes(self):
        modulo = _modulo(is_active=False)
        db = AsyncMock()
        db.get.return_value = modulo

        resultado = await toggle_module(db, MODULE_ID, True)
        self.assertTrue(resultado.is_active)
        db.scalars.assert_not_called()

    async def test_modulo_inexistente_devuelve_none(self):
        db = AsyncMock()
        db.get.return_value = None
        self.assertIsNone(await toggle_module(db, MODULE_ID, False))


if __name__ == "__main__":
    unittest.main()
