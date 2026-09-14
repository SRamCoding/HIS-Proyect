import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from app.sigarh.rrhh.laboral_catalogo import VINCULOS
from app.sigarh.rrhh.service import validar_vinculo_laboral, ReglaNegocioError

class LaboralTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_unknown_or_inactive_link(self):
        for value in (None, SimpleNamespace(is_active=False)):
            db = AsyncMock()
            db.get.return_value = value
            with self.assertRaises(ReglaNegocioError):
                await validar_vinculo_laboral(db, {"vinculo_laboral_codigo": "728_NOMBRADO"})

    async def test_partial_update_preserves_legacy_link(self):
        db = AsyncMock()
        await validar_vinculo_laboral(db, {"cargo_laboral": "Enfermero"})
        db.get.assert_not_called()

    async def test_accepts_active_catalog_entry(self):
        db = AsyncMock()
        db.get.return_value = SimpleNamespace(is_active=True)
        await validar_vinculo_laboral(db, {"vinculo_laboral_codigo": "276_NOMBRADO"})

    def test_named_condition_is_specific_to_276(self):
        self.assertEqual([r[1] for r in VINCULOS if r[3] == "Nombrado"], ["276"])
        self.assertEqual(len({r[0] for r in VINCULOS}), len(VINCULOS))
