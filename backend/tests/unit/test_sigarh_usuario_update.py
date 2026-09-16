"""Contrato actual del PATCH unificado de usuarios SIGARH/Hospitalario."""

import unittest
from uuid import uuid4

from pydantic import ValidationError

from app.sigarh.mantenimiento.schemas import UsuarioSigarhUpdate


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

    def test_profile_is_required_and_cannot_be_cleared(self):
        with self.assertRaises(ValidationError):
            UsuarioSigarhUpdate(perfil_id=None)

    def test_panel_selects_the_account_store(self):
        self.assertEqual(UsuarioSigarhUpdate(panel="app").panel, "app")
        with self.assertRaises(ValidationError):
            UsuarioSigarhUpdate(panel="admin")

    def test_relationship_ids_are_validated(self):
        for field in ("perfil_id", "empleado_id"):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                UsuarioSigarhUpdate.model_validate({field: "no-es-uuid"})

    def test_non_nullable_fields_reject_explicit_null(self):
        for field in ("username", "email", "is_active", "panel", "perfil_id"):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                UsuarioSigarhUpdate.model_validate({field: None})
if __name__ == "__main__":
    unittest.main()
