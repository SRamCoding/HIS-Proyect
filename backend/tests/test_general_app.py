"""General (panel app): pruebas HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_general_app -v
"""
import unittest
import uuid
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.sigarh.mantenimiento.models import Servicio, Departamento
from app.sigarh.general.models import DiagnosticoCIE10, Paquete, PaqueteItem
from app.sigarh.config_farmacia.models import Medicamento
from app.core.security import create_access_token


class GeneralAppTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="general"))
            self.dep_id = uuid.uuid4()
            self.serv_id = uuid.uuid4()
            self.dx_id = uuid.uuid4()
            self.paquete_id = uuid.uuid4()
            self.med_id = uuid.uuid4()
            db.add(Departamento(id=self.dep_id, tenant_id=self.tenant_id, codigo="DEP-TEST", nombre="Departamento de prueba"))
            db.add(Servicio(id=self.serv_id, tenant_id=self.tenant_id, departamento_id=self.dep_id,
                nombre="Servicio de prueba", codigo="SRV-TEST"))
            db.add(DiagnosticoCIE10(id=self.dx_id, tenant_id=self.tenant_id, codigo_cie10="J00",
                descripcion="Rinofaringitis aguda", capitulo="Enfermedades respiratorias"))
            db.add(Medicamento(id=self.med_id, tenant_id=self.tenant_id, codigo_interno="MED-TEST",
                nombre_comercial="Paracetamol 500mg", nombre_generico="Paracetamol"))
            db.add(Paquete(id=self.paquete_id, tenant_id=self.tenant_id, nombre="Paquete de prueba", codigo="PAQ-TEST"))
            await db.flush()
            db.add(PaqueteItem(paquete_id=self.paquete_id, medicamento_id=self.med_id, cantidad=2))
            # Registro de otro hospital: no debe filtrarse en las búsquedas de este tenant.
            db.add(DiagnosticoCIE10(tenant_id=self.other_tenant, codigo_cie10="Z99", descripcion="Otro hospital"))
            await db.commit()
        self.prefix = "/app/general"
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def test_gen_servicios_busqueda_y_detalle(self):
        r = await self.client.get(self.prefix + "/servicios", params={"q": "prueba"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["total"], 1)
        self.assertEqual(r.json()["items"][0]["departamento_nombre"], "Departamento de prueba")
        r = await self.client.get(self.prefix + f"/servicios/{self.serv_id}")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["codigo"], "SRV-TEST")
        r = await self.client.get(self.prefix + f"/servicios/{uuid.uuid4()}")
        self.assertEqual(r.status_code, 404)

    async def test_gen_diagnosticos_busqueda_capitulo_y_aislamiento(self):
        r = await self.client.get(self.prefix + "/diagnosticos", params={"q": "J00"})
        self.assertEqual(r.json()["total"], 1)
        self.assertEqual(r.json()["items"][0]["descripcion"], "Rinofaringitis aguda")
        r = await self.client.get(self.prefix + "/diagnosticos/capitulos")
        self.assertEqual(r.json(), ["Enfermedades respiratorias"])
        r = await self.client.get(self.prefix + "/diagnosticos", params={"capitulo": "Enfermedades respiratorias"})
        self.assertEqual(r.json()["total"], 1)
        r = await self.client.get(self.prefix + "/diagnosticos", params={"q": "Z99"})
        self.assertEqual(r.json()["total"], 0)

    async def test_gen_paquetes_detalle_con_items(self):
        r = await self.client.get(self.prefix + "/paquetes")
        self.assertEqual(r.json()["total"], 1)
        r = await self.client.get(self.prefix + f"/paquetes/{self.paquete_id}")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(len(r.json()["items"]), 1)
        self.assertEqual(r.json()["items"][0]["medicamento_nombre"], "Paracetamol 500mg")
        self.assertEqual(r.json()["items"][0]["cantidad"], 2)

    async def test_gen_tenant_isolation(self):
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims | {"tenant_id": str(self.other_tenant)})
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.other_tenant, module_code="general")); await db.commit()
        r = await self.client.get(self.prefix + f"/servicios/{self.serv_id}")
        self.assertEqual(r.status_code, 404)
        r = await self.client.get(self.prefix + "/diagnosticos")
        self.assertEqual(r.json()["total"], 1)  # solo ve el Z99 de su propio hospital


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(GeneralAppTests(name) for name in GeneralAppTests.__dict__ if name.startswith("test_gen_"))
