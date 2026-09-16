import uuid
from datetime import datetime, date
from decimal import Decimal
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, or_, and_, text, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.hospital.laboratorio.models import LabCorrelativo, LabCupo, LabMovimiento, LabMovimientoItem, LabFichaCovid
from app.hospital.laboratorio import schemas
from app.hospital.consulta_externa.models import OrdenLaboratorio, OrdenLaboratorioItem, AtencionMedica, Cita, ProgramacionMedica
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.emergencia.models import AdmisionEmergencia
from app.sigarh.laboratorio.models import ExamenLaboratorio
from app.sigarh.rrhh.models import Empleado, Especialidad
from app.sigarh.mantenimiento.models import Servicio
from app.sigarh.config_financiera.models import Seguro
from app.hospital.caja.models import Cobro, CobroItem
from app.tenants.hospitales.models import Tenant
from app.admin.auditoria.models import AuditLog


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


def columns(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def audit(db, tid, user, model, obj_id, action, before=None, after=None):
    db.add(AuditLog(tenant_id=tid, user_id=uuid.UUID(user["sub"]), user_name=user.get("name"),
        model=model, model_id=str(obj_id), action=action,
        old_values=jsonable_encoder(before), new_values=jsonable_encoder(after)))


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
    stmt = insert(LabCorrelativo).values(tenant_id=tid, tipo=kind, valor=1)
    stmt = stmt.on_conflict_do_update(index_elements=["tenant_id", "tipo"],
        set_={"valor": LabCorrelativo.valor + 1}).returning(LabCorrelativo.valor)
    n = await db.scalar(stmt)
    return f"{kind}-{tid.hex[:8]}-{n:08d}"


async def day_lock(db, tid, day):
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"),
                     {"key": f"laboratorio:{tid}:{day}"})


async def available(db, tid, day, excluding=None):
    cupo = (await db.execute(select(LabCupo).where(LabCupo.tenant_id == tid, LabCupo.fecha == day))).scalar_one_or_none()
    if cupo is None:
        raise HTTPException(409, detail="Configure los cupos de laboratorio para esta fecha")
    q = select(func.count()).select_from(LabMovimiento).where(
        LabMovimiento.tenant_id == tid, LabMovimiento.fecha == day, LabMovimiento.estado != "anulado")
    if excluding:
        q = q.where(LabMovimiento.id != excluding)
    used = await db.scalar(q)
    if used >= cupo.cupos:
        raise HTTPException(409, detail="No quedan cupos disponibles para esta fecha")


async def save_cupo(db, tid, user, data, creating):
    await day_lock(db, tid, data.fecha)
    obj = (await db.execute(select(LabCupo).where(LabCupo.tenant_id == tid, LabCupo.fecha == data.fecha))).scalar_one_or_none()
    if creating and obj:
        raise HTTPException(409, detail="Ya existe un registro para esta fecha; utilice Editar")
    if not creating and not obj:
        raise HTTPException(404, detail="Cupo no encontrado")
    used = await db.scalar(select(func.count()).select_from(LabMovimiento).where(
        LabMovimiento.tenant_id == tid, LabMovimiento.fecha == data.fecha, LabMovimiento.estado != "anulado"))
    if data.cupos < used:
        raise HTTPException(409, detail="No puede reducir los cupos por debajo de las reservas activas")
    before = columns(obj) if obj else None
    if obj is None:
        obj = LabCupo(tenant_id=tid, fecha=data.fecha, cupos=data.cupos, registrado_por=actor(user))
        db.add(obj)
    obj.cupos = data.cupos
    obj.registrado_por = actor(user)
    await db.flush()
    audit(db, tid, user, "LabCupo", obj.id, "actualizar" if before else "crear", before, columns(obj))
    return dict(columns(obj), usados=used, disponibles=obj.cupos-used)


async def list_cupos(db, tid, fecha=None):
    used = select(LabMovimiento.fecha, func.count().label("usados")).where(
        LabMovimiento.tenant_id == tid, LabMovimiento.estado != "anulado").group_by(LabMovimiento.fecha).subquery()
    q = select(LabCupo, func.coalesce(used.c.usados, 0)).outerjoin(used, used.c.fecha == LabCupo.fecha).where(LabCupo.tenant_id == tid)
    if fecha:
        q = q.where(LabCupo.fecha == fecha)
    return [dict(columns(c), usados=n, disponibles=c.cupos-n) for c, n in (await db.execute(q.order_by(LabCupo.fecha.desc()).limit(366))).all()]


