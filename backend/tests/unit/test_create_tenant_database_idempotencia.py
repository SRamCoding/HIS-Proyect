import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import asyncpg

from app.core.tenant_db import create_tenant_database


def _engine_que_falla_con(excepcion):
    conn = AsyncMock()
    conn.execute.side_effect = excepcion
    ctx = AsyncMock()
    ctx.__aenter__.return_value = conn
    engine = MagicMock()
    engine.connect.return_value = ctx
    engine.dispose = AsyncMock()
    return engine


class CreateTenantDatabaseIdempotenciaTests(unittest.IsolatedAsyncioTestCase):
    """create_tenant_database debe distinguir "la cree yo ahora" (True) de
    "ya existia" (False) -- el llamador usa esa distincion para decidir si
    le corresponde borrarla ante un fallo posterior. Antes solo devolvia
    None y el llamador asumia siempre "la cree yo", incluso cuando en
    realidad ya existia de un intento anterior."""

    async def test_devuelve_true_si_la_crea_de_verdad(self):
        engine = _engine_que_falla_con(None)
        engine.connect.return_value.__aenter__.return_value.execute = AsyncMock()
        with patch("app.core.tenant_db.create_async_engine", return_value=engine):
            resultado = await create_tenant_database("his_nuevo")
        self.assertTrue(resultado)

    async def test_devuelve_false_si_ya_existia(self):
        excepcion = Exception("duplicate")
        excepcion.__cause__ = asyncpg.exceptions.DuplicateDatabaseError("ya existe")
        engine = _engine_que_falla_con(excepcion)
        with patch("app.core.tenant_db.create_async_engine", return_value=engine):
            resultado = await create_tenant_database("his_existente")
        self.assertFalse(resultado)

    async def test_propaga_cualquier_otro_error(self):
        excepcion = RuntimeError("la bd esta caida")
        engine = _engine_que_falla_con(excepcion)
        with patch("app.core.tenant_db.create_async_engine", return_value=engine):
            with self.assertRaises(RuntimeError):
                await create_tenant_database("his_x")


if __name__ == "__main__":
    unittest.main()
