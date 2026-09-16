import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from app.admin.usuarios.service import _es_ultimo_administrador
from app.admin.modulos.service import create_module_dependency, _LOCK_GRAFO_DEPENDENCIAS


class UltimoAdministradorConcurrenciaTests(unittest.IsolatedAsyncioTestCase):
    """El chequeo del ultimo administrador debe bloquear TODAS las filas de
    administradores activos del ambito (no solo la del otro): sin eso, dos
    desactivaciones simultaneas de los dos unicos admins pueden contar cada
    una "el otro sigue activo" y las dos pasar."""

    def _user(self, uid=None, panel="admin", role="administrador", is_active=True):
        return SimpleNamespace(id=uid or uuid.uuid4(), panel=panel, role=role, is_active=is_active)

    async def test_la_consulta_usa_for_update_sobre_todo_el_ambito(self):
        user = self._user()
        otro_id = uuid.uuid4()
        db = AsyncMock()
        db.execute.return_value = SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [user.id, otro_id]))

        resultado = await _es_ultimo_administrador(user, db)

        self.assertFalse(resultado)  # hay otro admin activo ademas de user
        consulta = db.execute.call_args.args[0]
        # with_for_update() agrega FOR UPDATE al SQL compilado.
        self.assertIn("FOR UPDATE", str(consulta))

    async def test_es_el_ultimo_si_nadie_mas_esta_activo(self):
        user = self._user()
        db = AsyncMock()
        db.execute.return_value = SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [user.id]))
        self.assertTrue(await _es_ultimo_administrador(user, db))

    async def test_no_administrador_no_dispara_ninguna_consulta(self):
        user = self._user(role="app")
        db = AsyncMock()
        self.assertFalse(await _es_ultimo_administrador(user, db))
        db.execute.assert_not_called()


class DependenciaModuloConcurrenciaTests(unittest.IsolatedAsyncioTestCase):
    """Crear una dependencia entre modulos debe serializarse via un
    advisory lock de Postgres: el ciclo se puede formar por la COMBINACION
    de dos inserts concurrentes, no por chocar sobre la misma fila, asi que
    bloquear filas puntuales no alcanza."""

    async def test_adquiere_el_advisory_lock_antes_de_cualquier_otra_consulta(self):
        db = AsyncMock()
        db.add = MagicMock()  # db.add() es sincrono en SQLAlchemy real
        db.scalars.side_effect = [
            SimpleNamespace(all=lambda: ["mod_a", "mod_b"]),  # codigos validos
            SimpleNamespace(all=lambda: []),  # _existe_ciclo: sin dependientes
        ]
        db.scalar.return_value = None  # sin dependencia existente
        data = SimpleNamespace(module_code="mod_a", depends_on_code="mod_b", is_required=True)

        await create_module_dependency(db, data)

        primera_llamada = db.execute.call_args_list[0]
        self.assertIn("pg_advisory_xact_lock", str(primera_llamada.args[0]))
        self.assertEqual(primera_llamada.args[1], {"clave": _LOCK_GRAFO_DEPENDENCIAS})

    async def test_autodependencia_sigue_bloqueada_incluso_con_el_lock(self):
        db = AsyncMock()
        data = SimpleNamespace(module_code="mod_a", depends_on_code="mod_a", is_required=True)
        with self.assertRaises(HTTPException) as err:
            await create_module_dependency(db, data)
        self.assertEqual(err.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
