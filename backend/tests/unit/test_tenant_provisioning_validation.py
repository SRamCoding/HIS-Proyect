import pytest
from pydantic import ValidationError

from app.tenants.hospitales.schemas import TenantCreate


def valid_payload(**overrides):
    payload = {
        "name": "Hospital de Prueba",
        "domain": "hospital-prueba.techquk.com",
        "ruc": "20123456789",
        "hospital_level": "II-1",
        "active_modules": ["admision", "sigarh_mantenimiento"],
        "admin_name": "Administrador Hospital",
        "admin_email": "admin@hospital.test",
        "admin_password": "Clave-Segura1",
        "sigarh_name": "Responsable RRHH",
        "sigarh_email": "rrhh@hospital.test",
        "sigarh_password": "Otra-Clave2",
    }
    payload.update(overrides)
    return payload


def test_normaliza_dominio_correos_y_modulos():
    data = TenantCreate(**valid_payload(
        domain="HOSPITAL-PRUEBA.TECHQUK.COM.",
        admin_email="ADMIN@HOSPITAL.TEST",
        active_modules=["ADMISION", " sigarh_mantenimiento "],
    ))
    assert data.domain == "hospital-prueba.techquk.com"
    assert data.admin_email == "admin@hospital.test"
    assert data.active_modules == ["admision", "sigarh_mantenimiento"]


@pytest.mark.parametrize("domain", [
    "hospital-prueba.erp.local",
    "api.techquk.com",
    "hospital prueba.techquk.com",
    "-hospital.techquk.com",
])
def test_rechaza_dominios_invalidos_o_reservados(domain):
    with pytest.raises(ValidationError):
        TenantCreate(**valid_payload(domain=domain))


def test_rechaza_modulos_duplicados():
    with pytest.raises(ValidationError):
        TenantCreate(**valid_payload(active_modules=["admision", "admision"]))


def test_exige_usuarios_iniciales_completos_y_distintos():
    with pytest.raises(ValidationError):
        TenantCreate(**valid_payload(sigarh_name=None))
    with pytest.raises(ValidationError):
        TenantCreate(**valid_payload(sigarh_email="admin@hospital.test"))


def test_valida_ruc():
    with pytest.raises(ValidationError):
        TenantCreate(**valid_payload(ruc="123"))
