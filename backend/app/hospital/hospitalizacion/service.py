import uuid
from datetime import date, datetime
from fastapi import HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.hospitalizacion.models import HospCorrelativo, NotaEvolucion, ConsentimientoInformado
from app.sigarh.infraestructura_hosp.models import Piso, Cama
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import (
    Hospitalizacion, AtencionMedica, Interconsulta,
)
from app.sigarh.general.models import DiagnosticoCIE10
from app.hospital.emergencia.models import DestinoEmergencia, AtencionEmergencia, AdmisionEmergencia
from app.sigarh.rrhh.models import Empleado, Especialidad


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


def columns(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


async def own(db, model, tid, obj_id, active=False, lock=False):
    q = select(model).where(model.id == obj_id, model.tenant_id == tid)
    if active:
        q = q.where(model.is_active.is_(True))
    if lock:
        q = q.with_for_update().execution_options(populate_existing=True)
    obj = (await db.execute(q)).scalar_one_or_none()
    if obj is None:
        raise HTTPException(404, detail="Registro no encontrado en este hospital")
    return obj


async def number(db, tid, kind):
    stmt = insert(HospCorrelativo).values(tenant_id=tid, tipo=kind, valor=1)
    stmt = stmt.on_conflict_do_update(index_elements=["tenant_id", "tipo"],
        set_={"valor": HospCorrelativo.valor + 1}).returning(HospCorrelativo.valor)
    n = await db.scalar(stmt)
    return f"{kind}-{tid.hex[:8]}-{n:08d}"


# ─── Panel de Camas (ya existía; se corrige para reconocer origen Emergencia) ─

async def get_pisos(db: AsyncSession, tenant_id: uuid.UUID) -> list[Piso]:
    result = await db.execute(
        select(Piso).where(Piso.tenant_id == tenant_id, Piso.is_active == True).order_by(Piso.orden)
    )
    return result.scalars().all()


async def get_panel_camas(db: AsyncSession, tenant_id: uuid.UUID, piso_id: uuid.UUID | None = None) -> list[dict]:
    query = select(Cama).where(Cama.tenant_id == tenant_id, Cama.is_active == True)
    if piso_id:
        query = query.where(Cama.piso_id == piso_id)
    result = await db.execute(query.order_by(Cama.codigo))
    camas = result.scalars().all()

    items = []
    for cama in camas:
        item = {
            "id": cama.id, "codigo": cama.codigo, "nombre": cama.nombre, "tipo_cama": cama.tipo_cama,
            "estado": cama.estado, "sala_nombre": cama.sala_texto, "servicio_nombre": cama.servicio_texto,
            "paciente_nombre": None, "paciente_dni": None, "fecha_ingreso": None,
            "numero_hospitalizacion": None, "hospitalizacion_id": None, "hospitalizacion_cita_id": None,
        }
        if cama.estado == "OCUPADA":
            # patient_id ya vive directo en Hospitalizacion (cubre ambos orígenes);
            # ya no hace falta pasar por AtencionMedica/Cita como antes, que
            # dejaba sin paciente a las hospitalizaciones venidas de Emergencia.
            row = (await db.execute(
                select(Hospitalizacion, Patient).join(Patient, Patient.id == Hospitalizacion.patient_id)
                .where(Hospitalizacion.cama_id == cama.id, Hospitalizacion.estado == "internado")
            )).first()
            if row:
                hosp, paciente = row
                item["paciente_nombre"] = paciente.full_name
                item["paciente_dni"] = paciente.dni
                item["fecha_ingreso"] = hosp.fecha_ingreso
                item["numero_hospitalizacion"] = hosp.numero_hospitalizacion
                item["hospitalizacion_id"] = hosp.id
                if hosp.atencion_medica_id:
                    atencion = await db.get(AtencionMedica, hosp.atencion_medica_id)
                    item["hospitalizacion_cita_id"] = atencion.cita_id if atencion else None
        items.append(item)
    return items


# ─── Hospitalizaciones (listado/detalle real, ambos orígenes) ──────────────

def _hosp_query(tid):
    return (select(Hospitalizacion, Patient, ClinicalRecord.record_number, Cama, Especialidad, DiagnosticoCIE10)
        .join(Patient, Patient.id == Hospitalizacion.patient_id)
        .outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id)
        .join(Cama, Cama.id == Hospitalizacion.cama_id)
        .outerjoin(Especialidad, Especialidad.id == Hospitalizacion.especialidad_ingreso_id)
        .outerjoin(DiagnosticoCIE10, DiagnosticoCIE10.id == Hospitalizacion.diagnostico_ingreso_id)
        .where(Hospitalizacion.tenant_id == tid))


