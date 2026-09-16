import uuid
from datetime import date
from fastapi import HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.hospital.medicina_fisica.models import (
    ProgramaMedicinaFisica, TecnologoPrograma, ProgramacionMF, SesionMF,
)
from app.hospital.consulta_externa.service import _generar_slots
from app.hospital.admision.models import Patient
from app.sigarh.rrhh.models import Empleado


def actor(user):
    return f"{(user.get('name') or 'Usuario')[:210]} ({user['sub']})"


# ─── Programas ───────────────────────────────────────────────────────────

async def crear_programa(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> ProgramaMedicinaFisica:
    existente = await db.scalar(select(ProgramaMedicinaFisica).where(
        ProgramaMedicinaFisica.tenant_id == tid, ProgramaMedicinaFisica.nombre == data.nombre))
    if existente:
        raise HTTPException(409, detail="Ya existe un programa con ese nombre")
    programa = ProgramaMedicinaFisica(id=uuid.uuid4(), tenant_id=tid, **data.model_dump())
    db.add(programa)
    await db.flush()
    await db.commit()
    return programa


async def list_programas(db: AsyncSession, tid: uuid.UUID, solo_activos: bool = False) -> list[dict]:
    query = select(ProgramaMedicinaFisica).where(ProgramaMedicinaFisica.tenant_id == tid)
    if solo_activos:
        query = query.where(ProgramaMedicinaFisica.is_active.is_(True))
    programas = (await db.scalars(query.order_by(ProgramaMedicinaFisica.nombre))).all()
    resultado = []
    for p in programas:
        tecnologos = (await db.execute(select(Empleado).join(
            TecnologoPrograma, TecnologoPrograma.empleado_id == Empleado.id).where(
            TecnologoPrograma.programa_id == p.id, TecnologoPrograma.is_active.is_(True))))
        resultado.append({
            "id": p.id, "nombre": p.nombre, "descripcion": p.descripcion,
            "duracion_sesion_minutos": p.duracion_sesion_minutos, "is_active": p.is_active,
            "tecnologos": [{"id": e.id, "nombre": e.nombre_completo} for e in tecnologos.scalars().all()],
        })
    return resultado


async def update_programa(db: AsyncSession, tid: uuid.UUID, user: dict, programa_id: uuid.UUID, data) -> ProgramaMedicinaFisica:
    programa = await db.get(ProgramaMedicinaFisica, programa_id)
    if programa is None or programa.tenant_id != tid:
        raise HTTPException(404, detail="Programa no encontrado")
    cambios = data.model_dump(exclude_unset=True)
    for k, v in cambios.items():
        setattr(programa, k, v)
    await db.commit()
    return programa


async def asignar_tecnologo(db: AsyncSession, tid: uuid.UUID, user: dict, programa_id: uuid.UUID, data) -> dict:
    programa = await db.get(ProgramaMedicinaFisica, programa_id)
    if programa is None or programa.tenant_id != tid:
        raise HTTPException(404, detail="Programa no encontrado")
    empleado = await db.get(Empleado, data.empleado_id)
    if empleado is None or empleado.tenant_id != tid:
        raise HTTPException(404, detail="Empleado no encontrado")
    existente = await db.scalar(select(TecnologoPrograma).where(
        TecnologoPrograma.programa_id == programa_id, TecnologoPrograma.empleado_id == data.empleado_id))
    if existente:
        if existente.is_active:
            raise HTTPException(409, detail="Este tecnólogo ya está asignado a este programa")
        existente.is_active = True
    else:
        db.add(TecnologoPrograma(id=uuid.uuid4(), tenant_id=tid, programa_id=programa_id, empleado_id=data.empleado_id))
    await db.commit()
    return {"programa_id": programa_id, "empleado_id": data.empleado_id, "empleado_nombre": empleado.nombre_completo}


async def desasignar_tecnologo(db: AsyncSession, tid: uuid.UUID, user: dict, programa_id: uuid.UUID, empleado_id: uuid.UUID):
    asignacion = await db.scalar(select(TecnologoPrograma).where(
        TecnologoPrograma.tenant_id == tid, TecnologoPrograma.programa_id == programa_id,
        TecnologoPrograma.empleado_id == empleado_id))
    if asignacion is None or not asignacion.is_active:
        raise HTTPException(404, detail="Asignación no encontrada")
    asignacion.is_active = False
    await db.commit()
    return {"ok": True}


# ─── Programaciones (bloques de horario por tecnólogo) ──────────────────────

def _programacion_out(p: ProgramacionMF, programa: ProgramaMedicinaFisica | None, tecnologo: Empleado | None,
                       cupos_totales: int = 0, cupos_usados: int = 0) -> dict:
    return {
        "id": p.id, "programa_id": p.programa_id, "programa_nombre": programa.nombre if programa else None,
        "tecnologo_id": p.tecnologo_id, "tecnologo_nombre": tecnologo.nombre_completo if tecnologo else None,
        "fecha": p.fecha, "turno": p.turno, "hora_inicio": p.hora_inicio, "hora_fin": p.hora_fin,
        "tiempo_sesion_minutos": p.tiempo_sesion_minutos, "estado": p.estado, "motivo_bloqueo": p.motivo_bloqueo,
        "cupos_totales": cupos_totales, "cupos_usados": cupos_usados, "cupos_disponibles": max(cupos_totales - cupos_usados, 0),
    }


async def crear_programacion(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    programa = await db.get(ProgramaMedicinaFisica, data.programa_id)
    if programa is None or programa.tenant_id != tid:
        raise HTTPException(404, detail="Programa no encontrado")
    tecnologo = await db.get(Empleado, data.tecnologo_id)
    if tecnologo is None or tecnologo.tenant_id != tid:
        raise HTTPException(404, detail="Tecnólogo no encontrado")
    habilitado = await db.scalar(select(func.count()).where(
        TecnologoPrograma.programa_id == data.programa_id, TecnologoPrograma.empleado_id == data.tecnologo_id,
        TecnologoPrograma.is_active.is_(True)))
    if not habilitado:
        raise HTTPException(400, detail="El tecnólogo no está habilitado para este programa")

    prog = ProgramacionMF(id=uuid.uuid4(), tenant_id=tid, programa_id=data.programa_id, tecnologo_id=data.tecnologo_id,
        fecha=data.fecha, turno=data.turno, hora_inicio=data.hora_inicio, hora_fin=data.hora_fin,
        tiempo_sesion_minutos=data.tiempo_sesion_minutos or programa.duracion_sesion_minutos, registrado_por=actor(user))
    db.add(prog)
    await db.flush()
    await db.commit()
    return _programacion_out(prog, programa, tecnologo, len(_generar_slots(prog.hora_inicio, prog.hora_fin, prog.tiempo_sesion_minutos)), 0)


async def list_programaciones(db: AsyncSession, tid: uuid.UUID, fecha: date | None = None,
                               tecnologo_id: uuid.UUID | None = None, programa_id: uuid.UUID | None = None,
                               estado: str | None = None) -> list[dict]:
    query = select(ProgramacionMF).where(ProgramacionMF.tenant_id == tid)
    if fecha:
        query = query.where(ProgramacionMF.fecha == fecha)
    if tecnologo_id:
        query = query.where(ProgramacionMF.tecnologo_id == tecnologo_id)
    if programa_id:
        query = query.where(ProgramacionMF.programa_id == programa_id)
    if estado:
        query = query.where(ProgramacionMF.estado == estado)
    programaciones = (await db.scalars(query.order_by(ProgramacionMF.fecha, ProgramacionMF.hora_inicio))).all()
    if not programaciones:
        return []

    prog_ids = [p.id for p in programaciones]
    usados = dict((await db.execute(select(SesionMF.programacion_mf_id, func.count()).where(
        SesionMF.programacion_mf_id.in_(prog_ids), SesionMF.estado != "cancelada").group_by(
        SesionMF.programacion_mf_id))).all())
    programas = {p.id: p for p in (await db.scalars(select(ProgramaMedicinaFisica).where(
        ProgramaMedicinaFisica.id.in_({p.programa_id for p in programaciones}))))}
    tecnologos = {e.id: e for e in (await db.scalars(select(Empleado).where(
        Empleado.id.in_({p.tecnologo_id for p in programaciones}))))}

    resultado = []
    for p in programaciones:
        total = len(_generar_slots(p.hora_inicio, p.hora_fin, p.tiempo_sesion_minutos))
        resultado.append(_programacion_out(p, programas.get(p.programa_id), tecnologos.get(p.tecnologo_id),
            total, usados.get(p.id, 0)))
    return resultado


async def bloquear_programacion(db: AsyncSession, tid: uuid.UUID, user: dict, programacion_id: uuid.UUID, data) -> dict:
    prog = await db.get(ProgramacionMF, programacion_id)
    if prog is None or prog.tenant_id != tid:
        raise HTTPException(404, detail="Programación no encontrada")
    if prog.estado != "activo":
        raise HTTPException(409, detail=f"La programación ya está en estado '{prog.estado}'")
    prog.estado = "bloqueado"
    prog.motivo_bloqueo = data.motivo
    await db.commit()
    programa = await db.get(ProgramaMedicinaFisica, prog.programa_id)
    tecnologo = await db.get(Empleado, prog.tecnologo_id)
    return _programacion_out(prog, programa, tecnologo)


async def desbloquear_programacion(db: AsyncSession, tid: uuid.UUID, user: dict, programacion_id: uuid.UUID) -> dict:
    prog = await db.get(ProgramacionMF, programacion_id)
    if prog is None or prog.tenant_id != tid:
        raise HTTPException(404, detail="Programación no encontrada")
    if prog.estado != "bloqueado":
        raise HTTPException(409, detail="La programación no está bloqueada")
    prog.estado = "activo"
    prog.motivo_bloqueo = None
    await db.commit()
    programa = await db.get(ProgramaMedicinaFisica, prog.programa_id)
    tecnologo = await db.get(Empleado, prog.tecnologo_id)
    return _programacion_out(prog, programa, tecnologo)


# ─── Sesiones ────────────────────────────────────────────────────────────

async def _sesion_out(db: AsyncSession, s: SesionMF) -> dict:
    paciente = await db.get(Patient, s.patient_id)
    return {
        "id": s.id, "programacion_mf_id": s.programacion_mf_id, "patient_id": s.patient_id,
        "paciente_nombre": paciente.full_name if paciente else None, "paciente_dni": paciente.dni if paciente else None,
        "hora_inicio": s.hora_inicio, "hora_fin": s.hora_fin, "estado": s.estado,
        "escala_dolor_eva": s.escala_dolor_eva, "actividades_realizadas": s.actividades_realizadas,
        "evolucion": s.evolucion, "created_at": s.created_at,
    }


async def crear_sesion(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> dict:
    prog = await db.get(ProgramacionMF, data.programacion_mf_id)
    if prog is None or prog.tenant_id != tid:
        raise HTTPException(404, detail="Programación no encontrada")
    if prog.estado != "activo":
        raise HTTPException(409, detail=f"La programación está en estado '{prog.estado}', no se pueden agendar sesiones")
    paciente = await db.get(Patient, data.patient_id)
    if paciente is None or paciente.tenant_id != tid:
        raise HTTPException(404, detail="Paciente no encontrado")

    slots = {ini for ini, _ in _generar_slots(prog.hora_inicio, prog.hora_fin, prog.tiempo_sesion_minutos)}
    if data.hora_inicio not in slots:
        raise HTTPException(400, detail="La hora indicada no corresponde a un cupo válido de esta programación")
    ocupado = await db.scalar(select(func.count()).where(SesionMF.programacion_mf_id == data.programacion_mf_id,
        SesionMF.hora_inicio == data.hora_inicio, SesionMF.estado != "cancelada"))
    if ocupado:
        raise HTTPException(409, detail="Ese cupo ya está ocupado")

    sesion = SesionMF(id=uuid.uuid4(), tenant_id=tid, programacion_mf_id=data.programacion_mf_id,
        patient_id=data.patient_id, hora_inicio=data.hora_inicio, hora_fin=data.hora_fin, registrado_por=actor(user))
    db.add(sesion)
    await db.flush()
    await db.commit()
    return await _sesion_out(db, sesion)


async def list_sesiones(db: AsyncSession, tid: uuid.UUID, programacion_mf_id: uuid.UUID | None = None,
                         fecha: date | None = None, estado: str | None = None) -> list[dict]:
    query = select(SesionMF).where(SesionMF.tenant_id == tid)
    if programacion_mf_id:
        query = query.where(SesionMF.programacion_mf_id == programacion_mf_id)
    if fecha:
        query = query.join(ProgramacionMF, SesionMF.programacion_mf_id == ProgramacionMF.id).where(ProgramacionMF.fecha == fecha)
    if estado:
        query = query.where(SesionMF.estado == estado)
    sesiones = (await db.scalars(query.order_by(SesionMF.hora_inicio))).all()
    return [await _sesion_out(db, s) for s in sesiones]


async def ejecutar_sesion(db: AsyncSession, tid: uuid.UUID, user: dict, sesion_id: uuid.UUID, data) -> dict:
    sesion = await db.get(SesionMF, sesion_id)
    if sesion is None or sesion.tenant_id != tid:
        raise HTTPException(404, detail="Sesión no encontrada")
    if sesion.estado != "programada":
        raise HTTPException(409, detail=f"La sesión ya está en estado '{sesion.estado}'")

    sesion.estado = data.estado
    sesion.escala_dolor_eva = data.escala_dolor_eva
    sesion.actividades_realizadas = data.actividades_realizadas
    sesion.evolucion = data.evolucion
    await db.commit()
    return await _sesion_out(db, sesion)


async def reprogramar_bloque(db: AsyncSession, tid: uuid.UUID, user: dict, data) -> list[dict]:
    destino = await db.get(ProgramacionMF, data.programacion_mf_id)
    if destino is None or destino.tenant_id != tid:
        raise HTTPException(404, detail="Programación destino no encontrada")
    if destino.estado != "activo":
        raise HTTPException(409, detail="La programación destino no está activa")

    slots_destino = [ini for ini, _ in _generar_slots(destino.hora_inicio, destino.hora_fin, destino.tiempo_sesion_minutos)]
    ocupados = {r for r in (await db.scalars(select(SesionMF.hora_inicio).where(
        SesionMF.programacion_mf_id == destino.id, SesionMF.estado != "cancelada")))}
    libres = [s for s in slots_destino if s not in ocupados]

    if len(data.sesion_ids) > len(libres):
        raise HTTPException(409, detail="La programación destino no tiene cupos suficientes para reprogramar todas las sesiones")

    sesiones = (await db.scalars(select(SesionMF).where(
        SesionMF.id.in_(data.sesion_ids), SesionMF.tenant_id == tid))).all()
    if len(sesiones) != len(data.sesion_ids):
        raise HTTPException(404, detail="Alguna de las sesiones indicadas no existe")

    resultado = []
    for i, sesion in enumerate(sesiones):
        if sesion.estado != "programada":
            raise HTTPException(409, detail=f"La sesión {sesion.id} no está en estado 'programada'")
        {"programacion_mf_id": str(sesion.programacion_mf_id), "hora_inicio": sesion.hora_inicio}
        sesion.programacion_mf_id = destino.id
        sesion.hora_inicio = libres[i]
        duracion = destino.tiempo_sesion_minutos
        h, m = map(int, libres[i].split(":"))
        total = h * 60 + m + duracion
        sesion.hora_fin = f"{(total // 60) % 24:02d}:{total % 60:02d}"
        if data.mensaje:
            sesion.evolucion = ((sesion.evolucion or "") + f"\n[Reprogramado] {data.mensaje}").strip()
        resultado.append(sesion)
    await db.commit()
    return [await _sesion_out(db, s) for s in resultado]


# ─── Catálogo de empleados (candidatos a tecnólogo) ─────────────────────────

async def list_empleados(db: AsyncSession, tid: uuid.UUID, q: str = "") -> list[dict]:
    query = select(Empleado).where(Empleado.tenant_id == tid, Empleado.is_active.is_(True))
    if q:
        for term in q.split():
            query = query.where(or_(Empleado.nombres.icontains(term, autoescape=True),
                Empleado.apellido_paterno.icontains(term, autoescape=True),
                Empleado.apellido_materno.icontains(term, autoescape=True)))
    empleados = (await db.scalars(query.order_by(Empleado.apellido_paterno).limit(100))).all()
    return [{"id": e.id, "nombre": e.nombre_completo} for e in empleados]


# ─── Tablero de control ──────────────────────────────────────────────────

async def tablero_control(db: AsyncSession, tid: uuid.UUID, fecha: date) -> dict:
    programaciones = await list_programaciones(db, tid, fecha=fecha)
    por_estado_sesion = dict((await db.execute(select(SesionMF.estado, func.count()).join(
        ProgramacionMF, SesionMF.programacion_mf_id == ProgramacionMF.id).where(
        ProgramacionMF.tenant_id == tid, ProgramacionMF.fecha == fecha).group_by(SesionMF.estado))).all())
    return {
        "fecha": fecha,
        "programaciones": programaciones,
        "total_cupos": sum(p["cupos_totales"] for p in programaciones),
        "total_usados": sum(p["cupos_usados"] for p in programaciones),
        "por_estado_sesion": por_estado_sesion,
    }
