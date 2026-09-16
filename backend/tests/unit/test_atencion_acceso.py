import asyncio, uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import pytest
from fastapi import HTTPException
from app.hospital.consulta_externa import router, service

@pytest.mark.parametrize("permitido", [True, False])
def test_preflight_refleja_validacion_del_guardado(permitido):
    tid, cid = uuid.uuid4(), uuid.uuid4()
    db = SimpleNamespace(scalar=AsyncMock(return_value=SimpleNamespace(id=cid)))
    validar = AsyncMock(side_effect=None if permitido else ValueError("Vincule una cuenta medica"))
    with patch.object(router, "get_tenant_id", return_value=tid), patch.object(service, "validar_autor_clinico", validar):
        r = asyncio.run(router.acceso_atencion(cid, None, db, {"sub": str(uuid.uuid4())}))
    assert r["permitido"] == permitido
    assert bool(r["motivo"]) == (not permitido)
    validar.assert_awaited_once()

def test_preflight_no_expone_cita_ajena():
    db = SimpleNamespace(scalar=AsyncMock(return_value=None))
    with patch.object(router, "get_tenant_id", return_value=uuid.uuid4()):
        with pytest.raises(HTTPException) as e:
            asyncio.run(router.acceso_atencion(uuid.uuid4(), None, db, {}))
    assert e.value.status_code == 404
