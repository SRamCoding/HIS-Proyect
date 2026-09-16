import uuid
from datetime import date, datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.banco_sangre.models import (
    BancoSangreCorrelativo, Donante, UnidadSangre, ComponenteSanguineo,
    SolicitudTransfusional, SolicitudComponenteAsignado, MovimientoSangre,
)
from app.hospital.admision.models import Patient
from app.hospital.consulta_externa.models import AtencionMedica, Cita, Hospitalizacion
from app.hospital.emergencia.models import AtencionEmergencia, AdmisionEmergencia
from app.sigarh.rrhh.models import Empleado

# Vida útil de referencia por tipo de hemocomponente (estándar de medicina
# transfusional; el banco de sangre real puede ajustar según su sistema de
# conservación/anticoagulante exacto).
_VIDA_UTIL_DIAS = {
    "SANGRE_TOTAL": 35,
    "PAQUETE_GLOBULAR": 35,
    "PLASMA_FRESCO_CONGELADO": 365,
    "PLAQUETAS": 5,
    "CRIOPRECIPITADO": 365,
}

# Compatibilidad ABO/Rh para componentes celulares (Paquete Globular, Sangre
# Total) -- bioquímica de transfusión estándar. No se aplica a plasma,
# plaquetas ni crioprecipitado: su compatibilidad es distinta (o menos
# restrictiva) y la determina la prueba cruzada, no una regla automática aquí.
_COMPATIBLES_CELULARES = {"O": {"O"}, "A": {"A", "O"}, "B": {"B", "O"}, "AB": {"A", "B", "AB", "O"}}


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


async def _siguiente(db: AsyncSession, tid: uuid.UUID, tipo: str, prefijo: str) -> str:
    stmt = insert(BancoSangreCorrelativo).values(tenant_id=tid, tipo=tipo, valor=1)
    stmt = stmt.on_conflict_do_update(index_elements=["tenant_id", "tipo"],
        set_={"valor": BancoSangreCorrelativo.valor + 1}).returning(BancoSangreCorrelativo.valor)
    n = await db.scalar(stmt)
    return f"{prefijo}-{n:08d}"


def _compatible(tipo: str, g_don: str, rh_don: str, g_rec: str, rh_rec: str) -> bool:
    if tipo not in ("PAQUETE_GLOBULAR", "SANGRE_TOTAL"):
        return True
    if g_don not in _COMPATIBLES_CELULARES.get(g_rec, set()):
        return False
    if rh_rec == "-" and rh_don == "+":
        return False
    return True


async def _expirar_vencidos(db: AsyncSession, tid: uuid.UUID):
    """Nunca debe mostrarse como disponible un componente vencido -- se
    verifica de forma perezosa cada vez que se consulta el inventario."""
    hoy = date.today()
    vencidos = (await db.scalars(select(ComponenteSanguineo).where(
        ComponenteSanguineo.tenant_id == tid, ComponenteSanguineo.estado == "disponible",
        ComponenteSanguineo.fecha_vencimiento < hoy))).all()
    for c in vencidos:
        c.estado = "vencido"
        db.add(MovimientoSangre(id=uuid.uuid4(), tenant_id=tid, componente_id=c.id, tipo="vencimiento",
            observaciones=f"Vencido el {c.fecha_vencimiento.isoformat()}", registrado_por="sistema"))
    if vencidos:
        await db.commit()


# ─── Donantes ────────────────────────────────────────────────────────────

