from datetime import datetime, timedelta
from app.sigarh.creacion_roles.jornada import revisar_intervalos


def franja(dia, inicio=8, horas=4, guardia=False, agenda=True, tipo='ordinario'):
    a = datetime(2026, 9, dia, inicio)
    return (a, a + timedelta(hours=horas), guardia, agenda, tipo)


def test_consulta_mas_gestion_no_superpuesta():
    assert revisar_intervalos([franja(3), franja(3, 12, 2, agenda=False)], 9, 2026, 150) == []


def test_no_ofertar_guardia_como_consulta():
    errores = revisar_intervalos([franja(3, 19, 12, True)], 9, 2026, 150)
    assert any('cuatro horas' in e for e in errores)


def test_exceso_acumulado_entre_servicios():
    errores = revisar_intervalos([franja(d, horas=6, agenda=False) for d in range(1, 27)], 9, 2026, 150)
    assert any('156 horas' in e for e in errores)


def test_jornada_contratada_menor():
    assert any('jornada documentada' in e for e in revisar_intervalos([franja(d) for d in range(1, 12)], 9, 2026, 40))


def test_no_autorizar_complementarias_sin_reglas():
    assert revisar_intervalos([franja(3, tipo='complementario')], 9, 2026, 150)


def test_solapes_de_actividades_no_asistenciales():
    assert any('superpuestos' in e for e in revisar_intervalos([franja(3), franja(3, 10, 2, agenda=False)], 9, 2026, 150))


def test_guardias_ordinarias_exceso():
    assert any('60 horas' in e for e in revisar_intervalos([franja(d, 7, 12, True, False) for d in range(1, 7)], 9, 2026, 150))


def test_descanso_postguardia():
    assert any('descanso' in e for e in revisar_intervalos([franja(3, 19, 12, True, False), franja(4, 8)], 9, 2026, 150))