def order_query(tid):
    return (select(OrdenLaboratorio, Patient, ClinicalRecord.record_number,
                   Empleado, Servicio.nombre, Especialidad.nombre, Cita)
        .outerjoin(AtencionMedica, and_(AtencionMedica.id == OrdenLaboratorio.atencion_medica_id, AtencionMedica.tenant_id == tid))
        .outerjoin(Cita, and_(Cita.id == AtencionMedica.cita_id, Cita.tenant_id == tid))
        .outerjoin(ProgramacionMedica, and_(ProgramacionMedica.id == Cita.programacion_medica_id, ProgramacionMedica.tenant_id == tid))
        .join(Patient, and_(Patient.id == func.coalesce(OrdenLaboratorio.patient_id, Cita.patient_id), Patient.tenant_id == tid))
        .outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id)
        .outerjoin(Empleado, and_(Empleado.id == func.coalesce(OrdenLaboratorio.medico_id, ProgramacionMedica.medico_id), Empleado.tenant_id == tid))
        .outerjoin(Servicio, and_(Servicio.id == func.coalesce(OrdenLaboratorio.servicio_id, ProgramacionMedica.servicio_id), Servicio.tenant_id == tid))
        .outerjoin(Especialidad, and_(Especialidad.id == func.coalesce(OrdenLaboratorio.especialidad_id, ProgramacionMedica.especialidad_id), Especialidad.tenant_id == tid))
        .where(OrdenLaboratorio.tenant_id == tid))


def order_out(row):
    o, p, hc, medico, servicio, especialidad, cita = row
    return dict(columns(o), patient_id=p.id, paciente=p.full_name, dni=p.dni,
        historia=hc, sexo=p.gender, fecha_nacimiento=p.birth_date, telefono=p.phone,
        medico=medico.nombre_completo if medico else None,
        medico_id=medico.id if medico else o.medico_id, servicio=servicio,
        especialidad=especialidad, numero_cuenta=o.numero_cuenta or (cita.numero_cuenta if cita else None),
        fuente_financiamiento=o.fuente_financiamiento or (cita.fuente_financiamiento if cita else None))


def filtered_orders(q, f, movement=False):
    if f.get("q"):
        for term in f["q"].split():
            q = q.where(or_(*[c.icontains(term, autoescape=True) for c in
                (Patient.first_name, Patient.last_name_paterno, Patient.last_name_materno,
                 Patient.dni, ClinicalRecord.record_number, OrdenLaboratorio.numero_orden)]))
    for key, col in (("historia", ClinicalRecord.record_number), ("cuenta", func.coalesce(OrdenLaboratorio.numero_cuenta, Cita.numero_cuenta)),
                     ("apellido", Patient.last_name_paterno)):
        if f.get(key):
            q = q.where(col.icontains(f[key], autoescape=True))
    if f.get("tipos"):
        q = q.where(OrdenLaboratorio.tipo_servicio.in_(f["tipos"]))
    if f.get("fecha"):
        q = q.where((LabMovimiento.fecha if movement else func.date(OrdenLaboratorio.created_at)) == f["fecha"])
    if f.get("estado"):
        q = q.where((LabMovimiento.estado if movement else OrdenLaboratorio.estado) == f["estado"])
    if f.get("numero"):
        q = q.where((LabMovimiento.numero if movement else OrdenLaboratorio.numero_orden).icontains(f["numero"], autoescape=True))
    return q


async def paged(db, q, page, size):
    total = await db.scalar(select(func.count()).select_from(q.order_by(None).subquery()))
    rows = (await db.execute(q.offset((page-1)*size).limit(size))).all()
    return total, rows


async def list_orders(db, tid, f, page=1, size=20):
    q = filtered_orders(order_query(tid), f).order_by(OrdenLaboratorio.created_at.desc(), OrdenLaboratorio.id)
    total, rows = await paged(db, q, page, size)
    return {"items": [order_out(r) for r in rows], "total": total, "page": page, "page_size": size}


