import unittest
from datetime import date
from types import SimpleNamespace
from app.sigarh.rrhh.vigencia_laboral import impedimento_programacion, validar_fechas_laborales

class VigenciaTests(unittest.TestCase):
    def empleado(self, **values):
        return SimpleNamespace(**dict({"is_active": True, "fecha_ingreso": date(2026, 9, 10), "fecha_cese": date(2026, 9, 20), "fecha_nacimiento": None, "fecha_nombramiento": None}, **values))

    def test_boundaries_and_outside_period(self):
        emp = self.empleado()
        for day in (10, 20): self.assertIsNone(impedimento_programacion(emp, date(2026, 9, day)))
        for day in (9, 21): self.assertIsNotNone(impedimento_programacion(emp, date(2026, 9, day)))

    def test_inactive_and_unknown(self):
        self.assertIsNotNone(impedimento_programacion(None, date.today()))
        self.assertIsNotNone(impedimento_programacion(self.empleado(is_active=False), date(2026, 9, 15)))

    def test_legacy_dates_are_optional(self):
        self.assertIsNone(impedimento_programacion(self.empleado(fecha_ingreso=None, fecha_cese=None), date.today()))

    def test_patch_checks_stored_dates(self):
        self.assertIsNotNone(validar_fechas_laborales({"fecha_cese": date(2026, 9, 1)}, self.empleado()))
        self.assertIsNotNone(validar_fechas_laborales({"fecha_ingreso": date(2026, 10, 1)}, self.empleado()))
        self.assertIsNone(validar_fechas_laborales({"cargo_laboral": "Medico"}, self.empleado()))


class ProgramacionVigenciaTests(unittest.IsolatedAsyncioTestCase):
    async def test_manual_programming_rejects_inactive_employee(self):
        from unittest.mock import AsyncMock
        from fastapi import HTTPException
        from app.hospital.consulta_externa.service import _validar_vigencia_medico
        import uuid
        db = AsyncMock()
        db.scalar.return_value = SimpleNamespace(is_active=False)
        with self.assertRaises(HTTPException) as error:
            await _validar_vigencia_medico(db, uuid.uuid4(), uuid.uuid4(), date.today())
        self.assertEqual(error.exception.status_code, 409)
        db.commit.assert_not_called()