async def crear_donante(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> Donante:
    existente = await db.scalar(select(Donante).where(Donante.tenant_id == tid, Donante.dni == data.dni))
    if existente:
        raise HTTPException(409, detail="Ya existe un donante registrado con ese DNI")
    donante = Donante(id=uuid.uuid4(), tenant_id=tid, **data.model_dump())
    db.add(donante)
    await db.flush()
    await db.commit()
    return donante


async def list_donantes(db: AsyncSession, tid: uuid.UUID, q: str = "") -> list[dict]:
    query = select(Donante).where(Donante.tenant_id == tid)
    if q:
        query = query.where(or_(Donante.dni.icontains(q, autoescape=True), Donante.nombres.icontains(q, autoescape=True),
            Donante.apellido_paterno.icontains(q, autoescape=True), Donante.apellido_materno.icontains(q, autoescape=True)))
    donantes = (await db.scalars(query.order_by(Donante.apellido_paterno))).all()
    return [{
        "id": d.id, "dni": d.dni, "nombre_completo": d.nombre_completo, "fecha_nacimiento": d.fecha_nacimiento,
        "sexo": d.sexo, "celular": d.celular, "correo": d.correo, "grupo_sanguineo": d.grupo_sanguineo,
        "factor_rh": d.factor_rh, "fecha_ultima_donacion": d.fecha_ultima_donacion, "is_active": d.is_active,
    } for d in donantes]


# ─── Unidades de sangre (extracción + tamizaje) ─────────────────────────────

async def crear_unidad(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    donante = await db.get(Donante, data.donante_id)
    if donante is None or donante.tenant_id != tid:
        raise HTTPException(404, detail="Donante no encontrado")
    if not donante.is_active:
        raise HTTPException(409, detail="El donante está diferido permanentemente")

    numero = await _siguiente(db, tid, "UNIDAD", f"UNI-{tid.hex[:6].upper()}")
    unidad = UnidadSangre(id=uuid.uuid4(), tenant_id=tid, donante_id=data.donante_id, numero_unidad=numero,
        peso_kg=data.peso_kg, hemoglobina_g_dl=data.hemoglobina_g_dl, presion_sistolica=data.presion_sistolica,
        presion_diastolica=data.presion_diastolica, grupo_sanguineo=data.grupo_sanguineo, factor_rh=data.factor_rh,
        registrado_por=actor(user))
    db.add(unidad)
    donante.grupo_sanguineo = data.grupo_sanguineo
    donante.factor_rh = data.factor_rh
    donante.fecha_ultima_donacion = date.today()
    await db.flush()
    await db.commit()
    return await _unidad_out(db, unidad)


async def _unidad_out(db: AsyncSession, unidad: UnidadSangre) -> dict:
    donante = await db.get(Donante, unidad.donante_id)
    return {
        "id": unidad.id, "numero_unidad": unidad.numero_unidad, "donante_id": unidad.donante_id,
        "donante_nombre": donante.nombre_completo if donante else None, "donante_dni": donante.dni if donante else None,
        "fecha_extraccion": unidad.fecha_extraccion, "grupo_sanguineo": unidad.grupo_sanguineo, "factor_rh": unidad.factor_rh,
        "peso_kg": unidad.peso_kg, "hemoglobina_g_dl": unidad.hemoglobina_g_dl,
        "tamizaje_registrado": unidad.tamizaje_registrado_at is not None,
        "vih_reactivo": unidad.vih_reactivo, "hbsag_reactivo": unidad.hbsag_reactivo, "hcv_reactivo": unidad.hcv_reactivo,
        "sifilis_reactivo": unidad.sifilis_reactivo, "chagas_reactivo": unidad.chagas_reactivo,
        "apto": unidad.apto, "motivo_diferido": unidad.motivo_diferido, "estado": unidad.estado,
    }


async def list_unidades(db: AsyncSession, tid: uuid.UUID, estado: str | None = None) -> list[dict]:
    query = select(UnidadSangre).where(UnidadSangre.tenant_id == tid)
    if estado:
        query = query.where(UnidadSangre.estado == estado)
    unidades = (await db.scalars(query.order_by(UnidadSangre.fecha_extraccion.desc()))).all()
    return [await _unidad_out(db, u) for u in unidades]


async def registrar_tamizaje(db: AsyncSession, tid: uuid.UUID, user: dict, unidad_id: uuid.UUID, data) -> dict:
    unidad = await db.get(UnidadSangre, unidad_id)
    if unidad is None or unidad.tenant_id != tid:
        raise HTTPException(404, detail="Unidad no encontrada")
    if unidad.tamizaje_registrado_at is not None:
        raise HTTPException(409, detail="Esta unidad ya tiene tamizaje registrado")

    algun_reactivo = any([data.vih_reactivo, data.hbsag_reactivo, data.hcv_reactivo, data.sifilis_reactivo, data.chagas_reactivo])
    unidad.vih_reactivo = data.vih_reactivo
    unidad.hbsag_reactivo = data.hbsag_reactivo
    unidad.hcv_reactivo = data.hcv_reactivo
    unidad.sifilis_reactivo = data.sifilis_reactivo
    unidad.chagas_reactivo = data.chagas_reactivo
    unidad.tamizaje_registrado_at = datetime.utcnow()

    if algun_reactivo:
        unidad.apto = False
        unidad.motivo_diferido = data.motivo_diferido or "Tamizaje serológico reactivo"
        unidad.estado = "descartada"
    elif data.motivo_diferido:
        unidad.apto = False
        unidad.motivo_diferido = data.motivo_diferido
        unidad.estado = "descartada"
    else:
        unidad.apto = True

    await db.commit()
    return await _unidad_out(db, unidad)


async def fraccionar_unidad(db: AsyncSession, tid: uuid.UUID, user: dict, unidad_id: uuid.UUID, data) -> list[dict]:
    unidad = await db.get(UnidadSangre, unidad_id)
    if unidad is None or unidad.tenant_id != tid:
        raise HTTPException(404, detail="Unidad no encontrada")
    if unidad.apto is not True:
        raise HTTPException(400, detail="Solo se pueden fraccionar unidades aptas (tamizaje no reactivo)")
    if unidad.estado != "extraida":
        raise HTTPException(409, detail=f"La unidad ya está en estado '{unidad.estado}'")

    componentes = []
    for tipo in data.tipos:
        codigo = await _siguiente(db, tid, "COMPONENTE", f"CMP-{tid.hex[:6].upper()}")
        vencimiento = date.today() + timedelta(days=_VIDA_UTIL_DIAS[tipo])
        componente = ComponenteSanguineo(id=uuid.uuid4(), tenant_id=tid, unidad_sangre_id=unidad.id, codigo=codigo,
            tipo=tipo, grupo_sanguineo=unidad.grupo_sanguineo, factor_rh=unidad.factor_rh, fecha_vencimiento=vencimiento)
        db.add(componente)
        await db.flush()
        db.add(MovimientoSangre(id=uuid.uuid4(), tenant_id=tid, componente_id=componente.id,
            tipo="ingreso_fraccionamiento", observaciones=f"Fraccionado de {unidad.numero_unidad}", registrado_por=actor(user)))
        componentes.append(componente)

    unidad.estado = "fraccionada"
    await db.commit()
    return [_componente_out(c) for c in componentes]


def _componente_out(c: ComponenteSanguineo) -> dict:
    return {
        "id": c.id, "codigo": c.codigo, "tipo": c.tipo, "grupo_sanguineo": c.grupo_sanguineo, "factor_rh": c.factor_rh,
        "fecha_produccion": c.fecha_produccion, "fecha_vencimiento": c.fecha_vencimiento, "estado": c.estado,
        "dias_para_vencer": (c.fecha_vencimiento - date.today()).days,
    }


async def list_componentes(db: AsyncSession, tid: uuid.UUID, estado: str | None = None, tipo: str | None = None) -> list[dict]:
    await _expirar_vencidos(db, tid)
    query = select(ComponenteSanguineo).where(ComponenteSanguineo.tenant_id == tid)
    if estado:
        query = query.where(ComponenteSanguineo.estado == estado)
    if tipo:
        query = query.where(ComponenteSanguineo.tipo == tipo)
    componentes = (await db.scalars(query.order_by(ComponenteSanguineo.fecha_vencimiento))).all()
    return [_componente_out(c) for c in componentes]


async def inventario_resumen(db: AsyncSession, tid: uuid.UUID) -> list[dict]:
    await _expirar_vencidos(db, tid)
    rows = (await db.execute(select(ComponenteSanguineo.tipo, ComponenteSanguineo.grupo_sanguineo,
        ComponenteSanguineo.factor_rh, func.count()).where(ComponenteSanguineo.tenant_id == tid,
        ComponenteSanguineo.estado == "disponible").group_by(ComponenteSanguineo.tipo,
        ComponenteSanguineo.grupo_sanguineo, ComponenteSanguineo.factor_rh).order_by(ComponenteSanguineo.tipo))).all()
    return [{"tipo": t, "grupo_sanguineo": g, "factor_rh": rh, "unidades_disponibles": cnt} for t, g, rh, cnt in rows]


async def list_movimientos(db: AsyncSession, tid: uuid.UUID, componente_id: uuid.UUID | None = None,
                            page: int = 1, page_size: int = 20) -> dict:
    query = select(MovimientoSangre, ComponenteSanguineo).join(
        ComponenteSanguineo, MovimientoSangre.componente_id == ComponenteSanguineo.id).where(
        MovimientoSangre.tenant_id == tid)
    if componente_id:
        query = query.where(MovimientoSangre.componente_id == componente_id)
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    rows = (await db.execute(query.order_by(MovimientoSangre.created_at.desc())
        .offset((page - 1) * page_size).limit(page_size))).all()
    items = [{
        "id": m.id, "tipo": m.tipo, "componente_codigo": c.codigo, "componente_tipo": c.tipo,
        "observaciones": m.observaciones, "registrado_por": m.registrado_por, "created_at": m.created_at,
    } for m, c in rows]
    return {"items": items, "total": total or 0, "page": page, "page_size": page_size}


# ─── Solicitudes transfusionales ────────────────────────────────────────────

async def _resolver_patient_id(db: AsyncSession, tid: uuid.UUID, data) -> uuid.UUID:
    if data.atencion_medica_id:
        pid = await db.scalar(select(Cita.patient_id).join(AtencionMedica, AtencionMedica.cita_id == Cita.id).where(
            AtencionMedica.id == data.atencion_medica_id, AtencionMedica.tenant_id == tid))
    elif data.atencion_emergencia_id:
        pid = await db.scalar(select(AdmisionEmergencia.patient_id).join(AtencionEmergencia,
            AtencionEmergencia.admision_id == AdmisionEmergencia.id).where(
            AtencionEmergencia.id == data.atencion_emergencia_id, AtencionEmergencia.tenant_id == tid))
    else:
        pid = await db.scalar(select(Hospitalizacion.patient_id).where(
            Hospitalizacion.id == data.hospitalizacion_id, Hospitalizacion.tenant_id == tid))
    if pid is None:
        raise HTTPException(404, detail="No se encontró el origen clínico indicado")
    return pid


async def crear_solicitud(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    patient_id = await _resolver_patient_id(db, tid, data)
    numero = await _siguiente(db, tid, "SOLICITUD", f"TRF-{tid.hex[:6].upper()}")
    solicitud = SolicitudTransfusional(id=uuid.uuid4(), tenant_id=tid, atencion_medica_id=data.atencion_medica_id,
        atencion_emergencia_id=data.atencion_emergencia_id, hospitalizacion_id=data.hospitalizacion_id,
        patient_id=patient_id, medico_solicitante_id=data.medico_solicitante_id, numero_solicitud=numero,
        tipo_componente=data.tipo_componente, cantidad_unidades=data.cantidad_unidades,
        grupo_sanguineo_paciente=data.grupo_sanguineo_paciente, factor_rh_paciente=data.factor_rh_paciente,
        urgencia=data.urgencia, motivo_clinico=data.motivo_clinico, registrado_por=actor(user))
    db.add(solicitud)
    await db.flush()
    await db.commit()
    return await _solicitud_out(db, solicitud)


async def _solicitud_out(db: AsyncSession, s: SolicitudTransfusional) -> dict:
    paciente = await db.get(Patient, s.patient_id)
    medico = await db.get(Empleado, s.medico_solicitante_id) if s.medico_solicitante_id else None
    asignaciones = (await db.execute(select(SolicitudComponenteAsignado, ComponenteSanguineo).join(
        ComponenteSanguineo, SolicitudComponenteAsignado.componente_id == ComponenteSanguineo.id).where(
        SolicitudComponenteAsignado.solicitud_id == s.id))).all()
    return {
        "id": s.id, "numero_solicitud": s.numero_solicitud, "patient_id": s.patient_id,
        "paciente_nombre": paciente.full_name if paciente else None, "paciente_dni": paciente.dni if paciente else None,
        "medico_solicitante_nombre": medico.nombre_completo if medico else None,
        "tipo_componente": s.tipo_componente, "cantidad_unidades": s.cantidad_unidades,
        "grupo_sanguineo_paciente": s.grupo_sanguineo_paciente, "factor_rh_paciente": s.factor_rh_paciente,
        "urgencia": s.urgencia, "motivo_clinico": s.motivo_clinico, "estado": s.estado,
        "origen": "CONSULTA_EXTERNA" if s.atencion_medica_id else "EMERGENCIA" if s.atencion_emergencia_id else "HOSPITALIZACION",
        "created_at": s.created_at,
        "asignaciones": [{
            "id": a.id, "componente_id": c.id, "componente_codigo": c.codigo, "componente_tipo": c.tipo,
            "grupo_sanguineo": c.grupo_sanguineo, "factor_rh": c.factor_rh,
            "resultado_prueba_cruzada": a.resultado_prueba_cruzada, "dispensado": a.dispensado,
        } for a, c in asignaciones],
    }


async def list_solicitudes(db: AsyncSession, tid: uuid.UUID, estado: str | None = None) -> list[dict]:
    query = select(SolicitudTransfusional).where(SolicitudTransfusional.tenant_id == tid)
    if estado:
        query = query.where(SolicitudTransfusional.estado == estado)
    solicitudes = (await db.scalars(query.order_by(SolicitudTransfusional.created_at.desc()))).all()
    return [await _solicitud_out(db, s) for s in solicitudes]


async def asignar_componente(db: AsyncSession, tid: uuid.UUID, user: dict, solicitud_id: uuid.UUID, data) -> dict:
    solicitud = await db.get(SolicitudTransfusional, solicitud_id)
    if solicitud is None or solicitud.tenant_id != tid:
        raise HTTPException(404, detail="Solicitud no encontrada")
    if solicitud.estado not in ("pendiente", "en_pruebas_cruzadas"):
        raise HTTPException(409, detail=f"La solicitud está en estado '{solicitud.estado}'")

    componente = await db.get(ComponenteSanguineo, data.componente_id)
    if componente is None or componente.tenant_id != tid:
        raise HTTPException(404, detail="Componente no encontrado")
    if componente.estado != "disponible":
        raise HTTPException(409, detail=f"El componente está en estado '{componente.estado}', no disponible")
    if componente.tipo != solicitud.tipo_componente:
        raise HTTPException(400, detail="El tipo de componente no coincide con lo solicitado")
    if not _compatible(componente.tipo, componente.grupo_sanguineo, componente.factor_rh,
                        solicitud.grupo_sanguineo_paciente, solicitud.factor_rh_paciente):
        raise HTTPException(400, detail="Componente ABO/Rh incompatible con el paciente")

    ya_asignado = await db.scalar(select(func.count()).where(SolicitudComponenteAsignado.componente_id == data.componente_id))
    if ya_asignado:
        raise HTTPException(409, detail="Ese componente ya está asignado a otra solicitud")

    asignacion = SolicitudComponenteAsignado(id=uuid.uuid4(), tenant_id=tid, solicitud_id=solicitud_id,
        componente_id=data.componente_id)
    db.add(asignacion)
    componente.estado = "reservado"
    db.add(MovimientoSangre(id=uuid.uuid4(), tenant_id=tid, componente_id=componente.id, tipo="reserva",
        solicitud_id=solicitud_id, registrado_por=actor(user)))
    solicitud.estado = "en_pruebas_cruzadas"
    await db.commit()
    return await _solicitud_out(db, solicitud)


async def registrar_prueba_cruzada(db: AsyncSession, tid: uuid.UUID, user: dict, asignacion_id: uuid.UUID, data) -> dict:
    asignacion = await db.get(SolicitudComponenteAsignado, asignacion_id)
    if asignacion is None or asignacion.tenant_id != tid:
        raise HTTPException(404, detail="Asignación no encontrada")
    if asignacion.resultado_prueba_cruzada != "pendiente":
        raise HTTPException(409, detail="Esta asignación ya tiene un resultado de prueba cruzada")

    componente = await db.get(ComponenteSanguineo, asignacion.componente_id)
    asignacion.resultado_prueba_cruzada = data.resultado
    asignacion.observaciones = data.observaciones
    asignacion.prueba_cruzada_por = actor(user)
    asignacion.prueba_cruzada_at = datetime.utcnow()

    solicitud = await db.get(SolicitudTransfusional, asignacion.solicitud_id)
    if data.resultado == "incompatible":
        componente.estado = "disponible"
        db.add(MovimientoSangre(id=uuid.uuid4(), tenant_id=tid, componente_id=componente.id, tipo="liberacion_reserva",
            solicitud_id=solicitud.id, observaciones="Prueba cruzada incompatible", registrado_por=actor(user)))
        solicitud.estado = "pendiente"
    else:
        # autoflush ya refleja el resultado recién asignado arriba en la consulta.
        todas = (await db.scalars(select(SolicitudComponenteAsignado).where(
            SolicitudComponenteAsignado.solicitud_id == solicitud.id))).all()
        compatibles = sum(1 for a in todas if a.resultado_prueba_cruzada == "compatible")
        pendientes_o_incompatibles = sum(1 for a in todas if a.resultado_prueba_cruzada != "compatible")
        if pendientes_o_incompatibles == 0 and compatibles >= solicitud.cantidad_unidades:
            solicitud.estado = "lista_para_dispensar"

    await db.commit()
    return await _solicitud_out(db, solicitud)


async def dispensar(db: AsyncSession, tid: uuid.UUID, user: dict, asignacion_id: uuid.UUID) -> dict:
    asignacion = await db.get(SolicitudComponenteAsignado, asignacion_id)
    if asignacion is None or asignacion.tenant_id != tid:
        raise HTTPException(404, detail="Asignación no encontrada")
    if asignacion.resultado_prueba_cruzada != "compatible":
        raise HTTPException(409, detail="Solo se dispensan componentes con prueba cruzada compatible")
    if asignacion.dispensado:
        raise HTTPException(409, detail="Este componente ya fue dispensado")

    componente = await db.get(ComponenteSanguineo, asignacion.componente_id)
    componente.estado = "transfundido"
    asignacion.dispensado = True
    asignacion.dispensado_por = actor(user)
    asignacion.dispensado_at = datetime.utcnow()
    solicitud = await db.get(SolicitudTransfusional, asignacion.solicitud_id)
    db.add(MovimientoSangre(id=uuid.uuid4(), tenant_id=tid, componente_id=componente.id, tipo="salida_transfusion",
        solicitud_id=solicitud.id, registrado_por=actor(user)))

    # autoflush ya refleja asignacion.dispensado = True en esta consulta.
    pendientes = await db.scalar(select(func.count()).where(
        SolicitudComponenteAsignado.solicitud_id == solicitud.id, SolicitudComponenteAsignado.dispensado.is_(False)))
    if pendientes == 0:
        solicitud.estado = "dispensada"

    await db.commit()
    return await _solicitud_out(db, solicitud)


async def anular_solicitud(db: AsyncSession, tid: uuid.UUID, user: dict, solicitud_id: uuid.UUID, data) -> dict:
    solicitud = await db.get(SolicitudTransfusional, solicitud_id)
    if solicitud is None or solicitud.tenant_id != tid:
        raise HTTPException(404, detail="Solicitud no encontrada")
    if solicitud.estado == "dispensada":
        raise HTTPException(409, detail="No se puede anular una solicitud ya dispensada")

    asignaciones = (await db.scalars(select(SolicitudComponenteAsignado).where(
        SolicitudComponenteAsignado.solicitud_id == solicitud_id, SolicitudComponenteAsignado.dispensado.is_(False)))).all()
    for a in asignaciones:
        componente = await db.get(ComponenteSanguineo, a.componente_id)
        if componente.estado == "reservado":
            componente.estado = "disponible"
            db.add(MovimientoSangre(id=uuid.uuid4(), tenant_id=tid, componente_id=componente.id, tipo="liberacion_reserva",
                solicitud_id=solicitud.id, observaciones="Solicitud anulada", registrado_por=actor(user)))

    solicitud.estado = "anulada"
    await db.commit()
    return await _solicitud_out(db, solicitud)
