import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from starlette.requests import Request
from fastapi import HTTPException
from app.core.database import _bd_fisica_sigarh

TENANT = "55540838-24a6-4e78-843b-f9b93e57733a"
OTHER = "80f3d4ad-248f-47db-9a5f-3cb5ac09cd32"

class HospitalRoutingTests(unittest.IsolatedAsyncioTestCase):
    def request(self):
        return Request({"type": "http", "path": "/app/admision/pacientes", "headers": [(b"authorization", b"Bearer token"), (b"x-tenant-id", OTHER.encode())]})

    async def test_hospital_uses_signed_tenant_despite_header(self):
        db = AsyncMock()
        db.get.return_value = SimpleNamespace(database_name="his_hospital_reque", is_active=True)
        context = AsyncMock()
        context.__aenter__.return_value = db
        with patch("app.core.security.verify_token", return_value={"type": "access", "panel": "app", "tenant_id": TENANT}), patch("app.core.database.AsyncSessionLocal", return_value=context):
            self.assertEqual(await _bd_fisica_sigarh(self.request()), "his_hospital_reque")
        self.assertEqual(str(db.get.call_args.args[1]), TENANT)

    async def test_refresh_token_cannot_resolve_business_database(self):
        with patch("app.core.security.verify_token", return_value={"type": "refresh", "tenant_id": TENANT}):
            with self.assertRaises(HTTPException) as error:
                await _bd_fisica_sigarh(self.request())
            self.assertEqual(error.exception.status_code, 401)

    async def test_user_without_hospital_cannot_select_header(self):
        with patch("app.core.security.verify_token", return_value={"type": "access", "panel": "sigarh"}):
            with self.assertRaises(HTTPException) as error:
                await _bd_fisica_sigarh(self.request())
            self.assertEqual(error.exception.status_code, 403)
