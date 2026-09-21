import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.auth.router import _revocar_sesion_actual, _log_audit_seguro, logout

TENANT = "55540838-24a6-4e78-843b-f9b93e57733a"
UID = "11111111-1111-1111-1111-111111111111"


def _ctx(db):
    """Envuelve un mock de sesion en un context manager async, como el que
    devuelve AsyncSessionLocal()/get_tenant_sessionmaker()()."""
    context = AsyncMock()
    context.__aenter__.return_value = db
    return context


class RevocarSesionActualTests(unittest.IsolatedAsyncioTestCase):
    """_revocar_sesion_actual reemplazo a _cuenta_localizada para logout:
    va directo a la cuenta usando panel/tenant_id/auth_source del propio
    JWT en vez de recorrer todos los hospitales."""

    async def test_admin_confirma_revocacion_con_update_atomico(self):
        db = AsyncMock()
        db.execute.return_value = SimpleNamespace(rowcount=1)
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            ok = await _revocar_sesion_actual({"sub": UID, "panel": "admin"})
        self.assertTrue(ok)
        db.commit.assert_awaited_once()

    async def test_admin_sin_fila_afectada_devuelve_false(self):
        db = AsyncMock()
        db.execute.return_value = SimpleNamespace(rowcount=0)
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            ok = await _revocar_sesion_actual({"sub": UID, "panel": "admin"})
        self.assertFalse(ok)

    async def test_sub_invalido_devuelve_false_sin_tocar_la_bd(self):
        ok = await _revocar_sesion_actual({"sub": "no-es-un-uuid", "panel": "admin"})
        self.assertFalse(ok)

    async def test_hospital_no_encontrado_devuelve_false(self):
        central_db = AsyncMock()
        central_db.get.return_value = None
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(central_db)):
            ok = await _revocar_sesion_actual({"sub": UID, "panel": "sigarh", "tenant_id": TENANT})
        self.assertFalse(ok)

    async def test_cuenta_sigarh_se_revoca_en_bd_fisica_del_hospital(self):
        hospital = SimpleNamespace(database_name="his_hospital_reque")
        central_db = AsyncMock()
        central_db.get.return_value = hospital

        tenant_db = AsyncMock()
        tenant_db.execute.return_value = SimpleNamespace(rowcount=1)

        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(central_db)), \
             patch("app.core.tenant_db.get_tenant_sessionmaker", return_value=MagicMock(return_value=_ctx(tenant_db))):
            ok = await _revocar_sesion_actual({
                "sub": UID, "panel": "sigarh", "tenant_id": TENANT, "auth_source": "sigarh",
            })
        self.assertTrue(ok)
        tenant_db.commit.assert_awaited_once()


class LogAuditSeguroTests(unittest.IsolatedAsyncioTestCase):
    """El registro de auditoria del logout va en su propia sesion y nunca
    debe propagar sus propios errores -- si lo hiciera, un fallo al
    escribir el evento tapa la causa real y, peor, puede convertir una
    revocacion ya confirmada en un error de la peticion."""

    async def test_no_propaga_si_falla_el_commit(self):
        audit_db = AsyncMock()
        audit_db.add = MagicMock()  # db.add() es sincrono en SQLAlchemy real
        audit_db.commit.side_effect = RuntimeError("la bd de auditoria no responde")
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(audit_db)), \
             patch("app.core.audit.guardar_evento_en_fallback", AsyncMock()):
            await _log_audit_seguro(UID, "Nombre", None, "logout", model="User",
                                    description="x", ip_address=None)
        # No haber lanzado ya es la prueba.

    async def test_si_falla_el_registro_directo_cae_al_fallback(self):
        audit_db = AsyncMock()
        audit_db.add = MagicMock()
        audit_db.commit.side_effect = RuntimeError("la bd de auditoria no responde")
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(audit_db)), \
             patch("app.core.audit.guardar_evento_en_fallback", AsyncMock()) as fallback_mock:
            await _log_audit_seguro(UID, "Nombre", None, "logout_fallido", model="User",
                                    description="no se pudo revocar", ip_address="127.0.0.1")
        fallback_mock.assert_awaited_once()
        entrada, actor, ip = fallback_mock.await_args.args
        self.assertEqual(entrada["action"], "logout_fallido")
        self.assertEqual(actor["user_name"], "Nombre")
        self.assertEqual(ip, "127.0.0.1")


class LogoutEndpointTests(unittest.IsolatedAsyncioTestCase):
    """logout() debe fallar en voz alta si no puede confirmar la
    revocacion, y nunca debe depender de que la auditoria tambien
    funcione para responder exito."""

    def _request(self):
        return SimpleNamespace(client=SimpleNamespace(host="127.0.0.1"))

    def _response(self):
        # logout() ahora tambien limpia las cookies httpOnly de sesion via
        # response.delete_cookie(...) -- un MagicMock simplemente absorbe
        # esas llamadas sin necesitar una Response real de FastAPI.
        return MagicMock()

    async def test_responde_500_si_la_revocacion_no_se_pudo_confirmar(self):
        user = {"sub": UID, "panel": "admin", "name": "Admin"}
        with patch("app.auth.router._revocar_sesion_actual", AsyncMock(return_value=False)), \
             patch("app.auth.router._log_audit_seguro", AsyncMock()) as log_mock:
            with self.assertRaises(HTTPException) as err:
                await logout(self._request(), self._response(), user)
        self.assertEqual(err.exception.status_code, 500)
        log_mock.assert_awaited_once()
        self.assertEqual(log_mock.await_args.args[3], "logout_fallido")

    async def test_responde_500_si_la_revocacion_lanza_excepcion(self):
        user = {"sub": UID, "panel": "admin", "name": "Admin"}
        with patch("app.auth.router._revocar_sesion_actual", AsyncMock(side_effect=RuntimeError("bd caida"))), \
             patch("app.auth.router._log_audit_seguro", AsyncMock()):
            with self.assertRaises(HTTPException) as err:
                await logout(self._request(), self._response(), user)
        self.assertEqual(err.exception.status_code, 500)

    async def test_responde_ok_cuando_la_revocacion_se_confirma(self):
        user = {"sub": UID, "panel": "admin", "name": "Admin"}
        with patch("app.auth.router._revocar_sesion_actual", AsyncMock(return_value=True)), \
             patch("app.auth.router._log_audit_seguro", AsyncMock()) as log_mock:
            result = await logout(self._request(), self._response(), user)
        self.assertEqual(result, {"ok": True})
        self.assertEqual(log_mock.await_args.args[3], "logout")

    async def test_responde_ok_aunque_falle_la_escritura_de_auditoria(self):
        """Revocacion confirmada + auditoria caida = igual {"ok": True}.
        Antes, reusar la sesion de la revocacion para el intento de
        auditoria podia convertir esto en un 500 enganoso."""
        user = {"sub": UID, "panel": "admin", "name": "Admin"}
        audit_db = AsyncMock()
        audit_db.add = MagicMock()  # db.add() es sincrono en SQLAlchemy real
        audit_db.commit.side_effect = RuntimeError("la bd de auditoria no responde")
        with patch("app.auth.router._revocar_sesion_actual", AsyncMock(return_value=True)), \
             patch("app.core.database.AsyncSessionLocal", return_value=_ctx(audit_db)), \
             patch("app.core.audit.guardar_evento_en_fallback", AsyncMock()):
            result = await logout(self._request(), self._response(), user)
        self.assertEqual(result, {"ok": True})


if __name__ == "__main__":
    unittest.main()