def _hosp_out(row):
    hosp, paciente, hc, cama, especialidad, diagnostico = row
    return dict(columns(hosp), paciente=paciente.full_name, dni=paciente.dni, historia=hc,
        cama_codigo=cama.codigo, cama_nombre=cama.nombre,
        especialidad_ingreso_nombre=especialidad.nombre if especialidad else None,
        diagnostico_ingreso_codigo=diagnostico.codigo_cie10 if diagnostico else None,
        diagnostico_ingreso_descripcion=diagnostico.descripcion if diagnostico else None,
        origen="EMERGENCIA" if hosp.atencion_emergencia_id else "CONSULTA_EXTERNA")


async def list_hospitalizaciones(db, tid, f, page=1, size=20):
    q = _hosp_query(tid)
    if f.get("q"):
        for term in f["q"].split():
            q = q.where(or_(*[c.icontains(term, autoescape=True) for c in
                (Patient.first_name, Patient.last_name_paterno, Patient.last_name_materno,
                 Patient.dni, Hospitalizacion.numero_hospitalizacion)]))
    if f.get("estado"):
        q = q.where(Hospitalizacion.estado == f["estado"])
    if f.get("origen") == "EMERGENCIA":
        q = q.where(Hospitalizacion.atencion_emergencia_id.is_not(None))
    elif f.get("origen") == "CONSULTA_EXTERNA":
        q = q.where(Hospitalizacion.atencion_medica_id.is_not(None))
    total = await db.scalar(select(func.count()).select_from(q.order_by(None).subquery()))
    rows = (await db.execute(q.order_by(Hospitalizacion.fecha_ingreso.desc()).offset((page-1)*size).limit(size))).all()
    return {"items": [_hosp_out(r) for r in rows], "total": total, "page": page, "page_size": size}


async def hospitalizacion_detalle(db, tid, hosp_id):
    row = (await db.execute(_hosp_query(tid).where(Hospitalizacion.id == hosp_id))).first()
    if not row:
        raise HTTPException(404, detail="Hospitalización no encontrada")
    data = _hosp_out(row)
    notas = (await db.scalars(select(NotaEvolucion).where(NotaEvolucion.tenant_id == tid,
        NotaEvolucion.hospitalizacion_id == hosp_id).order_by(NotaEvolucion.created_at.desc()))).all()
    interconsultas = (await db.execute(select(Interconsulta, Especialidad)
        .join(Especialidad, Especialidad.id == Interconsulta.especialidad_destino_id)
        .where(Interconsulta.hospitalizacion_id == hosp_id))).all()
    consentimientos = (await db.scalars(select(ConsentimientoInformado).where(
        ConsentimientoInformado.tenant_id == tid, ConsentimientoInformado.hospitalizacion_id == hosp_id
    ).order_by(ConsentimientoInformado.created_at.desc()))).all()
    data["notas_evolucion"] = [dict(columns(n)) for n in notas]
    data["interconsultas"] = [dict(columns(i), especialidad_nombre=e.nombre) for i, e in interconsultas]
    data["consentimientos"] = [dict(columns(c)) for c in consentimientos]
    return data


