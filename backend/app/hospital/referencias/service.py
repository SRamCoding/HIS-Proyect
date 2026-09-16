from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.dialects.postgresql import insert

from app.hospital.referencias.models import ReferenciaCorrelativo
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import Referencia
from app.hospital.emergencia.models import DestinoEmergencia, AtencionEmergencia, AdmisionEmergencia
from app.sigarh.general.models import DiagnosticoCIE10


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


def columns(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


async def own(db, model, tid, obj_id, lock=False):
    q = select(model).where(model.id == obj_id, model.tenant_id == tid)
    if lock:
        q = q.with_for_update().execution_options(populate_existing=True)
    obj = (await db.execute(q)).scalar_one_or_none()
    if obj is None:
        raise HTTPException(404, detail="Registro no encontrado en este hospital")
    return obj


async def number(db, tid, kind):
    stmt = insert(ReferenciaCorrelativo).values(tenant_id=tid, tipo=kind, valor=1)
    stmt = stmt.on_conflict_do_update(index_elements=["tenant_id", "tipo"],
        set_={"valor": ReferenciaCorrelativo.valor + 1}).returning(ReferenciaCorrelativo.valor)
    n = await db.scalar(stmt)
    return f"{kind}-{tid.hex[:8]}-{n:08d}"


# ─── Consulta / listado ─────────────────────────────────────────────────────

def _ref_query(tid):
    return (select(Referencia, Patient, ClinicalRecord.record_number, DiagnosticoCIE10)
        .join(Patient, Patient.id == Referencia.patient_id)
        .outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id)
        .outerjoin(DiagnosticoCIE10, DiagnosticoCIE10.id == Referencia.diagnostico_id)
        .where(Referencia.tenant_id == tid))


async def _tenant_destino_nombre(ref):
    if not ref.tenant_destino_id:
        return None
    from app.core.tenant_db import get_tenant_by_id
    t = await get_tenant_by_id(ref.tenant_destino_id)
    return t.name if t else None


async def _ref_out(row):
    ref, paciente, hc, diagnostico = row
    return dict(columns(ref), paciente=paciente.full_name, dni=paciente.dni, historia=hc,
        diagnostico_codigo=diagnostico.codigo_cie10 if diagnostico else None,
        diagnostico_descripcion=diagnostico.descripcion if diagnostico else None,
        tenant_destino_nombre=await _tenant_destino_nombre(ref),
        origen="EMERGENCIA" if ref.atencion_emergencia_id else "CONSULTA_EXTERNA",
        destino_tipo="INTERNO" if ref.tenant_destino_id else "EXTERNO")


async def list_referencias(db, tid, f, page=1, size=20):
    q = _ref_query(tid)
    if f.get("q"):
        for term in f["q"].split():
            q = q.where(or_(*[c.icontains(term, autoescape=True) for c in
                (Patient.first_name, Patient.last_name_paterno, Patient.last_name_materno,
                 Patient.dni, Referencia.numero_referencia)]))
    if f.get("estado"):
        q = q.where(Referencia.estado == f["estado"])
    total = await db.scalar(select(func.count()).select_from(q.order_by(None).subquery()))
    rows = (await db.execute(q.order_by(Referencia.created_at.desc()).offset((page-1)*size).limit(size))).all()
    return {"items": [await _ref_out(r) for r in rows], "total": total, "page": page, "page_size": size}


async def referencia_detalle(db, tid, referencia_id):
    row = (await db.execute(_ref_query(tid).where(Referencia.id == referencia_id))).first()
    if not row:
        raise HTTPException(404, detail="Referencia no encontrada")
    return await _ref_out(row)


# ─── Admisión desde Emergencia ──────────────────────────────────────────────

async def destinos_emergencia_pendientes(db, tid):
    rows = (await db.execute(select(DestinoEmergencia, AtencionEmergencia, AdmisionEmergencia, Patient)
        .join(AtencionEmergencia, AtencionEmergencia.id == DestinoEmergencia.atencion_id)
        .join(AdmisionEmergencia, AdmisionEmergencia.id == AtencionEmergencia.admision_id)
        .join(Patient, Patient.id == AdmisionEmergencia.patient_id)
        .where(DestinoEmergencia.tenant_id == tid, DestinoEmergencia.destino == "REFERENCIA",
               DestinoEmergencia.estado == "pendiente")
        .order_by(DestinoEmergencia.created_at))).all()
    return [{"destino_id": d.id, "numero_cuenta": adm.numero_cuenta, "paciente_nombre": p.full_name,
        "paciente_dni": p.dni, "motivo_consulta": a.motivo_consulta, "created_at": d.created_at} for d, a, adm, p in rows]


