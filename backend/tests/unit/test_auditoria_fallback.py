import json
import unittest
import uuid
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.exc import IntegrityError

import app.core.audit as audit


def _ctx(db):
    context = AsyncMock()
    context.__aenter__.return_value = db
    return context


class MigrarEmergenciaATablaTests(unittest.IsolatedAsyncioTestCase):
    """Los eventos que cayeron al archivo de emergencia (BD central
    totalmente inalcanzable en su momento) antes quedaban atrapados ahi
    para siempre -- el reintento normal solo miraba la tabla."""

    def setUp(self):
        self._ruta_original = audit._FALLBACK_ARCHIVO_ULTIMO_RECURSO
        self._ruta_temp = Path(self._ruta_original).parent / "audit_fallback_emergencia_test.jsonl"
        audit._FALLBACK_ARCHIVO_ULTIMO_RECURSO = self._ruta_temp
        if self._ruta_temp.exists():
            self._ruta_temp.unlink()

    def tearDown(self):
        if self._ruta_temp.exists():
            self._ruta_temp.unlink()
        audit._FALLBACK_ARCHIVO_ULTIMO_RECURSO = self._ruta_original

    async def test_sin_archivo_no_hace_nada(self):
        self.assertEqual(await audit._migrar_emergencia_a_tabla(), 0)

    async def test_migra_cada_linea_a_la_tabla_y_vacia_el_archivo(self):
        registro = {
            "action": "logout", "model": "User", "model_id": None,
            "old_values": None, "new_values": None, "tenant_hint": None, "db_name_hint": None,
            "_actor": {"user_id": None, "user_name": "Admin", "tenant_id": None},
            "_ip_address": "127.0.0.1", "_ocurrido_en": datetime.utcnow().isoformat(),
        }
        self._ruta_temp.parent.mkdir(parents=True, exist_ok=True)
        with open(self._ruta_temp, "w", encoding="utf-8") as f:
            f.write(json.dumps(registro) + "\n")

        db = AsyncMock()
        db.add = MagicMock()
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            migrados = await audit._migrar_emergencia_a_tabla()

        self.assertEqual(migrados, 1)
        self.assertFalse(self._ruta_temp.exists())
        fila_creada = db.add.call_args.args[0]
        self.assertEqual(fila_creada.actor["user_name"], "Admin")

    async def test_si_la_bd_sigue_caida_conserva_el_archivo(self):
        registro = {
            "action": "logout", "model": "User", "model_id": None,
            "old_values": None, "new_values": None, "tenant_hint": None, "db_name_hint": None,
            "_actor": {}, "_ip_address": None, "_ocurrido_en": datetime.utcnow().isoformat(),
        }
        self._ruta_temp.parent.mkdir(parents=True, exist_ok=True)
        with open(self._ruta_temp, "w", encoding="utf-8") as f:
            f.write(json.dumps(registro) + "\n")

        db = AsyncMock()
        db.add = MagicMock()
        db.commit.side_effect = RuntimeError("sigue caida")
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            migrados = await audit._migrar_emergencia_a_tabla()

        self.assertEqual(migrados, 0)
        self.assertTrue(self._ruta_temp.exists())

    async def test_id_repetido_se_trata_como_ya_migrado_no_como_error(self):
        # Si el proceso murio entre insertar y reescribir el archivo en una
        # corrida anterior, la linea sigue en el archivo pero YA esta en la
        # tabla -- el mismo _id vuelve a intentarse, choca por clave
        # primaria, y eso debe contar como migrado (se descarta del
        # archivo), no como un fallo que la deja pendiente para siempre.
        id_fijo = str(uuid.uuid4())
        registro = {
            "action": "logout", "model": "User", "model_id": None,
            "old_values": None, "new_values": None, "tenant_hint": None, "db_name_hint": None,
            "_id": id_fijo, "_actor": {}, "_ip_address": None, "_ocurrido_en": datetime.utcnow().isoformat(),
        }
        self._ruta_temp.parent.mkdir(parents=True, exist_ok=True)
        with open(self._ruta_temp, "w", encoding="utf-8") as f:
            f.write(json.dumps(registro) + "\n")

        db = AsyncMock()
        db.add = MagicMock()
        db.commit.side_effect = IntegrityError("insert", {}, Exception("duplicate key"))
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)):
            migrados = await audit._migrar_emergencia_a_tabla()

        self.assertEqual(migrados, 1)
        self.assertFalse(self._ruta_temp.exists())
        db.rollback.assert_awaited_once()


