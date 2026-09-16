"""Regresiones del esquema y las validaciones de relaciones de Mantenimiento.

Sin escrituras en una base de datos: `validar_relaciones()` nunca toca `db`
cuando el id de la relación es None (`referencia()` corta antes de consultar),
así que las pruebas de regresión de más abajo pasan `db=None` a propósito.
"""

import unittest
from uuid import uuid4

from pydantic import ValidationError

from app.sigarh.mantenimiento import models as m
from app.sigarh.mantenimiento.schemas import (
    PerfilUsuarioCreate,
    UsuarioSigarhCreate,
    UsuarioSigarhUpdate,
    esquema_parcial,
)
from app.sigarh.mantenimiento.service import validar_relaciones


class UsuarioUpdateSchemaTests(unittest.TestCase):
    def test_rejects_internal_and_unknown_fields(self):
        for field in (
            "tenant_id", "id", "created_at", "updated_at",
            "role", "_sa_instance_state", "campo_desconocido",
        ):
            with self.subTest(field=field), self.assertRaises(ValidationError) as ctx:
                UsuarioSigarhUpdate.model_validate({field: str(uuid4())})
            self.assertEqual(ctx.exception.errors()[0]["type"], "extra_forbidden")

    def test_rejects_mixed_valid_and_internal_fields(self):
        with self.assertRaises(ValidationError):
            UsuarioSigarhUpdate(username="nuevo", tenant_id=str(uuid4()))

    def test_patch_only_includes_supplied_fields(self):
        self.assertEqual(UsuarioSigarhUpdate().model_dump(exclude_unset=True), {})
        self.assertEqual(
            UsuarioSigarhUpdate(is_active=False).model_dump(exclude_unset=True),
            {"is_active": False},
        )

    def test_nullable_relationship_can_be_cleared(self):
        # perfil_id es obligatorio en UsuarioSigarhCreate (uuid.UUID sin
        # "| None"), pero nullable en el modelo -- el Update debe aceptar
        # null explicito para poder "desasignar" el perfil de una cuenta.
        self.assertEqual(
            UsuarioSigarhUpdate(perfil_id=None).model_dump(exclude_unset=True),
            {"perfil_id": None},
        )

    def test_relationship_ids_are_validated(self):
        for field in ("perfil_id", "empleado_id"):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                UsuarioSigarhUpdate.model_validate({field: "no-es-uuid"})

    def test_non_nullable_fields_reject_explicit_null(self):
        # esquema_parcial solo relaja los campos *_id; los escalares (que
        # nunca deben aceptar null) siguen rechazandolo.
        for field in ("username", "email", "is_active"):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                UsuarioSigarhUpdate.model_validate({field: None})

    def test_create_still_requires_perfil_id(self):
        # El relajo de esquema_parcial es exclusivo del Update generado; el
        # Create (usado al dar de alta una cuenta) sigue exigiendo el perfil.
        with self.assertRaises(ValidationError):
            UsuarioSigarhCreate(username="nuevo", email="nuevo@example.invalid", password="x")


class RelacionLimpiableSinCrashTests(unittest.IsolatedAsyncioTestCase):
    """Regresion del bug encontrado al arreglar el punto anterior: una vez que
    esquema_parcial dejo pasar `perfil_id`/`rol_sistema_id` en None, ese None
    llegaba sin filtro a validar_relaciones(), que asumia ciegamente un objeto
    resuelto (`rol.panel`, `perfil.rol_sistema_id`) y explotaba con
    AttributeError -- un 500 en vez de un 422 claro, o directamente romper el
    guardado de "Sin rol" / "Sin perfil" desde el frontend."""

    async def test_usuario_sin_perfil_no_truena(self):
        await validar_relaciones(db=None, modelo=m.UsuarioSigarh, tenant_id=uuid4(), values={"perfil_id": None})

    async def test_perfil_sin_rol_no_truena(self):
        await validar_relaciones(
            db=None, modelo=m.PerfilUsuario, tenant_id=uuid4(),
            values={"rol_sistema_id": None, "modulos_acceso": []},
        )

    async def test_perfil_sin_rol_no_puede_tener_modulos(self):
        with self.assertRaises(Exception):
            await validar_relaciones(
                db=None, modelo=m.PerfilUsuario, tenant_id=uuid4(),
                values={"rol_sistema_id": None, "modulos_acceso": ["sigarh_mantenimiento"]},
            )


class PerfilUsuarioUpdateSchemaTests(unittest.TestCase):
    """Mismo relajo de esquema_parcial, verificado directamente sobre el
    Update de PerfilUsuario (se genera on-the-fly en el router, no vive como
    nombre exportado en schemas.py)."""

    def setUp(self):
        self.PerfilUsuarioUpdate = esquema_parcial(PerfilUsuarioCreate)

    def test_rol_sistema_id_can_be_cleared(self):
        self.assertEqual(
            self.PerfilUsuarioUpdate(rol_sistema_id=None).model_dump(exclude_unset=True),
            {"rol_sistema_id": None},
        )

    def test_create_still_requires_rol_sistema_id(self):
        with self.assertRaises(ValidationError):
            PerfilUsuarioCreate(nombre="Perfil de prueba")


if __name__ == "__main__":
    unittest.main()