async def admitir_desde_emergencia(db, tid, user, data):
    destino = await own(db, DestinoEmergencia, tid, data.destino_id, lock=True)
    if destino.destino != "REFERENCIA":
        raise HTTPException(422, detail="Este destino de emergencia no corresponde a referencia")
    if destino.estado != "pendiente":
        raise HTTPException(409, detail="Este destino ya fue resuelto")
    atencion = await own(db, AtencionEmergencia, tid, destino.atencion_id)
    admision = await own(db, AdmisionEmergencia, tid, atencion.admision_id, lock=True)
    if await db.scalar(select(Referencia.id).where(Referencia.atencion_emergencia_id == atencion.id)):
        raise HTTPException(409, detail="Esta atención de emergencia ya generó una referencia")
    if data.diagnostico_id and not await db.scalar(select(DiagnosticoCIE10.id).where(
        DiagnosticoCIE10.id == data.diagnostico_id, DiagnosticoCIE10.tenant_id == tid, DiagnosticoCIE10.is_active.is_(True))):
        raise HTTPException(422, detail="Seleccione un diagnóstico activo de este hospital")
    if data.tenant_destino_id:
        # Tenant vive en la BD central, no en la de este hospital -- se valida
        # ahí (get_tenants_disponibles abre su propia sesión central).
        from app.hospital.consulta_externa.service import get_tenants_disponibles
        disponibles = {str(t.id) for t in await get_tenants_disponibles(db, tid)}
        if str(data.tenant_destino_id) not in disponibles:
            raise HTTPException(422, detail="Hospital destino no válido")

    ref = Referencia(tenant_id=tid, atencion_emergencia_id=atencion.id, patient_id=admision.patient_id,
        registrado_por=actor(user), numero_referencia=await number(db, tid, "REF"),
        **data.model_dump(exclude={"destino_id"}))
    db.add(ref)
    destino.estado, destino.resolved_at = "completado", datetime.utcnow()
    destino.observacion = f"Referencia {ref.numero_referencia} generada"
    admision.estado = "derivado"
    await db.flush()
    await db.commit()
    return await referencia_detalle(db, tid, ref.id)


# ─── Resolución y contrarreferencia ──────────────────────────────────────────

async def resolver(db, tid, user, referencia_id, data):
    ref = await own(db, Referencia, tid, referencia_id, lock=True)
    if ref.estado != "enviada":
        raise HTTPException(409, detail="Solo se puede aceptar o rechazar una referencia recién enviada")
    columns(ref)
    ref.estado, ref.observacion_resolucion = data.estado, data.observacion_resolucion
    await db.flush()
    await db.commit()
    return await referencia_detalle(db, tid, ref.id)


async def registrar_contrarreferencia(db, tid, user, referencia_id, data):
    ref = await own(db, Referencia, tid, referencia_id, lock=True)
    if ref.estado not in ("enviada", "aceptada"):
        raise HTTPException(409, detail="No se puede registrar contrarreferencia de una referencia rechazada o ya contrarreferida")
    if data.diagnostico_contrarreferencia_id and not await db.scalar(select(DiagnosticoCIE10.id).where(
        DiagnosticoCIE10.id == data.diagnostico_contrarreferencia_id, DiagnosticoCIE10.tenant_id == tid, DiagnosticoCIE10.is_active.is_(True))):
        raise HTTPException(422, detail="Seleccione un diagnóstico activo de este hospital")
    columns(ref)
    for k, v in data.model_dump().items():
        setattr(ref, k, v)
    ref.estado = "contrarreferida"
    await db.flush()
    await db.commit()
    return await referencia_detalle(db, tid, ref.id)


# ─── Catálogos y documentos ─────────────────────────────────────────────────

async def catalogs(db, tid, kind, q=""):
    if kind == "diagnosticos":
        query = select(DiagnosticoCIE10).where(DiagnosticoCIE10.tenant_id == tid, DiagnosticoCIE10.is_active.is_(True))
        if q:
            for term in q.split():
                query = query.where(or_(DiagnosticoCIE10.codigo_cie10.icontains(term, autoescape=True),
                    DiagnosticoCIE10.descripcion.icontains(term, autoescape=True)))
        objs = (await db.scalars(query.order_by(DiagnosticoCIE10.codigo_cie10).limit(50))).all()
        return [{"id": x.id, "codigo": x.codigo_cie10, "descripcion": x.descripcion} for x in objs]
    if kind == "tenants":
        from app.hospital.consulta_externa.service import get_tenants_disponibles
        return [{"id": t.id, "nombre": t.name} for t in await get_tenants_disponibles(db, tid)]
    raise HTTPException(404, detail="Catálogo no encontrado")


