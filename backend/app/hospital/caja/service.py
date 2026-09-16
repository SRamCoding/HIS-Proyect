import uuid
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select, func, or_, text
from sqlalchemy.dialects.postgresql import insert

from app.hospital.caja.models import CajaCorrelativo, CajaSesion, Cobro, CobroItem
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import Cita, AtencionMedica, ProgramacionMedica, OrdenLaboratorio, OrdenImagen
from app.hospital.emergencia.models import AdmisionEmergencia
from app.hospital.laboratorio.models import LabMovimiento, LabMovimientoItem
from app.hospital.imagenes.models import ImagenMovimiento, ImagenMovimientoItem
from app.hospital.farmacia.models import FarmaciaMovimiento
from app.sigarh.config_financiera.models import Caja as CajaFisica, Tarifario, Seguro
from app.sigarh.rrhh.models import Empleado, Especialidad

CERO = Decimal("0")


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
    stmt = insert(CajaCorrelativo).values(tenant_id=tid, tipo=kind, valor=1)
    stmt = stmt.on_conflict_do_update(index_elements=["tenant_id", "tipo"],
        set_={"valor": CajaCorrelativo.valor + 1}).returning(CajaCorrelativo.valor)
    n = await db.scalar(stmt)
    return f"{kind}-{tid.hex[:8]}-{n:08d}"


async def origen_lock(db, tid, origen, origen_id):
    """Serializa cobros concurrentes sobre el mismo cargo (misma idea que los
    day_lock de Laboratorio/Farmacia, pero por origen+id en vez de por día)."""
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"),
                     {"key": f"caja:{tid}:{origen}:{origen_id}"})


# ─── Tarifas ──────────────────────────────────────────────────────────────

async def buscar_tarifa(db, tid, tipo_servicio, especialidad_id=None, seguro_id=None):
    """Busca la tarifa más específica disponible, en orden de preferencia:
    (especialidad+seguro) > (seguro) > (especialidad) > (genérica). El seguro
    pesa más que la especialidad porque muchas tarifas de seguro (ej. SIS) son
    tarifas topadas por norma -- cobrar la genérica en su lugar es un error
    de facturación, no solo de precisión."""
    base = select(Tarifario).where(Tarifario.tenant_id == tid, Tarifario.is_active.is_(True),
        Tarifario.tipo_servicio == tipo_servicio)
    combinaciones = []
    if especialidad_id and seguro_id:
        combinaciones.append((Tarifario.especialidad_id == especialidad_id, Tarifario.seguro_id == seguro_id))
    if seguro_id:
        combinaciones.append((Tarifario.especialidad_id.is_(None), Tarifario.seguro_id == seguro_id))
    if especialidad_id:
        combinaciones.append((Tarifario.especialidad_id == especialidad_id, Tarifario.seguro_id.is_(None)))
    combinaciones.append((Tarifario.especialidad_id.is_(None), Tarifario.seguro_id.is_(None)))
    for cond_esp, cond_seg in combinaciones:
        tarifa = await db.scalar(base.where(cond_esp, cond_seg).order_by(Tarifario.id).limit(1))
        if tarifa:
            return tarifa
    return None


async def _seguro_id_por_nombre(db, tid, fuente_financiamiento):
    """fuente_financiamiento hoy es texto libre (Cita/AdmisionEmergencia no
    tienen FK a Seguro); se resuelve contra el catálogo por nombre para poder
    aplicar la tarifa diferenciada cuando el texto coincide con un seguro
    configurado. Si no coincide, simplemente no hay tarifa diferenciada -- no
    se inventa una relación que el dato no tiene."""
    if not fuente_financiamiento or not fuente_financiamiento.strip():
        return None
    return await db.scalar(select(Seguro.id).where(Seguro.tenant_id == tid, Seguro.is_active.is_(True),
        func.lower(Seguro.nombre) == fuente_financiamiento.strip().lower()))