class AuditoriaFallbackTests(unittest.IsolatedAsyncioTestCase):
    """Si escribir en AuditLog falla, el evento cae a la tabla
    audit_log_fallback (no a un archivo) para poder reclamarse despues con
    SELECT ... FOR UPDATE SKIP LOCKED -- eso es lo que hace seguro el
    reintento con mas de un worker de Celery a la vez."""

    async def test_guardar_en_fallback_inserta_una_fila_por_entrada(self):
        db = AsyncMock()
        db.add = MagicMock()
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db)), \
             patch("app.admin.notificaciones.service.crear_notificacion", AsyncMock()), \
             patch("workers.tasks.reintentar_auditoria_fallback") as tarea_mock:
            await audit._guardar_en_fallback(
                [{"action": "created", "model": "Tenant", "model_id": "abc",
                  "old_values": None, "new_values": {}, "tenant_hint": None, "db_name_hint": None}],
                {"user_id": None, "user_name": "Admin", "tenant_id": None},
                "127.0.0.1",
            )
        db.add.assert_called_once()
        fila = db.add.call_args.args[0]
        self.assertEqual(fila.actor["user_name"], "Admin")
        self.assertEqual(fila.entrada["model"], "Tenant")
        db.commit.assert_awaited_once()
        tarea_mock.delay.assert_called_once()

    async def test_guardar_evento_en_fallback_es_el_punto_de_entrada_de_logout(self):
        with patch.object(audit, "_guardar_en_fallback", AsyncMock()) as mock_guardar:
            await audit.guardar_evento_en_fallback(
                {"action": "logout_fallido", "model": "User", "model_id": None,
                 "old_values": None, "new_values": None, "tenant_hint": None, "db_name_hint": None},
                {"user_id": "u1", "user_name": "Juan", "tenant_id": None},
                "10.0.0.1",
            )
        mock_guardar.assert_awaited_once()
        pila_pasada = mock_guardar.await_args.args[0]
        self.assertEqual(len(pila_pasada), 1)
        self.assertEqual(pila_pasada[0]["action"], "logout_fallido")


