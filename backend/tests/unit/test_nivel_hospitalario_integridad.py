import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from app.admin.niveles_hospitalarios.service import create_hospital_level, update_hospital_level
from app.admin.hospitales.router import actualizar_hospital
from app.tenants.hospitales.schemas import TenantUpdate

NIVEL_ID = uuid.uuid4()
TENANT_ID = uuid.uuid4()


class CrearNivelCodigoDuplicadoTests(unittest.IsolatedAsyncioTestCase):
    """code es unique a nivel de columna: sin un chequeo explicito, un
    duplicado revienta como IntegrityError sin controlar (500) en vez de
    un 409 legible."""

    async def test_rechaza_codigo_duplicado_con_409(self):
        db = AsyncMock()
        db.scalar.return_value = NIVEL_ID  # ya existe un nivel con ese code
        data = SimpleNamespace(code="II-1", name="x", description=None, color=None,
                               default_modules={}, default_roles={}, sort_order=0, is_active=True)
        with self.assertRaises(HTTPException) as err:
            await create_hospital_level(db, data, {})
        self.assertEqual(err.exception.status_code, 409)
        db.add.assert_not_called()

    async def test_permite_codigo_nuevo(self):
        db = AsyncMock()
        db.scalar.return_value = None
        db.add = MagicMock()
        data = SimpleNamespace(code="II-1", name="x", description=None, color=None,
                               default_modules={}, default_roles={}, sort_order=0, is_active=True)
        await create_hospital_level(db, data, {})
        db.add.assert_called_once()
        db.commit.assert_awaited_once()


class CambiarCodigoDeNivelTests(unittest.IsolatedAsyncioTestCase):
    """Tenant.hospital_level guarda el codigo como texto libre (no una FK):
    cambiar el codigo de un nivel que hospitales ya usan los deja
    apuntando a un codigo huerfano, sin ningun error visible."""

    def _nivel(self, code="II-1"):
        return SimpleNamespace(id=NIVEL_ID, code=code, name="Nivel II-1")

    async def test_bloquea_el_cambio_de_codigo_si_esta_en_uso(self):
        db = AsyncMock()
        db.scalar.return_value = 3  # 3 hospitales usan el codigo actual
        with patch("app.admin.niveles_hospitalarios.service.get_hospital_level_by_id", AsyncMock(return_value=self._nivel())):
            data = SimpleNamespace(model_dump=lambda exclude_unset: {"code": "II-2"})
            with self.assertRaises(HTTPException) as err:
                await update_hospital_level(db, NIVEL_ID, data, {})
        self.assertEqual(err.exception.status_code, 409)

    async def test_permite_el_cambio_de_codigo_si_no_esta_en_uso(self):
        nivel = self._nivel()
        db = AsyncMock()
        db.scalar.return_value = 0
        with patch("app.admin.niveles_hospitalarios.service.get_hospital_level_by_id", AsyncMock(return_value=nivel)):
            data = SimpleNamespace(model_dump=lambda exclude_unset: {"code": "II-2"})
            resultado = await update_hospital_level(db, NIVEL_ID, data, {})
        self.assertEqual(resultado.code, "II-2")

    async def test_no_valida_nada_si_el_codigo_no_cambia(self):
        nivel = self._nivel()
        db = AsyncMock()
        with patch("app.admin.niveles_hospitalarios.service.get_hospital_level_by_id", AsyncMock(return_value=nivel)):
            data = SimpleNamespace(model_dump=lambda exclude_unset: {"code": "II-1", "name": "Nuevo nombre"})
            await update_hospital_level(db, NIVEL_ID, data, {})
        db.scalar.assert_not_called()


class ActualizarHospitalNivelTests(unittest.IsolatedAsyncioTestCase):
    """Editar un hospital debe validar el nivel igual que crearlo -- antes
    solo se comprobaba al crear, y editar aceptaba cualquier codigo."""

    async def _run(self, db, hospital_level):
        data = TenantUpdate(name="Hospital X", hospital_level=hospital_level)
        return await actualizar_hospital(TENANT_ID, data, db=db, current_user={})

    async def test_rechaza_nivel_inexistente_o_inactivo(self):
        db = AsyncMock()
        db.execute.return_value = SimpleNamespace(scalar_one_or_none=lambda: SimpleNamespace(id=TENANT_ID))
        db.scalar.return_value = None  # el nivel no existe o esta inactivo
        with self.assertRaises(HTTPException) as err:
            await self._run(db, "IV-9")
        self.assertEqual(err.exception.status_code, 422)

    async def test_acepta_nivel_valido_y_activo(self):
        tenant = SimpleNamespace(id=TENANT_ID)
        db = AsyncMock()
        db.execute.return_value = SimpleNamespace(scalar_one_or_none=lambda: tenant)
        db.scalar.return_value = NIVEL_ID
        resultado = await self._run(db, "II-1")
        self.assertEqual(resultado, {"ok": True})
        self.assertEqual(tenant.hospital_level, "II-1")


if __name__ == "__main__":
    unittest.main()
