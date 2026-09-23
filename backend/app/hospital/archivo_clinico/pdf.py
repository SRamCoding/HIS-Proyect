"""Exportación privada del expediente. Solo relaciones clínicas explícitas.

No recupera adjuntos remotos ni datos de donantes, usuarios o movimientos
de almacén. Las evidencias de cierre se leen sin modificarlas.
"""
import hashlib
import json
import uuid
import base64
from datetime import date, datetime, timezone, timedelta
from io import BytesIO
from xml.sax.saxutils import escape

from fastapi import HTTPException
from sqlalchemy import select, or_, and_
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.graphics.barcode.code128 import Code128
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image

from app.core.database import Base
from app.hospital.archivo_clinico.service import _historias


# (tabla, propietario, tabla del propietario, título). El orden respeta las FK.
SOURCES = [
    ("citas", "patient_id", "patients", "Cita"),
    ("triajes", "cita_id", "citas", "Triaje de consulta externa"),
    ("atenciones_medicas", "cita_id", "citas", "Atención de consulta externa"),
    ("atencion_diagnosticos", "atencion_medica_id", "atenciones_medicas", "Diagnóstico de consulta externa"),
    ("admisiones_emergencia", "patient_id", "patients", "Ingreso a emergencia"),
    ("triajes_emergencia", "admision_id", "admisiones_emergencia", "Triaje de emergencia"),
    ("atenciones_emergencia", "admision_id", "admisiones_emergencia", "Atención de emergencia"),
    ("emergencia_diagnosticos", "atencion_emergencia_id", "atenciones_emergencia", "Diagnóstico de emergencia"),
    ("emergencia_destinos", "atencion_id", "atenciones_emergencia", "Destino de emergencia"),
    ("hospitalizaciones", "patient_id", "patients", "Hospitalización"),
    ("hosp_notas_evolucion", "hospitalizacion_id", "hospitalizaciones", "Evolución hospitalaria"),
    ("hosp_consentimientos", "hospitalizacion_id", "hospitalizaciones", "Consentimiento registrado"),
    ("ordenes_laboratorio", "patient_id", "patients", "Orden de laboratorio"),
    ("orden_laboratorio_items", "orden_id", "ordenes_laboratorio", "Examen solicitado de laboratorio"),
    ("lab_movimientos", "orden_id", "ordenes_laboratorio", "Procesamiento de laboratorio"),
    ("lab_movimiento_items", "movimiento_id", "lab_movimientos", "Resultado de laboratorio"),
    ("lab_fichas_covid", "patient_id", "patients", "Ficha COVID"),
    ("ordenes_imagen", "patient_id", "patients", "Orden de imágenes"),
    ("orden_imagen_items", "orden_id", "ordenes_imagen", "Examen solicitado de imágenes"),
    ("imagen_movimientos", "orden_id", "ordenes_imagen", "Procesamiento de imágenes"),
    ("imagen_movimiento_items", "movimiento_id", "imagen_movimientos", "Resultado de imágenes"),
    ("recetas", "atencion_medica_id", "atenciones_medicas", "Receta"),
    ("receta_items", "receta_id", "recetas", "Medicación prescrita"),
    ("farmacia_dispensaciones", "receta_id", "recetas", "Dispensación"),
    ("farmacia_dispensacion_items", "dispensacion_id", "farmacia_dispensaciones", "Medicación dispensada"),
    ("farmacotecnia_ordenes", "receta_id", "recetas", "Preparación farmacéutica"),
    ("interconsultas", "patient_id", "patients", "Interconsulta"),
    ("referencias", "patient_id", "patients", "Referencia y contrarreferencia"),
    ("banco_sangre_solicitudes", "patient_id", "patients", "Solicitud de sangre"),
    ("banco_sangre_solicitud_componentes", "solicitud_id", "banco_sangre_solicitudes", "Componente solicitado"),
    ("banco_sangre_movimientos", "solicitud_id", "banco_sangre_solicitudes", "Entrega de componente sanguíneo"),
    ("hemodialisis_pacientes", "patient_id", "patients", "Evaluación de hemodiálisis"),
    ("hemodialisis_sesiones", "paciente_hemodialisis_id", "hemodialisis_pacientes", "Sesión de hemodiálisis"),
    ("medicina_fisica_sesiones", "patient_id", "patients", "Sesión de medicina física"),
    ("procedimientos_atenciones", "patient_id", "patients", "Procedimiento"),
    ("servicio_social_evaluaciones", "patient_id", "patients", "Evaluación social"),
    ("servicio_social_gestiones", "evaluacion_social_id", "servicio_social_evaluaciones", "Gestión social"),
    ("epidemiologia_fichas", "patient_id", "patients", "Ficha epidemiológica"),
    ("sis_formatos_fua", "patient_id", "patients", "Formato de atención SIS"),
    ("telesalud_solicitudes", "patient_id", "patients", "Telesalud"),
    ("salud_ambiental_certificados_defuncion", "patient_id", "patients", "Registro de defunción"),
    ("firma_electronica_registros", "patient_id", "patients", "Registro de firma"),
    ("clinical_record_movements", "clinical_record_id", "clinical_records", "Movimiento de historia clínica"),
]