async def order_detail(db, tid, oid):
    row = (await db.execute(order_query(tid).where(OrdenLaboratorio.id == oid))).first()
    if not row:
        raise HTTPException(404, detail="Orden no encontrada")
    data = order_out(row)
    exams = (await db.execute(select(OrdenLaboratorioItem, ExamenLaboratorio).join(
        ExamenLaboratorio, ExamenLaboratorio.id == OrdenLaboratorioItem.examen_id).where(
        OrdenLaboratorioItem.orden_id == oid, ExamenLaboratorio.tenant_id == tid))).all()
    data["items"] = [dict(columns(e), examen_id=e.id, item_id=i.id) for i, e in exams]
    data["movimiento_id"] = await db.scalar(select(LabMovimiento.id).where(LabMovimiento.tenant_id == tid, LabMovimiento.orden_id == oid))
    return data


async def create_order(db, tid, user, data):
    await own(db, Patient, tid, data.patient_id, active=True)
    await own(db, Servicio, tid, data.servicio_id, active=True)
    await own(db, Empleado, tid, data.medico_id, active=True)
    if data.especialidad_id:
        await own(db, Especialidad, tid, data.especialidad_id, active=True)
    if data.emergencia_id:
        adm = await own(db, AdmisionEmergencia, tid, data.emergencia_id)
        if adm.patient_id != data.patient_id or data.tipo_servicio != "EMERGENCIA":
            raise HTTPException(422, detail="La admisión de emergencia no corresponde al paciente y tipo de servicio")
    for eid in data.examen_ids:
        await own(db, ExamenLaboratorio, tid, eid, active=True)
    obj = OrdenLaboratorio(tenant_id=tid, numero_orden=await number(db, tid, "OL"),
        registrado_por=actor(user), **data.model_dump(exclude={"examen_ids"}))
    db.add(obj)
    await db.flush()
    for eid in data.examen_ids:
        db.add(OrdenLaboratorioItem(orden_id=obj.id, examen_id=eid))
    await db.flush()
    audit(db, tid, user, "OrdenLaboratorio", obj.id, "crear", after=columns(obj))
    return await order_detail(db, tid, obj.id)


async def make_items(db, tid, mid, items):
    for item in items:
        exam = await own(db, ExamenLaboratorio, tid, item.examen_id, active=True)
        price = item.precio if item.precio is not None else Decimal(str(exam.precio)).quantize(Decimal("0.0001"))
        if price < 0:
            raise HTTPException(422, detail="El precio del catálogo no puede ser negativo")
        db.add(LabMovimientoItem(tenant_id=tid, movimiento_id=mid, examen_id=exam.id,
            codigo=exam.codigo, nombre=exam.nombre, tipo_muestra=exam.tipo_muestra,
            cantidad=item.cantidad, precio=price, unidad=exam.unidad_medida, referencia=exam.valores_referencia))


