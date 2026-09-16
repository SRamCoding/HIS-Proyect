import uuid
from datetime import datetime
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, or_, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.sis.models import SisCorrelativo, FormatoFua
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import AtencionMedica, Cita, AtencionDiagnostico, ProgramacionMedica
from app.hospital.emergencia.models import AtencionEmergencia, AdmisionEmergencia, EmergenciaDiagnostico
from app.sigarh.config_financiera.models import Seguro
from app.sigarh.general.models import DiagnosticoCIE10
from app.sigarh.rrhh.models import Empleado
from app.admin.auditoria.models import AuditLog


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


def columns(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def audit(db, tid, user, model, obj_id, action, before=None, after=None):
    db.add(AuditLog(tenant_id=tid, user_id=uuid.UUID(user["sub"]), user_name=user.get("name"),
        model=model, model_id=str(obj_id), action=action,
        old_values=jsonable_encoder(before), new_values=jsonable_encoder(after)))


async def own(db, model, tid, obj_id, lock=False):
    q = select(model).where(model.id == obj_id, model.tenant_id == tid)
    if lock:
        q = q.with_for_update().execution_options(populate_existing=True)
    obj = (await db.execute(q)).scalar_one_or_none()
    if obj is None:
        raise HTTPException(404, detail="Registro no encontrado en este hospital")
    return obj


async def number(db, tid):
    stmt = insert(SisCorrelativo).values(tenant_id=tid, tipo="FUA", valor=1)
    stmt = stmt.on_conflict_do_update(index_elements=["tenant_id", "tipo"],
        set_={"valor": SisCorrelativo.valor + 1}).returning(SisCorrelativo.valor)
    n = await db.scalar(stmt)
    return f"FUA-{tid.hex[:8]}-{n:08d}"


async def _seguro_por_texto(db, tid, fuente_financiamiento):
    """fuente_financiamiento es texto libre en Cita/AdmisionEmergencia (no hay
    FK a Seguro) -- se resuelve contra el catalogo por nombre, mismo criterio
    que usa Caja para aplicar tarifa diferenciada por seguro."""
    if not fuente_financiamiento or not fuente_financiamiento.strip():
        return None
    return (await db.execute(select(Seguro).where(Seguro.tenant_id == tid, Seguro.is_active.is_(True),
        func.lower(Seguro.nombre) == fuente_financiamiento.strip().lower()))).scalar_one_or_none()


async def list_atenciones_pendientes_fua(db, tid):
    """Atenciones firmadas, financiadas por un seguro que exige FUA (Seguro.
    requiere_fua, hoy solo SIS), que todavia no tienen un Formato FUA generado."""
    ya_generadas_medica = select(FormatoFua.atencion_medica_id).where(
        FormatoFua.tenant_id == tid, FormatoFua.atencion_medica_id.is_not(None))
    ya_generadas_emerg = select(FormatoFua.atencion_emergencia_id).where(
        FormatoFua.tenant_id == tid, FormatoFua.atencion_emergencia_id.is_not(None))

    items = []
    q_medica = (select(AtencionMedica, Cita, Patient, Seguro)
        .join(Cita, Cita.id == AtencionMedica.cita_id)
        .join(Patient, Patient.id == Cita.patient_id)
        .join(Seguro, and_(Seguro.tenant_id == tid, Seguro.is_active.is_(True),
              func.lower(Seguro.nombre) == func.lower(Cita.fuente_financiamiento)))
        .where(AtencionMedica.tenant_id == tid, AtencionMedica.estado == "firmado",
               Seguro.requiere_fua.is_(True), AtencionMedica.id.not_in(ya_generadas_medica)))
    for atencion, cita, paciente, seguro in (await db.execute(q_medica)).all():
        items.append({"origen": "CONSULTA_EXTERNA", "atencion_medica_id": atencion.id, "atencion_emergencia_id": None,
            "paciente_nombre": paciente.full_name, "paciente_dni": paciente.dni,
            "fecha_atencion": atencion.firmado_at or atencion.created_at, "seguro_nombre": seguro.nombre})

    q_emerg = (select(AtencionEmergencia, AdmisionEmergencia, Patient, Seguro)
        .join(AdmisionEmergencia, AdmisionEmergencia.id == AtencionEmergencia.admision_id)
        .join(Patient, Patient.id == AdmisionEmergencia.patient_id)
        .join(Seguro, and_(Seguro.tenant_id == tid, Seguro.is_active.is_(True),
              func.lower(Seguro.nombre) == func.lower(AdmisionEmergencia.fuente_financiamiento)))
        .where(AdmisionEmergencia.tenant_id == tid, AtencionEmergencia.estado == "firmado",
               Seguro.requiere_fua.is_(True), AtencionEmergencia.id.not_in(ya_generadas_emerg)))
    for atencion, admision, paciente, seguro in (await db.execute(q_emerg)).all():
        items.append({"origen": "EMERGENCIA", "atencion_medica_id": None, "atencion_emergencia_id": atencion.id,
            "paciente_nombre": paciente.full_name, "paciente_dni": paciente.dni,
            "fecha_atencion": atencion.firmado_at or atencion.created_at, "seguro_nombre": seguro.nombre})

    items.sort(key=lambda i: i["fecha_atencion"], reverse=True)
    return items


async def generar_fua(db, tid, user, data):
    if data.atencion_medica_id:
        atencion = await own(db, AtencionMedica, tid, data.atencion_medica_id, lock=True)
        if atencion.estado != "firmado":
            raise HTTPException(409, detail="Solo se genera FUA de una atención firmada")
        cita = await own(db, Cita, tid, atencion.cita_id)
        seguro = await _seguro_por_texto(db, tid, cita.fuente_financiamiento)
        patient_id, fecha_atencion = cita.patient_id, atencion.firmado_at or atencion.created_at
    else:
        atencion = await own(db, AtencionEmergencia, tid, data.atencion_emergencia_id, lock=True)
        if atencion.estado != "firmado":
            raise HTTPException(409, detail="Solo se genera FUA de una atención firmada")
        admision = await own(db, AdmisionEmergencia, tid, atencion.admision_id)
        seguro = await _seguro_por_texto(db, tid, admision.fuente_financiamiento)
        patient_id, fecha_atencion = admision.patient_id, atencion.firmado_at or atencion.created_at

    if not seguro or not seguro.requiere_fua:
        raise HTTPException(422, detail="Esta atención no está financiada por un seguro que exija FUA (SIS)")
    origen_col = FormatoFua.atencion_medica_id if data.atencion_medica_id else FormatoFua.atencion_emergencia_id
    origen_id = data.atencion_medica_id or data.atencion_emergencia_id
    if await db.scalar(select(FormatoFua.id).where(FormatoFua.tenant_id == tid, origen_col == origen_id)):
        raise HTTPException(409, detail="Esta atención ya tiene un FUA generado")

    fua = FormatoFua(tenant_id=tid, atencion_medica_id=data.atencion_medica_id,
        atencion_emergencia_id=data.atencion_emergencia_id, patient_id=patient_id, seguro_id=seguro.id,
        numero_fua=await number(db, tid), fecha_atencion=fecha_atencion, registrado_por=actor(user))
    db.add(fua)
    await db.flush()
    audit(db, tid, user, "FormatoFua", fua.id, "generar", after=columns(fua))
    await db.commit()
    return await fua_detalle(db, tid, fua.id)


def _fua_query(tid):
    return (select(FormatoFua, Patient, ClinicalRecord.record_number, Seguro)
        .join(Patient, Patient.id == FormatoFua.patient_id)
        .outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id)
        .join(Seguro, Seguro.id == FormatoFua.seguro_id)
        .where(FormatoFua.tenant_id == tid))


