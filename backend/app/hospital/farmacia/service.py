import csv, io, uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.hospital.farmacia.models import (
    FarmaciaCorrelativo, FarmaciaLote, FarmaciaMovimiento, FarmaciaMovimientoItem,
    FarmaciaDispensacion, FarmaciaDispensacionItem, FarmacotecniaOrden,
)
from app.hospital.consulta_externa.models import Receta, RecetaItem, AtencionMedica, Cita, ProgramacionMedica
from app.hospital.admision.models import Patient
from app.hospital.caja.models import Cobro, CobroItem
from app.sigarh.config_farmacia.models import Almacen, Medicamento
from app.sigarh.config_financiera.models import Seguro
from app.sigarh.mantenimiento.models import Servicio
from app.admin.auditoria.models import AuditLog

# actor()/audit() en el mismo formato que el resto de la app (Laboratorio,
# Caja, Hospitalizacion, ...): "Nombre (uuid)" para trazabilidad de auditoria.
def actor(user): return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"
def d(v): return float(v or 0)
def mov_dict(m):
    return {c.name: getattr(m,c.name) for c in m.__table__.columns}

def audit(db, tid, user, model, obj_id, action, before=None, after=None):
    db.add(AuditLog(tenant_id=tid, user_id=uuid.UUID(user["sub"]), user_name=user.get("name"),
        model=model, model_id=str(obj_id), action=action,
        old_values=jsonable_encoder(before), new_values=jsonable_encoder(after)))

async def next_number(db, tid, kind):
    year=datetime.utcnow().year
    q=await db.execute(select(FarmaciaCorrelativo).where(FarmaciaCorrelativo.tenant_id==tid,FarmaciaCorrelativo.tipo==kind,FarmaciaCorrelativo.anio==year).with_for_update())
    row=q.scalar_one_or_none()
    if not row: row=FarmaciaCorrelativo(tenant_id=tid,tipo=kind,anio=year,ultimo=0); db.add(row); await db.flush()
    row.ultimo+=1
    return f"{kind[:3]}-{year}-{row.ultimo:08d}"

async def validate_master(db, model, mid, tid, label):
    row=(await db.execute(select(model).where(model.id==mid,model.tenant_id==tid))).scalar_one_or_none()
    if not row: raise HTTPException(422, f"{label} no pertenece al hospital")
    return row

async def catalogs(db, tid, kind, q=""):
    if kind=="almacenes": model, label=Almacen, Almacen.nombre
    elif kind=="medicamentos": model, label=Medicamento, Medicamento.nombre_comercial
    elif kind=="pacientes": model, label=Patient, Patient.last_name_paterno
    elif kind=="seguros": model, label=Seguro, Seguro.nombre
    else: raise HTTPException(404,"Catálogo no soportado")
    stmt=select(model).where(model.tenant_id==tid)
    if hasattr(model,"is_active"): stmt=stmt.where(model.is_active==True)
    if q:
        fields=[label]
        if model is Medicamento: fields += [Medicamento.codigo_interno, Medicamento.dci]
        if model is Patient: fields += [Patient.dni, Patient.first_name]
        stmt=stmt.where(or_(*[f.ilike(f"%{q}%") for f in fields]))
    rows=(await db.execute(stmt.order_by(label).limit(100))).scalars().all()
    if model is Almacen: return [{"id":x.id,"codigo":x.codigo,"nombre":x.nombre,"tipo":x.tipo} for x in rows]
    if model is Medicamento: return [{"id":x.id,"codigo":x.codigo_interno,"nombre":x.nombre_comercial,"dci":x.dci,"unidad":x.unidad,"registro_sanitario":x.numero_registro_sanitario,"requiere_receta":x.requiere_receta} for x in rows]
    if model is Seguro: return [{"id":x.id,"nombre":x.nombre} for x in rows]
    return [{"id":x.id,"documento":x.dni,"nombre":x.full_name} for x in rows]

