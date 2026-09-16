"""Hemodiálisis: pruebas HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_hemodialisis -v
"""
import unittest
import uuid
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import ClinicalRecord
from app.sigarh.general.models import DiagnosticoCIE10
from app.core.security import create_access_token


class HemodialisisTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="hemodialisis"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))
            self.dx_id = uuid.uuid4()
            db.add(DiagnosticoCIE10(id=self.dx_id, tenant_id=self.tenant_id, codigo_cie10="N18.5",
                descripcion="Enfermedad renal cronica, etapa 5"))
            await db.commit()
        self.prefix = "/app/hemodialisis"
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def _inscribir(self):
        r = await self.client.post(self.prefix + "/hemodialis", json={
            "patient_id": str(self.pid), "diagnostico_id": str(self.dx_id),
            "acceso_vascular_tipo": "FAV", "peso_seco_kg": 68.5, "turno_habitual": "TARDE", "frecuencia_semanal": 3,
        })
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()

    async def test_hemodialisis_inscripcion_duplicada_por_paciente_es_rechazada(self):
        await self._inscribir()
        r = await self.client.post(self.prefix + "/hemodialis", json={
            "patient_id": str(self.pid), "acceso_vascular_tipo": "FAV", "peso_seco_kg": 70,
        })
        self.assertEqual(r.status_code, 409, r.text)

    async def test_hemodialisis_sesion_ultrafiltracion_se_calcula_automaticamente(self):
        hd = await self._inscribir()
        r = await self.client.post(self.prefix + "/sesiones", json={
            "paciente_hemodialisis_id": hd["id"], "turno": "TARDE", "peso_pre_kg": 71.0,
        })
        self.assertEqual(r.status_code, 201, r.text)
        sesion = r.json()
        self.assertEqual(sesion["estado"], "programada")
        self.assertEqual(sesion["acceso_vascular_utilizado"], "FAV")

        r = await self.client.post(f"{self.prefix}/sesiones/{sesion['id']}/estado", json={"estado": "en_curso"})
        self.assertEqual(r.status_code, 200, r.text)

        r = await self.client.post(f"{self.prefix}/sesiones/{sesion['id']}/estado",
            json={"estado": "completada", "peso_post_kg": 68.5})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["ultrafiltracion_litros"], 2.5)

    async def test_hemodialisis_transicion_invalida_de_sesion_es_rechazada(self):
        hd = await self._inscribir()
        sesion = (await self.client.post(self.prefix + "/sesiones", json={
            "paciente_hemodialisis_id": hd["id"], "turno": "MAÑANA",
        })).json()
        r = await self.client.post(f"{self.prefix}/sesiones/{sesion['id']}/estado", json={"estado": "completada"})
        self.assertEqual(r.status_code, 409, r.text)

    async def test_hemodialisis_no_permite_sesiones_para_paciente_inactivo(self):
        hd = await self._inscribir()
        r = await self.client.post(f"{self.prefix}/hemodialis/{hd['id']}/estado", json={"estado": "trasplantado"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "trasplantado")

        r = await self.client.post(self.prefix + "/sesiones", json={
            "paciente_hemodialisis_id": hd["id"], "turno": "TARDE",
        })
        self.assertEqual(r.status_code, 409, r.text)

        r = await self.client.post(f"{self.prefix}/hemodialis/{hd['id']}/estado", json={"estado": "fallecido"})
        self.assertEqual(r.status_code, 409, r.text)

    async def test_hemodialisis_listado_incluye_datos_del_paciente_y_diagnostico(self):
        await self._inscribir()
        r = await self.client.get(self.prefix + "/hemodialis")
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertIn("N18.5", data[0]["diagnostico"])
        self.assertIsNotNone(data[0]["paciente_dni"])


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(HemodialisisTests(name) for name in HemodialisisTests.__dict__ if name.startswith("test_hemodialisis_"))
