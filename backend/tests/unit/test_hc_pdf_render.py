import hashlib
import json
from datetime import date, datetime
from io import BytesIO
from types import SimpleNamespace
import uuid

import main  # noqa: F401 - registra todos los modelos clínicos
from pypdf import PdfReader
from app.hospital.archivo_clinico.pdf import render, evidence_status, SOURCES
from app.hospital.admision.numeracion import numero_historia
from app.core.database import Base


def test_numeracion_dni_con_ceros_y_excepciones():
    assert numero_historia("DNI", "00123456") == "00123456"
    for tipo, doc, nn in [("CE", "00123456", False), ("DNI", None, True), ("DNI", "abc", False)]:
        a, b = numero_historia(tipo, doc, nn), numero_historia(tipo, doc, nn)
        assert a.startswith("HC-") and a != b and len(a) <= 64


def test_fuentes_tienen_propietario_y_orden_correcto():
    seen = {"patients", "clinical_records"}
    for name, owner, parent, _ in SOURCES:
        assert parent in seen
        table = Base.metadata.tables[name]
        assert owner in table.c
        assert any(f.column.table.name == parent for f in table.c[owner].foreign_keys)
        seen.add(name)


def test_pdf_preserva_snapshot_firmado_escapa_texto_y_pagina():
    record = SimpleNamespace(record_number="00123456", previous_record_numbers=["HC-2026-000001"], notes="A & B <control>")
    patient = {"first_name": "María", "last_name_paterno": "Prueba", "birth_date": date(1990, 1, 2), "dni": "00123456"}
    content = {"motivo_consulta": "CONTENIDO CERRADO", "examen_clinico": "Evaluación extensa. " * 2500}
    evidence = {"contenido": content, "sha256": hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
                "medico_nombre": "Médico de prueba", "colegiatura": "123456", "usuario_nombre": "Usuario"}
    data = {"id": uuid.uuid4(), "estado": "firmado", "created_at": datetime(2026, 1, 2), "firmado_at": datetime(2026, 1, 2),
            "motivo_consulta": "CONTENIDO MODIFICADO", "cierre_evidencia": evidence}
    raw = render(record, patient, [{"table": "atenciones_medicas", "title": "Consulta externa", "data": data}], {}, {"name": "Hospital de prueba"})
    pdf = PdfReader(BytesIO(raw))
    text = "\n".join(p.extract_text() for p in pdf.pages)
    assert len(pdf.pages) > 3
    assert "CONTENIDO CERRADO" in text and "CONTENIDO MODIFICADO" not in text
    assert "A & B <control>" in text and "123456" in text
    assert "Integridad de la evidencia verificada" in text
    assert "sin certificado digital" in text
    assert "HC-2026-000001" in text
    assert all("Página" in p.extract_text() for p in pdf.pages)
    evidence["contenido"]["motivo_consulta"] = "alterado"
    assert evidence_status(evidence).startswith("ALERTA")


def test_ficha_no_incluye_contenido_clinico():
    record = SimpleNamespace(record_number="00123456", previous_record_numbers=[], notes=None)
    raw = render(record, {"dni": "00123456", "antecedente_alergias": "NO EXPORTAR EN FICHA"}, [], {}, {}, False)
    text = "\n".join(p.extract_text() for p in PdfReader(BytesIO(raw)).pages)
    assert "NO EXPORTAR EN FICHA" not in text


def test_ficha_incluye_logo_hospital_sin_consultar_urls():
    import base64
    from PIL import Image
    image = BytesIO()
    Image.new("RGB", (300, 150), "green").save(image, format="PNG")
    logo = "data:image/png;base64," + base64.b64encode(image.getvalue()).decode()
    record = SimpleNamespace(record_number="00123456", previous_record_numbers=[], notes=None)
    raw = render(record, {"dni": "00123456"}, [], {}, {"name": "Hospital con logo", "logo_url": logo}, False)
    pdf = PdfReader(BytesIO(raw))
    assert len(pdf.pages[0].images) == 1
    assert "Hospital con logo" in pdf.pages[0].extract_text()
