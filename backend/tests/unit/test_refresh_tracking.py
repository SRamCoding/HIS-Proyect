import pytest

from app.core import refresh_tracking as rt


@pytest.fixture(autouse=True)
def limpiar_estado_global():
    rt._jti_vigente.clear()
    yield
    rt._jti_vigente.clear()


def test_primer_refresh_sin_historial_se_acepta_y_reserva():
    assert rt.reservar_rotacion("sid-1", "jti-a", "jti-b") is True
    assert rt._jti_vigente["sid-1"] == "jti-b"


def test_jti_vigente_se_acepta_y_rota():
    rt.emitir_jti("sid-1", "jti-a")
    assert rt.reservar_rotacion("sid-1", "jti-a", "jti-b") is True
    assert rt._jti_vigente["sid-1"] == "jti-b"


def test_jti_viejo_ya_rotado_se_detecta_como_reuso_y_no_modifica_nada():
    rt.emitir_jti("sid-1", "jti-a")
    rt.emitir_jti("sid-1", "jti-b")  # rotacion: jti-a queda obsoleto
    assert rt.reservar_rotacion("sid-1", "jti-a", "jti-c") is False
    assert rt._jti_vigente["sid-1"] == "jti-b", "un intento rechazado no debe alterar el jti vigente"
    assert rt.reservar_rotacion("sid-1", "jti-b", "jti-c") is True


def test_sesiones_distintas_no_se_mezclan():
    rt.emitir_jti("sid-1", "jti-a")
    # sid-2 (otra sesion, ej. otro dispositivo del mismo usuario) no tiene
    # historial propio: se acepta como bootstrap, sin tocar sid-1.
    assert rt.reservar_rotacion("sid-2", "jti-a", "jti-z") is True
    assert rt._jti_vigente["sid-1"] == "jti-a"


def test_login_en_otro_dispositivo_no_invalida_la_sesion_original():
    # Reproduce el bug reportado: loguearse en una sesion B (otro sid) NO
    # debe hacer que el siguiente refresh legitimo de la sesion A se trate
    # como reuso.
    rt.emitir_jti("sid-A", "jti-a1")
    rt.emitir_jti("sid-B", "jti-b1")  # login en otro dispositivo
    assert rt.reservar_rotacion("sid-A", "jti-a1", "jti-a2") is True


def test_olvidar_borra_el_historial_de_esa_sesion():
    rt.emitir_jti("sid-1", "jti-a")
    rt.olvidar("sid-1")
    assert rt.reservar_rotacion("sid-1", "jti-cualquiera", "jti-nuevo") is True  # bootstrap de nuevo


def test_reservar_es_atomico_solo_una_gana_con_el_mismo_jti_viejo():
    rt.emitir_jti("sid-1", "jti-a")
    # Dos "renovaciones concurrentes" presentando el mismo jti viejo: solo
    # la primera en llamar debe ganar la reserva.
    primera = rt.reservar_rotacion("sid-1", "jti-a", "jti-ganadora")
    segunda = rt.reservar_rotacion("sid-1", "jti-a", "jti-perdedora")
    assert primera is True
    assert segunda is False
    assert rt._jti_vigente["sid-1"] == "jti-ganadora"