# ─── Cargos por origen ──────────────────────────────────────────────────────
# Cada cargo() devuelve (monto, descripcion, patient_id, tarifa_configurada).

async def _cargo_consulta_externa(db, tid, origen_id):
    cita = await own(db, Cita, tid, origen_id)
    if cita.estado == "cancelada":
        return CERO, "Consulta cancelada", cita.patient_id, True
    prog = await db.get(ProgramacionMedica, cita.programacion_medica_id)
    especialidad = await db.get(Especialidad, prog.especialidad_id) if prog and prog.especialidad_id else None
    seguro_id = await _seguro_id_por_nombre(db, tid, cita.fuente_financiamiento)
    tarifa = await buscar_tarifa(db, tid, "CONSULTA_EXTERNA", prog.especialidad_id if prog else None, seguro_id)
    desc = f"Consulta {especialidad.nombre if especialidad else ''} · Cita {cita.hora_inicio}".strip()
    monto = Decimal(str(tarifa.precio)) if tarifa else CERO
    return monto, desc, cita.patient_id, tarifa is not None


async def _cargo_emergencia(db, tid, origen_id):
    adm = await own(db, AdmisionEmergencia, tid, origen_id)
    seguro_id = await _seguro_id_por_nombre(db, tid, adm.fuente_financiamiento)
    tarifa = await buscar_tarifa(db, tid, "EMERGENCIA", None, seguro_id)
    desc = f"Atención de emergencia · {adm.servicio_emergencia}"
    monto = Decimal(str(tarifa.precio)) if tarifa else CERO
    return monto, desc, adm.patient_id, tarifa is not None


async def _paciente_de_orden_lab(db, tid, orden_id):
    row = (await db.execute(select(OrdenLaboratorio, AtencionMedica, Cita)
        .outerjoin(AtencionMedica, AtencionMedica.id == OrdenLaboratorio.atencion_medica_id)
        .outerjoin(Cita, Cita.id == AtencionMedica.cita_id)
        .where(OrdenLaboratorio.id == orden_id))).first()
    if not row:
        return None
    orden, _, cita = row
    return orden.patient_id or (cita.patient_id if cita else None)


async def _cargo_laboratorio(db, tid, origen_id):
    mov = await own(db, LabMovimiento, tid, origen_id)
    if mov.estado == "anulado":
        return CERO, "Laboratorio anulado", None, True
    total = await db.scalar(select(func.coalesce(func.sum(LabMovimientoItem.precio * LabMovimientoItem.cantidad), 0))
        .where(LabMovimientoItem.movimiento_id == mov.id))
    pid = await _paciente_de_orden_lab(db, tid, mov.orden_id)
    return Decimal(str(total)), f"Laboratorio · Movimiento {mov.numero}", pid, True


async def _paciente_de_orden_img(db, tid, orden_id):
    row = (await db.execute(select(OrdenImagen, AtencionMedica, Cita)
        .outerjoin(AtencionMedica, AtencionMedica.id == OrdenImagen.atencion_medica_id)
        .outerjoin(Cita, Cita.id == AtencionMedica.cita_id)
        .where(OrdenImagen.id == orden_id))).first()
    if not row:
        return None
    orden, _, cita = row
    return orden.patient_id or (cita.patient_id if cita else None)


async def _cargo_imagen(db, tid, origen_id):
    mov = await own(db, ImagenMovimiento, tid, origen_id)
    if mov.estado == "anulado":
        return CERO, "Imagenología anulada", None, True
    total = await db.scalar(select(func.coalesce(func.sum(ImagenMovimientoItem.precio * ImagenMovimientoItem.cantidad), 0))
        .where(ImagenMovimientoItem.movimiento_id == mov.id))
    pid = await _paciente_de_orden_img(db, tid, mov.orden_id)
    return Decimal(str(total)), f"Imagenología · Movimiento {mov.numero}", pid, True


