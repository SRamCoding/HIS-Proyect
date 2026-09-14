import unittest
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace
from fastapi import HTTPException
from app.sigarh.mantenimiento.router import autorizar

class MaintenancePermissionTests(unittest.IsolatedAsyncioTestCase):
    async def test_department_permission_cannot_edit_professions(self):
        central = AsyncMock()
        central.scalar.return_value = True
        context = AsyncMock()
        context.__aenter__.return_value = central
        user = {"tenant_id": "55540838-24a6-4e78-843b-f9b93e57733a", "panel": "sigarh",
                "active_modules": ["sigarh_mantenimiento.departamentos"], "permisos_accion": ["administrar_mantenimiento"]}
        with patch("app.core.database.AsyncSessionLocal", return_value=context):
            with self.assertRaises(HTTPException) as error:
                await autorizar(SimpleNamespace(headers={}), None, user, "profesiones", True)
            self.assertEqual(error.exception.status_code, 403)

    async def test_full_module_preserves_existing_admin_access(self):
        central = AsyncMock()
        central.scalar.return_value = True
        context = AsyncMock()
        context.__aenter__.return_value = central
        user = {"tenant_id": "55540838-24a6-4e78-843b-f9b93e57733a", "panel": "sigarh",
                "active_modules": ["sigarh_mantenimiento"], "permisos_accion": ["administrar_mantenimiento"]}
        with patch("app.core.database.AsyncSessionLocal", return_value=context):
            await autorizar(SimpleNamespace(headers={}), None, user, "profesiones", True)
