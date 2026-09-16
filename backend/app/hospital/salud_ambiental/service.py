import uuid
from datetime import datetime
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.salud_ambiental.models import SaludAmbientalCorrelativo, CertificadoDefuncion
from app.hospital.admision.models import Patient
from app.hospital.consulta_externa.models import Hospitalizacion
from app.hospital.emergencia.models import AtencionEmergencia, AdmisionEmergencia
from app.sigarh.rrhh.models import Empleado
from app.sigarh.mantenimiento.models import Profesion
from app.sigarh.general.models import DiagnosticoCIE10
from app.admin.auditoria.models import AuditLog


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


def audit(db, tid, user, model, obj_id, action, before=None, after=None):
    db.add(AuditLog(tenant_id=tid, user_id=uuid.UUID(user["sub"]), user_name=user.get("name"),
        model=model, model_id=str(obj_id), action=action,
        old_values=jsonable_encoder(before), new_values=jsonable_encoder(after)))


async def _siguiente(db: AsyncSession, tid: uuid.UUID, tipo: str, prefijo: str) -> str:
    stmt = insert(SaludAmbientalCorrelativo).values(tenant_id=tid, tipo=tipo, valor=1)
    stmt = stmt.on_conflict_do_update(index_elements=["tenant_id", "tipo"],
        set_={"valor": SaludAmbientalCorrelativo.valor + 1}).returning(SaludAmbientalCorrelativo.valor)
    n = await db.scalar(stmt)
    return f"{prefijo}-{n:08d}"


async def _validar_medico_certificador(db: AsyncSession, tid: uuid.UUID, medico_id: uuid.UUID) -> Empleado:
    """Un certificado de defunción, como cualquier documento clínico que
    cierra una atención, solo puede emitirlo un médico con colegiatura
    habilitada -- mismo criterio que Firma Electrónica."""
    medico = await db.scalar(select(Empleado).where(Empleado.id == medico_id, Empleado.tenant_id == tid, Empleado.is_active.is_(True)))
    profesion = await db.scalar(select(Profesion.codigo).where(Profesion.id == medico.profesion_id, Profesion.tenant_id == tid)) if medico and medico.profesion_id else None
    if not medico or profesion != "MED" or not medico.habilitado_colegio or not (medico.numero_cmp or medico.numero_colegiatura):
        raise HTTPException(400, detail="El médico certificador debe tener colegiatura y habilitación registrada")
    return medico


def pdf_document(title, hospital, sections):
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
    stream = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CellSA", fontName="Helvetica", fontSize=8, leading=11, wordWrap="CJK"))
    def para(value):
        return Paragraph(escape(str(value if value is not None else "-")).replace("\n", "<br/>"), styles["CellSA"])
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
        canvas.drawString(36, 22, "Certificado de Defunción - Registro interno - Documento generado por el sistema")
        canvas.drawRightString(A4[0] - 36, 22, f"Página {doc.page}")
    SimpleDocTemplate(stream, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=30,
                      bottomMargin=38, title=title).build(story, onFirstPage=footer, onLaterPages=footer)
    return stream.getvalue()