async def _cargo_farmacia(db, tid, origen_id):
    mov = await own(db, FarmaciaMovimiento, tid, origen_id)
    if mov.concepto != "VENTA":
        return CERO, "Este movimiento de farmacia no corresponde a una venta cobrable", mov.patient_id, True
    if mov.estado == "ANULADO":
        return CERO, "Venta de farmacia anulada", mov.patient_id, True
    return Decimal(str(mov.total)), f"Farmacia · Venta {mov.numero}", mov.patient_id, True


CARGOS = {
    "CONSULTA_EXTERNA": _cargo_consulta_externa,
    "EMERGENCIA": _cargo_emergencia,
    "LABORATORIO": _cargo_laboratorio,
    "IMAGEN": _cargo_imagen,
    "FARMACIA": _cargo_farmacia,
}


async def cargo_y_pendiente(db, tid, origen, origen_id):
    loader = CARGOS.get(origen)
    if loader is None:
        raise HTTPException(404, detail="Origen de cargo no reconocido")
    cargo, desc, patient_id, tarifa_ok = await loader(db, tid, origen_id)
    cobrado = await db.scalar(select(func.coalesce(func.sum(CobroItem.monto), 0)).select_from(CobroItem)
        .join(Cobro, Cobro.id == CobroItem.cobro_id)
        .where(Cobro.tenant_id == tid, Cobro.estado == "registrado",
               CobroItem.origen == origen, CobroItem.origen_id == origen_id))
    cobrado = Decimal(str(cobrado))
    pendiente = max(cargo - cobrado, CERO)
    return cargo, cobrado, pendiente, desc, patient_id, tarifa_ok


# ─── Cuentas (agregación de cargos por numero_cuenta) ───────────────────────

async def cuenta_detalle(db, tid, numero_cuenta):
    lineas = []
    patient_id = None

    citas = (await db.scalars(select(Cita.id).where(Cita.tenant_id == tid, Cita.numero_cuenta == numero_cuenta))).all()
    emergencias = (await db.scalars(select(AdmisionEmergencia.id).where(
        AdmisionEmergencia.tenant_id == tid, AdmisionEmergencia.numero_cuenta == numero_cuenta))).all()
    lab_movs = (await db.execute(select(LabMovimiento.id).join(OrdenLaboratorio, OrdenLaboratorio.id == LabMovimiento.orden_id)
        .outerjoin(AtencionMedica, AtencionMedica.id == OrdenLaboratorio.atencion_medica_id)
        .outerjoin(Cita, Cita.id == AtencionMedica.cita_id)
        .where(LabMovimiento.tenant_id == tid,
               func.coalesce(OrdenLaboratorio.numero_cuenta, Cita.numero_cuenta) == numero_cuenta))).scalars().all()
    img_movs = (await db.execute(select(ImagenMovimiento.id).join(OrdenImagen, OrdenImagen.id == ImagenMovimiento.orden_id)
        .outerjoin(AtencionMedica, AtencionMedica.id == OrdenImagen.atencion_medica_id)
        .outerjoin(Cita, Cita.id == AtencionMedica.cita_id)
        .where(ImagenMovimiento.tenant_id == tid,
               func.coalesce(OrdenImagen.numero_cuenta, Cita.numero_cuenta) == numero_cuenta))).scalars().all()
    farmacia_movs = (await db.scalars(select(FarmaciaMovimiento.id).where(
        FarmaciaMovimiento.tenant_id == tid, FarmaciaMovimiento.concepto == "VENTA",
        FarmaciaMovimiento.numero_cuenta == numero_cuenta))).all()

    for origen, ids in (("CONSULTA_EXTERNA", citas), ("EMERGENCIA", emergencias),
                        ("LABORATORIO", lab_movs), ("IMAGEN", img_movs), ("FARMACIA", farmacia_movs)):
        for oid in ids:
            cargo, cobrado, pendiente, desc, pid, tarifa_ok = await cargo_y_pendiente(db, tid, origen, oid)
            patient_id = patient_id or pid
            lineas.append({"origen": origen, "origen_id": oid, "descripcion": desc,
                "cargo": cargo, "cobrado": cobrado, "pendiente": pendiente, "tarifa_configurada": tarifa_ok})

    paciente = None
    if patient_id:
        p = await db.get(Patient, patient_id)
        hc = await db.scalar(select(ClinicalRecord.record_number).where(ClinicalRecord.patient_id == patient_id))
        if p:
            paciente = {"id": p.id, "nombre": p.full_name, "dni": p.dni, "historia": hc}

    return {
        "numero_cuenta": numero_cuenta, "paciente": paciente, "items": lineas,
        "total_cargo": sum((l["cargo"] for l in lineas), CERO),
        "total_cobrado": sum((l["cobrado"] for l in lineas), CERO),
        "total_pendiente": sum((l["pendiente"] for l in lineas), CERO),
    }


