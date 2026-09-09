"""Integración HTTP/PostgreSQL; todos los datos se revierten al terminar.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest discover -s tests -v
"""
import os
import unittest
import uuid
from datetime import date
from unittest.mock import patch

import httpx
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from main import app
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.hospital.admision.models import Patient, ClinicalRecord
from app.tenants.hospitales.models import Tenant, TenantModule


@unittest.skipUnless(os.getenv("RUN_ARCHIVO_DB_TESTS") == "1", "Requiere PostgreSQL explícito")
class ArchivoClinicoTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine(settings.DATABASE_URL, echo=False)
        self.connection = await self.engine.connect()
        self.transaction = await self.connection.begin()
        self.addAsyncCleanup(self.cleanup_database)
        self.tenant_id = uuid.uuid4()
        self.other_tenant = uuid.uuid4()
        self.record_id, self.other_record = uuid.uuid4(), uuid.uuid4()
        self.user_id = uuid.uuid4()
        async with self.session() as db:
            for tid in (self.tenant_id, self.other_tenant):
                db.add(Tenant(id=tid, name="TEST Archivo", domain=f"{tid}.test",
                              schema_name=f"test_{tid.hex}"))
            await db.flush()
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="archivo_clinico"))
            for tid, rid, name in ((self.tenant_id, self.record_id, "Ana"),
                                   (self.other_tenant, self.other_record, "Otra")):
                patient = Patient(id=uuid.uuid4(), tenant_id=tid, dni=rid.hex[:8],
                    first_name=name, second_name="María", last_name_paterno="Prueba",
                    last_name_materno="Archivo", birth_date=date(1990, 1, 1), gender="F")
                db.add(patient)
                await db.flush()
                db.add(ClinicalRecord(id=rid, patient_id=patient.id,
                    record_number=f"TEST-{rid.hex[:14]}", location="admision"))
            await db.commit()

        async def override_db():
            async with self.session() as db:
                try:
                    yield db
                    await db.commit()
                except Exception:
                    await db.rollback()
                    raise

        self.old_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_db] = override_db
        self.addCleanup(self.restore_overrides)
        self.session_patch = patch("app.core.database.AsyncSessionLocal", self.session)
        self.session_patch.start()
        self.addCleanup(self.session_patch.stop)
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")
        self.addAsyncCleanup(self.client.aclose)
        self.claims = {"sub": str(self.user_id), "name": "Operador de prueba", "panel": "app",
                       "tenant_id": str(self.tenant_id), "role": "archivo"}
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    def session(self):
        return AsyncSession(bind=self.connection, expire_on_commit=False,
                            join_transaction_mode="create_savepoint")

    def restore_overrides(self):
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.old_overrides)

    async def cleanup_database(self):
        await self.transaction.rollback()
        await self.connection.close()
        await self.engine.dispose()

    async def test_search_filters_pagination_and_isolation(self):
        response = await self.client.get("/app/archivo-clinico/historias",
            params={"q": "María Prueba", "is_digitized": "false", "location": "admi", "page_size": 1})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["id"], str(self.record_id))
        response = await self.client.get("/app/archivo-clinico/historias", params={"q": "%"})
        self.assertEqual(response.json()["total"], 0)
        response = await self.client.get("/app/archivo-clinico/historias", params={"page": 2, "page_size": 1})
        self.assertEqual(response.json()["items"], [])
        for params in ({"page": 0}, {"page_size": 101}):
            response = await self.client.get("/app/archivo-clinico/historias", params=params)
            self.assertEqual(response.status_code, 422)

    async def test_other_hospital_and_missing_record_are_not_exposed(self):
        for rid in (self.other_record, uuid.uuid4()):
            response = await self.client.get(f"/app/archivo-clinico/historias/{rid}/movimientos")
            self.assertEqual(response.status_code, 404, response.text)
            response = await self.client.patch(f"/app/archivo-clinico/historias/{rid}/digitalizar",
                                               json={"is_digitized": True})
            self.assertEqual(response.status_code, 404, response.text)
            response = await self.client.post("/app/admision/historia-clinica/mover",
                json={"clinical_record_id": str(rid), "to_location": "archivo"})
            self.assertEqual(response.status_code, 404, response.text)

    async def test_digitization_persists_both_states_and_validates(self):
        url = f"/app/archivo-clinico/historias/{self.record_id}/digitalizar"
        for state in (True, False):
            response = await self.client.patch(url, json={"is_digitized": state})
            self.assertEqual(response.status_code, 200, response.text)
            response = await self.client.get("/app/archivo-clinico/historias",
                                             params={"is_digitized": str(state).lower()})
            self.assertEqual(response.json()["total"], 1)
        for body in ({}, {"is_digitized": ""}, {"is_digitized": "false"},
                     {"is_digitized": None}, {"is_digitized": True, "tenant_id": str(self.other_tenant)}):
            response = await self.client.patch(url, json=body)
            self.assertEqual(response.status_code, 422, response.text)

    async def test_archive_only_user_moves_and_actor_cannot_be_spoofed(self):
        url = "/app/admision/historia-clinica/mover"
        for destination in (" archivo ", "consultorio"):
            response = await self.client.post(url, json={"clinical_record_id": str(self.record_id),
                "to_location": destination, "moved_by": "Impostor", "notes": "  "})
            self.assertEqual(response.status_code, 200, response.text)
        response = await self.client.get(f"/app/archivo-clinico/historias/{self.record_id}/movimientos")
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["historia"]["location"], "consultorio")
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["items"][0]["from_location"], "archivo")
        self.assertEqual(result["items"][1]["from_location"], "admision")
        self.assertIn(str(self.user_id), result["items"][0]["moved_by"])
        self.assertNotIn("Impostor", result["items"][0]["moved_by"])
        self.assertIsNone(result["items"][0]["notes"])

    async def test_empty_and_same_location_do_not_create_movements(self):
        url = "/app/admision/historia-clinica/mover"
        for destination, expected in (("   ", 422), ("x" * 51, 422), ("ADMISION", 409)):
            response = await self.client.post(url, json={"clinical_record_id": str(self.record_id),
                                                       "to_location": destination})
            self.assertEqual(response.status_code, expected, response.text)
        response = await self.client.get(f"/app/archivo-clinico/historias/{self.record_id}/movimientos")
        self.assertEqual(response.json()["total"], 0)

    async def test_management_module_can_still_move(self):
        async with self.session() as db:
            await db.execute(update(TenantModule).where(TenantModule.tenant_id == self.tenant_id)
                             .values(module_code="admision"))
            await db.commit()
        response = await self.client.post("/app/admision/historia-clinica/mover",
            json={"clinical_record_id": str(self.record_id), "to_location": "archivo"})
        self.assertEqual(response.status_code, 200, response.text)
        response = await self.client.get("/app/archivo-clinico/historias")
        self.assertEqual(response.status_code, 403)

    async def test_disabled_module_and_hospital_are_denied(self):
        async with self.session() as db:
            await db.execute(update(TenantModule).where(TenantModule.tenant_id == self.tenant_id)
                             .values(is_active=False))
            await db.commit()
        response = await self.client.get("/app/archivo-clinico/historias")
        self.assertEqual(response.status_code, 403)
        async with self.session() as db:
            await db.execute(update(TenantModule).where(TenantModule.tenant_id == self.tenant_id)
                             .values(is_active=True))
            await db.execute(update(Tenant).where(Tenant.id == self.tenant_id).values(is_active=False))
            await db.commit()
        response = await self.client.get("/app/archivo-clinico/historias")
        self.assertEqual(response.status_code, 403)

    async def test_refresh_tokens_panel_and_header_cannot_authorize(self):
        url = "/app/archivo-clinico/historias"
        self.client.headers["Authorization"] = "Bearer " + create_refresh_token(self.claims)
        self.assertEqual((await self.client.get(url)).status_code, 401)
        for changes in ({"panel": "admin"}, {"tenant_id": None}, {"tenant_id": "invalid"}):
            self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims | changes)
            response = await self.client.get(url, headers={"X-Tenant-ID": str(self.tenant_id)})
            self.assertEqual(response.status_code, 403, response.text)
        self.client.headers.pop("Authorization")
        self.assertIn((await self.client.get(url)).status_code, (401, 403))
