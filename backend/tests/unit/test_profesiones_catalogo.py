import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.sigarh.mantenimiento.profesiones_catalogo import GRUPOS, PROFESIONES, stable_id
from app.sigarh.rrhh.service import ReglaNegocioError, _validar_profesion_empleado


def test_referencias_catalogo():
    groups = {row[0] for row in GRUPOS}
    assert len({row[0] for row in PROFESIONES}) == len(PROFESIONES)
    assert all(row[2] in groups for row in PROFESIONES)
    assert next(row for row in PROFESIONES if row[0] == 'MED')[5] == 'medicos'
    tenant = uuid.uuid4()
    assert stable_id('profession', tenant, 'MED') != stable_id('profession', uuid.uuid4(), 'MED')


@pytest.mark.asyncio
async def test_grupo_incompatible_bloqueado():
    group = uuid.uuid4()
    db = SimpleNamespace(scalar=AsyncMock(return_value=SimpleNamespace(
        grupo_ocupacional_id=group, codigo='MED', colegio_profesional='CMP'
    )))
    with pytest.raises(ReglaNegocioError, match='grupo ocupacional'):
        await _validar_profesion_empleado(db, uuid.uuid4(), {
            'profesion_id': uuid.uuid4(), 'grupo_ocupacional_id': uuid.uuid4(),
        })


@pytest.mark.asyncio
async def test_habilitacion_requiere_colegiatura():
    group = uuid.uuid4()
    db = SimpleNamespace(scalar=AsyncMock(return_value=SimpleNamespace(
        grupo_ocupacional_id=group, codigo='MED', colegio_profesional='CMP'
    )))
    with pytest.raises(ReglaNegocioError, match='colegiatura'):
        await _validar_profesion_empleado(db, uuid.uuid4(), {
            'profesion_id': uuid.uuid4(), 'grupo_ocupacional_id': group,
            'habilitado_colegio': True,
        })


@pytest.mark.asyncio
async def test_empleado_anterior_sin_profesion_conservado():
    db = SimpleNamespace(scalar=AsyncMock())
    await _validar_profesion_empleado(db, uuid.uuid4(), {})
    db.scalar.assert_not_called()