async def buscar_cuentas(db, tid, q):
    """Números de cuenta candidatos para buscar (por número de cuenta, DNI o apellido del paciente)."""
    def filtros(cols):
        return [c.icontains(term, autoescape=True) for term in q.split() for c in cols]

    citas = select(Cita.numero_cuenta, Patient).join(Patient, Patient.id == Cita.patient_id).where(
        Cita.tenant_id == tid, Cita.numero_cuenta.is_not(None),
        or_(*filtros((Patient.dni, Patient.first_name, Patient.last_name_paterno, Patient.last_name_materno, Cita.numero_cuenta))))
    emergencias = select(AdmisionEmergencia.numero_cuenta, Patient).join(Patient, Patient.id == AdmisionEmergencia.patient_id).where(
        AdmisionEmergencia.tenant_id == tid,
        or_(*filtros((Patient.dni, Patient.first_name, Patient.last_name_paterno, Patient.last_name_materno, AdmisionEmergencia.numero_cuenta))))

    encontrados: set[str] = set()
    resultado = []
    for query in (citas, emergencias):
        for cuenta, p in (await db.execute(query.limit(20))).all():
            if cuenta and cuenta not in encontrados:
                encontrados.add(cuenta)
                resultado.append({"numero_cuenta": cuenta, "paciente": p.full_name, "dni": p.dni})
    return resultado[:20]


# ─── Sesiones de caja (apertura/cierre de turno) ────────────────────────────

async def sesion_activa_usuario(db, tid, cajero_id):
    return await db.scalar(select(CajaSesion).where(CajaSesion.tenant_id == tid,
        CajaSesion.cajero_id == cajero_id, CajaSesion.estado == "abierta").order_by(CajaSesion.abierta_at.desc()))


async def abrir_sesion(db, tid, user, data):
    cajero_id = uuid.UUID(user["empleado_id"]) if user.get("empleado_id") else None
    if not cajero_id:
        raise HTTPException(422, detail="La cuenta debe estar vinculada a un empleado para operar Caja")
    caja = await own(db, CajaFisica, tid, data.caja_id, active=True, lock=True)
    if caja.estado == "abierta":
        raise HTTPException(409, detail="Esta caja ya tiene un turno abierto")
    if await sesion_activa_usuario(db, tid, cajero_id):
        raise HTTPException(409, detail="Ya tiene un turno abierto en otra caja; ciérrelo antes de abrir uno nuevo")
    sesion = CajaSesion(tenant_id=tid, caja_id=caja.id, cajero_id=cajero_id, numero=await number(db, tid, "SC"),
        monto_apertura=data.monto_apertura, observaciones_apertura=data.observaciones_apertura, registrado_por=actor(user))
    db.add(sesion)
    caja.estado, caja.cajero_id, caja.monto_apertura = "abierta", cajero_id, data.monto_apertura
    await db.flush()
    await db.commit()
    return await sesion_detalle(db, tid, sesion.id)