async def patients(db, tid, q):
    query = select(Patient, ClinicalRecord.record_number).outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id).where(Patient.tenant_id == tid)
    for term in q.split():
        query = query.where(or_(*[c.icontains(term, autoescape=True) for c in
            (Patient.dni, Patient.first_name, Patient.last_name_paterno, Patient.last_name_materno, ClinicalRecord.record_number)]))
    return [{"id": p.id, "nombre": p.full_name, "dni": p.dni, "historia": hc}
            for p, hc in (await db.execute(query.order_by(Patient.last_name_paterno, Patient.id).limit(30))).all()]


def pdf_document(title, hospital, sections):
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
    stream = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CellRef", fontName="Helvetica", fontSize=8, leading=11, wordWrap="CJK"))
    def para(value):
        return Paragraph(escape(str(value if value is not None else "-")).replace("\n", "<br/>"), styles["CellRef"])
    story = [Paragraph(escape(hospital), styles["Title"]), Paragraph(escape(title), styles["Heading1"]), Spacer(1, 12)]
    for heading, headers, rows, widths in sections:
        story.append(Paragraph(escape(heading), styles["Heading2"]))
        table = LongTable([[para(v) for v in headers]] + [[para(v) for v in row] for row in rows],
                          colWidths=widths, repeatRows=1, splitInRow=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e7f1f8")),
            ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#bccbd5")),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.extend([table, Spacer(1, 12)])
    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.drawString(36, 22, "Referencia - Norma Técnica N.° 018-MINSA/DGSP-V.01 - Documento generado por el sistema")
        canvas.drawRightString(A4[0]-36, 22, f"Página {doc.page}")
    SimpleDocTemplate(stream, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=30,
                      bottomMargin=38, title=title).build(story, onFirstPage=footer, onLaterPages=footer)
    return stream.getvalue()


async def referencia_pdf(db, tid, referencia_id):
    d = await referencia_detalle(db, tid, referencia_id)
    from app.core.tenant_db import get_tenant_by_id
    tenant = await get_tenant_by_id(tid)
    hospital = tenant.name if tenant else None
    rows = [
        ["Paciente", d["paciente"], "Documento", d["dni"]],
        ["Historia clínica", d["historia"], "N.° referencia", d["numero_referencia"]],
        ["Destino", d["nombre_ipress_destino"] or d["tenant_destino_nombre"] or "—", "Especialidad", d["especialidad_destino"] or "—"],
        ["Diagnóstico", f"{d['diagnostico_codigo'] or ''} {d['diagnostico_descripcion'] or ''}".strip() or "—", "Estado", d["estado"]],
        ["Registrado por", d["registrado_por"], "Fecha", d["created_at"]],
    ]
    sections = [("Datos de la referencia", ["Dato", "Valor", "Dato", "Valor"], rows, [110,150,110,153])]
    sections.append(("Motivo", ["Contenido"], [[d["motivo"]]], [523]))
    if d["estado"] == "contrarreferida":
        sections.append(("Contrarreferencia", ["Dato", "Valor"], [
            ["Fecha", d["fecha_contrarreferencia"]], ["Profesional receptor", d["profesional_receptor"]],
            ["Resumen", d["resumen_contrarreferencia"]],
        ], [140,383]))
    return pdf_document(f"Referencia {d['numero_referencia']}", hospital or "Hospital", sections)


async def export_csv(db, tid, f):
    import csv
    from io import StringIO
    result = await list_referencias(db, tid, f, 1, 10001)
    if result["total"] > 10000:
        raise HTTPException(422, detail="Acote los filtros: el reporte admite hasta 10000 registros")
    keys = ["numero_referencia", "created_at", "paciente", "dni", "origen", "destino_tipo",
            "nombre_ipress_destino", "tenant_destino_nombre", "especialidad_destino", "estado", "registrado_por"]
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(keys)
    def safe(v):
        value = str(v) if v is not None else ""
        return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else value
    for row in result["items"]:
        writer.writerow([safe(row.get(k)) for k in keys])
    return ("﻿" + stream.getvalue()).encode("utf-8")
