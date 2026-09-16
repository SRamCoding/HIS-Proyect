import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from starlette.requests import Request
from fastapi import HTTPException

from app.tenants.entitlements import require_module_jwt

TENANT = "55540838-24a6-4e78-843b-f9b93e57733a"


def _ctx(db):
    context = AsyncMock()
    context.__aenter__.return_value = db
    return context


def _request():
    return Request({"type": "http", "path": "/app/laboratorio/examenes", "headers": []})


class ModuloGlobalBloqueaAccesoTests(unittest.IsolatedAsyncioTestCase):
    """require_module_jwt ahora exige tambien modules.is_active: apagar un
    modulo en el catalogo global debe cortar el acceso al instante, aunque
    el hospital lo siga teniendo asignado y activo en tenant_modules."""

    async def test_la_consulta_exige_el_modulo_activo_en_el_catalogo(self):
        db = AsyncMock()
        db.execute.return_value = SimpleNamespace(first=lambda: ("laboratorio",))
        dep = require_module_jwt("laboratorio")

        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            result = await dep(request=_request(), current_user={"panel": "app", "tenant_id": TENANT})

        self.assertEqual(result["tenant_id"], TENANT)
        query_text = str(db.execute.call_args.args[0])
        self.assertIn("modules", query_text)
        self.assertIn("m.is_active", query_text)

    async def test_bloquea_si_el_modulo_esta_desactivado_en_el_catalogo(self):
        # El JOIN con modules (m.is_active = true) hace que la consulta no
        # devuelva fila cuando el catalogo global tiene el modulo apagado,
        # sin importar que tenant_modules siga diciendo "activo".
        db = AsyncMock()
        db.execute.return_value = SimpleNamespace(first=lambda: None)
        dep = require_module_jwt("laboratorio")

        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            with self.assertRaises(HTTPException) as err:
                await dep(request=_request(), current_user={"panel": "app", "tenant_id": TENANT})
        self.assertEqual(err.exception.status_code, 403)

    async def test_permite_si_el_modulo_esta_activo_en_todo(self):
        db = AsyncMock()
        db.execute.return_value = SimpleNamespace(first=lambda: ("laboratorio",))
        dep = require_module_jwt("laboratorio")

        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            user = {"panel": "app", "tenant_id": TENANT}
            result = await dep(request=_request(), current_user=user)
        self.assertIs(result, user)


if __name__ == "__main__":
    unittest.main()
