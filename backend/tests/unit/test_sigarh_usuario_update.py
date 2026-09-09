"""Regresiones del PATCH de usuarios. Sin escrituras en una base de datos."""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from pydantic import ValidationError

from app.sigarh.mantenimiento.schemas import UsuarioSigarhUpdate


class UsuarioUpdateSchemaTests(unittest.TestCase):
    def test_rejects_internal_and_unknown_fields(self):
        for field in (
            "tenant_id", "id", "created_at", "updated_at",
            "role", "panel", "_sa_instance_state", "campo_desconocido",
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
        self.assertEqual(
            UsuarioSigarhUpdate(perfil_id=None).model_dump(exclude_unset=True),
            {"perfil_id": None},
        )

    def test_relationship_ids_are_validated(self):
        for field in ("perfil_id", "empleado_id"):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                UsuarioSigarhUpdate.model_validate({field: "no-es-uuid"})

    def test_non_nullable_fields_reject_explicit_null(self):
        for field in ("username", "email", "is_active"):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                UsuarioSigarhUpdate.model_validate({field: None})


class UsuarioUpdateEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def call_endpoint(self, payload, item):
        from app.sigarh.mantenimiento.router import actualizar_usuario

        db = SimpleNamespace(commit=AsyncMock(), refresh=AsyncMock())
        tenant_id = uuid4()
        user_id = item.id if item else uuid4()
        with patch(
            "app.sigarh.mantenimiento.router.obtener", new_callable=AsyncMock,
            return_value=item,
        ) as obtener:
            result = await actualizar_usuario(
                request=SimpleNamespace(headers={}), id=user_id,
                data=UsuarioSigarhUpdate.model_validate(payload), db=db,
                tenant={}, current_user={"tenant_id": str(tenant_id)},
            )
            obtener.assert_awaited_once()
            self.assertEqual(obtener.call_args.args[2:], (user_id, tenant_id))
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once_with(item)
        return result

    def make_item(self):
        return SimpleNamespace(
            id=uuid4(), tenant_id=uuid4(), username="original",
            email="original@example.invalid", password="hash-original",
            perfil_id=uuid4(), is_active=True,
        )

    async def test_partial_update_preserves_identity_and_omitted_fields(self):
        item = self.make_item()
        before = vars(item).copy()
        await self.call_endpoint({"is_active": False}, item)
        self.assertEqual(vars(item), {**before, "is_active": False})

    async def test_edit_form_payload_is_compatible(self):
        item = self.make_item()
        await self.call_endpoint({
            "username": "editado", "email": "editado@example.invalid",
            "perfil_id": None, "is_active": True,
        }, item)
        self.assertEqual(item.username, "editado")
        self.assertIsNone(item.perfil_id)
        self.assertEqual(item.password, "hash-original")

    async def test_empty_or_null_password_keeps_hash(self):
        for password in ("", None):
            with self.subTest(password=password):
                item = self.make_item()
                await self.call_endpoint({"password": password}, item)
                self.assertEqual(item.password, "hash-original")

    async def test_new_password_is_hashed(self):
        item = self.make_item()
        with patch("bcrypt.hashpw", return_value=b"hash-nuevo") as hashpw:
            await self.call_endpoint({"password": "clave-de-prueba"}, item)
        self.assertEqual(item.password, "hash-nuevo")
        self.assertEqual(hashpw.call_args.args[0], b"clave-de-prueba")


if __name__ == "__main__":
    unittest.main()
