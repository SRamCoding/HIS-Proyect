"""TeleSalud (Ley N.° 30421 / Ley N.° 31166): pruebas HTTP con PostgreSQL y
rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_telesalud -v
"""
import unittest
import uuid
from datetime import date
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import ProgramacionMedica, Cita
from app.sigarh.rrhh.models import Empleado, Especialidad, EmpleadoEspecialidad
from app.core.security import create_access_token


class TelesaludTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="telesalud"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))
            self.medico_id = uuid.uuid4()
            self.esp_id = uuid.uuid4()
            db.add(Empleado(id=self.medico_id, tenant_id=self.tenant_id, dni="88887777", nombres="Medico",
                apellido_paterno="De Prueba", apellido_materno="Tele", celular="999888777", correo="medico@test.pe",
                numero_cmp="CMP-1234"))
            db.add(Especialidad(id=self.esp_id, tenant_id=self.tenant_id, nombre="Medicina General",
                codigo="MED-GEN", is_active=True))
            db.add(EmpleadoEspecialidad(id=uuid.uuid4(), empleado_id=self.medico_id, especialidad_id=self.esp_id,
                numero_rne="RNE-5678"))

            self.prog_virtual_id = uuid.uuid4()
            db.add(ProgramacionMedica(id=self.prog_virtual_id, tenant_id=self.tenant_id, medico_id=self.medico_id,
                especialidad_id=self.esp_id, fecha=date.today(), turno="T", hora_inicio="15:00", hora_fin="15:30",
                modalidad="VIRTUAL"))
            self.cita_virtual_id = uuid.uuid4()
            db.add(Cita(id=self.cita_virtual_id, tenant_id=self.tenant_id, programacion_medica_id=self.prog_virtual_id,
                patient_id=self.pid, hora_inicio="15:00", hora_fin="15:15", estado="separada"))

            self.prog_presencial_id = uuid.uuid4()
            db.add(ProgramacionMedica(id=self.prog_presencial_id, tenant_id=self.tenant_id, medico_id=self.medico_id,
                fecha=date.today(), turno="M", hora_inicio="09:00", hora_fin="09:30", modalidad="PRESENCIAL"))
            self.cita_presencial_id = uuid.uuid4()
            db.add(Cita(id=self.cita_presencial_id, tenant_id=self.tenant_id, programacion_medica_id=self.prog_presencial_id,
                patient_id=self.pid, hora_inicio="09:00", hora_fin="09:15", estado="separada"))
            await db.commit()
        self.prefix = "/app/telesalud"
        self.hoy = date.today().isoformat()
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def test_telesalud_guia_rapida_expone_marco_legal_real(self):
        r = await self.client.get(self.prefix + "/guia-rapida-minsa")
        self.assertEqual(r.status_code, 200, r.text)
        normas = [n["norma"] for n in r.json()["marco_legal"]]
        self.assertIn("Ley N.° 30421", normas)
        self.assertIn("Ley N.° 31166", normas)

    async def test_telesalud_crear_solicitud_y_listar(self):
        r = await self.client.post(self.prefix + "/formulario-solicitud",
            json={"patient_id": str(self.pid), "motivo": "Control", "medio_preferido": "WHATSAPP"})
        self.assertEqual(r.status_code, 201, r.text)
        sol = r.json()
        self.assertEqual(sol["estado"], "pendiente")

        r = await self.client.get(self.prefix + "/formulario-solicitud", params={"estado": "pendiente"})
        self.assertEqual(len(r.json()), 1)

    async def test_telesalud_programar_exige_cita_virtual(self):
        sol = (await self.client.post(self.prefix + "/formulario-solicitud",
            json={"patient_id": str(self.pid), "motivo": "Control"})).json()

        r = await self.client.post(f"{self.prefix}/formulario-solicitud/{sol['id']}/programar",
            json={"cita_id": str(self.cita_presencial_id)})
        self.assertEqual(r.status_code, 400, r.text)

        r = await self.client.post(f"{self.prefix}/formulario-solicitud/{sol['id']}/programar",
            json={"cita_id": str(self.cita_virtual_id)})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "programada")

        r = await self.client.post(f"{self.prefix}/formulario-solicitud/{sol['id']}/programar",
            json={"cita_id": str(self.cita_virtual_id)})
        self.assertEqual(r.status_code, 409, r.text)

    async def test_telesalud_no_permite_enlazar_dos_solicitudes_a_la_misma_cita(self):
        sol1 = (await self.client.post(self.prefix + "/formulario-solicitud",
            json={"patient_id": str(self.pid), "motivo": "Control 1"})).json()
        sol2 = (await self.client.post(self.prefix + "/formulario-solicitud",
            json={"patient_id": str(self.pid), "motivo": "Control 2"})).json()

        r = await self.client.post(f"{self.prefix}/formulario-solicitud/{sol1['id']}/programar",
            json={"cita_id": str(self.cita_virtual_id)})
        self.assertEqual(r.status_code, 200, r.text)

        r = await self.client.post(f"{self.prefix}/formulario-solicitud/{sol2['id']}/programar",
            json={"cita_id": str(self.cita_virtual_id)})
        self.assertEqual(r.status_code, 409, r.text)

    async def test_telesalud_rechazar_solicitud_exige_motivo(self):
        sol = (await self.client.post(self.prefix + "/formulario-solicitud",
            json={"patient_id": str(self.pid), "motivo": "Control"})).json()

        r = await self.client.post(f"{self.prefix}/formulario-solicitud/{sol['id']}/rechazar", json={"motivo_rechazo": "No contesta"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "rechazada")

        r = await self.client.post(f"{self.prefix}/formulario-solicitud/{sol['id']}/rechazar", json={"motivo_rechazo": "otra vez"})
        self.assertEqual(r.status_code, 409, r.text)

    async def test_telesalud_monitor_y_medicos_solo_incluyen_modalidad_virtual(self):
        r = await self.client.get(self.prefix + "/monitor")
        self.assertEqual(r.status_code, 200, r.text)
        citas = r.json()
        self.assertEqual(len(citas), 1)
        self.assertEqual(citas[0]["cita_id"], str(self.cita_virtual_id))

        r = await self.client.get(self.prefix + "/medicos")
        self.assertEqual(r.status_code, 200, r.text)
        medicos = r.json()
        self.assertEqual(len(medicos), 1)
        self.assertEqual(medicos[0]["especialidades"][0]["numero_rne"], "RNE-5678")

    async def test_telesalud_resumen_cuenta_citas_virtuales_del_rango(self):
        r = await self.client.get(self.prefix + "/resumen-teleconsultas", params={"fecha_desde": self.hoy, "fecha_hasta": self.hoy})
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["citas_virtuales_programadas"], 1)  # la presencial no cuenta


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(TelesaludTests(name) for name in TelesaludTests.__dict__ if name.startswith("test_telesalud_"))
