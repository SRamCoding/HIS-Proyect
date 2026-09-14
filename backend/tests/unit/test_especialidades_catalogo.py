import uuid
import pytest
from pydantic import ValidationError

from app.sigarh.rrhh.especialidades_catalogo import (
    ESPECIALIDADES,
    SUBESPECIALIDADES,
    RECOMENDADAS_POR_NIVEL,
    catalogo_id,
    oferta_id,
)
from app.sigarh.rrhh.schemas import EspecialidadCreate


def test_catalogo_conareme_2026_completo_y_jerarquico():
    assert len(ESPECIALIDADES) == 44
    assert len(SUBESPECIALIDADES) == 40
    assert len(set(ESPECIALIDADES)) == 44
    assert len({nombre for nombre, _, _ in SUBESPECIALIDADES}) == 40
    assert all(parent in ESPECIALIDADES for _, parent, _ in SUBESPECIALIDADES)
    assert all(set(requisitos) <= set(ESPECIALIDADES) for _, _, requisitos in SUBESPECIALIDADES)


def test_ids_son_estables_por_catalogo_y_hospital():
    cardiologia = catalogo_id("especialidad", "CARDIOLOGÍA")
    assert cardiologia == catalogo_id("especialidad", "CARDIOLOGÍA")
    lima = uuid.UUID("80f3d4ad-248f-47db-9a5f-3cb5ac09cd32")
    reque = uuid.UUID("55540838-24a6-4e78-843b-f9b93e57733a")
    assert oferta_id(lima, cardiologia) != oferta_id(reque, cardiologia)


def test_nivel_superior_incluye_base_del_nivel_anterior():
    assert RECOMENDADAS_POR_NIVEL["II-1"] < RECOMENDADAS_POR_NIVEL["II-2"]
    assert RECOMENDADAS_POR_NIVEL["II-2"] < RECOMENDADAS_POR_NIVEL["III-1"]
    assert RECOMENDADAS_POR_NIVEL["III-1"] <= RECOMENDADAS_POR_NIVEL["III-2"]


def test_subespecialidad_propia_exige_especialidad_principal():
    with pytest.raises(ValidationError):
        EspecialidadCreate(nombre="Subespecialidad local", tipo="subespecialidad")
    parent_id = uuid.uuid4()
    value = EspecialidadCreate(
        nombre="Subespecialidad local",
        tipo="subespecialidad",
        parent_id=parent_id,
    )
    assert value.parent_id == parent_id
