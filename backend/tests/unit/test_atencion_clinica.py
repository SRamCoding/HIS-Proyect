import asyncio, uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError
from app.hospital.consulta_externa.schemas import AtencionMedicaCreate, AtencionMedicaUpdate, AtencionDiagnosticoCreate
from app.hospital.consulta_externa.service import validar_diagnosticos, validar_autor_clinico

@pytest.mark.parametrize("motivo", ["", "  ", None])
def test_motivo_no_vacio(motivo):
    with pytest.raises(ValidationError): AtencionMedicaCreate(motivo_consulta=motivo)

def test_destino_y_prestaciones_independientes():
    d = AtencionMedicaCreate(motivo_consulta=" Control ", destino_atencion="ALTA", prestaciones=["FARMACIA", "LABORATORIO"])
    assert d.motivo_consulta == "Control" and len(d.prestaciones) == 2
    with pytest.raises(ValidationError): AtencionMedicaCreate(motivo_consulta="Control", destino_atencion="FARMACIA")

def test_edicion_diagnosticos_y_tipo():
    d = AtencionMedicaUpdate(diagnosticos=[{"diagnostico_cie10_id": uuid.uuid4(), "tipo": "presuntivo"}])
    assert d.diagnosticos[0].tipo == "presuntivo"
    with pytest.raises(ValidationError): AtencionDiagnosticoCreate(diagnostico_cie10_id=uuid.uuid4(), tipo="inventado")

def test_diagnostico_duplicado():
    d = AtencionDiagnosticoCreate(diagnostico_cie10_id=uuid.uuid4())
    with pytest.raises(ValueError): asyncio.run(validar_diagnosticos(SimpleNamespace(), uuid.uuid4(), [d, d]))

def test_diagnostico_ajeno_o_inactivo():
    db = SimpleNamespace(scalars=AsyncMock(return_value=SimpleNamespace(all=lambda: [])))
    with pytest.raises(ValueError): asyncio.run(validar_diagnosticos(db, uuid.uuid4(), [AtencionDiagnosticoCreate(diagnostico_cie10_id=uuid.uuid4())]))

@pytest.mark.parametrize("role,panel,empleado", [("administrador", "app", uuid.uuid4()), ("medico", "app", None), ("medico", "portal", uuid.uuid4())])
def test_autor_rechaza_cuenta_incorrecta(role,panel,empleado):
    db = SimpleNamespace(scalar=AsyncMock(return_value=SimpleNamespace(role=role,panel=panel,empleado_id=empleado)))
    with pytest.raises(ValueError): asyncio.run(validar_autor_clinico(db,uuid.uuid4(),SimpleNamespace(),{"sub":str(uuid.uuid4())}))
