import pytest
from fastapi import HTTPException

from app.core import rate_limit


@pytest.fixture(autouse=True)
def limpiar_estado_global():
    rate_limit._intentos_ip_correo.clear()
    rate_limit._intentos_correo.clear()
    rate_limit._intentos_ip.clear()
    yield
    rate_limit._intentos_ip_correo.clear()
    rate_limit._intentos_correo.clear()
    rate_limit._intentos_ip.clear()


def test_permite_intentos_por_debajo_del_limite():
    for _ in range(4):
        rate_limit.verificar_limite_login("1.2.3.4", "a@test.pe")
        rate_limit.registrar_intento_fallido("1.2.3.4", "a@test.pe")
    rate_limit.verificar_limite_login("1.2.3.4", "a@test.pe")  # el 5to intento aun no deberia bloquear


def test_bloquea_al_superar_el_limite_ip_mas_correo():
    for _ in range(5):
        rate_limit.verificar_limite_login("1.2.3.4", "a@test.pe")
        rate_limit.registrar_intento_fallido("1.2.3.4", "a@test.pe")
    with pytest.raises(HTTPException) as exc:
        rate_limit.verificar_limite_login("1.2.3.4", "a@test.pe")
    assert exc.value.status_code == 429


def test_login_exitoso_limpia_solo_el_contador_ip_mas_correo():
    for _ in range(4):
        rate_limit.registrar_intento_fallido("1.2.3.4", "a@test.pe")
    rate_limit.limpiar_intentos("1.2.3.4", "a@test.pe")
    rate_limit.verificar_limite_login("1.2.3.4", "a@test.pe")  # no debe explotar


def test_correo_es_insensible_a_mayusculas_y_espacios():
    for _ in range(5):
        rate_limit.registrar_intento_fallido("1.2.3.4", "A@Test.pe")
    with pytest.raises(HTTPException):
        rate_limit.verificar_limite_login("1.2.3.4", "  a@test.pe  ")


def test_atacante_rotando_de_ip_igual_topa_el_limite_por_correo():
    # 10 IPs distintas, un intento fallido cada una contra la MISMA cuenta:
    # ninguna toca el limite IP+correo (1 cada una), pero juntas superan el
    # limite por correo solo (10).
    for i in range(10):
        rate_limit.verificar_limite_login(f"10.0.0.{i}", "victima@test.pe")
        rate_limit.registrar_intento_fallido(f"10.0.0.{i}", "victima@test.pe")
    with pytest.raises(HTTPException):
        rate_limit.verificar_limite_login("10.0.0.99", "victima@test.pe")


def test_una_ip_probando_muchas_cuentas_topa_el_limite_por_ip():
    # Misma IP, 20 correos distintos: ninguna combinacion IP+correo ni
    # correo+IP individual llega a su propio limite, pero la IP sola si.
    for i in range(20):
        rate_limit.verificar_limite_login("9.9.9.9", f"cuenta{i}@test.pe")
        rate_limit.registrar_intento_fallido("9.9.9.9", f"cuenta{i}@test.pe")
    with pytest.raises(HTTPException):
        rate_limit.verificar_limite_login("9.9.9.9", "cuenta-nueva@test.pe")


def test_login_exitoso_no_resetea_el_limite_por_ip_de_otras_cuentas():
    # La IP prueba 20 cuentas fallidas y luego acierta una: el ataque contra
    # las OTRAS cuentas desde esa misma IP no debe olvidarse.
    for i in range(20):
        rate_limit.registrar_intento_fallido("9.9.9.9", f"cuenta{i}@test.pe")
    rate_limit.limpiar_intentos("9.9.9.9", "cuenta-que-si-entro@test.pe")
    with pytest.raises(HTTPException):
        rate_limit.verificar_limite_login("9.9.9.9", "cuenta-nueva-2@test.pe")


def test_claves_vencidas_se_eliminan_del_diccionario():
    rate_limit.registrar_intento_fallido("1.2.3.4", "temporal@test.pe")
    assert "1.2.3.4|temporal@test.pe" in rate_limit._intentos_ip_correo
    # Simula que la ventana ya paso.
    rate_limit._intentos_ip_correo["1.2.3.4|temporal@test.pe"][0] -= rate_limit._VENTANA_SEGUNDOS + 1
    rate_limit.verificar_limite_login("1.2.3.4", "temporal@test.pe")
    assert "1.2.3.4|temporal@test.pe" not in rate_limit._intentos_ip_correo
