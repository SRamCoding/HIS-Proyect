import unittest,uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock
from app.sigarh.rrhh.service import validar_referencias_empleado, ReglaNegocioError

class EmpleadoReferenciasTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_group_from_another_hospital(self):
        db=AsyncMock()
        db.get.return_value=SimpleNamespace(tenant_id=uuid.uuid4(), is_active=True)
        with self.assertRaises(ReglaNegocioError):
            await validar_referencias_empleado(db,uuid.uuid4(),{"grupo_ocupacional_id":uuid.uuid4()})

    async def test_optional_salary_and_legacy_type_do_not_block(self):
        db=AsyncMock()
        await validar_referencias_empleado(db,uuid.uuid4(),{"nivel_remunerativo_id":None,"tipo_trabajador_id":None})
        db.get.assert_not_called()

    async def test_accepts_active_group(self):
        tid=uuid.uuid4()
        db=AsyncMock()
        db.get.return_value=SimpleNamespace(tenant_id=tid,is_active=True)
        await validar_referencias_empleado(db,tid,{"grupo_ocupacional_id":uuid.uuid4()})