async def admitir_desde_emergencia(db, tid, user, data):
    destino = await own(db, DestinoEmergencia, tid, data.destino_id, lock=True)
    if destino.destino != "HOSPITALIZACION":
        raise HTTPException(422, detail="Este destino de emergencia no corresponde a hospitalización")
    if destino.estado != "pendiente":
        raise HTTPException(409, detail="Este destino ya fue resuelto")
    atencion = await own(db, AtencionEmergencia, tid, destino.atencion_id)
    admision = await own(db, AdmisionEmergencia, tid, atencion.admision_id, lock=True)
    if await db.scalar(select(Hospitalizacion.id).where(Hospitalizacion.atencion_emergencia_id == atencion.id)):
        raise HTTPException(409, detail="Esta atención de emergencia ya generó una hospitalización")
    cama = await own(db, Cama, tid, data.cama_id, active=True, lock=True)
    if cama.estado != "DISPONIBLE":
        raise HTTPException(409, detail=f"La cama {cama.codigo} no está disponible (estado actual: {cama.estado})")
    if data.diagnostico_ingreso_id and not await db.scalar(select(DiagnosticoCIE10.id).where(
        DiagnosticoCIE10.id == data.diagnostico_ingreso_id, DiagnosticoCIE10.tenant_id == tid, DiagnosticoCIE10.is_active.is_(True))):
        raise HTTPException(422, detail="Seleccione un diagnóstico activo de este hospital")
    if data.especialidad_ingreso_id and not await db.scalar(select(Especialidad.id).where(
        Especialidad.id == data.especialidad_ingreso_id, Especialidad.tenant_id == tid, Especialidad.is_active.is_(True))):
        raise HTTPException(422, detail="Seleccione una especialidad activa de este hospital")

    hosp = Hospitalizacion(tenant_id=tid, atencion_emergencia_id=atencion.id, patient_id=admision.patient_id,
        cama_id=cama.id, especialidad_ingreso_id=data.especialidad_ingreso_id,
        diagnostico_ingreso_id=data.diagnostico_ingreso_id,
        numero_hospitalizacion=await number(db, tid, "HOSP"), registrado_por=actor(user))
    db.add(hosp)
    cama.estado = "OCUPADA"
    destino.estado, destino.resolved_at = "completado", datetime.utcnow()
    destino.observacion = f"Hospitalizado en cama {cama.codigo}"
    admision.estado = "derivado"
    await db.flush()
    await db.commit()
    return await hospitalizacion_detalle(db, tid, hosp.id)


async def dar_alta(db, tid, user, hosp_id, data):
    hosp = await own(db, Hospitalizacion, tid, hosp_id, lock=True)
    if hosp.estado == "alta":
        raise HTTPException(409, detail="Esta hospitalización ya tiene alta registrada")
    columns(hosp)
    cama = await own(db, Cama, tid, hosp.cama_id, lock=True)
    cama.estado = "DISPONIBLE"
    hosp.estado, hosp.fecha_alta, hosp.resumen_alta = "alta", datetime.utcnow(), data.resumen_alta
    await db.flush()
    await db.commit()
    return await hospitalizacion_detalle(db, tid, hosp.id)


# ─── Notas de evolución ─────────────────────────────────────────────────────

async def crear_nota(db, tid, user, hosp_id, data):
    hosp = await own(db, Hospitalizacion, tid, hosp_id)
    if hosp.estado != "internado":
        raise HTTPException(409, detail="No se pueden agregar notas a una hospitalización con alta")
    empleado_id = uuid.UUID(user["empleado_id"]) if user.get("empleado_id") else None
    if not empleado_id:
        raise HTTPException(422, detail="La cuenta debe estar vinculada a un empleado para registrar notas")
    if user.get("role") == "enfermera" and data.tipo != "ENFERMERIA":
        raise HTTPException(403, detail="La cuenta de enfermería solo puede registrar notas de Enfermería")
    nota = NotaEvolucion(tenant_id=tid, hospitalizacion_id=hosp_id, autor_id=empleado_id,
        registrado_por=actor(user), **data.model_dump())
    db.add(nota)
    await db.flush()
    await db.commit()
    return columns(nota)


async def listar_notas(db, tid, hosp_id):
    await own(db, Hospitalizacion, tid, hosp_id)
    notas = (await db.scalars(select(NotaEvolucion).where(NotaEvolucion.tenant_id == tid,
        NotaEvolucion.hospitalizacion_id == hosp_id).order_by(NotaEvolucion.created_at.desc()))).all()
    out = []
    for n in notas:
        autor = await db.get(Empleado, n.autor_id)
        out.append(dict(columns(n), autor_nombre=autor.nombre_completo if autor else None))
    return out


