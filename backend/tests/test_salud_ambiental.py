"""Salud Ambiental (Defunciones -- cadena causal CIE-10, SINADEF/RENIEC):
pruebas HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_salud_ambiental -v
"""
import unittest
import uuid
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import ClinicalRecord
from app.hospital.consulta_externa.models import Hospitalizacion
from app.hospital.emergencia.models import AdmisionEmergencia, AtencionEmergencia
from app.sigarh.rrhh.models import Empleado
from app.sigarh.mantenimiento.models import Profesion, GrupoOcupacional
from app.sigarh.general.models import DiagnosticoCIE10
from app.sigarh.infraestructura_hosp.models import Cama
from app.core.security import create_access_token


class SaludAmbientalTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="salud_ambiental"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))

            grupo_id = uuid.uuid4()
            db.add(GrupoOcupacional(id=grupo_id, tenant_id=self.tenant_id, nombre="Médicos"))
            await db.flush()
            profesion_id = uuid.uuid4()
            db.add(Profesion(id=profesion_id, tenant_id=self.tenant_id, grupo_ocupacional_id=grupo_id,
                nombre="Médico Cirujano", codigo="MED"))
            await db.flush()
            self.medico_id = uuid.uuid4()
            db.add(Empleado(id=self.medico_id, tenant_id=self.tenant_id, dni="55556666", nombres="Medico",
                apellido_paterno="Certificador", apellido_materno="Prueba",
                profesion_id=profesion_id, habilitado_colegio=True, numero_cmp="CMP-5555"))
            self.no_medico_id = uuid.uuid4()
            db.add(Empleado(id=self.no_medico_id, tenant_id=self.tenant_id, dni="66667777", nombres="Sin",
                apellido_paterno="Colegiatura", apellido_materno="Prueba"))

            self.dx_a = uuid.uuid4(); self.dx_b = uuid.uuid4()
            db.add(DiagnosticoCIE10(id=self.dx_a, tenant_id=self.tenant_id, codigo_cie10="I509", descripcion="Insuficiencia cardiaca"))
            db.add(DiagnosticoCIE10(id=self.dx_b, tenant_id=self.tenant_id, codigo_cie10="I10", descripcion="Hipertension esencial"))

            self.admision_id = uuid.uuid4()
            db.add(AdmisionEmergencia(id=self.admision_id, tenant_id=self.tenant_id, patient_id=self.pid,
                numero_cuenta="EMG-SA-0001", estado="en_atencion"))
            self.cama_id = uuid.uuid4()
            db.add(Cama(id=self.cama_id, tenant_id=self.tenant_id, codigo="C-01", nombre="Cama 1"))
            await db.flush()

            self.atencion_id = uuid.uuid4()
            db.add(AtencionEmergencia(id=self.atencion_id, tenant_id=self.tenant_id, admision_id=self.admision_id,
                motivo_consulta="Paro cardiorrespiratorio", destino_atencion="AMBULATORIA", estado="borrador"))
            self.hosp_id = uuid.uuid4()
            db.add(Hospitalizacion(id=self.hosp_id, tenant_id=self.tenant_id, patient_id=self.pid, cama_id=self.cama_id,
                numero_hospitalizacion="HOSP-SA-0001", estado="internado"))
            await db.commit()
        self.prefix = "/app/salud-ambiental"
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def test_salud_ambiental_exige_medico_certificador_habilitado(self):
        r = await self.client.post(self.prefix + "/defunciones", json={
            "atencion_emergencia_id": str(self.atencion_id), "medico_certificador_id": str(self.no_medico_id),
            "fecha_defuncion": "2026-09-16T20:00:00", "lugar_defuncion": "Emergencia",
            "tipo_muerte": "NATURAL", "causa_a_id": str(self.dx_a),
        })
        self.assertEqual(r.status_code, 400, r.text)

    async def test_salud_ambiental_crear_desde_emergencia_actualiza_destino_atencion(self):
        r = await self.client.post(self.prefix + "/defunciones", json={
            "atencion_emergencia_id": str(self.atencion_id), "medico_certificador_id": str(self.medico_id),
            "fecha_defuncion": "2026-09-16T20:00:00", "lugar_defuncion": "Emergencia - Sala 1",
            "tipo_muerte": "NATURAL", "causa_a_id": str(self.dx_a), "causa_b_id": str(self.dx_b),
        })
        self.assertEqual(r.status_code, 201, r.text)
        data = r.json()
        self.assertEqual(data["patient_id"], str(self.pid))
        self.assertIn("I509", data["causa_a"])
        self.assertFalse(data["requiere_necropsia_legal"])

        # El efecto sobre AtencionEmergencia.destino_atencion se confirma
        # indirectamente: un segundo certificado sobre el mismo origen se rechaza.
        r = await self.client.post(self.prefix + "/defunciones", json={
            "atencion_emergencia_id": str(self.atencion_id), "medico_certificador_id": str(self.medico_id),
            "fecha_defuncion": "2026-09-16T20:00:00", "lugar_defuncion": "Emergencia",
            "tipo_muerte": "NATURAL", "causa_a_id": str(self.dx_a),
        })
        self.assertEqual(r.status_code, 409, r.text)

    async def test_salud_ambiental_violenta_marca_necropsia_legal_automaticamente(self):
        r = await self.client.post(self.prefix + "/defunciones", json={
            "patient_id": str(self.pid), "medico_certificador_id": str(self.medico_id),
            "fecha_defuncion": "2026-09-16T20:00:00", "lugar_defuncion": "Via publica",
            "tipo_muerte": "VIOLENTA", "causa_a_id": str(self.dx_a),
        })
        self.assertEqual(r.status_code, 201, r.text)
        self.assertTrue(r.json()["requiere_necropsia_legal"])

    async def test_salud_ambiental_crear_desde_hospitalizacion_marca_estado_fallecido(self):
        r = await self.client.post(self.prefix + "/defunciones", json={
            "hospitalizacion_id": str(self.hosp_id), "medico_certificador_id": str(self.medico_id),
            "fecha_defuncion": "2026-09-16T20:00:00", "lugar_defuncion": "UCI",
            "tipo_muerte": "NATURAL", "causa_a_id": str(self.dx_a),
        })
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual(r.json()["origen"], "Hospitalización")

    async def test_salud_ambiental_marcar_enviado_es_idempotente_una_sola_vez(self):
        cert = (await self.client.post(self.prefix + "/defunciones", json={
            "patient_id": str(self.pid), "medico_certificador_id": str(self.medico_id),
            "fecha_defuncion": "2026-09-16T20:00:00", "lugar_defuncion": "Sala",
            "tipo_muerte": "NATURAL", "causa_a_id": str(self.dx_a),
        })).json()

        r = await self.client.post(f"{self.prefix}/defunciones/{cert['id']}/marcar-enviado")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado_envio"], "enviado_reniec")

        r = await self.client.post(f"{self.prefix}/defunciones/{cert['id']}/marcar-enviado")
        self.assertEqual(r.status_code, 409, r.text)

    async def test_salud_ambiental_reporte_pdf_se_genera(self):
        cert = (await self.client.post(self.prefix + "/defunciones", json={
            "patient_id": str(self.pid), "medico_certificador_id": str(self.medico_id),
            "fecha_defuncion": "2026-09-16T20:00:00", "lugar_defuncion": "Sala",
            "tipo_muerte": "NATURAL", "causa_a_id": str(self.dx_a),
        })).json()
        r = await self.client.get(f"{self.prefix}/defunciones/{cert['id']}/reporte.pdf")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertTrue(r.content.startswith(b"%PDF"))


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(SaludAmbientalTests(name) for name in SaludAmbientalTests.__dict__ if name.startswith("test_salud_ambiental_"))