async def list_movements(db,tid,tipo=None,ambito=None,almacen=None,start=None,end=None,q=None,page=1,size=20,concepto=None):
    stmt=select(FarmaciaMovimiento).where(FarmaciaMovimiento.tenant_id==tid)
    for value,col in [(tipo,FarmaciaMovimiento.tipo),(ambito,FarmaciaMovimiento.ambito)]:
        if value: stmt=stmt.where(col==value.upper())
    if almacen: stmt=stmt.where(or_(FarmaciaMovimiento.almacen_origen_id==almacen,FarmaciaMovimiento.almacen_destino_id==almacen))
    if concepto: stmt=stmt.where(FarmaciaMovimiento.concepto==concepto.upper())
    if start: stmt=stmt.where(func.date(FarmaciaMovimiento.created_at)>=start)
    if end: stmt=stmt.where(func.date(FarmaciaMovimiento.created_at)<=end)
    if q: stmt=stmt.where(or_(FarmaciaMovimiento.numero.ilike(f"%{q}%"),FarmaciaMovimiento.numero_documento.ilike(f"%{q}%"),FarmaciaMovimiento.numero_cuenta.ilike(f"%{q}%")))
    total=await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows=(await db.execute(stmt.order_by(FarmaciaMovimiento.created_at.desc()).offset((page-1)*size).limit(size))).scalars().all()
    return {"items":[mov_dict(x) for x in rows],"total":total,"page":page,"page_size":size}

async def movement_detail(db, tid, mid):
    m = (await db.execute(select(FarmaciaMovimiento).where(FarmaciaMovimiento.id == mid, FarmaciaMovimiento.tenant_id == tid))).scalar_one_or_none()
    if not m:
        raise HTTPException(404, "Movimiento no encontrado")
    items = (await db.execute(select(FarmaciaMovimientoItem).where(
        FarmaciaMovimientoItem.movimiento_id == mid, FarmaciaMovimientoItem.tenant_id == tid))).scalars().all()
    out = mov_dict(m)
    out["items"] = [mov_dict(x) for x in items]
    if m.patient_id:
        paciente = await db.get(Patient, m.patient_id)
        out["paciente"] = paciente.full_name if paciente else None
        out["paciente_dni"] = paciente.dni if paciente else None
    if m.concepto == "VENTA":
        # Estado de pago real, tomado de Caja (CobroItem origen='FARMACIA') --
        # una venta no se marca pagada aqui, solo al registrarse el cobro.
        cobrado = await db.scalar(select(func.coalesce(func.sum(CobroItem.monto), 0)).select_from(CobroItem)
            .join(Cobro, Cobro.id == CobroItem.cobro_id)
            .where(Cobro.tenant_id == tid, Cobro.estado == "registrado",
                   CobroItem.origen == "FARMACIA", CobroItem.origen_id == mid))
        cobrado = Decimal(str(cobrado))
        out["monto_cobrado"] = cobrado
        out["monto_pendiente"] = max(m.total - cobrado, Decimal("0"))
        out["estado_pago"] = "pagado" if cobrado >= m.total and m.total > 0 else ("parcial" if cobrado > 0 else "pendiente")
    return out