def _fua_out(row):
    fua, paciente, historia, seguro = row
    return dict(columns(fua), paciente_nombre=paciente.full_name, paciente_dni=paciente.dni,
        historia=historia, seguro_nombre=seguro.nombre,
        origen="CONSULTA_EXTERNA" if fua.atencion_medica_id else "EMERGENCIA")


async def list_fua(db, tid, estado=None, q=None, page=1, size=20):
    query = _fua_query(tid)
    if estado:
        query = query.where(FormatoFua.estado == estado)
    if q:
        for term in q.split():
            query = query.where(or_(FormatoFua.numero_fua.icontains(term, autoescape=True),
                Patient.dni.icontains(term, autoescape=True),
                Patient.first_name.icontains(term, autoescape=True),
                Patient.last_name_paterno.icontains(term, autoescape=True)))
    total = await db.scalar(select(func.count()).select_from(query.order_by(None).subquery()))
    rows = (await db.execute(query.order_by(FormatoFua.created_at.desc())
        .offset((page - 1) * size).limit(size))).all()
    return {"items": [_fua_out(r) for r in rows], "total": total, "page": page, "page_size": size}


async def fua_detalle(db, tid, fua_id):
    row = (await db.execute(_fua_query(tid).where(FormatoFua.id == fua_id))).first()
    if not row:
        raise HTTPException(404, detail="FUA no encontrado")
    data = _fua_out(row)
    fua = row[0]
    if fua.atencion_medica_id:
        atencion = await db.get(AtencionMedica, fua.atencion_medica_id)
        cita = await db.get(Cita, atencion.cita_id)
        prog = await db.get(ProgramacionMedica, cita.programacion_medica_id) if cita else None
        profesional = await db.get(Empleado, atencion.firmado_por_id) if atencion.firmado_por_id else None
        dx_rows = (await db.execute(select(AtencionDiagnostico, DiagnosticoCIE10).join(
            DiagnosticoCIE10, DiagnosticoCIE10.id == AtencionDiagnostico.diagnostico_cie10_id
        ).where(AtencionDiagnostico.atencion_medica_id == fua.atencion_medica_id))).all()
        data.update(
            numero_cuenta=cita.numero_cuenta if cita else None,
            servicio_o_especialidad=None,
            profesional_nombre=profesional.nombre_completo if profesional else None,
            prestaciones=atencion.prestaciones or [],
            destino_atencion=atencion.destino_atencion,
            diagnosticos=[{"codigo": d.codigo_cie10, "descripcion": d.descripcion, "tipo": ad.tipo} for ad, d in dx_rows],
        )
    else:
        atencion = await db.get(AtencionEmergencia, fua.atencion_emergencia_id)
        admision = await db.get(AdmisionEmergencia, atencion.admision_id)
        profesional = await db.get(Empleado, atencion.medico_id) if atencion.medico_id else None
        dx_rows = (await db.execute(select(EmergenciaDiagnostico, DiagnosticoCIE10).join(
            DiagnosticoCIE10, DiagnosticoCIE10.id == EmergenciaDiagnostico.diagnostico_cie10_id
        ).where(EmergenciaDiagnostico.atencion_emergencia_id == fua.atencion_emergencia_id))).all()
        data.update(
            numero_cuenta=admision.numero_cuenta,
            servicio_o_especialidad=admision.servicio_emergencia,
            profesional_nombre=profesional.nombre_completo if profesional else None,
            prestaciones=[atencion.destino_atencion] if atencion.destino_atencion else [],
            destino_atencion=atencion.destino_atencion,
            diagnosticos=[{"codigo": d.codigo_cie10, "descripcion": d.descripcion, "tipo": ad.tipo} for ad, d in dx_rows],
        )
    return data


