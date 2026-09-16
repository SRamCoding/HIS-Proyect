"""Hospitalizacion: pruebas HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_hospitalizacion -v
"""
import unittest
import uuid
from datetime import date
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.emergencia.models import AdmisionEmergencia, AtencionEmergencia, DestinoEmergencia
from app.sigarh.infraestructura_hosp.models import Cama
from app.sigarh.rrhh.models import Empleado, Especialidad
from app.core.security import create_access_token


class HospitalizacionTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="hospitalizacion"))
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="emergencia"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))
            self.staff = uuid.uuid4()
            self.espec = uuid.uuid4()
            self.cama_id = uuid.uuid4()
            db.add(Empleado(id=self.staff, tenant_id=self.tenant_id, dni="99999999", nombres="Medico",
                apellido_paterno="Prueba", apellido_materno="Hosp"))
            db.add(Especialidad(id=self.espec, tenant_id=self.tenant_id, nombre="Medicina Interna"))
            db.add(Cama(id=self.cama_id, tenant_id=self.tenant_id, codigo="CAMA-TEST-1", nombre="Cama de prueba"))

            self.admision_id = uuid.uuid4()
            self.atencion_emerg_id = uuid.uuid4()
            self.destino_id = uuid.uuid4()
            db.add(AdmisionEmergencia(id=self.admision_id, tenant_id=self.tenant_id, patient_id=self.pid,
                numero_cuenta="EMG-TEST-1", servicio_emergencia="Emergencia General", estado="derivado"))
            db.add(AtencionEmergencia(id=self.atencion_emerg_id, tenant_id=self.tenant_id, admision_id=self.admision_id,
                motivo_consulta="Dolor abdominal", destino_atencion="HOSPITALIZACION", estado="firmado"))
            db.add(DestinoEmergencia(id=self.destino_id, tenant_id=self.tenant_id, atencion_id=self.atencion_emerg_id,
                destino="HOSPITALIZACION", estado="pendiente"))

            # Segunda atencion de emergencia, independiente, con destino INTERCONSULTA
            self.admision_id2 = uuid.uuid4()
            self.atencion_emerg_id2 = uuid.uuid4()
            self.destino_interc_id = uuid.uuid4()
            self.pid2 = await self.crear_paciente_extra(db, "Interconsulta Emergencia")
            db.add(AdmisionEmergencia(id=self.admision_id2, tenant_id=self.tenant_id, patient_id=self.pid2,
                numero_cuenta="EMG-TEST-2", servicio_emergencia="Emergencia General", estado="derivado"))
            db.add(AtencionEmergencia(id=self.atencion_emerg_id2, tenant_id=self.tenant_id, admision_id=self.admision_id2,
                motivo_consulta="Dolor toracico", destino_atencion="INTERCONSULTA", estado="firmado"))
            db.add(DestinoEmergencia(id=self.destino_interc_id, tenant_id=self.tenant_id, atencion_id=self.atencion_emerg_id2,
                destino="INTERCONSULTA", estado="pendiente"))
            await db.commit()
        self.prefix = "/app/hospitalizacion"
        self.claims = {**self.claims, "empleado_id": str(self.staff)}
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def post(self, path, data, status=201):
        r = await self.client.post(self.prefix+path, json=data)
        self.assertEqual(r.status_code, status, r.text)
        return r.json()

    async def admitir(self):
        return await self.post("/hospitalizaciones/admitir-emergencia", {
            "destino_id": str(self.destino_id), "cama_id": str(self.cama_id), "especialidad_ingreso_id": str(self.espec)})

    async def crear_paciente_extra(self, db, nombre):
        from datetime import date as date_
        patient = Patient(tenant_id=self.tenant_id, dni=str(uuid.uuid4().int)[:8], first_name=nombre,
            last_name_paterno="Prueba", last_name_materno="Extra", birth_date=date_(1985, 5, 5), gender="M")
        db.add(patient)
        await db.flush()
        return patient.id

    async def test_hosp_admitir_desde_emergencia_ocupa_cama_y_resuelve_destino(self):
        hosp = await self.admitir()
        self.assertEqual(hosp["estado"], "internado")
        self.assertEqual(hosp["origen"], "EMERGENCIA")
        r = await self.client.get(self.prefix+"/panel-camas")
        cama = next(c for c in r.json() if c["id"] == str(self.cama_id))
        self.assertEqual(cama["estado"], "OCUPADA")
        self.assertEqual(cama["paciente_dni"], (await self.client.get(self.prefix+f"/hospitalizaciones/{hosp['id']}")).json()["dni"])
        await self.post("/hospitalizaciones/admitir-emergencia", {
            "destino_id": str(self.destino_id), "cama_id": str(self.cama_id)}, 409)
        r = await self.client.get(self.prefix+"/emergencia-pendientes")
        self.assertEqual(r.json(), [])

    async def test_hosp_cama_no_disponible_rechaza_admision(self):
        async with self.session() as db:
            cama = await db.get(Cama, self.cama_id)
            cama.estado = "MANTENIMIENTO"
            await db.commit()
        await self.post("/hospitalizaciones/admitir-emergencia", {
            "destino_id": str(self.destino_id), "cama_id": str(self.cama_id)}, 409)

    async def test_hosp_seguimiento_interconsulta_consentimiento_y_alta(self):
        hosp = await self.admitir()
        hid = hosp["id"]
        nota = await self.post(f"/hospitalizaciones/{hid}/notas", {
            "tipo": "MEDICA", "contenido": "Paciente estable", "pulso": 80, "temperatura": 36.5})
        self.assertEqual(nota["tipo"], "MEDICA")
        r = await self.client.get(self.prefix+f"/hospitalizaciones/{hid}/notas")
        self.assertEqual(len(r.json()), 1)

        interc = await self.post(f"/hospitalizaciones/{hid}/interconsultas", {
            "especialidad_destino_id": str(self.espec), "motivo": "Evaluación por cardiología"})
        self.assertEqual(interc["estado"], "pendiente")
        await self.post(f"/hospitalizaciones/{hid}/interconsultas", {
            "especialidad_destino_id": str(self.espec), "motivo": "Duplicada"}, 409)

        consent = await self.post(f"/hospitalizaciones/{hid}/consentimientos", {
            "procedimiento": "Colecistectomía", "riesgos_beneficios": "Riesgo de sangrado, beneficio resolutivo",
            "firmante_nombre": "Paciente de Prueba", "firmante_documento": "12345678",
            "relacion_firmante": "PACIENTE", "fecha": "2030-01-01"})
        self.assertEqual(consent["estado"], "registrado")
        r = await self.client.get(self.prefix+f"/consentimientos/{consent['id']}/comprobante.pdf")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.content.startswith(b"%PDF"))
        r = await self.client.post(self.prefix+f"/consentimientos/{consent['id']}/revocar", json={"motivo_revocacion": "Cambio de plan"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "revocado")

        r = await self.client.post(self.prefix+f"/hospitalizaciones/{hid}/alta", json={"resumen_alta": "Evolución favorable"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "alta")
        r = await self.client.get(self.prefix+"/panel-camas")
        cama = next(c for c in r.json() if c["id"] == str(self.cama_id))
        self.assertEqual(cama["estado"], "DISPONIBLE")
        await self.post(f"/hospitalizaciones/{hid}/notas", {"tipo": "MEDICA", "contenido": "No debería poder"}, 409)
        await self.post(f"/hospitalizaciones/{hid}/alta", {}, 409)

    async def test_hosp_censo_diario(self):
        await self.admitir()
        r = await self.client.get(self.prefix+"/censo-diario", params={"fecha": str(date.today())})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["total_internados"], 1)
        r = await self.client.get(self.prefix+"/censo-diario/reporte.pdf")
        self.assertTrue(r.content.startswith(b"%PDF"))
        r = await self.client.get(self.prefix+"/censo-diario/reporte.csv")
        self.assertEqual(r.status_code, 200)

    async def test_hosp_admitir_interconsulta_desde_emergencia(self):
        r = await self.client.get(self.prefix + "/emergencia-pendientes", params={"destino": "INTERCONSULTA"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(len(r.json()), 1)
        self.assertEqual(r.json()[0]["destino_id"], str(self.destino_interc_id))

        interc = await self.post("/interconsultas/admitir-emergencia", {
            "destino_id": str(self.destino_interc_id), "especialidad_destino_id": str(self.espec),
            "motivo": "Evaluación por cardiología desde emergencia", "urgente": True})
        self.assertEqual(interc["estado"], "pendiente")
        self.assertEqual(interc["origen"], "EMERGENCIA")
        self.assertEqual(interc["paciente_dni"], (await self._paciente_dni(self.pid2)))

        # El destino de emergencia queda resuelto y no vuelve a aparecer pendiente
        r = await self.client.get(self.prefix + "/emergencia-pendientes", params={"destino": "INTERCONSULTA"})
        self.assertEqual(r.json(), [])
        await self.post("/interconsultas/admitir-emergencia", {
            "destino_id": str(self.destino_interc_id), "especialidad_destino_id": str(self.espec),
            "motivo": "Duplicada"}, 409)

        # Aparece en el tablero global de Interconsultas de Hospitalizacion
        r = await self.client.get(self.prefix + "/interconsultas")
        self.assertEqual(r.status_code, 200, r.text)
        origenes = {i["origen"] for i in r.json()}
        self.assertIn("EMERGENCIA", origenes)

        # Y tambien en la cola de programacion de Consulta Externa/Admision,
        # lista para convertirse en una Cita real (mismo flujo que Consulta Externa)
        r = await self.client.get("/app/consulta-externa/interconsultas/pendientes")
        self.assertEqual(r.status_code, 200, r.text)
        pendientes_ce = [i for i in r.json() if i["id"] == interc["id"]]
        self.assertEqual(len(pendientes_ce), 1)
        self.assertEqual(pendientes_ce[0]["origen"], "EMERGENCIA")

    async def _paciente_dni(self, patient_id):
        async with self.session() as db:
            p = await db.get(Patient, patient_id)
            return p.dni

    async def test_hosp_tenant_isolation(self):
        hosp = await self.admitir()
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims | {"tenant_id": str(self.other_tenant), "empleado_id": str(uuid.uuid4())})
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.other_tenant, module_code="hospitalizacion")); await db.commit()
        r = await self.client.get(self.prefix+f"/hospitalizaciones/{hosp['id']}")
        self.assertEqual(r.status_code, 404)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(HospitalizacionTests(name) for name in HospitalizacionTests.__dict__ if name.startswith("test_hosp_"))
