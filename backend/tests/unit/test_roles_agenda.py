import pytest
from app.hospital.consulta_externa.service import _generar_slots
from app.sigarh.creacion_roles.service import _solape_semanal, _rango_min


def test_cupos_nocturnos():
    slots = _generar_slots("19:00", "07:00", 15)
    assert len(slots) == 48
    assert slots[0] == ("19:00", "19:15")
    assert slots[-1] == ("06:45", "07:00")
    assert len(set(slots)) == 48


def test_cupos_diurnos():
    assert len(_generar_slots("08:00", "12:00", 15)) == 16


def test_tiempo_invalido():
    with pytest.raises(ValueError):
        _generar_slots("08:00", "12:00", 0)


@pytest.mark.parametrize("dia,siguiente", [(1, 2), (6, 0)])
def test_solape_al_dia_siguiente(dia, siguiente):
    assert _solape_semanal({dia}, _rango_min("19:00", "07:00"),
                          {siguiente}, _rango_min("06:00", "08:00"))
    assert not _solape_semanal({dia}, _rango_min("19:00", "07:00"),
                              {siguiente}, _rango_min("07:00", "09:00"))


def test_aprobacion_revierte_si_falla_agenda():
    import asyncio
    import uuid
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, patch
    from app.sigarh.roles_pendientes import service
    creador, revisor = uuid.uuid4(), uuid.uuid4()
    rol = SimpleNamespace(servicio_id=uuid.uuid4(), status="pending", created_by_id=creador,
                          mes=9, anio=2026, empleados=[])
    db = SimpleNamespace(flush=AsyncMock(), commit=AsyncMock(), rollback=AsyncMock())
    sync = AsyncMock(side_effect=RuntimeError("fallo agenda"))
    async def ejecutar():
        with patch.object(service, "obtener_rol_orm", AsyncMock(return_value=rol)), \
             patch.object(service, "puede_aprobar_roles", AsyncMock(return_value=True)), \
             patch.object(service, "diagnosticar_rol", AsyncMock(return_value=[])), \
             patch.object(service, "sincronizar_programacion_sigarh", sync):
            with pytest.raises(RuntimeError):
                await service.aprobar_rol(db, uuid.uuid4(), uuid.uuid4(), {"sub": str(revisor)})
    asyncio.run(ejecutar())
    db.commit.assert_not_awaited()
    db.rollback.assert_awaited_once()
    assert sync.await_args.kwargs == {"commit": False}
