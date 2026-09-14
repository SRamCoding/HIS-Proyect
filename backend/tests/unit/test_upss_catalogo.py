import uuid

from app.sigarh.mantenimiento.upss_catalogo import (
    ESPECIALIDADES_SERVICIO,
    RECOMENDADAS,
    SERVICIOS,
    UPSS,
    stable_id,
)
from app.sigarh.rrhh.especialidades_catalogo import ESPECIALIDADES


def test_catalogo_upss_cubre_categorias_ipress():
    codigos = {codigo for codigo, _, _ in UPSS}

    assert len(UPSS) == 15
    assert set(RECOMENDADAS) == {
        "I-1",
        "I-2",
        "I-3",
        "I-4",
        "II-1",
        "II-2",
        "II-E",
        "III-1",
        "III-2",
        "III-E",
    }
    assert all(recomendadas <= codigos for recomendadas in RECOMENDADAS.values())
    assert "UPSS-UCI" in RECOMENDADAS["II-2"]
    assert "UPSS-HD" in RECOMENDADAS["III-1"]


def test_servicios_referencian_upss_y_especialidades_existentes():
    codigos_upss = {codigo for codigo, _, _ in UPSS}
    codigos_servicio = {codigo for codigo, _, _ in SERVICIOS}
    especialidades = set(ESPECIALIDADES)

    assert set(ESPECIALIDADES_SERVICIO) == codigos_servicio
    assert all(set(upss) <= codigos_upss for _, _, upss in SERVICIOS)
    assert all(
        set(nombres) <= especialidades for nombres in ESPECIALIDADES_SERVICIO.values()
    )


def test_ids_de_catalogo_son_estables_y_aislados_por_hospital():
    tenant_a = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    tenant_b = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")

    assert stable_id("upss", tenant_a, "UPSS-CE") == stable_id(
        "upss", tenant_a, "UPSS-CE"
    )
    assert stable_id("upss", tenant_a, "UPSS-CE") != stable_id(
        "upss", tenant_b, "UPSS-CE"
    )
