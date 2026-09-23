"""Crear/editar/quitar logo y exposición pública en PostgreSQL aislado."""
import base64
import uuid
from io import BytesIO
from unittest.mock import AsyncMock, patch
from PIL import Image
from sqlalchemy import select
from app.admin.niveles_hospitalarios.models import HospitalLevel
from main import app
from app.core.dependencies import get_admin_user
from app.core.config import settings
from test_hc_pdf import HcPdfTests


def logo(color):
    output = BytesIO()
    Image.new("RGB", (200, 100), color).save(output, format="PNG")
    return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode()


class HospitalBrandingTests(HcPdfTests):
    async def test_branding_create_update_remove_and_public(self):
        # Usuario hospitalario no puede editar el logo de una institución.
        denied = await self.client.patch(f"/admin/hospitales/{self.tenant_id}", json={"logo_url": logo("red")})
        self.assertEqual(denied.status_code, 403)
        app.dependency_overrides[get_admin_user] = lambda: {"sub": str(self.user_id), "panel": "admin", "role": "administrador"}
        async with self.session() as db:
            level = await db.scalar(select(HospitalLevel).where(HospitalLevel.code == "II-1"))
            if not level:
                db.add(HospitalLevel(code="II-1", name="Nivel de prueba", is_active=True))
                await db.commit()
        payload = {"name": "Hospital de marca", "domain": f"marca-{uuid.uuid4().hex[:10]}.{settings.TENANT_BASE_DOMAIN}",
            "hospital_level": "II-1",
            "logo_url": logo("green"), "admin_name": "Admin", "admin_email": "app@marca.test", "admin_password": "Clave-Segura1",
            "sigarh_name": "RRHH", "sigarh_email": "sigarh@marca.test", "sigarh_password": "Otra-Clave2"}
        with patch("app.admin.hospitales.router._encolar_aprovisionamiento", new_callable=AsyncMock):
            created = await self.client.post("/admin/hospitales", json=payload)
        self.assertEqual(created.status_code, 201, created.text[:200])
        tid = created.json()["id"]
        first_logo = created.json()["logo_url"]
        self.assertTrue(first_logo.startswith("data:image/png;base64,"))
        public = await self.client.get(f"/auth/tenant-publico/{tid}")
        self.assertEqual(public.json()["logo_url"], first_logo)
        self.assertNotIn("database_name", public.json())
        detail = await self.client.get(f"/admin/hospitales/{tid}")
        self.assertEqual(detail.json()["logo_url"], first_logo)
        await self.client.patch(f"/admin/hospitales/{tid}", json={"name": "Hospital renombrado", "logo_url": logo("blue")})
        public = (await self.client.get(f"/auth/tenant-publico/{tid}")).json()
        self.assertEqual(public["name"], "Hospital renombrado")
        self.assertNotEqual(public["logo_url"], first_logo)
        # Una edición ajena al logo no lo borra.
        await self.client.patch(f"/admin/hospitales/{tid}", json={"phone": "123456"})
        self.assertEqual((await self.client.get(f"/auth/tenant-publico/{tid}")).json()["logo_url"], public["logo_url"])
        invalid = await self.client.patch(f"/admin/hospitales/{tid}", json={"logo_url": "data:image/svg+xml;base64,PHN2Zz4="})
        self.assertEqual(invalid.status_code, 422)
        await self.client.patch(f"/admin/hospitales/{tid}", json={"logo_url": None})
        self.assertIsNone((await self.client.get(f"/auth/tenant-publico/{tid}")).json()["logo_url"])
        # La resolución por dominio selecciona la misma institución.
        resolved = await self.client.get("/auth/resolver-dominio", params={"domain": payload["domain"]})
        self.assertEqual(resolved.json()["tenant_id"], tid)


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromTestCase(HospitalBrandingTests)
