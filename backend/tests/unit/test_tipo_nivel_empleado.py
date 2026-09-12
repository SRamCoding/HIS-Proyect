import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from app.sigarh.rrhh.service import validar_tipo_nivel_empleado,ReglaNegocioError
from app.sigarh.mantenimiento.escalas_catalogo import PROF_NIVELES

class TipoNivelTests(unittest.IsolatedAsyncioTestCase):
 async def test_rejects_cas_type_for_named_worker(self):
  db=AsyncMock()
  db.get.return_value=SimpleNamespace(vinculos_codigos=["1057_CONTRATADO"])
  with self.assertRaises(ReglaNegocioError):
   await validar_tipo_nivel_empleado(db,{"tipo_trabajador_id":"id","vinculo_laboral_codigo":"276_NOMBRADO"})
 async def test_rejects_medical_level_for_nurse(self):
  db=AsyncMock()
  db.get.side_effect=[SimpleNamespace(profesion_codigo="MED"),SimpleNamespace(codigo="ENF")]
  with self.assertRaises(ReglaNegocioError):
   await validar_tipo_nivel_empleado(db,{"nivel_remunerativo_id":"id","profesion_id":"nurse"})
 async def test_accepts_matching_profession(self):
  db=AsyncMock()
  db.get.side_effect=[SimpleNamespace(profesion_codigo="ENF"),SimpleNamespace(codigo="ENF")]
  await validar_tipo_nivel_empleado(db,{"nivel_remunerativo_id":"id","profesion_id":"nurse"})
 async def test_legacy_empty_values_remain_valid(self):
  db=AsyncMock()
  await validar_tipo_nivel_empleado(db,{})
  db.get.assert_not_called()
 def test_profession_specific_numbering(self):
  self.assertEqual(PROF_NIVELES["MED"],("1","2","3","4","5"))
  self.assertEqual(PROF_NIVELES["ENF"],("10","11","12","13","14"))
  self.assertEqual(PROF_NIVELES["QFA"],("IV","V","VI","VII","VIII"))