LABELS = {
    "first_name": "Primer nombre", "second_name": "Segundo nombre",
    "last_name_paterno": "Apellido paterno", "last_name_materno": "Apellido materno",
    "birth_date": "Fecha de nacimiento", "gender": "Sexo", "marital_status": "Estado civil",
    "document_type": "Tipo de documento", "dni": "Documento", "is_nn": "Paciente no identificado",
    "ethnicity": "Etnia", "language": "Idioma", "phone": "Teléfono", "email": "Correo",
    "phone_is_whatsapp": "Teléfono con WhatsApp", "birth_same_as_address": "Nacimiento en la localidad del domicilio",
    "education_level": "Grado de instrucción", "occupation": "Ocupación",
    "address": "Dirección", "department_id": "Departamento", "province_id": "Provincia",
    "district_id": "Distrito", "populated_center": "Centro poblado", "country": "País",
    "birth_department_id": "Departamento de nacimiento", "birth_province_id": "Provincia de nacimiento",
    "birth_district_id": "Distrito de nacimiento", "birth_country": "País de nacimiento",
    "birth_populated_center": "Centro poblado de nacimiento", "insurance_type": "Seguro",
    "insurance_number": "Número de seguro", "created_at": "Fecha de registro",
    "updated_at": "Última actualización", "firmado_at": "Fecha de cierre",
    "from_location": "Servicio de origen", "to_location": "Servicio de destino",
    "moved_by": "Responsable", "notes": "Observaciones", "sha256": "Huella SHA-256",
    "antecedentes_snapshot": "Antecedentes registrados en la atención",
    "cierre_evidencia": "Evidencia del cierre",
}
LIMA = timezone(timedelta(hours=-5))


def label(key):
    return LABELS.get(key, key.removesuffix("_id").replace("_", " ").capitalize())


def scalar(value):
    if value is None or value == "":
        return "No registrado"
    if isinstance(value, bool):
        return "Sí" if value else "No"
    if isinstance(value, datetime):
        return value.replace(tzinfo=value.tzinfo or timezone.utc).astimezone(LIMA).strftime("%d/%m/%Y %H:%M (Lima)")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    return str(value)