async def cerrar_sesion(db, tid, user, sesion_id, data):
    sesion = await own(db, CajaSesion, tid, sesion_id, lock=True)
    if sesion.estado != "abierta":
        raise HTTPException(409, detail="Este turno ya está cerrado")
    columns(sesion)
    efectivo = await db.scalar(select(func.coalesce(func.sum(Cobro.monto), 0)).where(
        Cobro.tenant_id == tid, Cobro.caja_sesion_id == sesion.id, Cobro.estado == "registrado",
        Cobro.forma_pago == "EFECTIVO"))
    sistema = sesion.monto_apertura + Decimal(str(efectivo))
    sesion.estado = "cerrada"
    sesion.monto_cierre_declarado = data.monto_cierre_declarado
    sesion.monto_cierre_sistema = sistema
    sesion.diferencia = data.monto_cierre_declarado - sistema
    sesion.observaciones_cierre = data.observaciones_cierre
    sesion.cerrada_at = datetime.utcnow()
    caja = await own(db, CajaFisica, tid, sesion.caja_id, lock=True)
    caja.estado, caja.cajero_id = "cerrada", None
    await db.flush()
    await db.commit()
    return await sesion_detalle(db, tid, sesion.id)


async def sesion_detalle(db, tid, sesion_id):
    sesion = await own(db, CajaSesion, tid, sesion_id)
    caja = await db.get(CajaFisica, sesion.caja_id)
    cajero = await db.get(Empleado, sesion.cajero_id)
    resumen = (await db.execute(select(Cobro.forma_pago, func.coalesce(func.sum(Cobro.monto), 0), func.count())
        .where(Cobro.tenant_id == tid, Cobro.caja_sesion_id == sesion.id, Cobro.estado == "registrado")
        .group_by(Cobro.forma_pago))).all()
    return dict(columns(sesion), caja_nombre=caja.nombre if caja else None,
        cajero_nombre=cajero.nombre_completo if cajero else None,
        resumen_formas_pago=[{"forma_pago": fp, "total": t, "cantidad": c} for fp, t, c in resumen])


async def list_sesiones(db, tid, f, page=1, size=20):
    q = select(CajaSesion).where(CajaSesion.tenant_id == tid)
    if f.get("estado"):
        q = q.where(CajaSesion.estado == f["estado"])
    if f.get("caja_id"):
        q = q.where(CajaSesion.caja_id == f["caja_id"])
    total = await db.scalar(select(func.count()).select_from(q.order_by(None).subquery()))
    rows = (await db.scalars(q.order_by(CajaSesion.abierta_at.desc()).offset((page-1)*size).limit(size))).all()
    out = []
    for s in rows:
        caja = await db.get(CajaFisica, s.caja_id)
        cajero = await db.get(Empleado, s.cajero_id)
        out.append(dict(columns(s), caja_nombre=caja.nombre if caja else None,
            cajero_nombre=cajero.nombre_completo if cajero else None))
    return {"items": out, "total": total, "page": page, "page_size": size}


# ─── Cobros ──────────────────────────────────────────────────────────────

