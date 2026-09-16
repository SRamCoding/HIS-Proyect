"""Auditoría: pruebas HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_auditoria -v
"""
import unittest
import uuid
from datetime import datetime, timedelta
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.admin.auditoria.models import AuditLog
from app.core.security import create_access_token


class AuditoriaTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="auditoria"))
            self.otro_registro_id = str(uuid.uuid4())
            db.add(AuditLog(tenant_id=self.tenant_id, user_id=self.user_id, user_name="Operador de prueba",
                action="crear", model="Cobro", model_id=str(uuid.uuid4()),
                old_values=None, new_values={"monto": "35.50"}, created_at=datetime.utcnow() - timedelta(days=1)))
            db.add(AuditLog(tenant_id=self.tenant_id, user_id=self.user_id, user_name="Operador de prueba",
                action="anular", model="Cobro", model_id=self.otro_registro_id,
                old_values={"estado": "registrado"}, new_values={"estado": "anulado"}, created_at=datetime.utcnow()))
            db.add(AuditLog(tenant_id=self.tenant_id, user_id=self.user_id, user_name="Otro operador",
                action="crear", model="Hospitalizacion", model_id=str(uuid.uuid4()),
                new_values={"estado": "internado"}, created_at=datetime.utcnow()))
            db.add(AuditLog(tenant_id=self.other_tenant, user_id=self.user_id, user_name="De otro hospital",
                action="crear", model="Cobro", model_id=str(uuid.uuid4()), created_at=datetime.utcnow()))
            await db.commit()
        self.prefix = "/app/auditoria"

    async def test_aud_lista_filtra_por_modelo_accion_y_texto(self):
        r = await self.client.get(self.prefix + "/auditoria", params={"modelo": "Cobro"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["total"], 2)
        r = await self.client.get(self.prefix + "/auditoria", params={"accion": "anular"})
        self.assertEqual(r.json()["total"], 1)
        r = await self.client.get(self.prefix + "/auditoria", params={"q": self.otro_registro_id})
        self.assertEqual(r.json()["total"], 1)
        self.assertEqual(r.json()["items"][0]["model_id"], self.otro_registro_id)

    async def test_aud_detalle_muestra_antes_y_despues(self):
        r = await self.client.get(self.prefix + "/auditoria", params={"q": self.otro_registro_id})
        audit_id = r.json()["items"][0]["id"]
        r = await self.client.get(self.prefix + f"/auditoria/{audit_id}")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["old_values"]["estado"], "registrado")
        self.assertEqual(r.json()["new_values"]["estado"], "anulado")
        r = await self.client.get(self.prefix + f"/auditoria/{uuid.uuid4()}")
        self.assertEqual(r.status_code, 404)

    async def test_aud_resumen_agrega_por_modelo_y_accion(self):
        r = await self.client.get(self.prefix + "/auditoria-general/resumen")
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["total"], 3)
        modelos = {m["modelo"]: m["total"] for m in data["por_modelo"]}
        self.assertEqual(modelos.get("Cobro"), 2)
        self.assertEqual(modelos.get("Hospitalizacion"), 1)

    async def test_aud_catalogo_modelos_y_csv(self):
        r = await self.client.get(self.prefix + "/catalogos/modelos")
        self.assertEqual(sorted(r.json()), ["Cobro", "Hospitalizacion"])
        r = await self.client.get(self.prefix + "/reportes/auditoria.csv")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Cobro", r.text)

    async def test_aud_tenant_isolation(self):
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims | {"tenant_id": str(self.other_tenant)})
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.other_tenant, module_code="auditoria")); await db.commit()
        r = await self.client.get(self.prefix + "/auditoria")
        self.assertEqual(r.json()["total"], 1)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(AuditoriaTests(name) for name in AuditoriaTests.__dict__ if name.startswith("test_aud_"))