async def create_movement(db, tid, user, data):
    origin = await validate_master(db, Almacen, data.almacen_origen_id, tid, "Almacén origen") if data.almacen_origen_id else None
    dest = await validate_master(db, Almacen, data.almacen_destino_id, tid, "Almacén destino") if data.almacen_destino_id else None
    payload = data.model_dump(exclude={"items", "confirmar"})
    m = FarmaciaMovimiento(tenant_id=tid, numero=await next_number(db, tid, data.tipo), registrado_por=actor(user), **payload)
    db.add(m)
    await db.flush()
    total = Decimal("0")
    for raw in data.items:
        med = await validate_master(db, Medicamento, raw.medicamento_id, tid, "Medicamento")
        target = dest if data.tipo == "INGRESO" else origin
        stmt = select(FarmaciaLote).where(FarmaciaLote.tenant_id == tid, FarmaciaLote.almacen_id == target.id,
            FarmaciaLote.medicamento_id == med.id, FarmaciaLote.numero_lote == raw.numero_lote).with_for_update()
        lot = (await db.execute(stmt)).scalar_one_or_none()
        if not lot:
            if data.tipo == "SALIDA":
                raise HTTPException(409, f"Lote {raw.numero_lote} sin existencia")
            lot = FarmaciaLote(tenant_id=tid, almacen_id=target.id, medicamento_id=med.id, numero_lote=raw.numero_lote,
                fecha_vencimiento=raw.fecha_vencimiento, registro_sanitario=raw.registro_sanitario or med.numero_registro_sanitario,
                costo_unitario=raw.precio_unitario, precio_venta=raw.precio_unitario, estado="LIBERADO", stock_actual=0)
            db.add(lot)
            await db.flush()
        if data.confirmar:
            if data.tipo == "SALIDA" and lot.stock_actual < raw.cantidad:
                raise HTTPException(409, f"Stock insuficiente para {med.nombre_comercial}, lote {raw.numero_lote}")
            lot.stock_actual += raw.cantidad if data.tipo == "INGRESO" else -raw.cantidad
            # Una distribución interna actualiza ambos establecimientos en la misma transacción.
            if data.tipo == "SALIDA" and dest:
                dl = (await db.execute(select(FarmaciaLote).where(FarmaciaLote.tenant_id == tid, FarmaciaLote.almacen_id == dest.id,
                    FarmaciaLote.medicamento_id == med.id, FarmaciaLote.numero_lote == raw.numero_lote).with_for_update())).scalar_one_or_none()
                if not dl:
                    dl = FarmaciaLote(tenant_id=tid, almacen_id=dest.id, medicamento_id=med.id, numero_lote=raw.numero_lote,
                        fecha_vencimiento=raw.fecha_vencimiento, registro_sanitario=raw.registro_sanitario or med.numero_registro_sanitario,
                        costo_unitario=raw.precio_unitario, precio_venta=raw.precio_unitario, estado="LIBERADO", stock_actual=0)
                    db.add(dl)
                dl.stock_actual += raw.cantidad
        sub = raw.cantidad * raw.precio_unitario
        total += sub
        db.add(FarmaciaMovimientoItem(tenant_id=tid, movimiento_id=m.id, medicamento_id=med.id, lote_id=lot.id,
            codigo=med.codigo_interno, descripcion=med.nombre_comercial, unidad=med.unidad, subtotal=sub,
            **raw.model_dump(exclude={"lote_id", "medicamento_id"})))
    m.total = total
    m.estado = "CONFIRMADO" if data.confirmar else "BORRADOR"
    m.confirmado_at = datetime.utcnow() if data.confirmar else None
    # Nota: una venta NO se marca pagada aqui. El pago real se registra en Caja
    # (CobroItem origen='FARMACIA', origen_id=movimiento.id) -- movement_detail
    # calcula estado_pago leyendo esos cobros, igual que Laboratorio/Imagenología.
    await db.flush()
    audit(db, tid, user, "FarmaciaMovimiento", m.id, "confirmar" if data.confirmar else "crear", after=mov_dict(m))
    await db.commit()
    return await movement_detail(db, tid, m.id)