async def save_movement(db, tid, user, data, mid=None):
    obj = await own(db, LabMovimiento, tid, mid, lock=True) if mid else None
    if obj and (obj.version != data.version or obj.estado != "agendado"):
        raise HTTPException(409, detail="Solo se puede editar un movimiento agendado sin cambios concurrentes")
    if obj and obj.orden_id != data.orden_id:
        raise HTTPException(422, detail="No puede cambiar la orden del movimiento")
    order = await own(db, OrdenLaboratorio, tid, data.orden_id, lock=True)
    await order_detail(db, tid, order.id)  # Comprueba también el paciente vinculado.
    if not obj and order.estado != "pendiente":
        raise HTTPException(409, detail="La orden ya fue procesada o anulada")
    if not obj and await db.scalar(select(LabMovimiento.id).where(LabMovimiento.tenant_id == tid, LabMovimiento.orden_id == order.id)):
        raise HTTPException(409, detail="Esta orden ya tiene un movimiento")
    await own(db, Empleado, tid, data.toma_examen_id, active=True)
    if data.medico_id:
        await own(db, Empleado, tid, data.medico_id, active=True)
        order.medico_id = data.medico_id
    requested = set((await db.scalars(select(OrdenLaboratorioItem.examen_id).where(OrdenLaboratorioItem.orden_id == order.id))).all())
    if not requested.issubset({i.examen_id for i in data.items}):
        raise HTTPException(422, detail="Debe incluir todos los exámenes solicitados en la orden")
    for day in sorted({data.fecha, obj.fecha if obj else data.fecha}):
        await day_lock(db, tid, day)
    await available(db, tid, data.fecha, mid)
    before = columns(obj) if obj else None
    values = data.model_dump(exclude={"items", "version", "medico_id"})
    if not obj:
        obj = LabMovimiento(tenant_id=tid, numero=await number(db, tid, "ML"),
                            registrado_por=actor(user), **values)
        db.add(obj)
        await db.flush()
    else:
        for k, v in values.items():
            setattr(obj, k, v)
        obj.version += 1
        await db.execute(delete(LabMovimientoItem).where(LabMovimientoItem.tenant_id == tid, LabMovimientoItem.movimiento_id == obj.id))
    await make_items(db, tid, obj.id, data.items)
    if data.cuenta_nueva and not order.numero_cuenta:
        order.numero_cuenta = await number(db, tid, "CL")
    order.estado = "en_proceso"
    await db.flush()
    audit(db, tid, user, "LabMovimiento", obj.id, "editar" if before else "agendar", before, data.model_dump())
    return await movement_detail(db, tid, obj.id)


async def list_movements(db, tid, f, page=1, size=20):
    q = order_query(tid).add_columns(LabMovimiento).join(LabMovimiento,
        and_(LabMovimiento.orden_id == OrdenLaboratorio.id, LabMovimiento.tenant_id == tid))
    q = filtered_orders(q, f, True).order_by(LabMovimiento.fecha.desc(), LabMovimiento.created_at.desc(), LabMovimiento.id)
    total, rows = await paged(db, q, page, size)
    return {"items": [dict(order_out(r[:-1]), orden_id=r[0].id, **{
        "id": r[-1].id, "numero": r[-1].numero, "fecha": r[-1].fecha, "estado": r[-1].estado,
        "registrado_por": r[-1].registrado_por, "version": r[-1].version}) for r in rows],
        "total": total, "page": page, "page_size": size}


async def movement_detail(db, tid, mid):
    obj = await own(db, LabMovimiento, tid, mid)
    order = await order_detail(db, tid, obj.orden_id)
    items = (await db.scalars(select(LabMovimientoItem).where(LabMovimientoItem.tenant_id == tid,
        LabMovimientoItem.movimiento_id == mid).order_by(LabMovimientoItem.nombre))).all()
    staff = await own(db, Empleado, tid, obj.toma_examen_id)
    total = sum((i.precio*i.cantidad for i in items), Decimal("0"))
    # Estado de pago real, tomado de Caja (CobroItem origen='LABORATORIO') -- no
    # del campo "comprobante" (texto libre, solo una anotación del técnico).
    cobrado = await db.scalar(select(func.coalesce(func.sum(CobroItem.monto), 0)).select_from(CobroItem)
        .join(Cobro, Cobro.id == CobroItem.cobro_id)
        .where(Cobro.tenant_id == tid, Cobro.estado == "registrado",
               CobroItem.origen == "LABORATORIO", CobroItem.origen_id == mid))
    cobrado = Decimal(str(cobrado))
    estado_pago = "pagado" if cobrado >= total and total > 0 else ("parcial" if cobrado > 0 else "pendiente")
    return dict(columns(obj), orden=order, toma_examen=staff.nombre_completo,
        items=[dict(columns(i), subtotal=i.precio*i.cantidad) for i in items],
        total=total, monto_cobrado=cobrado, monto_pendiente=max(total-cobrado, Decimal("0")), estado_pago=estado_pago)