# ─── Interconsultas intrahospitalarias ──────────────────────────────────────

async def crear_interconsulta(db, tid, user, hosp_id, data):
    hosp = await own(db, Hospitalizacion, tid, hosp_id)
    if hosp.estado != "internado":
        raise HTTPException(409, detail="No se pueden solicitar interconsultas en una hospitalización con alta")
    if await db.scalar(select(Interconsulta.id).where(Interconsulta.hospitalizacion_id == hosp_id)):
        raise HTTPException(409, detail="Esta hospitalización ya tiene una interconsulta activa")
    if not await db.scalar(select(Especialidad.id).where(Especialidad.id == data.especialidad_destino_id,
        Especialidad.tenant_id == tid, Especialidad.is_active.is_(True))):
        raise HTTPException(422, detail="Seleccione una especialidad activa de este hospital")
    if data.diagnostico_id and not await db.scalar(select(DiagnosticoCIE10.id).where(
        DiagnosticoCIE10.id == data.diagnostico_id, DiagnosticoCIE10.tenant_id == tid, DiagnosticoCIE10.is_active.is_(True))):
        raise HTTPException(422, detail="Seleccione un diagnóstico activo de este hospital")
    interc = Interconsulta(tenant_id=tid, hospitalizacion_id=hosp_id, patient_id=hosp.patient_id,
        solicitado_por=actor(user), **data.model_dump())
    db.add(interc)
    await db.flush()
    await db.commit()
    return columns(interc)


async def listar_interconsultas(db, tid, hosp_id):
    await own(db, Hospitalizacion, tid, hosp_id)
    rows = (await db.execute(select(Interconsulta, Especialidad).join(Especialidad,
        Especialidad.id == Interconsulta.especialidad_destino_id).where(
        Interconsulta.hospitalizacion_id == hosp_id).order_by(Interconsulta.created_at.desc()))).all()
    return [dict(columns(i), especialidad_nombre=e.nombre) for i, e in rows]


async def listar_todas_interconsultas(db, tid, estado=None):
    # Solo interconsultas intrahospitalarias (Hospitalizacion + Emergencia): el
    # especialista va a ver al paciente internado/en emergencia. Las de Consulta
    # Externa generan una Cita futura y se gestionan desde Admision/Agendamiento,
    # un flujo distinto -- no se mezclan aqui.
    q = (select(Interconsulta, Especialidad, Patient, Hospitalizacion, AdmisionEmergencia)
        .join(Especialidad, Especialidad.id == Interconsulta.especialidad_destino_id)
        .join(Patient, Patient.id == Interconsulta.patient_id)
        .outerjoin(Hospitalizacion, Hospitalizacion.id == Interconsulta.hospitalizacion_id)
        .outerjoin(AtencionEmergencia, AtencionEmergencia.id == Interconsulta.atencion_emergencia_id)
        .outerjoin(AdmisionEmergencia, AdmisionEmergencia.id == AtencionEmergencia.admision_id)
        .where(Interconsulta.tenant_id == tid,
               or_(Interconsulta.hospitalizacion_id.is_not(None), Interconsulta.atencion_emergencia_id.is_not(None))))
    if estado:
        q = q.where(Interconsulta.estado == estado)
    rows = (await db.execute(q.order_by(Interconsulta.urgente.desc(), Interconsulta.created_at.desc()))).all()
    return [dict(columns(i), especialidad_nombre=e.nombre,
        origen="HOSPITALIZACION" if h else "EMERGENCIA",
        hospitalizacion_numero=h.numero_hospitalizacion if h else None,
        numero_cuenta_emergencia=adm.numero_cuenta if adm else None,
        paciente_nombre=p.full_name, paciente_dni=p.dni) for i, e, p, h, adm in rows]


