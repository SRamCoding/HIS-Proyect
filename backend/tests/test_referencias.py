"""Referencias: pruebas HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_referencias -v
"""
import unittest
import uuid
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import ClinicalRecord
from app.hospital.emergencia.models import AdmisionEmergencia, AtencionEmergencia, DestinoEmergencia
from app.sigarh.general.models import DiagnosticoCIE10
from app.core.security import create_access_token


class ReferenciasTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="referencias"))
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="emergencia"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))
            self.dx = uuid.uuid4()
            db.add(DiagnosticoCIE10(id=self.dx, tenant_id=self.tenant_id, codigo_cie10="A00", descripcion="Diagnóstico de prueba"))

            self.admision_id = uuid.uuid4()
            self.atencion_emerg_id = uuid.uuid4()
            self.destino_id = uuid.uuid4()
            db.add(AdmisionEmergencia(id=self.admision_id, tenant_id=self.tenant_id, patient_id=self.pid,
                numero_cuenta="EMG-REF-1", servicio_emergencia="Emergencia General", estado="derivado"))
            db.add(AtencionEmergencia(id=self.atencion_emerg_id, tenant_id=self.tenant_id, admision_id=self.admision_id,
                motivo_consulta="Requiere especialista", destino_atencion="REFERENCIA", estado="firmado"))
            db.add(DestinoEmergencia(id=self.destino_id, tenant_id=self.tenant_id, atencion_id=self.atencion_emerg_id,
                destino="REFERENCIA", estado="pendiente"))
            await db.commit()
        self.prefix = "/app/referencias"
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def post(self, path, data, status=201):
        r = await self.client.post(self.prefix+path, json=data)
        self.assertEqual(r.status_code, status, r.text)
        return r.json()

    async def admitir(self, **overrides):
        body = {"destino_id": str(self.destino_id), "nombre_ipress_destino": "Hospital Regional de Prueba",
            "especialidad_destino": "Cardiología", "diagnostico_id": str(self.dx), "motivo": "Evaluación especializada"}
        body.update(overrides)
        return await self.post("/referencias/admitir-emergencia", body)

    async def test_ref_admitir_desde_emergencia_resuelve_destino(self):
        ref = await self.admitir()
        self.assertEqual(ref["estado"], "enviada")
        self.assertEqual(ref["origen"], "EMERGENCIA")
        self.assertEqual(ref["destino_tipo"], "EXTERNO")
        r = await self.client.get(self.prefix+"/emergencia-pendientes")
        self.assertEqual(r.json(), [])
        await self.post("/referencias/admitir-emergencia", {"destino_id": str(self.destino_id), "motivo": "x"}, 409)

    async def test_ref_sin_destino_rechaza(self):
        await self.post("/referencias/admitir-emergencia", {"destino_id": str(self.destino_id), "motivo": "x"}, 422)

    async def test_ref_resolver_y_contrarreferencia(self):
        ref = await self.admitir()
        r = await self.client.post(self.prefix+f"/referencias/{ref['id']}/resolver", json={"estado": "aceptada", "observacion_resolucion": "Cupo confirmado"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "aceptada")
        await self.client.post(self.prefix+f"/referencias/{ref['id']}/resolver", json={"estado": "rechazada"})
        r = await self.client.post(self.prefix+f"/referencias/{ref['id']}/contrarreferencia", json={
            "fecha_contrarreferencia": "2030-01-01", "profesional_receptor": "Dr. Receptor",
            "resumen_contrarreferencia": "Paciente evaluado y estable, continuar manejo ambulatorio", "diagnostico_contrarreferencia_id": str(self.dx)})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "contrarreferida")
        r = await self.client.get(self.prefix+f"/referencias/{ref['id']}/comprobante.pdf")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.content.startswith(b"%PDF"))
        r = await self.client.post(self.prefix+f"/referencias/{ref['id']}/contrarreferencia", json={
            "fecha_contrarreferencia": "2030-01-01", "profesional_receptor": "x", "resumen_contrarreferencia": "x"})
        self.assertEqual(r.status_code, 409)

    async def test_ref_rechazada_bloquea_contrarreferencia(self):
        ref = await self.admitir()
        await self.client.post(self.prefix+f"/referencias/{ref['id']}/resolver", json={"estado": "rechazada", "observacion_resolucion": "Sin cupo"})
        r = await self.client.post(self.prefix+f"/referencias/{ref['id']}/contrarreferencia", json={
            "fecha_contrarreferencia": "2030-01-01", "profesional_receptor": "x", "resumen_contrarreferencia": "x"})
        self.assertEqual(r.status_code, 409)

    async def test_ref_listado_y_csv(self):
        await self.admitir()
        r = await self.client.get(self.prefix+"/referencias", params={"estado": "enviada"})
        self.assertEqual(r.json()["total"], 1)
        r = await self.client.get(self.prefix+"/reportes/referencias.csv")
        self.assertEqual(r.status_code, 200)

    async def test_ref_tenant_isolation(self):
        ref = await self.admitir()
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims | {"tenant_id": str(self.other_tenant)})
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.other_tenant, module_code="referencias")); await db.commit()
        r = await self.client.get(self.prefix+f"/referencias/{ref['id']}")
        self.assertEqual(r.status_code, 404)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(ReferenciasTests(name) for name in ReferenciasTests.__dict__ if name.startswith("test_ref_"))