async def crear_cobro(db, tid, user, sesion_id, data):
    sesion = await own(db, CajaSesion, tid, sesion_id, lock=True)
    if sesion.estado != "abierta":
        raise HTTPException(409, detail="La sesión de caja no está abierta")
    if data.patient_id:
        await own(db, Patient, tid, data.patient_id)
    detalles = []
    for item in data.items:
        await origen_lock(db, tid, item.origen, item.origen_id)
        _, _, pendiente, _, _, _ = await cargo_y_pendiente(db, tid, item.origen, item.origen_id)
        if item.monto > pendiente + Decimal("0.0001"):
            raise HTTPException(409, detail=f"El monto de '{item.descripcion}' excede lo pendiente (S/ {pendiente})")
        detalles.append(item)
    total = sum((i.monto for i in detalles), CERO)
    cobro = Cobro(tenant_id=tid, caja_sesion_id=sesion.id, numero=await number(db, tid, "CB"),
        numero_cuenta=data.numero_cuenta, patient_id=data.patient_id, forma_pago=data.forma_pago,
        fuente_financiamiento=data.fuente_financiamiento, monto=total, registrado_por=actor(user))
    db.add(cobro)
    await db.flush()
    for item in detalles:
        db.add(CobroItem(tenant_id=tid, cobro_id=cobro.id, origen=item.origen, origen_id=item.origen_id,
            descripcion=item.descripcion, monto=item.monto))
    await db.flush()
    await db.commit()
    return await cobro_detalle(db, tid, cobro.id)


async def anular_cobro(db, tid, user, cobro_id, motivo):
    cobro = await own(db, Cobro, tid, cobro_id, lock=True)
    if cobro.estado != "registrado":
        raise HTTPException(409, detail="Este cobro ya está anulado")
    sesion = await own(db, CajaSesion, tid, cobro.caja_sesion_id)
    if sesion.estado != "abierta":
        raise HTTPException(409, detail="No se puede anular un cobro de una sesión de caja ya cerrada")
    columns(cobro)
    cobro.estado, cobro.motivo_anulacion = "anulado", motivo
    await db.flush()
    await db.commit()
    return await cobro_detalle(db, tid, cobro.id)


async def cobro_detalle(db, tid, cobro_id):
    cobro = await own(db, Cobro, tid, cobro_id)
    items = (await db.scalars(select(CobroItem).where(CobroItem.tenant_id == tid,
        CobroItem.cobro_id == cobro.id).order_by(CobroItem.descripcion))).all()
    paciente = None
    if cobro.patient_id:
        p = await db.get(Patient, cobro.patient_id)
        hc = await db.scalar(select(ClinicalRecord.record_number).where(ClinicalRecord.patient_id == cobro.patient_id))
        if p:
            paciente = {"id": p.id, "nombre": p.full_name, "dni": p.dni, "historia": hc}
    sesion = await db.get(CajaSesion, cobro.caja_sesion_id)
    caja = await db.get(CajaFisica, sesion.caja_id) if sesion else None
    return dict(columns(cobro), paciente=paciente, items=[columns(i) for i in items],
        caja_nombre=caja.nombre if caja else None, sesion_numero=sesion.numero if sesion else None)


async def list_cobros(db, tid, f, page=1, size=20):
    q = select(Cobro).where(Cobro.tenant_id == tid)
    if f.get("numero"):
        q = q.where(Cobro.numero.icontains(f["numero"], autoescape=True))
    if f.get("cuenta"):
        q = q.where(Cobro.numero_cuenta.icontains(f["cuenta"], autoescape=True))
    if f.get("estado"):
        q = q.where(Cobro.estado == f["estado"])
    if f.get("forma_pago"):
        q = q.where(Cobro.forma_pago == f["forma_pago"])
    if f.get("fecha"):
        q = q.where(func.date(Cobro.created_at) == f["fecha"])
    total = await db.scalar(select(func.count()).select_from(q.order_by(None).subquery()))
    rows = (await db.scalars(q.order_by(Cobro.created_at.desc()).offset((page-1)*size).limit(size))).all()
    out = []
    for c in rows:
        paciente = await db.get(Patient, c.patient_id) if c.patient_id else None
        out.append(dict(columns(c), paciente=paciente.full_name if paciente else None, dni=paciente.dni if paciente else None))
    return {"items": out, "total": total, "page": page, "page_size": size}