async def crear_certificado(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    medico = await _validar_medico_certificador(db, tid, data.medico_certificador_id)

    atencion_emergencia = None
    hospitalizacion = None
    patient_id = data.patient_id

    if data.atencion_emergencia_id:
        atencion_emergencia = await db.get(AtencionEmergencia, data.atencion_emergencia_id)
        if atencion_emergencia is None or atencion_emergencia.tenant_id != tid:
            raise HTTPException(404, detail="Atención de emergencia no encontrada")
        admision = await db.get(AdmisionEmergencia, atencion_emergencia.admision_id)
        patient_id = admision.patient_id
        if await db.scalar(select(CertificadoDefuncion.id).where(CertificadoDefuncion.atencion_emergencia_id == data.atencion_emergencia_id)):
            raise HTTPException(409, detail="Ya existe un certificado de defunción para esta atención")
    elif data.hospitalizacion_id:
        hospitalizacion = await db.get(Hospitalizacion, data.hospitalizacion_id)
        if hospitalizacion is None or hospitalizacion.tenant_id != tid:
            raise HTTPException(404, detail="Hospitalización no encontrada")
        patient_id = hospitalizacion.patient_id
        if await db.scalar(select(CertificadoDefuncion.id).where(CertificadoDefuncion.hospitalizacion_id == data.hospitalizacion_id)):
            raise HTTPException(409, detail="Ya existe un certificado de defunción para esta hospitalización")

    paciente = await db.get(Patient, patient_id)
    if paciente is None or paciente.tenant_id != tid:
        raise HTTPException(404, detail="Paciente no encontrado")

    for campo, dx_id in (("causa_a_id", data.causa_a_id), ("causa_b_id", data.causa_b_id),
                          ("causa_c_id", data.causa_c_id), ("causa_d_id", data.causa_d_id)):
        if dx_id and not await db.scalar(select(DiagnosticoCIE10.id).where(DiagnosticoCIE10.id == dx_id, DiagnosticoCIE10.tenant_id == tid)):
            raise HTTPException(400, detail=f"{campo}: diagnóstico CIE-10 no encontrado")

    numero = await _siguiente(db, tid, "CERTDEF", f"DEF-{tid.hex[:6].upper()}")
    certificado = CertificadoDefuncion(id=uuid.uuid4(), tenant_id=tid, atencion_emergencia_id=data.atencion_emergencia_id,
        hospitalizacion_id=data.hospitalizacion_id, patient_id=patient_id, medico_certificador_id=data.medico_certificador_id,
        numero_certificado=numero, fecha_defuncion=data.fecha_defuncion, lugar_defuncion=data.lugar_defuncion,
        tipo_muerte=data.tipo_muerte, causa_a_id=data.causa_a_id, causa_b_id=data.causa_b_id,
        causa_c_id=data.causa_c_id, causa_d_id=data.causa_d_id, requiere_necropsia_legal=data.requiere_necropsia_legal,
        observaciones=data.observaciones, registrado_por=actor(user))
    db.add(certificado)

    if atencion_emergencia is not None and atencion_emergencia.destino_atencion != "FALLECIDO":
        atencion_emergencia.destino_atencion = "FALLECIDO"
    if hospitalizacion is not None and hospitalizacion.estado != "fallecido":
        hospitalizacion.estado = "fallecido"
        hospitalizacion.fecha_alta = hospitalizacion.fecha_alta or data.fecha_defuncion

    await db.flush()
    audit(db, tid, user, "CertificadoDefuncion", certificado.id, "crear", after={"numero_certificado": numero, "patient_id": str(patient_id)})
    await db.commit()
    return await _certificado_out(db, certificado)


async def _certificado_out(db: AsyncSession, c: CertificadoDefuncion) -> dict:
    paciente = await db.get(Patient, c.patient_id)
    medico = await db.get(Empleado, c.medico_certificador_id)
    async def dx(dx_id):
        if not dx_id:
            return None
        d = await db.get(DiagnosticoCIE10, dx_id)
        return f"{d.codigo_cie10} · {d.descripcion}" if d else None
    return {
        "id": c.id, "numero_certificado": c.numero_certificado, "patient_id": c.patient_id,
        "paciente_nombre": paciente.full_name if paciente else None, "paciente_dni": paciente.dni if paciente else None,
        "origen": "Emergencia" if c.atencion_emergencia_id else "Hospitalización" if c.hospitalizacion_id else "Directo",
        "fecha_defuncion": c.fecha_defuncion, "lugar_defuncion": c.lugar_defuncion, "tipo_muerte": c.tipo_muerte,
        "causa_a": await dx(c.causa_a_id), "causa_b": await dx(c.causa_b_id),
        "causa_c": await dx(c.causa_c_id), "causa_d": await dx(c.causa_d_id),
        "medico_certificador_nombre": medico.nombre_completo if medico else None,
        "medico_certificador_colegiatura": (medico.numero_cmp or medico.numero_colegiatura) if medico else None,
        "requiere_necropsia_legal": c.requiere_necropsia_legal, "estado_envio": c.estado_envio,
        "fecha_envio": c.fecha_envio, "observaciones": c.observaciones, "created_at": c.created_at,
    }


async def list_certificados(db: AsyncSession, tid: uuid.UUID, tipo_muerte: str | None = None,
                             estado_envio: str | None = None) -> list[dict]:
    query = select(CertificadoDefuncion).where(CertificadoDefuncion.tenant_id == tid)
    if tipo_muerte:
        query = query.where(CertificadoDefuncion.tipo_muerte == tipo_muerte)
    if estado_envio:
        query = query.where(CertificadoDefuncion.estado_envio == estado_envio)
    certificados = (await db.scalars(query.order_by(CertificadoDefuncion.fecha_defuncion.desc()))).all()
    return [await _certificado_out(db, c) for c in certificados]


async def get_certificado(db: AsyncSession, tid: uuid.UUID, certificado_id: uuid.UUID) -> dict:
    c = await db.get(CertificadoDefuncion, certificado_id)
    if c is None or c.tenant_id != tid:
        raise HTTPException(404, detail="Certificado no encontrado")
    return await _certificado_out(db, c)


async def marcar_enviado(db: AsyncSession, tid: uuid.UUID, user: dict, certificado_id: uuid.UUID) -> dict:
    c = await db.get(CertificadoDefuncion, certificado_id)
    if c is None or c.tenant_id != tid:
        raise HTTPException(404, detail="Certificado no encontrado")
    if c.estado_envio == "enviado_reniec":
        raise HTTPException(409, detail="Este certificado ya fue marcado como enviado")
    c.estado_envio = "enviado_reniec"
    c.fecha_envio = datetime.utcnow()
    audit(db, tid, user, "CertificadoDefuncion", c.id, "marcar_enviado")
    await db.commit()
    return await _certificado_out(db, c)


async def certificado_pdf(db: AsyncSession, tid: uuid.UUID, certificado_id: uuid.UUID) -> bytes:
    from app.core.tenant_db import get_tenant_by_id
    c = await db.get(CertificadoDefuncion, certificado_id)
    if c is None or c.tenant_id != tid:
        raise HTTPException(404, detail="Certificado no encontrado")
    data = await _certificado_out(db, c)
    tenant = await get_tenant_by_id(tid)
    hospital = tenant.name if tenant else "Hospital"

    sections = [("Datos del certificado", ["N.° certificado", "Fecha de defunción", "Lugar", "Tipo de muerte"],
        [[data["numero_certificado"], data["fecha_defuncion"], data["lugar_defuncion"], data["tipo_muerte"]]],
        [105, 140, 140, 90])]
    sections.append(("Fallecido/a", ["Nombre", "DNI"], [[data["paciente_nombre"], data["paciente_dni"]]], [320, 155]))
    sections.append(("Causas de muerte (CIE-10)", ["Causa A (directa)", "Causa B", "Causa C (básica)", "Causa D (contribuyente)"],
        [[data["causa_a"], data["causa_b"] or "—", data["causa_c"] or "—", data["causa_d"] or "—"]], [120, 120, 120, 115]))
    sections.append(("Médico certificador", ["Nombre", "Colegiatura", "Requiere necropsia legal"],
        [[data["medico_certificador_nombre"], data["medico_certificador_colegiatura"], "Sí" if data["requiere_necropsia_legal"] else "No"]],
        [180, 130, 165]))
    return pdf_document(f"Certificado de Defunción {data['numero_certificado']}", hospital, sections)
