"""Fact-Config (panel app): pruebas HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_fact_config -v
"""
import unittest
import uuid
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.sigarh.config_farmacia.models import Medicamento
from app.sigarh.infraestructura.models import Catalogo
from app.sigarh.config_financiera.models import Tarifario, Seguro
from app.sigarh.rrhh.models import Especialidad
from app.core.security import create_access_token


class FactConfigTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="fact_config"))
            self.tipo_id = uuid.uuid4()
            self.med_id = uuid.uuid4()
            self.espec_id = uuid.uuid4()
            self.seguro_id = uuid.uuid4()
            self.tarifa_id = uuid.uuid4()
            db.add(Catalogo(id=self.tipo_id, tenant_id=self.tenant_id, categoria="tipos_producto", nombre="Medicamento"))
            db.add(Especialidad(id=self.espec_id, tenant_id=self.tenant_id, nombre="Medicina Interna"))
            db.add(Seguro(id=self.seguro_id, tenant_id=self.tenant_id, codigo="SIS", nombre="SIS - Seguro Integral de Salud"))
            await db.flush()
            db.add(Medicamento(id=self.med_id, tenant_id=self.tenant_id, tipo_producto_id=self.tipo_id,
                codigo_interno="MED-FC", nombre_comercial="Amoxicilina 500mg", nombre_generico="Amoxicilina",
                dci="Amoxicilina", precio_referencia=12.5))
            db.add(Tarifario(id=self.tarifa_id, tenant_id=self.tenant_id, descripcion_servicio="Consulta general",
                tipo_servicio="CONSULTA_EXTERNA", especialidad_id=self.espec_id, seguro_id=self.seguro_id, precio=35.0))
            await db.commit()
        self.prefix = "/app/fact-config"
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def test_fc_bienes_busqueda_tipo_y_detalle(self):
        r = await self.client.get(self.prefix + "/bienes-insumos", params={"q": "amoxicilina"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["total"], 1)
        self.assertEqual(r.json()["items"][0]["tipo_producto_nombre"], "Medicamento")
        r = await self.client.get(self.prefix + "/catalogos/tipos-producto")
        self.assertEqual(r.json(), [{"id": str(self.tipo_id), "nombre": "Medicamento"}])
        r = await self.client.get(self.prefix + "/bienes-insumos", params={"tipo_id": str(self.tipo_id)})
        self.assertEqual(r.json()["total"], 1)
        r = await self.client.get(self.prefix + f"/bienes-insumos/{self.med_id}")
        self.assertEqual(r.json()["nombre_comercial"], "Amoxicilina 500mg")
        r = await self.client.get(self.prefix + f"/bienes-insumos/{uuid.uuid4()}")
        self.assertEqual(r.status_code, 404)

    async def test_fc_servicios_busqueda_tipo_y_detalle(self):
        r = await self.client.get(self.prefix + "/servicios", params={"q": "consulta"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["total"], 1)
        item = r.json()["items"][0]
        self.assertEqual(item["especialidad_nombre"], "Medicina Interna")
        self.assertEqual(item["seguro_nombre"], "SIS - Seguro Integral de Salud")
        r = await self.client.get(self.prefix + "/servicios", params={"tipo_servicio": "EMERGENCIA"})
        self.assertEqual(r.json()["total"], 0)
        r = await self.client.get(self.prefix + f"/servicios/{self.tarifa_id}")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(str(r.json()["precio"]), "35.0")

    async def test_fc_tenant_isolation(self):
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims | {"tenant_id": str(self.other_tenant)})
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.other_tenant, module_code="fact_config")); await db.commit()
        r = await self.client.get(self.prefix + f"/bienes-insumos/{self.med_id}")
        self.assertEqual(r.status_code, 404)
        r = await self.client.get(self.prefix + "/servicios")
        self.assertEqual(r.json()["total"], 0)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(FactConfigTests(name) for name in FactConfigTests.__dict__ if name.startswith("test_fc_"))
