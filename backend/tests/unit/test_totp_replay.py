import pyotp
import pytest
from app.core import totp


@pytest.fixture(autouse=True)
def limpiar_estado_global():
    totp._ULTIMO_CODIGO_ACEPTADO.clear()
    yield
    totp._ULTIMO_CODIGO_ACEPTADO.clear()


def test_codigo_correcto_se_acepta():
    secreto = totp.generar_secreto()
    codigo = pyotp.TOTP(secreto).now()
    assert totp.verificar_codigo("user-1", secreto, codigo) is True


def test_codigo_incorrecto_se_rechaza():
    secreto = totp.generar_secreto()
    assert totp.verificar_codigo("user-1", secreto, "000000") is False


def test_mismo_codigo_no_se_puede_reusar_para_el_mismo_usuario():
    secreto = totp.generar_secreto()
    codigo = pyotp.TOTP(secreto).now()
    assert totp.verificar_codigo("user-1", secreto, codigo) is True
    assert totp.verificar_codigo("user-1", secreto, codigo) is False, \
        "el mismo codigo TOTP no debe aceptarse dos veces (reuso/replay)"


def test_el_reuso_bloqueado_no_afecta_a_otro_usuario():
    secreto = totp.generar_secreto()
    codigo = pyotp.TOTP(secreto).now()
    assert totp.verificar_codigo("user-1", secreto, codigo) is True
    # Mismo codigo, secreto y timing podrian coincidir para otra cuenta
    # (con su propio secreto) -- el bloqueo de reuso es por cuenta.
    assert totp.verificar_codigo("user-2", secreto, codigo) is True
