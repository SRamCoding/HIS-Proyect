import uuid
from datetime import date

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.sigarh.rrhh.models import (
    Empleado, Especialidad, EmpleadoEspecialidad,
    DiasFeriado, MotivoJustificacion, Tolerancia,
    RegistroAsistencia, Justificacion,
)
from app.sigarh.mantenimiento.models import (
    TipoTrabajador, GrupoOcupacional, Dependencia, HorarioGuardia,
)


class ReglaNegocioError(Exception):
    """Operación bloqueada por regla de negocio -> HTTP 409."""


def _cols(obj) -> dict:
    return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}


def _min(hhmm: str | None) -> int | None:
    if not hhmm or ":" not in hhmm:
        return None
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _hhmm(mins: int) -> str:
    mins = max(0, mins)
    return f"{mins // 60:02d}:{mins % 60:02d}"


# ─── Empleados ────────────────────────────────────────────────────────────────

_EMP_OPTS = (selectinload(Empleado.especialidades).selectinload(EmpleadoEspecialidad.especialidad),)


async def listar_empleados(db: AsyncSession, tenant_id: uuid.UUID) -> list[Empleado]:
    result = await db.execute(
        select(Empleado).where(Empleado.tenant_id == tenant_id).order_by(Empleado.apellido_paterno)
    )
    return result.scalars().all()