async def admitir_interconsulta_desde_emergencia(db, tid, user, data):
    destino = await own(db, DestinoEmergencia, tid, data.destino_id, lock=True)
    if destino.destino != "INTERCONSULTA":
        raise HTTPException(422, detail="Este destino de emergencia no corresponde a interconsulta")
    if destino.estado != "pendiente":
        raise HTTPException(409, detail="Este destino ya fue resuelto")
    atencion = await own(db, AtencionEmergencia, tid, destino.atencion_id)
    admision = await own(db, AdmisionEmergencia, tid, atencion.admision_id, lock=True)
    if await db.scalar(select(Interconsulta.id).where(Interconsulta.atencion_emergencia_id == atencion.id)):
        raise HTTPException(409, detail="Esta atención de emergencia ya generó una interconsulta")
    if not await db.scalar(select(Especialidad.id).where(Especialidad.id == data.especialidad_destino_id,
        Especialidad.tenant_id == tid, Especialidad.is_active.is_(True))):
        raise HTTPException(422, detail="Seleccione una especialidad activa de este hospital")
    if data.diagnostico_id and not await db.scalar(select(DiagnosticoCIE10.id).where(
        DiagnosticoCIE10.id == data.diagnostico_id, DiagnosticoCIE10.tenant_id == tid, DiagnosticoCIE10.is_active.is_(True))):
        raise HTTPException(422, detail="Seleccione un diagnóstico activo de este hospital")

    interc = Interconsulta(tenant_id=tid, atencion_emergencia_id=atencion.id, patient_id=admision.patient_id,
        especialidad_destino_id=data.especialidad_destino_id, diagnostico_id=data.diagnostico_id,
        motivo=data.motivo, urgente=data.urgente, solicitado_por=actor(user))
    db.add(interc)
    destino.estado, destino.resolved_at = "completado", datetime.utcnow()
    destino.observacion = "Interconsulta generada"
    await db.flush()
    await db.commit()
    especialidad = await db.get(Especialidad, interc.especialidad_destino_id)
    paciente = await db.get(Patient, interc.patient_id)
    return dict(columns(interc), especialidad_nombre=especialidad.nombre if especialidad else None,
        origen="EMERGENCIA", hospitalizacion_numero=None, numero_cuenta_emergencia=admision.numero_cuenta,
        paciente_nombre=paciente.full_name, paciente_dni=paciente.dni)


# ─── Consentimientos informados ─────────────────────────────────────────────

async def crear_consentimiento(db, tid, user, hosp_id, data):
    await own(db, Hospitalizacion, tid, hosp_id)
    empleado_id = uuid.UUID(user["empleado_id"]) if user.get("empleado_id") else None
    if not empleado_id:
        raise HTTPException(422, detail="La cuenta debe estar vinculada a un empleado para registrar consentimientos")
    consent = ConsentimientoInformado(tenant_id=tid, hospitalizacion_id=hosp_id, medico_id=empleado_id,
        numero=await number(db, tid, "CI"), registrado_por=actor(user), **data.model_dump())
    db.add(consent)
    await db.flush()
    await db.commit()
    return columns(consent)


async def listar_consentimientos(db, tid, hosp_id):
    await own(db, Hospitalizacion, tid, hosp_id)
    consentimientos = (await db.scalars(select(ConsentimientoInformado).where(
        ConsentimientoInformado.tenant_id == tid, ConsentimientoInformado.hospitalizacion_id == hosp_id
    ).order_by(ConsentimientoInformado.created_at.desc()))).all()
    return [columns(c) for c in consentimientos]


async def revocar_consentimiento(db, tid, user, consentimiento_id, data):
    consent = await own(db, ConsentimientoInformado, tid, consentimiento_id, lock=True)
    if consent.estado == "revocado":
        raise HTTPException(409, detail="Este consentimiento ya fue revocado")
    columns(consent)
    consent.estado, consent.motivo_revocacion = "revocado", data.motivo_revocacion
    await db.flush()
    await db.commit()
    return columns(consent)