async def transition(db, tid, user, mid, action, data):
    obj = await own(db, LabMovimiento, tid, mid, lock=True)
    if obj.version != data.version:
        raise HTTPException(409, detail="El movimiento cambió. Actualice la pantalla")
    before = columns(obj)
    order = await own(db, OrdenLaboratorio, tid, obj.orden_id, lock=True)
    if action == "tomar-muestra":
        if obj.estado != "agendado":
            raise HTTPException(409, detail="La muestra ya fue tomada o el movimiento está cerrado")
        obj.estado, obj.toma_at = "en_proceso", datetime.utcnow()
    elif action == "validar":
        if obj.estado != "en_proceso":
            raise HTTPException(409, detail="Debe registrar la toma de muestra antes de validar")
        items = (await db.scalars(select(LabMovimientoItem).where(LabMovimientoItem.tenant_id == tid,
            LabMovimientoItem.movimiento_id == mid))).all()
        if not items or any(not i.resultados for i in items):
            raise HTTPException(422, detail="Registre resultados de todos los exámenes antes de validar")
        obj.estado, obj.validado_at, obj.validado_por = "atendido", datetime.utcnow(), actor(user)
        order.estado = "completada"
    elif action == "anular":
        if obj.estado in ("anulado", "atendido"):
            raise HTTPException(409, detail="No se puede anular un movimiento cerrado")
        if not data.motivo:
            raise HTTPException(422, detail="Indique el motivo de anulación")
        await day_lock(db, tid, obj.fecha)
        obj.estado, obj.motivo_anulacion = "anulado", data.motivo
        order.estado = "anulada"
    else:
        raise HTTPException(404, detail="Acción no encontrada")
    obj.version += 1
    await db.flush()
    audit(db, tid, user, "LabMovimiento", mid, action, before, columns(obj))
    return await movement_detail(db, tid, mid)


async def save_results(db, tid, user, mid, data):
    obj = await own(db, LabMovimiento, tid, mid, lock=True)
    if obj.estado != "en_proceso" or obj.version != data.version:
        raise HTTPException(409, detail="Solo se pueden editar resultados en proceso; actualice si hubo cambios")
    ids = [i.item_id for i in data.items]
    if len(ids) != len(set(ids)):
        raise HTTPException(422, detail="No repita resultados del mismo examen")
    before = {}
    for item in data.items:
        target = await own(db, LabMovimientoItem, tid, item.item_id)
        if target.movimiento_id != mid:
            raise HTTPException(404, detail="Examen no encontrado en este movimiento")
        before[str(target.id)] = target.resultados
        target.resultados = [v.model_dump() for v in item.valores]
    obj.version += 1
    await db.flush()
    audit(db, tid, user, "LabMovimiento", mid, "resultados", before, data.model_dump())
    return await movement_detail(db, tid, mid)


async def catalogs(db, tid, kind, q=""):
    models = {"examenes": ExamenLaboratorio, "empleados": Empleado,
              "servicios": Servicio, "especialidades": Especialidad, "seguros": Seguro}
    model = models.get(kind)
    if model is None:
        raise HTTPException(404, detail="Catálogo no encontrado")
    query = select(model).where(model.tenant_id == tid, model.is_active.is_(True))
    if q:
        fields = [model.nombres, model.apellido_paterno, model.apellido_materno] if kind == "empleados" else [model.nombre]
        for term in q.split():
            query = query.where(or_(*[c.icontains(term, autoescape=True) for c in fields]))
    objs = (await db.scalars(query.order_by(model.id).limit(100))).all()
    if kind == "examenes":
        return [columns(x) for x in objs]
    return [{"id": x.id, "nombre": x.nombre_completo if kind == "empleados" else x.nombre} for x in objs]


async def patients(db, tid, q):
    query = select(Patient, ClinicalRecord.record_number).outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id).where(Patient.tenant_id == tid)
    for term in q.split():
        query = query.where(or_(*[c.icontains(term, autoescape=True) for c in
            (Patient.dni, Patient.first_name, Patient.last_name_paterno, Patient.last_name_materno, ClinicalRecord.record_number)]))
    return [{"id": p.id, "nombre": p.full_name, "dni": p.dni, "historia": hc,
             "sexo": p.gender, "fecha_nacimiento": p.birth_date, "telefono": p.phone}
            for p, hc in (await db.execute(query.order_by(Patient.last_name_paterno, Patient.id).limit(30))).all()]