async def obtener_empleado(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Empleado | None:
    result = await db.execute(
        select(Empleado).options(*_EMP_OPTS).where(Empleado.id == id, Empleado.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def obtener_empleado_por_dni(db: AsyncSession, dni: str, tenant_id: uuid.UUID) -> Empleado | None:
    result = await db.execute(
        select(Empleado).options(*_EMP_OPTS).where(Empleado.dni == dni, Empleado.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def _correo_duplicado(db: AsyncSession, tenant_id: uuid.UUID, correo: str, excluir: uuid.UUID | None = None) -> bool:
    q = select(func.count()).select_from(Empleado).where(
        Empleado.tenant_id == tenant_id, func.lower(Empleado.correo) == correo.lower()
    )
    if excluir:
        q = q.where(Empleado.id != excluir)
    return bool(await db.scalar(q))


async def crear_empleado(db: AsyncSession, tenant_id: uuid.UUID, data) -> Empleado:
    if data.correo and await _correo_duplicado(db, tenant_id, data.correo):
        raise ReglaNegocioError(f"Ya existe un empleado con el correo {data.correo}.")
    empleado = Empleado(tenant_id=tenant_id, **data.model_dump())
    db.add(empleado)
    await db.commit()
    return await obtener_empleado(db, empleado.id, tenant_id)


async def actualizar_empleado(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Empleado | None:
    empleado = await obtener_empleado(db, id, tenant_id)
    if not empleado:
        return None
    cambios = data.model_dump(exclude_unset=True)
    if cambios.get("correo") and await _correo_duplicado(db, tenant_id, cambios["correo"], excluir=id):
        raise ReglaNegocioError(f"Ya existe un empleado con el correo {cambios['correo']}.")
    for f, v in cambios.items():
        setattr(empleado, f, v)
    await db.commit()
    return await obtener_empleado(db, id, tenant_id)


async def eliminar_empleado(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    empleado = await obtener_empleado(db, id, tenant_id)
    if not empleado:
        return False
    await db.delete(empleado)
    await db.commit()
    return True


# ─── Especialidades del empleado ──────────────────────────────────────────────

async def agregar_especialidad(db: AsyncSession, empleado_id: uuid.UUID, data) -> EmpleadoEspecialidad:
    esp = EmpleadoEspecialidad(empleado_id=empleado_id, **data.model_dump())
    db.add(esp)
    await db.commit()
    res = await db.execute(
        select(EmpleadoEspecialidad)
        .options(selectinload(EmpleadoEspecialidad.especialidad))
        .where(EmpleadoEspecialidad.id == esp.id)
    )
    return res.scalar_one()


async def eliminar_especialidad(db: AsyncSession, id: uuid.UUID) -> bool:
    esp = await db.scalar(select(EmpleadoEspecialidad).where(EmpleadoEspecialidad.id == id))
    if not esp:
        return False
    await db.delete(esp)
    await db.commit()
    return True


# ─── Catálogo de Especialidades ───────────────────────────────────────────────

async def _serializar_especialidades(db: AsyncSession, tenant_id: uuid.UUID, items: list[Especialidad]) -> list[dict]:
    if not items:
        return []
    conteos = dict((await db.execute(
        select(EmpleadoEspecialidad.especialidad_id, func.count(func.distinct(EmpleadoEspecialidad.empleado_id)))
        .join(Empleado, Empleado.id == EmpleadoEspecialidad.empleado_id)
        .where(Empleado.tenant_id == tenant_id)
        .group_by(EmpleadoEspecialidad.especialidad_id)
    )).all())
    return [{**_cols(e), "medicos_asignados": conteos.get(e.id, 0)} for e in items]


async def listar_especialidades(db: AsyncSession, tenant_id: uuid.UUID) -> list[dict]:
    items = (await db.execute(
        select(Especialidad).where(Especialidad.tenant_id == tenant_id).order_by(Especialidad.nombre)
    )).scalars().all()
    return await _serializar_especialidades(db, tenant_id, items)


async def _esp_orm(db, id, tenant_id):
    return await db.scalar(select(Especialidad).where(Especialidad.id == id, Especialidad.tenant_id == tenant_id))


async def crear_especialidad(db: AsyncSession, tenant_id: uuid.UUID, data) -> dict:
    esp = Especialidad(tenant_id=tenant_id, **data.model_dump())
    db.add(esp)
    await db.commit()
    await db.refresh(esp)
    return {**_cols(esp), "medicos_asignados": 0}


async def actualizar_especialidad(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> dict | None:
    esp = await _esp_orm(db, id, tenant_id)
    if not esp:
        return None
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(esp, f, v)
    await db.commit()
    return (await _serializar_especialidades(db, tenant_id, [await _esp_orm(db, id, tenant_id)]))[0]


async def eliminar_especialidad_catalogo(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    esp = await _esp_orm(db, id, tenant_id)
    if not esp:
        return False
    usada = await db.scalar(select(func.count()).select_from(EmpleadoEspecialidad).where(EmpleadoEspecialidad.especialidad_id == id))
    if usada:
        raise ReglaNegocioError(f"No se puede eliminar: la especialidad está asignada a {usada} empleado(s).")
    await db.delete(esp)
    await db.commit()
    return True


# ─── Días Feriados ────────────────────────────────────────────────────────────

async def listar_feriados(db: AsyncSession, tenant_id: uuid.UUID, anio: int | None = None, mes: int | None = None) -> list[DiasFeriado]:
    q = select(DiasFeriado).where(DiasFeriado.tenant_id == tenant_id)
    if anio:
        q = q.where(func.extract("year", DiasFeriado.fecha) == anio)
    if mes:
        q = q.where(func.extract("month", DiasFeriado.fecha) == mes)
    return (await db.execute(q.order_by(DiasFeriado.fecha))).scalars().all()


async def crear_feriado(db: AsyncSession, tenant_id: uuid.UUID, data) -> DiasFeriado:
    fer = DiasFeriado(tenant_id=tenant_id, **data.model_dump())
    db.add(fer)
    await db.commit()
    await db.refresh(fer)
    return fer


async def actualizar_feriado(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> DiasFeriado | None:
    fer = await db.scalar(select(DiasFeriado).where(DiasFeriado.id == id, DiasFeriado.tenant_id == tenant_id))
    if not fer:
        return None
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(fer, f, v)
    await db.commit()
    await db.refresh(fer)
    return fer


async def eliminar_feriado(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    fer = await db.scalar(select(DiasFeriado).where(DiasFeriado.id == id, DiasFeriado.tenant_id == tenant_id))
    if not fer:
        return False
    await db.delete(fer)
    await db.commit()
    return True


# ─── Motivos Justificación ────────────────────────────────────────────────────

async def _serializar_motivos(db: AsyncSession, tenant_id: uuid.UUID, items: list[MotivoJustificacion]) -> list[dict]:
    if not items:
        return []
    usos = dict((await db.execute(
        select(Justificacion.motivo_id, func.count())
        .where(Justificacion.tenant_id == tenant_id)
        .group_by(Justificacion.motivo_id)
    )).all())
    return [{**_cols(m), "usos": usos.get(m.id, 0)} for m in items]


async def listar_motivos(db: AsyncSession, tenant_id: uuid.UUID) -> list[dict]:
    items = (await db.execute(
        select(MotivoJustificacion).where(MotivoJustificacion.tenant_id == tenant_id).order_by(MotivoJustificacion.nombre)
    )).scalars().all()
    return await _serializar_motivos(db, tenant_id, items)


async def _mot_orm(db, id, tenant_id):
    return await db.scalar(select(MotivoJustificacion).where(MotivoJustificacion.id == id, MotivoJustificacion.tenant_id == tenant_id))


async def crear_motivo(db: AsyncSession, tenant_id: uuid.UUID, data) -> dict:
    mot = MotivoJustificacion(tenant_id=tenant_id, **data.model_dump())
    db.add(mot)
    await db.commit()
    await db.refresh(mot)
    return {**_cols(mot), "usos": 0}


async def actualizar_motivo(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> dict | None:
    mot = await _mot_orm(db, id, tenant_id)
    if not mot:
        return None
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(mot, f, v)
    await db.commit()
    return (await _serializar_motivos(db, tenant_id, [await _mot_orm(db, id, tenant_id)]))[0]


async def eliminar_motivo(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    mot = await _mot_orm(db, id, tenant_id)
    if not mot:
        return False
    usado = await db.scalar(select(func.count()).select_from(Justificacion).where(Justificacion.motivo_id == id))
    if usado:
        raise ReglaNegocioError(f"No se puede eliminar: el motivo se usa en {usado} justificación(es).")
    await db.delete(mot)
    await db.commit()
    return True


# ─── Tolerancias ──────────────────────────────────────────────────────────────

async def _serializar_tolerancias(db: AsyncSession, tenant_id: uuid.UUID, items: list[Tolerancia]) -> list[dict]:
    if not items:
        return []
    deps = dict((await db.execute(
        select(Dependencia.id, Dependencia.nombre).where(Dependencia.tenant_id == tenant_id)
    )).all())
    grupos = dict((await db.execute(
        select(GrupoOcupacional.id, GrupoOcupacional.nombre).where(GrupoOcupacional.tenant_id == tenant_id)
    )).all())
    return [
        {
            **_cols(t),
            "dependencia_nombre": deps.get(t.dependencia_id),
            "grupo_ocupacional_nombre": grupos.get(t.grupo_ocupacional_id),
        }
        for t in items
    ]


async def listar_tolerancias(db: AsyncSession, tenant_id: uuid.UUID) -> list[dict]:
    items = (await db.execute(
        select(Tolerancia).where(Tolerancia.tenant_id == tenant_id).order_by(Tolerancia.created_at.desc())
    )).scalars().all()
    return await _serializar_tolerancias(db, tenant_id, items)


async def _tol_orm(db, id, tenant_id):
    return await db.scalar(select(Tolerancia).where(Tolerancia.id == id, Tolerancia.tenant_id == tenant_id))


async def crear_tolerancia(db: AsyncSession, tenant_id: uuid.UUID, data) -> dict:
    tol = Tolerancia(tenant_id=tenant_id, **data.model_dump())
    db.add(tol)
    await db.commit()
    return (await _serializar_tolerancias(db, tenant_id, [await _tol_orm(db, tol.id, tenant_id)]))[0]


async def actualizar_tolerancia(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> dict | None:
    tol = await _tol_orm(db, id, tenant_id)
    if not tol:
        return None
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(tol, f, v)
    await db.commit()
    return (await _serializar_tolerancias(db, tenant_id, [await _tol_orm(db, id, tenant_id)]))[0]


async def eliminar_tolerancia(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    tol = await _tol_orm(db, id, tenant_id)
    if not tol:
        return False
    await db.delete(tol)
    await db.commit()
    return True


# ─── Registro Asistencia ──────────────────────────────────────────────────────

async def _tolerancia_grupo(db: AsyncSession, tenant_id: uuid.UUID, grupo_id: uuid.UUID | None) -> int:
    """Minutos de tolerancia por marcación para el grupo ocupacional (0 si no hay)."""
    if not grupo_id:
        return 0
    val = await db.scalar(
        select(Tolerancia.minutos_tolerancia)
        .where(
            Tolerancia.tenant_id == tenant_id,
            Tolerancia.grupo_ocupacional_id == grupo_id,
            Tolerancia.is_active.is_(True),
        )
        .order_by(Tolerancia.created_at.desc())
        .limit(1)
    )
    return int(val or 0)


async def _calcular_tardanza(db: AsyncSession, tenant_id: uuid.UUID, grupo_id, programada: str | None, real: str | None) -> int:
    p, r = _min(programada), _min(real)
    if p is None or r is None or r <= p:
        return 0
    tol = await _tolerancia_grupo(db, tenant_id, grupo_id)
    return max(0, (r - p) - tol)


def _horas_trabajadas(entrada: str | None, salida: str | None) -> str | None:
    e, s = _min(entrada), _min(salida)
    if e is None or s is None:
        return None
    diff = s - e
    if diff < 0:
        diff += 24 * 60
    return _hhmm(diff)


async def _serializar_asistencia(db: AsyncSession, tenant_id: uuid.UUID, items: list[RegistroAsistencia]) -> list[dict]:
    if not items:
        return []
    emps = {
        e.id: e for e in (await db.execute(
            select(Empleado).where(Empleado.tenant_id == tenant_id)
        )).scalars().all()
    }
    grupos = dict((await db.execute(
        select(GrupoOcupacional.id, GrupoOcupacional.nombre).where(GrupoOcupacional.tenant_id == tenant_id)
    )).all())
    horarios = dict((await db.execute(
        select(HorarioGuardia.id, HorarioGuardia.nombre).where(HorarioGuardia.tenant_id == tenant_id)
    )).all())
    out = []
    for a in items:
        emp = emps.get(a.empleado_id)
        out.append({
            **_cols(a),
            "empleado_nombre": emp.nombre_completo if emp else None,
            "grupo_ocupacional_nombre": grupos.get(a.grupo_ocupacional_id),
            "horario_guardia_nombre": horarios.get(a.horario_guardia_id),
            "horas_trabajadas": _horas_trabajadas(a.hora_entrada_real, a.hora_salida_real),
        })
    return out


async def listar_asistencia(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    fecha: date | None = None,
    empleado_id: uuid.UUID | None = None,
    grupo_ocupacional_id: uuid.UUID | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    solo_tardanza: bool = False,
) -> list[dict]:
    q = select(RegistroAsistencia).where(RegistroAsistencia.tenant_id == tenant_id)
    if fecha:
        q = q.where(RegistroAsistencia.fecha == fecha)
    if empleado_id:
        q = q.where(RegistroAsistencia.empleado_id == empleado_id)
    if grupo_ocupacional_id:
        q = q.where(RegistroAsistencia.grupo_ocupacional_id == grupo_ocupacional_id)
    if desde:
        q = q.where(RegistroAsistencia.fecha >= desde)
    if hasta:
        q = q.where(RegistroAsistencia.fecha <= hasta)
    if solo_tardanza:
        q = q.where(RegistroAsistencia.minutos_tardanza > 0)
    items = (await db.execute(q.order_by(RegistroAsistencia.fecha.desc()))).scalars().all()
    return await _serializar_asistencia(db, tenant_id, items)


async def _asis_orm(db, id, tenant_id):
    return await db.scalar(select(RegistroAsistencia).where(RegistroAsistencia.id == id, RegistroAsistencia.tenant_id == tenant_id))


async def crear_asistencia(db: AsyncSession, tenant_id: uuid.UUID, data, usuario: str | None = None) -> dict:
    payload = data.model_dump()
    tardanza = await _calcular_tardanza(
        db, tenant_id, payload.get("grupo_ocupacional_id"),
        payload.get("hora_entrada_programada"), payload.get("hora_entrada_real"),
    )
    asis = RegistroAsistencia(tenant_id=tenant_id, minutos_tardanza=tardanza, registrado_por=usuario, **payload)
    if tardanza > 0 and asis.estado == "presente":
        asis.estado = "tardanza"
    db.add(asis)
    await db.commit()
    return (await _serializar_asistencia(db, tenant_id, [await _asis_orm(db, asis.id, tenant_id)]))[0]


async def actualizar_asistencia(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> dict | None:
    asis = await _asis_orm(db, id, tenant_id)
    if not asis:
        return None
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(asis, f, v)
    asis.minutos_tardanza = await _calcular_tardanza(
        db, tenant_id, asis.grupo_ocupacional_id, asis.hora_entrada_programada, asis.hora_entrada_real,
    )
    await db.commit()
    return (await _serializar_asistencia(db, tenant_id, [await _asis_orm(db, id, tenant_id)]))[0]


async def eliminar_asistencia(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    asis = await _asis_orm(db, id, tenant_id)
    if not asis:
        return False
    await db.delete(asis)
    await db.commit()
    return True


# ─── Justificaciones ──────────────────────────────────────────────────────────

async def _serializar_justificaciones(db: AsyncSession, tenant_id: uuid.UUID, items: list[Justificacion]) -> list[dict]:
    if not items:
        return []
    emps = {
        e.id: e for e in (await db.execute(select(Empleado).where(Empleado.tenant_id == tenant_id))).scalars().all()
    }
    motivos = dict((await db.execute(
        select(MotivoJustificacion.id, MotivoJustificacion.nombre).where(MotivoJustificacion.tenant_id == tenant_id)
    )).all())
    tipos = dict((await db.execute(
        select(TipoTrabajador.id, TipoTrabajador.nombre).where(TipoTrabajador.tenant_id == tenant_id)
    )).all())
    out = []
    for j in items:
        emp = emps.get(j.empleado_id)
        dias = (j.fecha_fin - j.fecha_inicio).days + 1 if j.fecha_inicio and j.fecha_fin else 0
        out.append({
            **_cols(j),
            "empleado_nombre": emp.nombre_completo if emp else None,
            "empleado_dni": emp.dni if emp else None,
            "empleado_regimen": tipos.get(emp.tipo_trabajador_id) if emp else None,
            "empleado_cargo": emp.cargo_laboral if emp else None,
            "motivo_nombre": motivos.get(j.motivo_id),
            "dias": max(dias, 0),
        })
    return out


async def listar_justificaciones(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    empleado_id: uuid.UUID | None = None,
    estado: str | None = None,
    motivo_id: uuid.UUID | None = None,
    desde: date | None = None,
    hasta: date | None = None,
) -> list[dict]:
    q = select(Justificacion).where(Justificacion.tenant_id == tenant_id)
    if empleado_id:
        q = q.where(Justificacion.empleado_id == empleado_id)
    if estado:
        q = q.where(Justificacion.estado == estado)
    if motivo_id:
        q = q.where(Justificacion.motivo_id == motivo_id)
    if desde:
        q = q.where(Justificacion.fecha_fin >= desde)
    if hasta:
        q = q.where(Justificacion.fecha_inicio <= hasta)
    items = (await db.execute(q.order_by(Justificacion.fecha_inicio.desc()))).scalars().all()
    return await _serializar_justificaciones(db, tenant_id, items)


async def _just_orm(db, id, tenant_id):
    return await db.scalar(select(Justificacion).where(Justificacion.id == id, Justificacion.tenant_id == tenant_id))


async def crear_justificacion(db: AsyncSession, tenant_id: uuid.UUID, data) -> dict:
    payload = data.model_dump()
    if not payload.get("fecha_tramite"):
        payload["fecha_tramite"] = date.today()
    j = Justificacion(tenant_id=tenant_id, **payload)
    db.add(j)
    await db.commit()
    return (await _serializar_justificaciones(db, tenant_id, [await _just_orm(db, j.id, tenant_id)]))[0]


async def actualizar_justificacion(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> dict | None:
    j = await _just_orm(db, id, tenant_id)
    if not j:
        return None
    cambios = data if isinstance(data, dict) else data.model_dump(exclude_unset=True)
    for f, v in cambios.items():
        if hasattr(j, f):
            setattr(j, f, v)
    await db.commit()
    return (await _serializar_justificaciones(db, tenant_id, [await _just_orm(db, id, tenant_id)]))[0]


async def eliminar_justificacion(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    j = await _just_orm(db, id, tenant_id)
    if not j:
        return False
    await db.delete(j)
    await db.commit()
    return True