async def list_stock(db,tid,almacen=None,q=None,days=90):
    stmt=select(FarmaciaLote,Medicamento,Almacen).join(Medicamento,Medicamento.id==FarmaciaLote.medicamento_id).join(Almacen,Almacen.id==FarmaciaLote.almacen_id).where(FarmaciaLote.tenant_id==tid,FarmaciaLote.stock_actual>0)
    if almacen: stmt=stmt.where(FarmaciaLote.almacen_id==almacen)
    if q: stmt=stmt.where(or_(Medicamento.nombre_comercial.ilike(f"%{q}%"),Medicamento.codigo_interno.ilike(f"%{q}%"),FarmaciaLote.numero_lote.ilike(f"%{q}%")))
    rows=(await db.execute(stmt.order_by(FarmaciaLote.fecha_vencimiento))).all(); today=date.today()
    return [{"lote_id":l.id,"almacen_id":a.id,"almacen":a.nombre,"medicamento_id":m.id,"codigo":m.codigo_interno,"medicamento":m.nombre_comercial,"dci":m.dci,"unidad":m.unidad,"forma_farmaceutica":m.forma_farmaceutica,"concentracion":m.concentracion,"registro_sanitario":l.registro_sanitario or m.numero_registro_sanitario,"requiere_receta":m.requiere_receta,"controlado":m.controlado,"cadena_frio":m.requiere_cadena_frio,"lote":l.numero_lote,"vencimiento":l.fecha_vencimiento,"stock":d(l.stock_actual),"costo":d(l.costo_unitario),"valor":d(l.stock_actual*l.costo_unitario),"estado":("VENCIDO" if l.fecha_vencimiento<today else "VENCIMIENTO" if l.fecha_vencimiento<=today+timedelta(days=days) else l.estado)} for l,m,a in rows]

async def list_recipes(db,tid,status=None,q=None):
    stmt=select(Receta,Patient,Servicio).join(AtencionMedica,AtencionMedica.id==Receta.atencion_medica_id).join(Cita,Cita.id==AtencionMedica.cita_id).join(Patient,Patient.id==Cita.patient_id).outerjoin(ProgramacionMedica,ProgramacionMedica.id==Cita.programacion_medica_id).outerjoin(Servicio,Servicio.id==ProgramacionMedica.servicio_id).where(Receta.tenant_id==tid)
    if status: stmt=stmt.where(Receta.estado==status)
    if q: stmt=stmt.where(or_(Receta.numero_receta.ilike(f"%{q}%"),Patient.dni.ilike(f"%{q}%"),Patient.last_name_paterno.ilike(f"%{q}%")))
    rows=(await db.execute(stmt.order_by(Receta.created_at.desc()).limit(200))).all()
    return [{"id":r.id,"numero":r.numero_receta,"fecha":r.created_at,"estado":r.estado,"paciente":p.full_name,"documento":p.dni,"servicio":s.nombre if s else None} for r,p,s in rows]

async def recipe_detail(db,tid,rid):
    r=(await db.execute(select(Receta).where(Receta.id==rid,Receta.tenant_id==tid))).scalar_one_or_none()
    if not r: raise HTTPException(404,"Receta no encontrada")
    rows=(await db.execute(select(RecetaItem,Medicamento).join(Medicamento,Medicamento.id==RecetaItem.medicamento_id).where(RecetaItem.receta_id==rid,Medicamento.tenant_id==tid))).all()
    return {"id":r.id,"numero":r.numero_receta,"estado":r.estado,"items":[{"id":i.id,"medicamento_id":m.id,"codigo":m.codigo_interno,"nombre":m.nombre_comercial,"cantidad":i.cantidad,"dosis":i.dosis,"frecuencia":i.frecuencia,"duracion_dias":i.duracion_dias,"via":m.via_administracion} for i,m in rows]}

