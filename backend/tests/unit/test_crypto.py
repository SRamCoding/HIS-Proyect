import pytest
from app.core.crypto import cifrar, descifrar


def test_cifrar_y_descifrar_recupera_el_valor_original():
    plano = "KHLINHBD65M75KQIKAW7UFTSLKZIE2UD"
    cifrado = cifrar(plano)
    assert cifrado != plano
    assert descifrar(cifrado) == plano


def test_cifrado_no_es_determinista():
    # Fernet incluye un IV/nonce aleatorio -- cifrar el mismo valor dos
    # veces no debe dar el mismo texto cifrado (evita que un dump de la BD
    # revele que dos cuentas comparten secreto por tener el mismo cifrado).
    plano = "MISMO_SECRETO_BASE32"
    assert cifrar(plano) != cifrar(plano)


def test_descifrar_dato_corrupto_lanza_valueerror():
    with pytest.raises(ValueError):
        descifrar("esto-no-es-un-token-fernet-valido")