async def listar_todos_consentimientos(db, tid, estado=None):
    q = (select(ConsentimientoInformado, Hospitalizacion, Patient)
        .join(Hospitalizacion, Hospitalizacion.id == ConsentimientoInformado.hospitalizacion_id)
        .join(Patient, Patient.id == Hospitalizacion.patient_id)
        .where(ConsentimientoInformado.tenant_id == tid))
    if estado:
        q = q.where(ConsentimientoInformado.estado == estado)
    rows = (await db.execute(q.order_by(ConsentimientoInformado.created_at.desc()))).all()
    return [dict(columns(c), hospitalizacion_numero=h.numero_hospitalizacion,
        paciente_nombre=p.full_name, paciente_dni=p.dni) for c, h, p in rows]


async def consentimiento_detalle(db, tid, consentimiento_id):
    consent = await own(db, ConsentimientoInformado, tid, consentimiento_id)
    hosp = await db.get(Hospitalizacion, consent.hospitalizacion_id)
    paciente = await db.get(Patient, hosp.patient_id) if hosp else None
    medico = await db.get(Empleado, consent.medico_id)
    return dict(columns(consent), paciente_nombre=paciente.full_name if paciente else None,
        paciente_dni=paciente.dni if paciente else None,
        numero_hospitalizacion=hosp.numero_hospitalizacion if hosp else None,
        medico_nombre=medico.nombre_completo if medico else None)


# ─── Censo diario ───────────────────────────────────────────────────────────

async def censo_diario(db, tid, fecha: date):
    inicio_dia = datetime.combine(fecha, datetime.min.time())
    fin_dia = datetime.combine(fecha, datetime.max.time())
    q = (_hosp_query(tid).where(Hospitalizacion.fecha_ingreso <= fin_dia,
        or_(Hospitalizacion.fecha_alta.is_(None), Hospitalizacion.fecha_alta >= inicio_dia)))
    rows = (await db.execute(q.order_by(Hospitalizacion.fecha_ingreso))).all()
    items = []
    for row in rows:
        hosp = row[0]
        dias = (min(hosp.fecha_alta or fin_dia, fin_dia).date() - hosp.fecha_ingreso.date()).days + 1
        items.append(dict(_hosp_out(row), dias_internado=dias))
    total_camas = await db.scalar(select(func.count()).where(Cama.tenant_id == tid, Cama.is_active.is_(True)))
    return {"fecha": fecha, "items": items, "total_internados": len(items),
        "total_camas": total_camas or 0, "ingresos_del_dia": sum(1 for h in items if h["fecha_ingreso"].date() == fecha),
        "altas_del_dia": sum(1 for h in items if h["fecha_alta"] and h["fecha_alta"].date() == fecha)}


# ─── Catálogos y documentos ─────────────────────────────────────────────────

async def catalogs(db, tid, kind, q=""):
    models = {"empleados": Empleado, "especialidades": Especialidad}
    model = models.get(kind)
    if model is None:
        raise HTTPException(404, detail="Catálogo no encontrado")
    query = select(model).where(model.tenant_id == tid, model.is_active.is_(True))
    if q:
        fields = [model.nombres, model.apellido_paterno, model.apellido_materno] if kind == "empleados" else [model.nombre]
        for term in q.split():
            query = query.where(or_(*[c.icontains(term, autoescape=True) for c in fields]))
    objs = (await db.scalars(query.order_by(model.id).limit(100))).all()
    return [{"id": x.id, "nombre": x.nombre_completo if kind == "empleados" else x.nombre} for x in objs]


async def camas_disponibles(db, tid, servicio_id=None):
    q = select(Cama).where(Cama.tenant_id == tid, Cama.is_active.is_(True), Cama.estado == "DISPONIBLE")
    if servicio_id:
        q = q.where(Cama.servicio_id == servicio_id)
    return [{"id": c.id, "codigo": c.codigo, "nombre": c.nombre, "servicio_nombre": c.servicio_texto}
            for c in (await db.scalars(q.order_by(Cama.codigo))).all()]


