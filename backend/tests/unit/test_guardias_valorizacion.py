import unittest
import uuid
from datetime import date
from decimal import Decimal
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock
from fastapi import HTTPException
from app.sigarh.mantenimiento.guardias_catalogo import importes_nivel, stable_id, FERIADOS_2026
from app.sigarh.mantenimiento.service import seleccionar_tarifa
from app.sigarh.creacion_roles.valorizacion import tipo_por_fecha, estimar_rol

class GuardiasTests(unittest.IsolatedAsyncioTestCase):
    def test_importes_y_escalas_no_equivalentes(self):
        self.assertEqual(importes_nivel('MED-5')[3], '213.44')
        self.assertEqual(importes_nivel('ENF-10')[0], '87.65')
        self.assertEqual(importes_nivel('TME-5'), importes_nivel('OBS-V'))
        self.assertEqual(importes_nivel('ODO-I')[0], '92.54')
        self.assertEqual(importes_nivel('TAS-STA')[0], '36.67')
        for code in ('ADM-IV', 'TES-I', 'TAS-SPA', 'AAS-STA', 'MED-6', 'ODO-INVALIDO'):
            self.assertIsNone(importes_nivel(code))

    def test_domingo_feriado_sabado(self):
        self.assertEqual(tipo_por_fecha('MINSA-GNO', date(2026, 9, 13), set()), 'MINSA-GNF')
        self.assertEqual(tipo_por_fecha('MINSA-GDO', date(2026, 9, 12), set()), 'MINSA-GDO')
        self.assertEqual(tipo_por_fecha('MINSA-GDO', date(2026, 7, 28), {date(2026, 7, 28)}), 'MINSA-GDF')
        self.assertIsNone(tipo_por_fecha('RETEN', date(2026, 9, 13), set()))
        self.assertEqual(len(FERIADOS_2026), 16)
        a, b = uuid.uuid4(), uuid.uuid4()
        self.assertNotEqual(stable_id(a, 'GDO'), stable_id(b, 'GDO'))

    def test_prioridad_y_ambiguedad(self):
        generic = NS(grupo_ocupacional_id=None, nivel_remunerativo_id=None)
        specific = NS(grupo_ocupacional_id='g', nivel_remunerativo_id='n')
        self.assertIs(seleccionar_tarifa([generic, specific]), specific)
        with self.assertRaises(HTTPException) as exc:
            seleccionar_tarifa([specific, specific])
        self.assertEqual(exc.exception.status_code, 409)
        with self.assertRaises(HTTPException) as exc:
            seleccionar_tarifa([])
        self.assertEqual(exc.exception.status_code, 404)

    async def fixture(self, vinculo='276_NOMBRADO', overlap=False, year=2026):
        tid = uuid.uuid4()
        emp = NS(id='e', nombre_completo='Trabajador', nivel_remunerativo_id='n', profesion_id='p', grupo_ocupacional_id='g',
            vinculo_laboral_codigo=vinculo, is_active=True, fecha_ingreso=date(2020, 1, 1), fecha_cese=None)
        horario = NS(id='h', nombre='Diurna', is_active=True, hora_inicio='07:00', hora_fin='19:00', tipo_guardia_id='do')
        tipo = NS(id='do', codigo='MINSA-GDO')
        tipos = [tipo, NS(id='df', codigo='MINSA-GDF')]
        tarifas = [NS(id=t, tipo_guardia_id=t, valor=Decimal('100.01'), moneda='PEN', sustento='norma',
            vigencia_desde=date(2017, 8, 11), vigencia_hasta=None, grupo_ocupacional_id=None, nivel_remunerativo_id='n') for t in ('do', 'df')]
        turno = NS(horario_guardia_id='h', dias_semana=[0])
        acts = [NS(turnos=[turno]), NS(turnos=[turno])]
        hors = {'h': horario}
        if overlap:
            hors['h2'] = NS(**{**vars(horario), 'id': 'h2'})
            acts.append(NS(turnos=[NS(horario_guardia_id='h2', dias_semana=[0])]))
        rol = NS(anio=year, mes=9, tipo_rol='ordinario', empleados=[NS(empleado_id='e', actividades=acts)])
        db = AsyncMock()
        db.scalars.side_effect = [NS(all=lambda rows=rows: rows) for rows in
            (tipos, tarifas, [NS(id='n', profesion_codigo='MED')], [NS(id='p', codigo='MED')], [], [])]
        return await estimar_rol(db, tid, rol, {'emps': {'e': emp}, 'hors': hors}), db

    async def test_estima_domingo_sin_duplicar_actividades(self):
        result, db = await self.fixture()
        self.assertEqual(len(result['detalle']), 4)
        self.assertEqual(result['total_estimado'], '400.04')
        self.assertTrue(all(f['tipo'] == 'MINSA-GDF' for f in result['detalle']))
        self.assertEqual(result['pendientes'], 0)
        # Todas las lecturas deben estar filtradas por el hospital autenticado.
        for call in db.scalars.call_args_list:
            self.assertIn('tenant_id', str(call.args[0]))

    async def test_cas_superposicion_calendario_pendientes(self):
        for kwargs in ({'vinculo': '1057_CONTRATADO'}, {'overlap': True}, {'year': 2027}):
            result, _ = await self.fixture(**kwargs)
            self.assertEqual(result['total_estimado'], '0.00')
            self.assertTrue(all(f['pendiente'] for f in result['detalle']))
