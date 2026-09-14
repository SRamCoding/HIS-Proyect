"""Lectura e importación idempotente del catálogo CIE-10 oficial del MINSA."""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.sigarh.general.models import DiagnosticoCIE10


_NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
_CODE = re.compile(r"^\s*([A-Z][0-9]{2}[0-9A-Z]{1,3})\s*-\s*(.+?)\s*$")


@dataclass(frozen=True)
class CIE10Row:
    codigo_cie10: str
    descripcion: str
    capitulo: str
    grupo: str
    categoria: str


def _first_cell(row: ET.Element, shared_strings: list[str]) -> tuple[str, str]:
    cell = row.find("x:c", _NS)
    if cell is None:
        return "", ""
    value = cell.find("x:v", _NS)
    if value is None or value.text is None:
        return cell.attrib.get("s", "0"), ""
    text = shared_strings[int(value.text)] if cell.attrib.get("t") == "s" else value.text
    return cell.attrib.get("s", "0"), text.strip()


def read_minsa_xlsx(path: Path) -> list[CIE10Row]:
    """Extrae únicamente las subcategorías clínicas de la hoja VOLUMEN VIGENTE."""
    with ZipFile(path) as archive:
        shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        shared = [
            "".join(node.text or "" for node in item.findall(".//x:t", _NS))
            for item in shared_root.findall("x:si", _NS)
        ]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = [node.attrib["name"] for node in workbook.findall(".//x:sheet", _NS)]
        if sheets != ["VOLUMEN VIGENTE"]:
            raise ValueError(f"Hoja CIE-10 inesperada: {sheets}")
        worksheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))

    chapter = group = category = ""
    records: list[CIE10Row] = []
    seen: set[str] = set()
    for row in worksheet.findall(".//x:sheetData/x:row", _NS):
        style, value = _first_cell(row, shared)
        if not value:
            continue
        if style in {"3", "8"}:
            chapter = value
        elif style == "5":
            group = value
        elif style == "6":
            category = value
        elif style in {"7", "9"}:
            match = _CODE.fullmatch(value)
            if not match:
                raise ValueError(f"Fila {row.attrib.get('r')}: código CIE-10 inválido: {value}")
            code, description = match.groups()
            if code in seen:
                raise ValueError(f"Código CIE-10 duplicado en el Excel: {code}")
            if not all((chapter, group, category)):
                raise ValueError(f"Fila {row.attrib.get('r')}: jerarquía incompleta para {code}")
            seen.add(code)
            records.append(CIE10Row(code, description, chapter, group, category))

    if len(records) != 12_986:
        raise ValueError(f"Cantidad inesperada de códigos CIE-10: {len(records)}")
    return records


async def import_cie10(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    records: list[CIE10Row],
    *,
    dry_run: bool = False,
    batch_size: int = 1_000,
) -> dict[str, int]:
    """Inserta o actualiza por (tenant_id, código), conservando los UUID existentes."""
    existing = set((await db.scalars(
        DiagnosticoCIE10.__table__.select()
        .with_only_columns(DiagnosticoCIE10.codigo_cie10)
        .where(DiagnosticoCIE10.tenant_id == tenant_id)
    )).all())
    source_codes = {record.codigo_cie10 for record in records}
    result = {
        "total_fuente": len(records),
        "nuevos": len(source_codes - existing),
        "actualizados": len(source_codes & existing),
        "no_incluidos_en_fuente": len(existing - source_codes),
    }
    if dry_run:
        return result

    table = DiagnosticoCIE10.__table__
    for start in range(0, len(records), batch_size):
        values = [
            {
                "id": uuid.uuid4(),
                "tenant_id": tenant_id,
                "codigo_cie10": item.codigo_cie10,
                "descripcion": item.descripcion,
                "capitulo": item.capitulo,
                "grupo": item.grupo,
                "categoria": item.categoria,
                "sexo": "ambos",
                "morbilidad": False,
                "intrahospitalario": False,
                "gestacion": False,
                "is_active": True,
            }
            for item in records[start:start + batch_size]
        ]
        statement = insert(table).values(values)
        await db.execute(statement.on_conflict_do_update(
            constraint="uq_cie10_tenant_codigo",
            set_={
                "descripcion": statement.excluded.descripcion,
                "capitulo": statement.excluded.capitulo,
                "grupo": statement.excluded.grupo,
                "categoria": statement.excluded.categoria,
                "is_active": True,
            },
        ))
    await db.commit()
    return result