async def catalogs(db, tid, kind, q=""):
    if kind == "cajas":
        objs = (await db.scalars(select(CajaFisica).where(CajaFisica.tenant_id == tid, CajaFisica.is_active.is_(True))
            .order_by(CajaFisica.nombre))).all()
        return [columns(x) for x in objs]
    if kind == "seguros":
        objs = (await db.scalars(select(Seguro).where(Seguro.tenant_id == tid, Seguro.is_active.is_(True))
            .order_by(Seguro.nombre))).all()
        return [{"id": x.id, "nombre": x.nombre} for x in objs]
    if kind == "pacientes":
        query = select(Patient, ClinicalRecord.record_number).outerjoin(ClinicalRecord, ClinicalRecord.patient_id == Patient.id).where(Patient.tenant_id == tid)
        for term in q.split():
            query = query.where(or_(*[c.icontains(term, autoescape=True) for c in
                (Patient.dni, Patient.first_name, Patient.last_name_paterno, Patient.last_name_materno, ClinicalRecord.record_number)]))
        return [{"id": p.id, "nombre": p.full_name, "dni": p.dni, "historia": hc}
                for p, hc in (await db.execute(query.order_by(Patient.last_name_paterno, Patient.id).limit(30))).all()]
    raise HTTPException(404, detail="Catálogo no encontrado")


# ─── Documentos ─────────────────────────────────────────────────────────────

def pdf_document(title, hospital, sections):
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
    stream = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CellCaja", fontName="Helvetica", fontSize=8, leading=11, wordWrap="CJK"))
    def para(value):
        return Paragraph(escape(str(value if value is not None else "-")).replace("\n", "<br/>"), styles["CellCaja"])
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
        canvas.drawString(36, 22, "Caja - Comprobante interno, no es un comprobante de pago SUNAT")
        canvas.drawRightString(A4[0]-36, 22, f"Página {doc.page}")
    SimpleDocTemplate(stream, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=30,
                      bottomMargin=38, title=title).build(story, onFirstPage=footer, onLaterPages=footer)
    return stream.getvalue()


async def comprobante_pdf(db, tid, cobro_id):
    d = await cobro_detalle(db, tid, cobro_id)
    from app.core.tenant_db import get_tenant_by_id
    tenant = await get_tenant_by_id(tid)
    hospital = tenant.name if tenant else None
    rows = [
        ["Paciente", d["paciente"]["nombre"] if d["paciente"] else "—", "Historia clínica", d["paciente"]["historia"] if d["paciente"] else "—"],
        ["N.° cuenta", d["numero_cuenta"], "Caja", d["caja_nombre"]],
        ["Sesión", d["sesion_numero"], "Forma de pago", d["forma_pago"]],
        ["Fuente financiamiento", d["fuente_financiamiento"], "Estado", d["estado"]],
        ["Registrado por", d["registrado_por"], "Fecha (UTC)", d["created_at"]],
    ]
    sections = [("Datos del cobro", ["Dato", "Valor", "Dato", "Valor"], rows, [90,170,90,173])]
    sections.append(("Conceptos cobrados", ["Origen", "Descripción", "Monto S/"],
        [[i["origen"], i["descripcion"], f"{i['monto']:.4f}"] for i in d["items"]], [90,313,120]))
    sections.append(("Total", ["Total S/"], [[f"{d['monto']:.4f}"]], [523]))
    return pdf_document(f"Comprobante interno {d['numero']}", hospital or "Hospital", sections)


async def export_csv(db, tid, f):
    import csv
    from io import StringIO
    result = await list_cobros(db, tid, f, 1, 10001)
    if result["total"] > 10000:
        raise HTTPException(422, detail="Acote los filtros: el reporte admite hasta 10000 registros")
    keys = ["numero", "created_at", "numero_cuenta", "paciente", "dni", "forma_pago",
            "fuente_financiamiento", "monto", "estado", "registrado_por"]
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(keys)
    def safe(v):
        value = str(v) if v is not None else ""
        return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else value
    for row in result["items"]:
        writer.writerow([safe(row.get(k)) for k in keys])
    return ("﻿" + stream.getvalue()).encode("utf-8")