async def destinos_emergencia_pendientes(db, tid, destino="HOSPITALIZACION"):
    rows = (await db.execute(select(DestinoEmergencia, AtencionEmergencia, AdmisionEmergencia, Patient)
        .join(AtencionEmergencia, AtencionEmergencia.id == DestinoEmergencia.atencion_id)
        .join(AdmisionEmergencia, AdmisionEmergencia.id == AtencionEmergencia.admision_id)
        .join(Patient, Patient.id == AdmisionEmergencia.patient_id)
        .where(DestinoEmergencia.tenant_id == tid, DestinoEmergencia.destino == destino,
               DestinoEmergencia.estado == "pendiente")
        .order_by(DestinoEmergencia.created_at))).all()
    return [{"destino_id": d.id, "numero_cuenta": adm.numero_cuenta, "paciente_nombre": p.full_name,
        "paciente_dni": p.dni, "motivo_consulta": a.motivo_consulta, "created_at": d.created_at} for d, a, adm, p in rows]


def pdf_document(title, hospital, sections):
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
    stream = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CellHosp", fontName="Helvetica", fontSize=8, leading=11, wordWrap="CJK"))
    def para(value):
        return Paragraph(escape(str(value if value is not None else "-")).replace("\n", "<br/>"), styles["CellHosp"])
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
        canvas.drawString(36, 22, "Hospitalización - Documento generado por el sistema")
        canvas.drawRightString(A4[0]-36, 22, f"Página {doc.page}")
    SimpleDocTemplate(stream, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=30,
                      bottomMargin=38, title=title).build(story, onFirstPage=footer, onLaterPages=footer)
    return stream.getvalue()


async def consentimiento_pdf(db, tid, consentimiento_id):
    d = await consentimiento_detalle(db, tid, consentimiento_id)
    from app.core.tenant_db import get_tenant_by_id
    tenant = await get_tenant_by_id(tid)
    hospital = tenant.name if tenant else None
    rows = [
        ["Paciente", d["paciente_nombre"], "Documento", d["paciente_dni"]],
        ["Hospitalización", d["numero_hospitalizacion"], "N.° consentimiento", d["numero"]],
        ["Procedimiento", d["procedimiento"], "Fecha", d["fecha"]],
        ["Firmante", d["firmante_nombre"], "Relación", d["relacion_firmante"]],
        ["Documento firmante", d["firmante_documento"], "Testigo", d["testigo_nombre"] or "—"],
        ["Médico responsable", d["medico_nombre"], "Estado", d["estado"]],
    ]
    sections = [("Datos del consentimiento", ["Dato", "Valor", "Dato", "Valor"], rows, [110,150,110,153])]
    sections.append(("Riesgos y beneficios explicados", ["Contenido"], [[d["riesgos_beneficios"]]], [523]))
    return pdf_document(f"Consentimiento informado {d['numero']}", hospital or "Hospital", sections)


async def censo_pdf(db, tid, fecha):
    censo = await censo_diario(db, tid, fecha)
    from app.core.tenant_db import get_tenant_by_id
    tenant = await get_tenant_by_id(tid)
    hospital = tenant.name if tenant else None
    rows = [[i["numero_hospitalizacion"], i["paciente"], i["dni"], i["cama_codigo"],
             i["diagnostico_ingreso_descripcion"], i["dias_internado"]] for i in censo["items"]]
    sections = [("Resumen", ["Fecha", "Camas totales", "Internados", "Ingresos", "Altas"],
        [[censo["fecha"], censo["total_camas"], censo["total_internados"], censo["ingresos_del_dia"], censo["altas_del_dia"]]],
        [105,105,105,105,103])]
    sections.append(("Pacientes internados", ["N.° hospitalización", "Paciente", "DNI", "Cama", "Diagnóstico", "Días"],
        rows, [95,140,70,70,113,35]))
    return pdf_document(f"Censo diario {fecha}", hospital or "Hospital", sections)


async def export_censo_csv(db, tid, fecha):
    import csv
    from io import StringIO
    censo = await censo_diario(db, tid, fecha)
    stream = StringIO()
    writer = csv.writer(stream)
    keys = ["numero_hospitalizacion", "paciente", "dni", "cama_codigo", "diagnostico_ingreso_descripcion",
            "fecha_ingreso", "dias_internado", "origen"]
    writer.writerow(keys)
    def safe(v):
        value = str(v) if v is not None else ""
        return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else value
    for row in censo["items"]:
        writer.writerow([safe(row.get(k)) for k in keys])
    return ("﻿" + stream.getvalue()).encode("utf-8")
