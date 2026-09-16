import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.admin.usuarios.router import _roles_por_lote


class RolesPorLoteTests(unittest.IsolatedAsyncioTestCase):
    """_roles_por_lote reemplaza a _rol_nombre_sigarh (una consulta por
    perfil, otra por rol, POR CADA cuenta SIGARH) por dos consultas totales
    sin importar cuantas cuentas se resuelvan a la vez."""

    async def test_resuelve_varios_perfiles_con_dos_consultas_en_total(self):
        rol_id = uuid.uuid4()
        perfil_a = uuid.uuid4()
        perfil_b = uuid.uuid4()
        perfil_sin_rol = uuid.uuid4()

        session = AsyncMock()
        session.scalars.side_effect = [
            SimpleNamespace(all=lambda: [
                SimpleNamespace(id=perfil_a, rol_sistema_id=rol_id),
                SimpleNamespace(id=perfil_b, rol_sistema_id=rol_id),
                SimpleNamespace(id=perfil_sin_rol, rol_sistema_id=None),
            ]),
            SimpleNamespace(all=lambda: [SimpleNamespace(id=rol_id, nombre="Jefe de Enfermería")]),
        ]

        resultado = await _roles_por_lote(session, {perfil_a, perfil_b, perfil_sin_rol})

        self.assertEqual(session.scalars.await_count, 2)
        self.assertEqual(resultado[perfil_a], "Jefe de Enfermería")
        self.assertEqual(resultado[perfil_b], "Jefe de Enfermería")
        self.assertEqual(resultado[perfil_sin_rol], "SIGARH")

    async def test_sin_perfiles_no_consulta_nada(self):
        session = AsyncMock()
        resultado = await _roles_por_lote(session, set())
        self.assertEqual(resultado, {})
        session.scalars.assert_not_called()


if __name__ == "__main__":
    unittest.main()