async def patient_history(db, tid, pid):
    await own(db, Patient, tid, pid)
    q = order_query(tid).add_columns(LabMovimiento, LabMovimientoItem).join(LabMovimiento,
        and_(LabMovimiento.orden_id == OrdenLaboratorio.id, LabMovimiento.tenant_id == tid)).join(
        LabMovimientoItem, and_(LabMovimientoItem.movimiento_id == LabMovimiento.id, LabMovimientoItem.tenant_id == tid)
        ).where(Patient.id == pid).order_by(LabMovimiento.fecha.desc()).limit(200)
    return [{"fecha": r[-2].fecha, "movimiento": r[-2].numero, "examen": r[-1].nombre,
        "codigo": r[-1].codigo, "cuenta": order_out(r[:-2])["numero_cuenta"],
        "comprobante": r[-2].comprobante, "orden": r[0].numero_orden, "estado": r[-2].estado}
        for r in (await db.execute(q)).all()]


async def list_covid(db, tid, f, page, size):
    q = select(LabFichaCovid, Patient, ClinicalRecord.record_number).join(Patient,
        and_(Patient.id == LabFichaCovid.patient_id, Patient.tenant_id == tid)).outerjoin(
        ClinicalRecord, ClinicalRecord.patient_id == Patient.id).where(LabFichaCovid.tenant_id == tid)
    for key, col in (("dni", Patient.dni), ("historia", ClinicalRecord.record_number),
                     ("apellido", Patient.last_name_paterno), ("materno", Patient.last_name_materno)):
        if f.get(key):
            q = q.where(col.icontains(f[key], autoescape=True))
    if f.get("fecha"):
        q = q.where(LabFichaCovid.fecha == f["fecha"])
    if f.get("estado"):
        q = q.where(LabFichaCovid.resultado == f["estado"])
    total, rows = await paged(db, q.order_by(LabFichaCovid.fecha.desc(), LabFichaCovid.id), page, size)
    return {"items": [dict(columns(c), paciente=p.full_name, dni=p.dni, historia=hc) for c, p, hc in rows],
            "total": total, "page": page, "page_size": size}


async def save_covid(db, tid, user, data, cid=None):
    await own(db, Patient, tid, data.patient_id)
    obj = await own(db, LabFichaCovid, tid, cid, lock=True) if cid else None
    before = columns(obj) if obj else None
    if obj and obj.version != data.version:
        raise HTTPException(409, detail="La ficha cambió; vuelva a cargarla")
    if obj:
        for k, v in data.model_dump(exclude={"version"}).items():
            setattr(obj, k, v)
        obj.version += 1
    else:
        obj = LabFichaCovid(tenant_id=tid, registrado_por=actor(user), **data.model_dump())
        db.add(obj)
    await db.flush()
    audit(db, tid, user, "LabFichaCovid", obj.id, "editar" if before else "crear", before, columns(obj))
    return columns(obj)


async def audits(db, tid, mid):
    await own(db, LabMovimiento, tid, mid)
    return [columns(a) for a in (await db.scalars(select(AuditLog).where(
        AuditLog.tenant_id == tid, AuditLog.model == "LabMovimiento", AuditLog.model_id == str(mid)
    ).order_by(AuditLog.created_at.desc()).limit(200))).all()]


def pdf_document(title, hospital, sections):
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
    stream = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CellLab", fontName="Helvetica", fontSize=8, leading=11, wordWrap="CJK"))
    def para(value):
        return Paragraph(escape(str(value if value is not None else "-")).replace("\n", "<br/>"), styles["CellLab"])
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
        canvas.drawString(36, 22, "Laboratorio - Documento generado por el sistema")
        canvas.drawRightString(A4[0]-36, 22, f"Página {doc.page}")
    SimpleDocTemplate(stream, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=30,
                      bottomMargin=38, title=title).build(story, onFirstPage=footer, onLaterPages=footer)
    return stream.getvalue()