async def dispense(db, tid, user, rid, data):
    rec = await recipe_detail(db, tid, rid)
    await validate_master(db, Almacen, data.almacen_id, tid, "Farmacia")
    requested = {x.receta_item_id: Decimal(x.cantidad) for x in data.items}
    med_by_item = {uuid.UUID(str(x["id"])): uuid.UUID(str(x["medicamento_id"])) for x in rec["items"]}
    if not set(requested) <= set(med_by_item):
        raise HTTPException(422, "Ítem ajeno a la receta")
    movement = FarmaciaMovimiento(tenant_id=tid, numero=await next_number(db, tid, "DISPENSACION"), tipo="SALIDA",
        ambito="FARMACIA", concepto="DISPENSACION", almacen_origen_id=data.almacen_id, observaciones=data.observaciones,
        estado="CONFIRMADO", registrado_por=actor(user), confirmado_at=datetime.utcnow())
    db.add(movement)
    await db.flush()
    disp = FarmaciaDispensacion(tenant_id=tid, numero=await next_number(db, tid, "DISPENSACION"), receta_id=rid,
        almacen_id=data.almacen_id, movimiento_id=movement.id, estado="DESPACHADA", observaciones=data.observaciones,
        dispensado_por=actor(user))
    db.add(disp)
    await db.flush()
    total = Decimal(0)
    for item_id, qty in requested.items():
        med_id = med_by_item[item_id]
        remaining = qty
        prescribed = Decimal(str(next(x["cantidad"] for x in rec["items"] if uuid.UUID(str(x["id"])) == item_id)))
        already = await db.scalar(select(func.coalesce(func.sum(FarmaciaDispensacionItem.cantidad), 0))
            .join(FarmaciaDispensacion, FarmaciaDispensacion.id == FarmaciaDispensacionItem.dispensacion_id)
            .where(FarmaciaDispensacionItem.receta_item_id == item_id, FarmaciaDispensacion.tenant_id == tid,
                   FarmaciaDispensacion.estado != "ANULADA"))
        if Decimal(str(already or 0)) + qty > prescribed:
            raise HTTPException(409, "La cantidad supera lo prescrito")
        lots = (await db.execute(select(FarmaciaLote).where(FarmaciaLote.tenant_id == tid, FarmaciaLote.almacen_id == data.almacen_id,
            FarmaciaLote.medicamento_id == med_id, FarmaciaLote.stock_actual > 0, FarmaciaLote.fecha_vencimiento >= date.today(),
            FarmaciaLote.estado == "LIBERADO").order_by(FarmaciaLote.fecha_vencimiento).with_for_update())).scalars().all()
        med = await validate_master(db, Medicamento, med_id, tid, "Medicamento")
        if sum((x.stock_actual for x in lots), Decimal(0)) < qty:
            raise HTTPException(409, f"Stock insuficiente: {med.nombre_comercial}")
        for lot in lots:
            take = min(remaining, lot.stock_actual)
            lot.stock_actual -= take
            remaining -= take
            sub = take * lot.precio_venta
            total += sub
            db.add(FarmaciaDispensacionItem(tenant_id=tid, dispensacion_id=disp.id, receta_item_id=item_id, lote_id=lot.id, cantidad=take))
            db.add(FarmaciaMovimientoItem(tenant_id=tid, movimiento_id=movement.id, medicamento_id=med.id, lote_id=lot.id,
                codigo=med.codigo_interno, descripcion=med.nombre_comercial, unidad=med.unidad, numero_lote=lot.numero_lote,
                fecha_vencimiento=lot.fecha_vencimiento, registro_sanitario=lot.registro_sanitario, cantidad=take,
                precio_unitario=lot.precio_venta, subtotal=sub))
            if remaining <= 0:
                break
    movement.total = total
    r = (await db.execute(select(Receta).where(Receta.id == rid))).scalar_one()
    prescribed = sum(Decimal(str(x["cantidad"])) for x in rec["items"])
    dispatched = await db.scalar(select(func.coalesce(func.sum(FarmaciaDispensacionItem.cantidad), 0))
        .join(FarmaciaDispensacion, FarmaciaDispensacion.id == FarmaciaDispensacionItem.dispensacion_id)
        .where(FarmaciaDispensacion.receta_id == rid, FarmaciaDispensacion.estado != "ANULADA"))
    r.estado = "despachada" if Decimal(str(dispatched or 0)) >= prescribed else "parcial"
    await db.flush()
    audit(db, tid, user, "FarmaciaMovimiento", movement.id, "dispensar", after=mov_dict(movement))
    audit(db, tid, user, "FarmaciaDispensacion", disp.id, "crear", after=mov_dict(disp))
    await db.commit()
    return {"id": disp.id, "numero": disp.numero, "estado": disp.estado, "total": d(total)}


