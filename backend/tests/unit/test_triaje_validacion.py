import pytest
from pydantic import ValidationError
from app.hospital.consulta_externa.schemas import TriajeCreate, TriajeUpdate

MEDICIONES = dict(pulso=110, temperatura=39.2, presion_sistolica=150,
                  presion_diastolica=95, frecuencia_cardiaca=110, frecuencia_respiratoria=18)

def test_permite_mediciones_alteradas():
    assert TriajeCreate(**MEDICIONES).temperatura == 39.2
    assert TriajeCreate(**MEDICIONES).frecuencia_respiratoria == 18

def test_no_permite_triaje_vacio():
    with pytest.raises(ValidationError):
        TriajeCreate()

@pytest.mark.parametrize("campo,valor", [("pulso", -1), ("peso", 0), ("talla", -1), ("saturacion_o2", 101), ("temperatura", float("nan"))])
def test_rechaza_datos_invalidos(campo, valor):
    with pytest.raises(ValidationError):
        TriajeCreate(**(MEDICIONES | {campo: valor}))

def test_edicion_parcial_y_obligatorios():
    assert TriajeUpdate(peso=70).peso == 70
    with pytest.raises(ValidationError):
        TriajeUpdate(pulso=None)
