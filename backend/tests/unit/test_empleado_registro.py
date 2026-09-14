import unittest
from datetime import date, timedelta
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock
from pydantic import ValidationError
from app.sigarh.rrhh.schemas import EmpleadoCreate, EmpleadoUpdate, EmpleadoEspecialidadCreate
from app.sigarh.rrhh.service import sincronizar_especialidades_empleado, ReglaNegocioError
import uuid

class RegistroTests(unittest.IsolatedAsyncioTestCase):
    def test_mayoria_de_edad_exacta(self):
        hoy = date.today()
        cumple = date(hoy.year - 18, hoy.month, hoy.day)
        base = dict(dni='99123456', nombres='Prueba', apellido_paterno='Registro', apellido_materno='Empleado')
        EmpleadoCreate(**base, fecha_nacimiento=cumple)
        with self.assertRaises(ValidationError):
            EmpleadoCreate(**base, fecha_nacimiento=cumple + timedelta(days=1))

    def test_banco_y_limites(self):
        for data in ({'numero_cci': '123'}, {'tipo_cuenta': 'otro'}, {'is_active': None}, {'apellido_paterno': 'a' * 101}):
            with self.assertRaises(ValidationError):
                EmpleadoUpdate(**data)
        self.assertEqual(EmpleadoUpdate(numero_cci='1' * 20).numero_cci, '1' * 20)

    async def test_especialidad_de_otro_hospital_no_se_modifica(self):
        db = AsyncMock()
        db.get.side_effect = [NS(codigo='MED'), NS(tenant_id=uuid.uuid4(), is_active=True)]
        emp = NS(id=uuid.uuid4(), tenant_id=uuid.uuid4(), profesion_id=uuid.uuid4())
        with self.assertRaises(ReglaNegocioError):
            await sincronizar_especialidades_empleado(db, emp, [EmpleadoEspecialidadCreate(especialidad_id=uuid.uuid4())])
        db.add.assert_not_called()
        db.delete.assert_not_called()
        db.commit.assert_not_called()

    async def test_rechaza_especialidades_duplicadas(self):
        db = AsyncMock()
        db.get.return_value = NS(codigo='MED')
        esp = EmpleadoEspecialidadCreate(especialidad_id=uuid.uuid4())
        with self.assertRaises(ReglaNegocioError):
            await sincronizar_especialidades_empleado(db, NS(profesion_id='p'), [esp, esp])
        db.commit.assert_not_called()
