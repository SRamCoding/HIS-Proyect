from pathlib import Path

from app.sigarh.general.cie10_import import read_minsa_xlsx


FILE = Path(__file__).parents[1] / "data" / "cie10" / "CIE10_MINSA_OFICIAL.xlsx"


def test_read_official_minsa_catalog_with_hierarchy():
    records = read_minsa_xlsx(FILE)

    assert len(records) == 12_986
    assert len({record.codigo_cie10 for record in records}) == len(records)
    first = records[0]
    assert first.codigo_cie10 == "A000"
    assert first.descripcion.startswith("COLERA DEBIDO A VIBRIO CHOLERAE")
    assert first.capitulo.startswith("CAPITULO I:")
    assert first.grupo.startswith("(A00 - A09)")
    assert first.categoria == "A00 - COLERA"
    assert records[-1].codigo_cie10 == "U85X"


def test_catalog_includes_six_character_minsa_extensions():
    records = {record.codigo_cie10: record for record in read_minsa_xlsx(FILE)}

    assert records["Z30051"].descripcion == "PRESCRIPCION INICIAL DE METODO INYECTABLE MENSUAL"