def evidence_status(evidence):
    if not evidence or not isinstance(evidence.get("contenido"), dict) or not evidence.get("sha256"):
        return "Evidencia de cierre no disponible"
    digest = hashlib.sha256(json.dumps(evidence["contenido"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return "Integridad de la evidencia verificada" if digest == evidence["sha256"] else "ALERTA: la evidencia no coincide con su huella registrada"


async def collect(db, tenant_id, record_id, complete=True):
    row = (await db.execute(_historias(tenant_id).where(
        Base.metadata.tables["clinical_records"].c.id == record_id))).first()
    if row is None:
        raise HTTPException(404, "Historia clínica no encontrada")
    record, patient = row
    patient_data = {c.name: getattr(patient, c.name) for c in patient.__table__.columns}
    ids = {"patients": [patient.id], "clinical_records": [record.id]}
    entries = []
    if complete:
        for name, owner, parent, title in SOURCES:
            table = Base.metadata.tables[name]
            rows_by_id = {}
            # Evita sobrepasar el límite de parámetros de PostgreSQL en HC extensas.
            relationships = [(owner, ids.get(parent, []))]
            # Órdenes antiguas pueden guardar solo el origen clínico, sin
            # patient_id. Admitir ese origen exclusivamente si patient_id es NULL.
            if owner == "patient_id":
                for fk in table.foreign_keys:
                    if fk.parent.name in {"atencion_medica_id", "atencion_emergencia_id", "emergencia_id", "hospitalizacion_id"}:
                        relationships.append((fk.parent.name, ids.get(fk.column.table.name, [])))
            for link, owners in relationships:
                for start in range(0, len(owners), 1000):
                    query = select(table).where(table.c[link].in_(owners[start:start + 1000]))
                    if "tenant_id" in table.c:
                        query = query.where(table.c.tenant_id == tenant_id)
                    if "patient_id" in table.c:
                        query = query.where(or_(table.c.patient_id == patient.id,
                            and_(table.c.patient_id.is_(None), link != "patient_id")))
                    for r in (await db.execute(query)).mappings():
                        rows_by_id[r["id"]] = dict(r)
            rows = list(rows_by_id.values())
            ids[name] = [r["id"] for r in rows]
            entries.extend({"table": name, "title": title, "data": r} for r in rows)
    # Solo campos descriptivos de catálogos; nunca serializar empleados/usuarios.
    lookup = {}
    for table_name, data in [("patients", patient_data), *[(e["table"], e["data"]) for e in entries]]:
        table = Base.metadata.tables[table_name]
        for fk in table.foreign_keys:
            target = fk.column.table
            value = data.get(fk.parent.name)
            extra_catalogs = {
                "farmacia_lotes": ("numero_lote", "fecha_vencimiento", "registro_sanitario"),
                "banco_sangre_componentes": ("numero_componente", "tipo", "grupo_abo", "factor_rh", "fecha_vencimiento"),
                "programaciones_medicas": ("codigo", "fecha", "turno", "hora_inicio", "hora_fin"),
                "medicina_fisica_programaciones": ("fecha", "turno", "hora_inicio", "hora_fin"),
                "medicina_fisica_programas": ("nombre", "descripcion"),
            }
            if value is None or not (target.name.startswith(("sigarh_", "ubigeo_")) or target.name in extra_catalogs):
                continue
            key = (target.name, str(value))
            if key not in lookup:
                names = [n for n in extra_catalogs.get(target.name, ("codigo_cie10", "codigo", "descripcion", "nombre", "nombre_generico", "nombre_comercial",
                                    "apellido_paterno", "apellido_materno", "nombres", "numero_cmp", "numero_colegiatura")) if n in target.c]
                if not names:
                    continue
                query = select(*(target.c[n] for n in names)).where(fk.column == value)
                if "tenant_id" in target.c:
                    query = query.where(target.c.tenant_id == tenant_id)
                found = (await db.execute(query)).first()
                lookup[key] = " / ".join(scalar(v) for v in found if v is not None) if found else "Referencia no disponible"
    # CIE-10 que figura en la instantánea, incluso si el diagnóstico actual
    # fue corregido posteriormente. La descripción se identifica como catálogo.
    dx_table = Base.metadata.tables["sigarh_diagnosticos_cie10"]
    for entry in entries:
        content = (entry["data"].get("cierre_evidencia") or {}).get("contenido") or {}
        for dx in content.get("diagnosticos") or []:
            dxid = dx.get("id")
            try:
                value = uuid.UUID(str(dxid))
            except (ValueError, TypeError):
                continue
            key = (dx_table.name, str(value))
            if key not in lookup:
                found = (await db.execute(select(dx_table.c.codigo_cie10, dx_table.c.descripcion).where(
                    dx_table.c.id == value, dx_table.c.tenant_id == tenant_id))).first()
                lookup[key] = " / ".join(found) if found else "Referencia no disponible"
    for entry in entries:
        data = entry["data"]
        number = data.get("numero_orden") or data.get("numero_cuenta") or data.get("numero_hospitalizacion") or str(data["id"])
        lookup[(entry["table"], str(data["id"]))] = f"{entry['title']} · {number} · {scalar(data.get('created_at'))}"
    lookup[("clinical_records", str(record.id))] = record.record_number
    return record, patient_data, entries, lookup


def render(record, patient, entries, lookup, hospital, complete=True):
    output = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="HCBody", parent=styles["BodyText"], fontSize=9, leading=13, spaceAfter=5, splitLongWords=True))
    story = []
    def paragraph(text, style="HCBody"):
        story.append(Paragraph(escape(str(text)).replace("\n", "<br/>"), styles[style]))
    def heading(text):
        paragraph(text, "Heading2")
    def resolved_value(key, value, table_name):
        table = Base.metadata.tables.get(table_name) if table_name else None
        if table is not None and key in table.c:
            for fk in table.c[key].foreign_keys:
                value = lookup.get((fk.column.table.name, str(value)), value)
        if key == "gender":
            value = {"M": "Masculino", "F": "Femenino"}.get(value, value)
        return value
    def grid(keys):
        if not keys:
            paragraph("No registrado")
            return
        cells = [Paragraph(escape(f"{label(k)}: {scalar(resolved_value(k, patient.get(k), 'patients'))}"), styles["HCBody"]) for k in keys]
        if len(cells) % 2:
            cells.append(Paragraph("", styles["HCBody"]))
        rows = [cells[i:i + 2] for i in range(0, len(cells), 2)]
        table = Table(rows, colWidths=[255, 255], hAlign="LEFT")
        table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                  ("LINEBELOW", (0, 0), (-1, -1), .25, colors.HexColor("#CAD5D2")),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        story.append(table)
    def fields(data, table_name=None):
        table = Base.metadata.tables.get(table_name) if table_name else None
        for key, value in data.items():
            if key in {"id", "tenant_id", "patient_id", "cierre_evidencia"}:
                continue
            if key.endswith("_id"):
                resolved = None
                if table is not None and key in table.c:
                    for fk in table.c[key].foreign_keys:
                        resolved = lookup.get((fk.column.table.name, str(value)))
                if not resolved:
                    continue
                value = resolved
            if isinstance(value, dict):
                heading(label(key))
                fields(value)
            elif isinstance(value, list):
                heading(label(key))
                if not value:
                    paragraph("Sin registros")
                for item in value:
                    if isinstance(item, dict):
                        if key == "diagnosticos" and item.get("id"):
                            paragraph("Diagnóstico (catálogo): " + lookup.get(("sigarh_diagnosticos_cie10", str(item["id"])), str(item["id"])))
                        fields(item)
                        story.append(Spacer(1, 4))
                    else:
                        paragraph(scalar(item))
            else:
                paragraph(f"{label(key)}: {scalar(value)}")

    logo = hospital.get("logo_url") or ""
    if logo.startswith("data:image/png;base64,"):
        try:
            logo_image = Image(BytesIO(base64.b64decode(logo.split(",", 1)[1], validate=True)))
            scale = min(140 / logo_image.imageWidth, 48 / logo_image.imageHeight)
            logo_image.drawWidth = logo_image.imageWidth * scale
            logo_image.drawHeight = logo_image.imageHeight * scale
            logo_image.hAlign = "CENTER"
            story.extend([logo_image, Spacer(1, 6)])
        except (ValueError, OSError):
            pass
    paragraph(hospital.get("name") or "Hospital", "Title")
    ruc = hospital.get("ruc")
    paragraph(" · ".join(filter(None, [f"RUC {ruc}" if ruc else None, hospital.get("address"), hospital.get("phone")])))
    paragraph("FICHA DE HISTORIA CLÍNICA", "Heading1")
    paragraph(f"HC: {record.record_number}", "Heading2")
    if record.previous_record_numbers:
        paragraph("Números anteriores: " + ", ".join(record.previous_record_numbers))
    heading("Datos del titular")
    personal = ["last_name_paterno", "last_name_materno", "first_name", "second_name", "birth_date", "gender", "marital_status",
                "document_type", "dni", "is_nn", "ethnicity", "language", "phone", "phone_is_whatsapp", "email", "education_level", "occupation"]
    grid(personal)
    heading("Domicilio y lugar de nacimiento")
    grid([k for k in patient if k in {"address", "department_id", "province_id", "district_id", "populated_center", "country"} or k.startswith("birth_") and k != "birth_date"])
    heading("Seguro y observaciones")
    grid(["insurance_type", "insurance_number"])
    paragraph(record.notes or "Sin observaciones registradas")
    story.append(Spacer(1, 10))
    story.append(Code128(record.record_number, barHeight=32, barWidth=0.65, humanReadable=True))
    if complete:
        story.append(PageBreak())
        heading("Antecedentes actuales del paciente")
        fields({k: v for k, v in patient.items() if k.startswith("antecedent")})
        paragraph("Los antecedentes anteriores corresponden al registro actual. Cada cierre conserva su propia evidencia histórica.")
        heading("Expediente clínico y movimientos")
        paragraph("Incluye registros estructurados vinculados a este paciente. Los adjuntos externos se mencionan por su referencia; no se incorporan sus archivos. Fechas y horas en Lima.")
        if not entries:
            paragraph("No hay atenciones ni movimientos registrados.")
        entries = sorted(entries, key=lambda e: (str(e["data"].get("created_at") or ""), e["table"], str(e["data"].get("id"))))
        for entry in entries:
            data = entry["data"]
            heading(entry["title"] + " — " + scalar(data.get("created_at")))
            paragraph("Referencia del registro: " + str(data["id"]))
            evidence = data.get("cierre_evidencia")
            is_attention = entry["table"] in {"atenciones_medicas", "atenciones_emergencia"}
            if is_attention and data.get("estado") == "firmado":
                paragraph("ATENCIÓN CERRADA — cierre interno sin certificado digital")
                paragraph("Fecha de cierre: " + scalar(data.get("firmado_at")))
                paragraph(evidence_status(evidence))
                if evidence and isinstance(evidence.get("contenido"), dict):
                    heading("Contenido conservado al cierre")
                    fields({k: v for k, v in evidence["contenido"].items() if k != "estado"})
                    heading("Responsable del cierre")
                    fields({k: evidence.get(k) for k in ("medico_nombre", "colegiatura", "usuario_nombre", "sha256")})
                    supplemental = {k: v for k, v in data.items() if k not in evidence["contenido"]
                                    and k not in {"id", "tenant_id", "cita_id", "admision_id", "cierre_evidencia", "estado", "firmado_at", "firmado_por_id", "created_at", "updated_at"} and v is not None}
                    if supplemental:
                        heading("Información complementaria actual (fuera de la evidencia de cierre)")
                        fields(supplemental, entry["table"])
                else:
                    paragraph("Registro histórico sin instantánea verificable. Los siguientes datos corresponden al registro disponible.")
                    fields(data, entry["table"])
            else:
                if is_attention:
                    paragraph("BORRADOR — SIN FIRMA")
                fields(data, entry["table"])
    generated = scalar(datetime.now(timezone.utc))
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#176B60"))
        canvas.line(40, 42, A4[0] - 40, 42)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(40, 30, f"HC {record.record_number} · Documento confidencial")
        canvas.drawRightString(A4[0] - 40, 30, f"Página {doc.page}")
        canvas.setFont("Helvetica", 7)
        canvas.drawString(40, 19, "Exportado: " + generated)
        canvas.restoreState()
    SimpleDocTemplate(output, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=35, bottomMargin=57,
                      title="Historia clínica", author=hospital.get("name") or "Hospital").build(story, onFirstPage=footer, onLaterPages=footer)
    return output.getvalue()
