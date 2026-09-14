import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import pytest
from app.hospital.consulta_externa import service
from app.hospital.consulta_externa.schemas import CitaUpdate


def database(cita, programacion=None):
    return SimpleNamespace(
        execute=AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: cita)),
        scalar=AsyncMock(return_value=programacion), commit=AsyncMock(),
    )


@pytest.mark.parametrize("estado", ["atendida", "cancelada", "no_asistio", "confirmada"])
def test_confirmar_rechaza_estados_incorrectos(estado):
    db = database(SimpleNamespace(estado=estado))
    with pytest.raises(ValueError):
        asyncio.run(service.confirmar_cita(db, uuid.uuid4(), uuid.uuid4()))
    db.commit.assert_not_awaited()


def test_confirmar_rechaza_agenda_inactiva():
    db = database(SimpleNamespace(estado="separada", programacion_medica_id=uuid.uuid4()), SimpleNamespace(estado="inactivo"))
    with pytest.raises(ValueError, match="activa"):
        asyncio.run(service.confirmar_cita(db, uuid.uuid4(), uuid.uuid4()))
    db.commit.assert_not_awaited()


def test_confirmar_revalida_rol_antes_de_guardar():
    cita = SimpleNamespace(estado="separada", programacion_medica_id=uuid.uuid4())
    db = database(cita, SimpleNamespace(estado="activo"))
    with patch.object(service, "_validar_rol_programacion", AsyncMock(side_effect=ValueError("rol revocado"))):
        with pytest.raises(ValueError, match="revocado"):
            asyncio.run(service.confirmar_cita(db, uuid.uuid4(), uuid.uuid4()))
    assert cita.estado == "separada"
    db.commit.assert_not_awaited()


@pytest.mark.parametrize("estado", ["atendida", "confirmada", None, "inventado"])
def test_edicion_no_permite_saltar_flujo(estado):
    cita = SimpleNamespace(estado="separada")
    db = database(cita)
    with pytest.raises(ValueError):
        asyncio.run(service.update_cita(db, uuid.uuid4(), uuid.uuid4(), CitaUpdate(estado=estado)))
    assert cita.estado == "separada"
    db.commit.assert_not_awaited()