class RecuperarFilaBloqueadaTests(unittest.IsolatedAsyncioTestCase):
    def _fila(self, model_id="abc"):
        return SimpleNamespace(
            id=uuid.uuid4(), ocurrido_en=datetime.utcnow(), ip_address="127.0.0.1",
            actor={"user_id": None, "user_name": "Admin", "tenant_id": None},
            entrada={"action": "created", "model": "Tenant", "model_id": model_id,
                     "old_values": None, "new_values": {}, "tenant_hint": None, "db_name_hint": None},
        )

    async def test_recupera_e_inserta_con_el_mismo_id_de_la_fila(self):
        db = AsyncMock()
        db.add = MagicMock()
        fila = self._fila()
        resultado = await audit._recuperar_fila_fallback_bloqueada(db, fila)
        self.assertEqual(resultado, "recuperado")
        registro = db.add.call_args.args[0]
        self.assertEqual(registro.id, fila.id)
        self.assertEqual(registro.created_at, fila.ocurrido_en)
        db.delete.assert_awaited_once_with(fila)
        db.commit.assert_awaited()

    async def test_choque_de_clave_primaria_confirmado_se_trata_como_ya_recuperado(self):
        # El IntegrityError por si solo NO alcanza: se confirma que el
        # AuditLog con este id realmente existe antes de borrar el
        # respaldo (si no, seria un IntegrityError real, no una repeticion).
        db = AsyncMock()
        db.add = MagicMock()
        db.flush.side_effect = IntegrityError("insert", {}, Exception("duplicate key"))
        fila = self._fila()
        db2 = AsyncMock()
        db2.get.side_effect = [SimpleNamespace(id=fila.id), fila]  # AuditLog existe, luego se busca la fila del fallback
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db2)):
            resultado = await audit._recuperar_fila_fallback_bloqueada(db, fila)
        self.assertEqual(resultado, "ya_estaba")
        db.rollback.assert_awaited_once()
        db2.delete.assert_awaited_once_with(fila)

    async def test_integrity_error_sin_duplicado_real_conserva_el_pendiente(self):
        # Este es el bug reportado: un NOT NULL / FK / CHECK tambien lanza
        # IntegrityError, y NO es una repeticion -- debe conservar la fila
        # del fallback, no borrarla.
        db = AsyncMock()
        db.add = MagicMock()
        db.flush.side_effect = IntegrityError("insert", {}, Exception("null value in column violates not-null constraint"))
        fila = self._fila()
        db2 = AsyncMock()
        db2.get.return_value = None  # el AuditLog NO existe: no fue una repeticion
        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db2)):
            resultado = await audit._recuperar_fila_fallback_bloqueada(db, fila)
        self.assertEqual(resultado, "sigue_fallando")
        db2.delete.assert_not_called()

    async def test_no_accede_a_fila_id_despues_del_rollback(self):
        # Simula la expiracion de atributos que Session.rollback() provoca
        # en SQLAlchemy: si el codigo accediera a `fila.id` DESPUES del
        # rollback (en vez de la variable capturada antes), este objeto
        # revienta -- reproduce el riesgo de MissingGreenlet en una sesion
        # async real sin necesitar una sesion real.
        class FilaConIdSensible:
            def __init__(self, real_id):
                self._real_id = real_id
                self.expirado = False
                self.ocurrido_en = datetime.utcnow()
                self.ip_address = "127.0.0.1"
                self.actor = {"user_id": None, "user_name": "Admin", "tenant_id": None}
                self.entrada = {"action": "created", "model": "Tenant", "model_id": "abc",
                                "old_values": None, "new_values": {}, "tenant_hint": None, "db_name_hint": None}

            @property
            def id(self):
                if self.expirado:
                    raise RuntimeError("acceso a atributo expirado tras rollback (simula MissingGreenlet)")
                return self._real_id

        fila = FilaConIdSensible(uuid.uuid4())
        db = AsyncMock()
        db.add = MagicMock()
        db.flush.side_effect = IntegrityError("insert", {}, Exception("duplicate key"))
        db.rollback = AsyncMock(side_effect=lambda: setattr(fila, "expirado", True))

        db2 = AsyncMock()
        db2.get.side_effect = [SimpleNamespace(id=fila._real_id), fila]

        with patch("app.core.database.AsyncSessionLocal", return_value=_ctx(db2)):
            resultado = await audit._recuperar_fila_fallback_bloqueada(db, fila)

        self.assertEqual(resultado, "ya_estaba")

    async def test_error_generico_no_propaga_y_reporta_sigue_fallando(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.flush.side_effect = RuntimeError("bd caida a mitad de camino")
        fila = self._fila()
        resultado = await audit._recuperar_fila_fallback_bloqueada(db, fila)
        self.assertEqual(resultado, "sigue_fallando")
        db.rollback.assert_awaited_once()
        db.delete.assert_not_called()


class ReintentarFallbackPendienteTests(unittest.IsolatedAsyncioTestCase):
    async def test_sin_filas_pendientes_no_reintenta_nada(self):
        db_select = AsyncMock()
        db_select.execute.return_value = SimpleNamespace(scalar_one_or_none=lambda: None)
        db_count = AsyncMock()
        db_count.scalar.return_value = 0

        with patch("app.core.database.AsyncSessionLocal", side_effect=[_ctx(db_select), _ctx(db_count)]):
            resultado = await audit.reintentar_fallback_pendiente()

        self.assertEqual(resultado, {"reintentados": 0, "recuperados": 0, "pendientes": 0, "migrados_de_emergencia": 0})

    async def test_procesa_filas_una_por_una_hasta_agotarlas(self):
        fila = SimpleNamespace(
            id=uuid.uuid4(), ocurrido_en=datetime.utcnow(), ip_address=None,
            actor={}, entrada={"action": "created", "model": "Tenant", "model_id": "x",
                                "old_values": None, "new_values": {}, "tenant_hint": None, "db_name_hint": None},
        )
        db_ronda1 = AsyncMock()
        db_ronda1.execute.return_value = SimpleNamespace(scalar_one_or_none=lambda: fila)
        db_ronda1.add = MagicMock()
        db_ronda2 = AsyncMock()
        db_ronda2.execute.return_value = SimpleNamespace(scalar_one_or_none=lambda: None)
        db_count = AsyncMock()
        db_count.scalar.return_value = 0

        with patch("app.core.database.AsyncSessionLocal", side_effect=[_ctx(db_ronda1), _ctx(db_ronda2), _ctx(db_count)]):
            resultado = await audit.reintentar_fallback_pendiente()

        self.assertEqual(resultado, {"reintentados": 1, "recuperados": 1, "pendientes": 0, "migrados_de_emergencia": 0})
        db_ronda1.delete.assert_awaited_once_with(fila)


if __name__ == "__main__":
    unittest.main()
