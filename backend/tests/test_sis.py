"""SIS (Formato FUA + Afiliaciones): pruebas HTTP con PostgreSQL y rollback
por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_sis -v
"""
import unittest
import uuid
from datetime import date, datetime
from sqlalchemy import select, update
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import ProgramacionMedica, Cita, AtencionMedica, AtencionDiagnostico
from app.sigarh.rrhh.models import Empleado
from app.sigarh.general.models import DiagnosticoCIE10
from app.sigarh.config_financiera.models import Seguro
from app.core.security import create_access_token


class SisTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="sis"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))
            self.medico_id = uuid.uuid4()
            self.dx_id = uuid.uuid4()
            self.seguro_sis_id = uuid.uuid4()
            self.seguro_particular_id = uuid.uuid4()
            db.add(Empleado(id=self.medico_id, tenant_id=self.tenant_id, dni="88887777", nombres="Medico",
                apellido_paterno="De Prueba", apellido_materno="Sis"))
            db.add(DiagnosticoCIE10(id=self.dx_id, tenant_id=self.tenant_id, codigo_cie10="A00.0",
                descripcion="Cólera de prueba"))
            db.add(Seguro(id=self.seguro_sis_id, tenant_id=self.tenant_id, codigo="SIS",
                nombre="SIS - Seguro Integral de Salud", tipo_entidad="Público", requiere_fua=True, is_active=True))
            db.add(Seguro(id=self.seguro_particular_id, tenant_id=self.tenant_id, codigo="PARTICULAR",
                nombre="Particular", tipo_entidad="Privado", requiere_fua=False, is_active=True))
            await db.flush()

            self.prog_id = uuid.uuid4()
            db.add(ProgramacionMedica(id=self.prog_id, tenant_id=self.tenant_id, medico_id=self.medico_id,
                fecha=date.today(), turno="M", hora_inicio="08:00", hora_fin="08:15"))
            await db.flush()

            self.cita_sis_id = uuid.uuid4()
            db.add(Cita(id=self.cita_sis_id, tenant_id=self.tenant_id, programacion_medica_id=self.prog_id,
                patient_id=self.pid, hora_inicio="08:00", hora_fin="08:15",
                fuente_financiamiento="SIS - Seguro Integral de Salud", numero_cuenta="CTA-SIS-1"))
            # Segunda atencion, financiada por Particular -- no debe aparecer como pendiente de FUA.
            self.cita_particular_id = uuid.uuid4()
            db.add(Cita(id=self.cita_particular_id, tenant_id=self.tenant_id, programacion_medica_id=self.prog_id,
                patient_id=self.pid, hora_inicio="08:15", hora_fin="08:30",
                fuente_financiamiento="Particular", numero_cuenta="CTA-PART-1"))
            await db.flush()

            self.atencion_sis_id = uuid.uuid4()
            db.add(AtencionMedica(id=self.atencion_sis_id, tenant_id=self.tenant_id, cita_id=self.cita_sis_id,
                motivo_consulta="Control", prestaciones=["FARMACIA"], destino_atencion="ALTA",
                estado="firmado", firmado_por_id=self.medico_id, firmado_at=datetime.utcnow()))
            self.atencion_particular_id = uuid.uuid4()
            db.add(AtencionMedica(id=self.atencion_particular_id, tenant_id=self.tenant_id, cita_id=self.cita_particular_id,
                motivo_consulta="Control particular", destino_atencion="ALTA",
                estado="firmado", firmado_por_id=self.medico_id, firmado_at=datetime.utcnow()))
            await db.flush()

            db.add(AtencionDiagnostico(atencion_medica_id=self.atencion_sis_id, diagnostico_cie10_id=self.dx_id, tipo="definitivo"))
            await db.commit()
        self.prefix = "/app/sis"
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def test_sis_pendientes_solo_incluye_atenciones_financiadas_por_seguro_que_exige_fua(self):
        r = await self.client.get(self.prefix + "/formato-fua/pendientes")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(len(r.json()), 1)
        self.assertEqual(r.json()[0]["atencion_medica_id"], str(self.atencion_sis_id))

    async def test_sis_generar_fua_flujo_completo_y_duplicado_rechazado(self):
        r = await self.client.post(self.prefix + "/formato-fua", json={"atencion_medica_id": str(self.atencion_sis_id)})
        self.assertEqual(r.status_code, 201, r.text)
        fua = r.json()
        self.assertEqual(fua["estado"], "generado")
        self.assertEqual(fua["diagnosticos"][0]["codigo"], "A00.0")
        self.assertEqual(fua["prestaciones"], ["FARMACIA"])

        r = await self.client.post(self.prefix + "/formato-fua", json={"atencion_medica_id": str(self.atencion_sis_id)})
        self.assertEqual(r.status_code, 409, r.text)

        r = await self.client.get(self.prefix + "/formato-fua/pendientes")
        self.assertEqual(r.json(), [])

        r = await self.client.get(self.prefix + f"/formato-fua/{fua['id']}/reporte.pdf")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.content.startswith(b"%PDF"))

    async def test_sis_no_genera_fua_para_atencion_sin_seguro_que_lo_exija(self):
        r = await self.client.post(self.prefix + "/formato-fua", json={"atencion_medica_id": str(self.atencion_particular_id)})
        self.assertEqual(r.status_code, 422, r.text)

    async def test_sis_transiciones_de_estado_validas_e_invalidas(self):
        fua = (await self.client.post(self.prefix + "/formato-fua", json={"atencion_medica_id": str(self.atencion_sis_id)})).json()
        fid = fua["id"]

        r = await self.client.post(f"{self.prefix}/formato-fua/{fid}/estado", json={"estado": "pagado"})
        self.assertEqual(r.status_code, 409, r.text)  # generado -> pagado no es una transicion valida

        r = await self.client.post(f"{self.prefix}/formato-fua/{fid}/estado", json={"estado": "enviado"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "enviado")

        r = await self.client.post(f"{self.prefix}/formato-fua/{fid}/estado", json={"estado": "pagado"})
        self.assertEqual(r.status_code, 200, r.text)

        r = await self.client.post(f"{self.prefix}/formato-fua/{fid}/estado", json={"estado": "enviado"})
        self.assertEqual(r.status_code, 409, r.text)  # pagado es estado final

    async def test_sis_observar_y_anular_requieren_motivo(self):
        fua = (await self.client.post(self.prefix + "/formato-fua", json={"atencion_medica_id": str(self.atencion_sis_id)})).json()
        r = await self.client.post(f"{self.prefix}/formato-fua/{fua['id']}/estado", json={"estado": "anulado"})
        self.assertEqual(r.status_code, 422, r.text)
        r = await self.client.post(f"{self.prefix}/formato-fua/{fua['id']}/estado",
            json={"estado": "anulado", "observaciones": "Datos incorrectos"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "anulado")

    async def test_sis_afiliaciones_solo_lista_pacientes_con_seguro_sis(self):
        async with self.session() as db:
            await db.execute(update(Patient).where(Patient.id == self.pid).values(insurance_type="SIS - Seguro Integral de Salud", insurance_number="SIS-000123"))
            await db.commit()
        r = await self.client.get(self.prefix + "/afiliaciones")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["total"], 1)
        self.assertEqual(r.json()["items"][0]["insurance_number"], "SIS-000123")


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(SisTests(name) for name in SisTests.__dict__ if name.startswith("test_sis_"))