async def cancel_movement(db, tid, user, mid, motivo):
    m = (await db.execute(select(FarmaciaMovimiento).where(FarmaciaMovimiento.id == mid,
        FarmaciaMovimiento.tenant_id == tid).with_for_update())).scalar_one_or_none()
    if not m:
        raise HTTPException(404, "Movimiento no encontrado")
    if m.estado != "CONFIRMADO":
        raise HTTPException(409, "Solo se anulan movimientos confirmados")
    before = mov_dict(m)
    items = (await db.execute(select(FarmaciaMovimientoItem).where(
        FarmaciaMovimientoItem.movimiento_id == mid, FarmaciaMovimientoItem.tenant_id == tid))).scalars().all()
    for item in items:
        lot = (await db.execute(select(FarmaciaLote).where(FarmaciaLote.id == item.lote_id,
            FarmaciaLote.tenant_id == tid).with_for_update())).scalar_one()
        if m.tipo == "INGRESO" and lot.stock_actual < item.cantidad:
            raise HTTPException(409, "No se puede anular: el lote ya fue consumido")
        lot.stock_actual += item.cantidad if m.tipo == "SALIDA" else -item.cantidad
        if m.tipo == "SALIDA" and m.almacen_destino_id:
            dl = (await db.execute(select(FarmaciaLote).where(FarmaciaLote.tenant_id == tid, FarmaciaLote.almacen_id == m.almacen_destino_id,
                FarmaciaLote.medicamento_id == item.medicamento_id, FarmaciaLote.numero_lote == item.numero_lote).with_for_update())).scalar_one_or_none()
            if not dl or dl.stock_actual < item.cantidad:
                raise HTTPException(409, "El stock transferido ya fue consumido en destino")
            dl.stock_actual -= item.cantidad
    m.estado = "ANULADO"
    m.motivo_anulacion = motivo
    disp = (await db.execute(select(FarmaciaDispensacion).where(FarmaciaDispensacion.movimiento_id == mid,
        FarmaciaDispensacion.tenant_id == tid))).scalar_one_or_none()
    if disp:
        disp.estado = "ANULADA"
    await db.flush()
    audit(db, tid, user, "FarmaciaMovimiento", m.id, "anular", before=before, after=mov_dict(m))
    await db.commit()
    return await movement_detail(db, tid, mid)

async def report(db,tid,kind,start=None,end=None,almacen=None,q=None):
    if kind in {"saldos","saldo-almacen","digemid"}: return await list_stock(db,tid,almacen,q)
    stmt=select(FarmaciaMovimientoItem,FarmaciaMovimiento).join(FarmaciaMovimiento,FarmaciaMovimiento.id==FarmaciaMovimientoItem.movimiento_id).where(FarmaciaMovimiento.tenant_id==tid,FarmaciaMovimiento.estado=="CONFIRMADO")
    if start: stmt=stmt.where(func.date(FarmaciaMovimiento.created_at)>=start)
    if end: stmt=stmt.where(func.date(FarmaciaMovimiento.created_at)<=end)
    rows=(await db.execute(stmt)).all()
    detail=[{"fecha":m.created_at,"movimiento":m.numero,"tipo":m.tipo,"concepto":m.concepto,"codigo":i.codigo,"medicamento":i.descripcion,"lote":i.numero_lote,"vencimiento":i.fecha_vencimiento,"cantidad":d(i.cantidad),"precio":d(i.precio_unitario),"total":d(i.subtotal)} for i,m in rows]
    if kind=="idi-diario": return [x for x in detail if x["tipo"]=="SALIDA"]
    if kind=="ici-diario":
        grouped={}
        for x in detail:
            k=(x["codigo"],x["medicamento"]); g=grouped.setdefault(k,{"codigo":k[0],"medicamento":k[1],"ingresos":0.0,"salidas":0.0,"valor_salidas":0.0})
            g["ingresos" if x["tipo"]=="INGRESO" else "salidas"]+=x["cantidad"]
            if x["tipo"]=="SALIDA": g["valor_salidas"]+=x["total"]
        return list(grouped.values())
    return detail

