"""Epidemiología (ENO -- RENACE/CDC-MINSA): pruebas HTTP con PostgreSQL y
rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_epidemiologia -v
"""
import unittest
import uuid
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import ClinicalRecord
from app.hospital.emergencia.models import AdmisionEmergencia, AtencionEmergencia
from app.sigarh.rrhh.models import Empleado
from app.sigarh.mantenimiento.models import Profesion
from app.core.security import create_access_token


class EpidemiologiaTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="epidemiologia"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))

            profesion_id = uuid.uuid4()
            db.add(Profesion(id=profesion_id, tenant_id=self.tenant_id, grupo_ocupacional_id=uuid.uuid4(),
                nombre="Médico Cirujano", codigo="MED"))
            self.medico_id = uuid.uuid4()
            db.add(Empleado(id=self.medico_id, tenant_id=self.tenant_id, dni="44445555", nombres="Medico",
                apellido_paterno="Notificante", apellido_materno="Prueba",
                profesion_id=profesion_id, habilitado_colegio=True, numero_cmp="CMP-4444"))

            self.admision_id = uuid.uuid4()
            db.add(AdmisionEmergencia(id=self.admision_id, tenant_id=self.tenant_id, patient_id=self.pid,
                numero_cuenta="EMG-EPI-0001", estado="en_atencion"))
            self.atencion_id = uuid.uuid4()
            db.add(AtencionEmergencia(id=self.atencion_id, tenant_id=self.tenant_id, admision_id=self.admision_id,
                motivo_consulta="Fiebre y dolor retroocular", destino_atencion="AMBULATORIA", estado="borrador"))
            await db.commit()
        self.prefix = "/app/epidemiologia"
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def test_epidemiologia_rechaza_datos_clinicos_incompletos(self):
        r = await self.client.post(self.prefix + "/ficha-dengue", json={
            "atencion_emergencia_id": str(self.atencion_id), "medico_notificante_id": str(self.medico_id),
            "tipo_ficha": "DENGUE", "datos_clinicos": {"fecha_inicio_sintomas": "2026-09-14"},
        })
        self.assertEqual(r.status_code, 422, r.text)

    async def test_epidemiologia_crea_ficha_dengue_valida_desde_emergencia(self):
        r = await self.client.post(self.prefix + "/ficha-dengue", json={
            "atencion_emergencia_id": str(self.atencion_id), "medico_notificante_id": str(self.medico_id),
            "tipo_ficha": "DENGUE", "datos_clinicos": {
                "fecha_inicio_sintomas": "2026-09-14", "signos_alarma": ["dolor_abdominal"],
                "clasificacion": "CON_SENALES_ALARMA", "resultado_prueba": "POSITIVO", "plaquetas": 95000,
            },
        })
        self.assertEqual(r.status_code, 201, r.text)
        data = r.json()
        self.assertEqual(data["patient_id"], str(self.pid))
        self.assertEqual(data["datos_clinicos"]["clasificacion"], "CON_SENALES_ALARMA")

    async def test_epidemiologia_no_permite_dos_fichas_mismo_tipo_para_la_misma_atencion(self):
        body = {"atencion_emergencia_id": str(self.atencion_id), "medico_notificante_id": str(self.medico_id),
            "tipo_ficha": "DENGUE", "datos_clinicos": {"fecha_inicio_sintomas": "2026-09-14", "clasificacion": "SIN_SENALES_ALARMA"}}
        r1 = await self.client.post(self.prefix + "/ficha-dengue", json=body)
        self.assertEqual(r1.status_code, 201, r1.text)
        r2 = await self.client.post(self.prefix + "/ficha-dengue", json=body)
        self.assertEqual(r2.status_code, 409, r2.text)

    async def test_epidemiologia_endpoint_rechaza_tipo_ficha_equivocado(self):
        r = await self.client.post(self.prefix + "/ficha-covid", json={
            "patient_id": str(self.pid), "medico_notificante_id": str(self.medico_id),
            "tipo_ficha": "DENGUE", "datos_clinicos": {"fecha_inicio_sintomas": "2026-09-14", "clasificacion": "SIN_SENALES_ALARMA"},
        })
        self.assertEqual(r.status_code, 400, r.text)

    async def test_epidemiologia_ficha_diabetes_directa_sin_origen_clinico(self):
        r = await self.client.post(self.prefix + "/ficha-diabetes", json={
            "patient_id": str(self.pid), "medico_notificante_id": str(self.medico_id),
            "tipo_ficha": "DIABETES", "datos_clinicos": {
                "tipo_diabetes": "TIPO_2", "fecha_diagnostico": "2024-01-15", "hba1c": 8.2,
                "complicaciones": ["retinopatia"],
            },
        })
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual(r.json()["origen"], "Directo")

    async def test_epidemiologia_marcar_enviado_es_idempotente_una_sola_vez(self):
        ficha = (await self.client.post(self.prefix + "/ficha-diabetes", json={
            "patient_id": str(self.pid), "medico_notificante_id": str(self.medico_id),
            "tipo_ficha": "DIABETES", "datos_clinicos": {"tipo_diabetes": "TIPO_2", "fecha_diagnostico": "2024-01-15"},
        })).json()
        r = await self.client.post(f"{self.prefix}/fichas/{ficha['id']}/marcar-enviado")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado_envio"], "enviada_red_salud")
        r = await self.client.post(f"{self.prefix}/fichas/{ficha['id']}/marcar-enviado")
        self.assertEqual(r.status_code, 409, r.text)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(EpidemiologiaTests(name) for name in EpidemiologiaTests.__dict__ if name.startswith("test_epidemiologia_"))