async def cambiar_estado_fua(db, tid, user, fua_id, data):
    fua = await own(db, FormatoFua, tid, fua_id, lock=True)
    if fua.estado in ("pagado", "anulado"):
        raise HTTPException(409, detail=f"Este FUA ya está {fua.estado} y no admite más cambios")
    transiciones = {"generado": {"enviado", "anulado"}, "enviado": {"observado", "pagado", "anulado"},
        "observado": {"enviado", "anulado"}}
    if data.estado not in transiciones.get(fua.estado, set()):
        raise HTTPException(409, detail=f"No se puede pasar de '{fua.estado}' a '{data.estado}'")
    before = columns(fua)
    fua.estado = data.estado
    if data.observaciones:
        fua.observaciones = data.observaciones
    await db.flush()
    audit(db, tid, user, "FormatoFua", fua.id, "cambiar_estado", before=before, after=columns(fua))
    await db.commit()
    return await fua_detalle(db, tid, fua.id)


def pdf_document(title, hospital, sections):
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
    stream = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CellSis", fontName="Helvetica", fontSize=8, leading=11, wordWrap="CJK"))
    def para(value):
        return Paragraph(escape(str(value if value is not None else "-")).replace("\n", "<br/>"), styles["CellSis"])
    story = [Paragraph(escape(hospital), styles["Title"]), Paragraph(escape(title), styles["Heading1"]), Spacer(1, 12)]
    for heading, headers, rows, widths in sections:
        story.append(Paragraph(escape(heading), styles["Heading2"]))
        table = LongTable([[para(v) for v in headers]] + [[para(v) for v in row] for row in rows],
                          colWidths=widths, repeatRows=1, splitInRow=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e7f1f8")),
            ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#bccbd5")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.extend([table, Spacer(1, 12)])
    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.drawString(36, 22, "SIS - Formato Único de Atención (FUA) - Documento generado por el sistema")
        canvas.drawRightString(A4[0] - 36, 22, f"Página {doc.page}")
    SimpleDocTemplate(stream, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=30,
                      bottomMargin=38, title=title).build(story, onFirstPage=footer, onLaterPages=footer)
    return stream.getvalue()


async def fua_pdf(db, tid, fua_id):
    d = await fua_detalle(db, tid, fua_id)
    from app.core.tenant_db import get_tenant_by_id
    tenant = await get_tenant_by_id(tid)
    hospital = tenant.name if tenant else "Hospital"
    rows_asegurado = [
        ["Paciente", d["paciente_nombre"], "Documento", d["paciente_dni"]],
        ["Historia clínica", d["historia"], "N.° cuenta", d.get("numero_cuenta")],
        ["Seguro", d["seguro_nombre"], "N.° FUA", d["numero_fua"]],
        ["Fecha de atención", d["fecha_atencion"], "Estado", d["estado"]],
        ["Origen", "Consulta Externa" if d["origen"] == "CONSULTA_EXTERNA" else "Emergencia",
         "Profesional", d.get("profesional_nombre") or "—"],
    ]
    sections = [("I. Datos del asegurado y la atención", ["Dato", "Valor", "Dato", "Valor"], rows_asegurado, [110, 150, 110, 153])]
    dx_rows = [[dx["codigo"], dx["descripcion"], dx["tipo"]] for dx in d["diagnosticos"]] or [["—", "Sin diagnóstico registrado", "—"]]
    sections.append(("II. Diagnósticos CIE-10", ["Código", "Descripción", "Tipo"], dx_rows, [70, 353, 100]))
    prest_rows = [[p] for p in d["prestaciones"]] or [["Sin prestaciones adicionales registradas"]]
    sections.append(("III. Prestaciones brindadas", ["Prestación"], prest_rows, [523]))
    if d.get("observaciones"):
        sections.append(("Observaciones", ["Detalle"], [[d["observaciones"]]], [523]))
    return pdf_document(f"Formato FUA {d['numero_fua']}", hospital, sections)


async def list_afiliaciones_sis(db, tid, q=None, page=1, size=20):
    """SIS no tiene un catalogo propio en este proyecto -- se reutiliza el
    dato real ya capturado en Admision (Patient.insurance_type/insurance_number),
    filtrado a pacientes cuyo seguro registrado es SIS. Ver/editar la afiliacion
    se hace desde Admision > Pacientes, que ya es dueño de ese dato."""
    query = (select(Patient, ClinicalRecord.record_number)
        .outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id)
        .where(Patient.tenant_id == tid, Patient.insurance_type.icontains("SIS", autoescape=True)))
    if q:
        for term in q.split():
            query = query.where(or_(Patient.dni.icontains(term, autoescape=True),
                Patient.first_name.icontains(term, autoescape=True),
                Patient.last_name_paterno.icontains(term, autoescape=True),
                Patient.last_name_materno.icontains(term, autoescape=True)))
    total = await db.scalar(select(func.count()).select_from(query.order_by(None).subquery()))
    rows = (await db.execute(query.order_by(Patient.last_name_paterno, Patient.id)
        .offset((page - 1) * size).limit(size))).all()
    return {"items": [{"id": p.id, "nombre": p.full_name, "dni": p.dni, "historia": hc,
        "insurance_type": p.insurance_type, "insurance_number": p.insurance_number,
        "is_active": p.is_active} for p, hc in rows], "total": total, "page": page, "page_size": size}
