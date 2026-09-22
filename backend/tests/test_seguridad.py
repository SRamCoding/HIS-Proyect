"""Seguridad (panel app): pruebas HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_seguridad -v

Nota sobre aislamiento por hospital: a diferencia de las demás tablas de este
proyecto, User.tenant_id no se usa para las cuentas panel='app' (SIGARH >
Mantenimiento > Usuarios las crea sin ese campo, porque ya viven en la BD
física propia del hospital -- confirmado contra las cuentas reales de Reque).
Ese aislamiento es por base de datos física, no por columna, y este arnés de
pruebas simula el multi-tenant con una sola conexión compartida por
savepoints -- no puede reproducir bases físicas separadas. Por eso este
archivo no incluye una prueba de "aislamiento por tenant" para /empleados:
probarla aquí daría una falsa sensación de cobertura sobre un mecanismo que
en realidad garantiza el propio get_tenant_sessionmaker, ya usado por todos
los módulos por igual.
"""
import unittest
import uuid
from sqlalchemy import select, func
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.auth.models import User, PerfilHospital
from app.sigarh.rrhh.models import Empleado
from app.core.security import create_access_token


class SeguridadTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            # /app/seguridad/empleados NO filtra por tenant_id -- las cuentas
            # panel='app' se aislan por BD FISICA del hospital en producción real
            # (ver docstring del módulo arriba), no por columna. Este arnés de
            # pruebas comparte una sola BD central real con datos preexistentes
            # (incluye la cuenta real "Lennart Sosa" y la que crea el fixture base
            # de ArchivoClinicoTests), así que contar filas "totales" en vez de
            # contra un baseline medido en caliente da un número distinto según
            # qué más exista en la BD -- se mide antes de agregar los usuarios
            # propios de esta prueba, en vez de asumir un total absoluto.
            base = select(User).where(User.panel == "app")
            self.baseline_total = await db.scalar(select(func.count()).select_from(base.subquery()))
            self.baseline_activos = await db.scalar(select(func.count()).select_from(
                base.where(User.is_active.is_(True)).subquery()))
            self.baseline_sin_perfil = await db.scalar(select(func.count()).select_from(
                base.where(User.perfil_usuario_id.is_(None), User.perfil_hospital_id.is_(None)).subquery()))
            self.baseline_sin_empleado = await db.scalar(select(func.count()).select_from(
                base.where(User.empleado_id.is_(None)).subquery()))
            self.baseline_roles = set(await db.scalars(select(User.role).where(User.panel == "app").distinct()))

            db.add(TenantModule(tenant_id=self.tenant_id, module_code="seguridad"))
            self.empleado_id = uuid.uuid4()
            self.perfil_id = uuid.uuid4()
            self.user_con_todo_id = uuid.uuid4()
            self.user_sin_perfil_id = uuid.uuid4()
            db.add(Empleado(id=self.empleado_id, tenant_id=self.tenant_id, dni="87654321",
                nombres="Medico", apellido_paterno="De Prueba", apellido_materno="Seguridad"))
            db.add(PerfilHospital(id=self.perfil_id, tenant_id=self.tenant_id, nombre="Médico de guardia",
                role="medico", modulos=["consulta_externa"], is_active=True))
            # No hay relaciones ORM declaradas desde User hacia estas tablas; el
            # flush explícito conserva el orden exigido por sus llaves foráneas.
            await db.flush()
            # Sin tenant_id: así es como SIGARH > Mantenimiento > Usuarios las crea de verdad.
            db.add(User(id=self.user_con_todo_id, name="Medico De Prueba", email="medico.seg@test.com",
                password="x", role="medico", panel="app",
                empleado_id=self.empleado_id, perfil_hospital_id=self.perfil_id, is_active=True))
            db.add(User(id=self.user_sin_perfil_id, name="Sin Perfil Asignado", email="sinperfil.seg@test.com",
                password="x", role="enfermera", panel="app", is_active=False))
            # Cuenta de otro panel: no debe aparecer en /empleados (que solo lista panel='app').
            db.add(User(name="Usuario SIGARH", email="sigarh.seg@test.com", password="x",
                role="rrhh", panel="sigarh"))
            await db.commit()
        self.prefix = "/app/seguridad"
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def test_seg_lista_solo_panel_app(self):
        r = await self.client.get(self.prefix + "/empleados")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["total"], self.baseline_total + 2)

    async def test_seg_busqueda_por_nombre_y_filtros(self):
        r = await self.client.get(self.prefix + "/empleados", params={"q": "Medico De Prueba"})
        self.assertEqual(r.json()["total"], 1)
        item = r.json()["items"][0]
        self.assertEqual(item["empleado_nombre"], "De Prueba Seguridad, Medico")
        self.assertEqual(item["perfil_nombre"], "Médico de guardia")
        self.assertEqual(item["modulos"], ["consulta_externa"])
        r = await self.client.get(self.prefix + "/empleados", params={"role": "enfermera"})
        self.assertEqual(r.json()["total"], 1)
        r = await self.client.get(self.prefix + "/empleados", params={"estado": "inactivo"})
        self.assertEqual(r.json()["total"], 1)
        self.assertIsNone(r.json()["items"][0]["perfil_nombre"])

    async def test_seg_detalle_y_catalogo_roles(self):
        r = await self.client.get(self.prefix + f"/empleados/{self.user_con_todo_id}")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertTrue(r.json()["empleado_activo"])
        r = await self.client.get(self.prefix + f"/empleados/{uuid.uuid4()}")
        self.assertEqual(r.status_code, 404)
        r = await self.client.get(self.prefix + "/catalogos/roles")
        self.assertEqual(sorted(r.json()), sorted(self.baseline_roles | {"enfermera", "medico"}))

    async def test_seg_resumen_agrega_correctamente(self):
        r = await self.client.get(self.prefix + "/resumen")
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["total"], self.baseline_total + 2)
        self.assertEqual(data["activos"], self.baseline_activos + 1)
        self.assertEqual(data["inactivos"], data["total"] - data["activos"])
        self.assertEqual(data["sin_perfil_hospitalario"], self.baseline_sin_perfil + 1)
        self.assertEqual(data["sin_empleado_vinculado"], self.baseline_sin_empleado + 1)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(SeguridadTests(name) for name in SeguridadTests.__dict__ if name.startswith("test_seg_"))