async def csv_report(db,tid,kind,start=None,end=None,almacen=None,q=None):
    rows=await report(db,tid,kind,start,end,almacen,q); out=io.StringIO(newline="");
    if rows:
        w=csv.DictWriter(out,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    return '\ufeff'+out.getvalue()


# \u2500\u2500\u2500 Farmacotecnia (preparaciones magistrales / redosificaci\u00f3n) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

async def list_farmacotecnia(db, tid, estado=None):
    stmt = select(FarmacotecniaOrden).where(FarmacotecniaOrden.tenant_id == tid)
    if estado:
        stmt = stmt.where(FarmacotecniaOrden.estado == estado.upper())
    rows = (await db.execute(stmt.order_by(FarmacotecniaOrden.created_at.desc()))).scalars().all()
    return [mov_dict(x) for x in rows]


async def create_farmacotecnia(db, tid, user, data):
    row = FarmacotecniaOrden(tenant_id=tid, numero=await next_number(db, tid, "FARMACOTECNIA"), **data.model_dump())
    db.add(row)
    await db.flush()
    audit(db, tid, user, "FarmacotecniaOrden", row.id, "crear", after=mov_dict(row))
    await db.commit()
    await db.refresh(row)
    return mov_dict(row)


async def update_farmacotecnia_estado(db, tid, user, oid, data):
    row = (await db.execute(select(FarmacotecniaOrden).where(FarmacotecniaOrden.id == oid,
        FarmacotecniaOrden.tenant_id == tid).with_for_update())).scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Orden no encontrada")
    before = mov_dict(row)
    row.estado = data.estado.upper()
    row.control_calidad = data.control_calidad
    row.observaciones = data.observaciones
    row.responsable = actor(user)
    await db.flush()
    audit(db, tid, user, "FarmacotecniaOrden", row.id, "actualizar_estado", before=before, after=mov_dict(row))
    await db.commit()
    await db.refresh(row)
    return mov_dict(row)


# \u2500\u2500\u2500 Reporte PDF \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

def pdf_document(title, hospital, headers, rows):
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
    stream = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CellFarm", fontName="Helvetica", fontSize=7, leading=9, wordWrap="CJK"))
    def para(value):
        return Paragraph(escape(str(value if value is not None else "-")), styles["CellFarm"])
    story = [Paragraph(escape(hospital), styles["Title"]), Paragraph(escape(title), styles["Heading2"]), Spacer(1, 10)]
    if rows:
        table = LongTable([[para(h) for h in headers]] + [[para(r.get(k, "")) for k in headers] for r in rows],
                          repeatRows=1, splitInRow=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#167dac")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#bccbd5")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("Sin registros para estos filtros.", styles["Normal"]))
    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.drawString(20, 16, "Farmacia - Documento generado por el sistema")
        canvas.drawRightString(landscape(A4)[0]-20, 16, f"P\u00e1gina {doc.page}")
    SimpleDocTemplate(stream, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=24,
                      bottomMargin=30, title=title).build(story, onFirstPage=footer, onLaterPages=footer)
    return stream.getvalue()


async def pdf_report(db, tid, kind, start=None, end=None, almacen=None, q=None):
    rows = await report(db, tid, kind, start, end, almacen, q)
    from app.core.tenant_db import get_tenant_by_id
    tenant = await get_tenant_by_id(tid)
    headers = list(rows[0].keys()) if rows else []
    return pdf_document(f"Farmacia \u00b7 {kind.upper()}", tenant.name if tenant else "Hospital", headers, rows)