async def movement_pdf(db, tid, mid, kind):
    d = await movement_detail(db, tid, mid)
    if kind == "resultados" and d["estado"] != "atendido":
        raise HTTPException(409, detail="El informe se emite después de validar todos los resultados")
    from app.core.tenant_db import get_tenant_by_id
    tenant = await get_tenant_by_id(tid)
    hospital = tenant.name if tenant else None
    o = d["orden"]
    birth, taken = o["fecha_nacimiento"], d["fecha"]
    age = taken.year - birth.year - ((taken.month, taken.day) < (birth.month, birth.day))
    rows = [
        ["Paciente", o["paciente"], "Historia clínica", o["historia"]],
        ["Médico solicitante", o["medico"], "Sexo / edad", f"{o['sexo']} / {age} años"],
        ["Procedencia", o["servicio"], "Movimiento", d["numero"]],
        ["Cuenta", o["numero_cuenta"], "Fecha programada", d["fecha"]],
        ["Fuente financiamiento", o["fuente_financiamiento"], "Estado", d["estado"]],
        ["Toma de muestra (UTC)", d["toma_at"], "Responsable muestra", d["toma_examen"]],
    ]
    sections = [("Datos del paciente", ["Dato", "Valor", "Dato", "Valor"], rows, [90,170,90,173])]
    if kind == "ticket":
        sections.append(("Exámenes programados", ["Código", "Descripción", "Cantidad", "P. unit. S/", "Subtotal S/"],
            [[i["codigo"], i["nombre"], i["cantidad"], f"{i['precio']:.4f}", f"{i['subtotal']:.4f}"] for i in d["items"]],
            [60,243,50,85,85]))
        sections.append(("Importe referencial - no es comprobante de pago", ["Total S/", "Observaciones"],
            [[f"{d['total']:.4f}", d["observaciones"]]], [100,423]))
    else:
        for item in d["items"]:
            sections.append((item["nombre"], ["Parámetro", "Resultado", "Unidad", "Referencia / observación"],
                [[r["parametro"], r["valor"], r.get("unidad"), "\n".join(filter(None,[r.get("referencia"),r.get("observacion")]))]
                 for r in item["resultados"]], [125,170,58,170]))
        sections.append(("Validación del informe", ["Responsable", "Fecha (UTC)"],
            [[d["validado_por"], d["validado_at"]]], [340,183]))
    return pdf_document("Resultados de laboratorio" if kind == "resultados" else "Ticket de laboratorio", hospital or "Hospital", sections)


async def covid_pdf(db, tid, cid):
    obj = await own(db, LabFichaCovid, tid, cid)
    p = await own(db, Patient, tid, obj.patient_id)
    hc = await db.scalar(select(ClinicalRecord.record_number).where(ClinicalRecord.patient_id == p.id))
    from app.core.tenant_db import get_tenant_by_id
    tenant = await get_tenant_by_id(tid)
    hospital = tenant.name if tenant else None
    return pdf_document("Ficha Covid", hospital or "Hospital", [
        ("Registro de prueba", ["Campo", "Valor"], [
            ["Paciente", p.full_name], ["Documento", p.dni], ["Historia", hc], ["Fecha", obj.fecha],
            ["Tipo de prueba", obj.tipo_prueba], ["Muestra", obj.muestra], ["Resultado", obj.resultado],
            ["Observaciones", obj.observaciones], ["Registrado por", obj.registrado_por],
        ], [140,383])])


async def export_csv(db, tid, kind, f):
    import csv
    from io import StringIO
    if kind not in ("ordenes", "movimientos", "ficha-covid"):
        raise HTTPException(404, detail="Reporte no encontrado")
    loader = {"ordenes": list_orders, "movimientos": list_movements, "ficha-covid": list_covid}[kind]
    result = await loader(db, tid, f, 1, 10001)
    if result["total"] > 10000:
        raise HTTPException(422, detail="Acote los filtros: el reporte admite hasta 10000 registros")
    keys = (["fecha", "paciente", "dni", "historia", "tipo_prueba", "muestra", "resultado", "observaciones"]
            if kind == "ficha-covid" else
            ["numero_orden", "numero", "fecha", "historia", "paciente", "numero_cuenta", "tipo_servicio",
             "servicio", "medico", "fuente_financiamiento", "estado", "registrado_por"])
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(keys)
    def safe(v):
        value = str(v) if v is not None else ""
        return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else value
    for row in result["items"]:
        writer.writerow([safe(row.get(k)) for k in keys])
    return ("\ufeff" + stream.getvalue()).encode("utf-8")
