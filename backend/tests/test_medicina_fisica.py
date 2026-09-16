"""Medicina Física y Rehabilitación: pruebas HTTP con PostgreSQL y rollback
por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_medicina_fisica -v
"""
import unittest
import uuid
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import ClinicalRecord
from app.sigarh.rrhh.models import Empleado
from app.core.security import create_access_token


class MedicinaFisicaTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="medicina_fisica"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))
            self.tecnologo_id = uuid.uuid4()
            self.otro_empleado_id = uuid.uuid4()
            db.add(Empleado(id=self.tecnologo_id, tenant_id=self.tenant_id, dni="44443333", nombres="Tecnologo",
                apellido_paterno="De", apellido_materno="Prueba"))
            db.add(Empleado(id=self.otro_empleado_id, tenant_id=self.tenant_id, dni="33334444", nombres="Otro",
                apellido_paterno="Empleado", apellido_materno="Sin Habilitar"))
            await db.commit()
        self.prefix = "/app/medicina-fisica"
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def _crear_programa(self, nombre="Fisioterapia"):
        r = await self.client.post(self.prefix + "/programas", json={"nombre": nombre, "duracion_sesion_minutos": 30})
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()["id"]

    async def _programa_con_tecnologo(self):
        programa_id = await self._crear_programa()
        await self.client.post(f"{self.prefix}/programas/{programa_id}/tecnologos", json={"empleado_id": str(self.tecnologo_id)})
        return programa_id

    async def test_medicina_fisica_programa_duplicado_por_nombre_es_rechazado(self):
        await self._crear_programa("Fisioterapia")
        r = await self.client.post(self.prefix + "/programas", json={"nombre": "Fisioterapia"})
        self.assertEqual(r.status_code, 409, r.text)

    async def test_medicina_fisica_no_permite_programacion_con_tecnologo_no_habilitado(self):
        programa_id = await self._crear_programa()
        r = await self.client.post(self.prefix + "/programaciones", json={
            "programa_id": programa_id, "tecnologo_id": str(self.otro_empleado_id),
            "fecha": "2026-10-05", "turno": "TARDE", "hora_inicio": "14:00", "hora_fin": "15:00",
        })
        self.assertEqual(r.status_code, 400, r.text)

    async def test_medicina_fisica_sesion_respeta_slots_y_evita_doble_reserva(self):
        programa_id = await self._programa_con_tecnologo()
        prog = (await self.client.post(self.prefix + "/programaciones", json={
            "programa_id": programa_id, "tecnologo_id": str(self.tecnologo_id),
            "fecha": "2026-10-05", "turno": "TARDE", "hora_inicio": "14:00", "hora_fin": "15:00",
        })).json()
        self.assertEqual(prog["cupos_totales"], 2)

        r = await self.client.post(self.prefix + "/sesiones-m-fisica", json={
            "programacion_mf_id": prog["id"], "patient_id": str(self.pid), "hora_inicio": "14:07", "hora_fin": "14:37",
        })
        self.assertEqual(r.status_code, 400, r.text)

        r = await self.client.post(self.prefix + "/sesiones-m-fisica", json={
            "programacion_mf_id": prog["id"], "patient_id": str(self.pid), "hora_inicio": "14:00", "hora_fin": "14:30",
        })
        self.assertEqual(r.status_code, 201, r.text)

        r = await self.client.post(self.prefix + "/sesiones-m-fisica", json={
            "programacion_mf_id": prog["id"], "patient_id": str(self.pid), "hora_inicio": "14:00", "hora_fin": "14:30",
        })
        self.assertEqual(r.status_code, 409, r.text)

    async def test_medicina_fisica_ejecutar_sesion_registra_datos_clinicos(self):
        programa_id = await self._programa_con_tecnologo()
        prog = (await self.client.post(self.prefix + "/programaciones", json={
            "programa_id": programa_id, "tecnologo_id": str(self.tecnologo_id),
            "fecha": "2026-10-05", "turno": "TARDE", "hora_inicio": "14:00", "hora_fin": "14:30",
        })).json()
        sesion = (await self.client.post(self.prefix + "/sesiones-m-fisica", json={
            "programacion_mf_id": prog["id"], "patient_id": str(self.pid), "hora_inicio": "14:00", "hora_fin": "14:30",
        })).json()

        r = await self.client.post(f"{self.prefix}/sesiones-m-fisica/{sesion['id']}/ejecutar", json={
            "estado": "atendida", "escala_dolor_eva": 3, "actividades_realizadas": "Kinesioterapia",
        })
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "atendida")

        r = await self.client.post(f"{self.prefix}/sesiones-m-fisica/{sesion['id']}/ejecutar", json={"estado": "no_asistio"})
        self.assertEqual(r.status_code, 409, r.text)

    async def test_medicina_fisica_bloquear_programacion_impide_nuevas_sesiones(self):
        programa_id = await self._programa_con_tecnologo()
        prog = (await self.client.post(self.prefix + "/programaciones", json={
            "programa_id": programa_id, "tecnologo_id": str(self.tecnologo_id),
            "fecha": "2026-10-05", "turno": "TARDE", "hora_inicio": "14:00", "hora_fin": "14:30",
        })).json()

        r = await self.client.post(f"{self.prefix}/programaciones/{prog['id']}/bloquear", json={"motivo": "Mantenimiento"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "bloqueado")

        r = await self.client.post(self.prefix + "/sesiones-m-fisica", json={
            "programacion_mf_id": prog["id"], "patient_id": str(self.pid), "hora_inicio": "14:00", "hora_fin": "14:30",
        })
        self.assertEqual(r.status_code, 409, r.text)

    async def test_medicina_fisica_reprogramar_bloque_mueve_sesiones_a_otra_programacion(self):
        programa_id = await self._programa_con_tecnologo()
        origen = (await self.client.post(self.prefix + "/programaciones", json={
            "programa_id": programa_id, "tecnologo_id": str(self.tecnologo_id),
            "fecha": "2026-10-05", "turno": "TARDE", "hora_inicio": "14:00", "hora_fin": "14:30",
        })).json()
        destino = (await self.client.post(self.prefix + "/programaciones", json={
            "programa_id": programa_id, "tecnologo_id": str(self.tecnologo_id),
            "fecha": "2026-10-06", "turno": "TARDE", "hora_inicio": "09:00", "hora_fin": "10:00",
        })).json()
        sesion = (await self.client.post(self.prefix + "/sesiones-m-fisica", json={
            "programacion_mf_id": origen["id"], "patient_id": str(self.pid), "hora_inicio": "14:00", "hora_fin": "14:30",
        })).json()

        r = await self.client.post(self.prefix + "/sesiones-m-fisica/acciones/reprogramar-bloque", json={
            "sesion_ids": [sesion["id"]], "programacion_mf_id": destino["id"], "mensaje": "Reprogramado",
        })
        self.assertEqual(r.status_code, 200, r.text)
        movida = r.json()[0]
        self.assertEqual(movida["programacion_mf_id"], destino["id"])
        self.assertEqual(movida["hora_inicio"], "09:00")


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(MedicinaFisicaTests(name) for name in MedicinaFisicaTests.__dict__ if name.startswith("test_medicina_fisica_"))
