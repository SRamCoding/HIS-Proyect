import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from app.admin.roles.schemas import SystemRoleCreate
from app.admin.roles.service import create_system_role


def test_codigo_medico_normalizado():
    rol = SystemRoleCreate(name=' Medico ', label='Médico', panel='app')
    assert rol.name == 'medico'


def test_codigo_duplicado_no_crea_otro_rol():
    db = SimpleNamespace(scalar=AsyncMock(return_value='existente'))
    rol = SystemRoleCreate(name='MEDICO', label='Médico', panel='app')
    with pytest.raises(HTTPException) as error:
        asyncio.run(create_system_role(db, rol))
    assert error.value.status_code == 409


def test_sigarh_no_crea_roles_app():
    from app.sigarh.mantenimiento.schemas import RolSistemaCreate
    with pytest.raises(ValidationError):
        RolSistemaCreate(codigo='MEDICO', nombre='Médico', panel='app')
