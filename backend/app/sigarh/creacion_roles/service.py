"""Lógica compartida de Roles de Turno: armado del detalle + CRUD + builder anidado.

Importado por los routers de creacion_roles, roles_pendientes y roles_aprobados.
"""
import uuid
from calendar import monthrange
from datetime import datetime, date

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.sigarh.creacion_roles.models import (
    Rol, RolEmpleado, RolActividad, RolTurno, SolicitudModificacionRol, MODALIDADES,
)
from app.sigarh.mantenimiento.models import Departamento, Servicio, Actividad, HorarioGuardia, PerfilUsuario, RolSistema, TipoTrabajador, GrupoOcupacional
from app.sigarh.rrhh.models import Empleado, EmpleadoEspecialidad

EDITABLE = ("draft", "rejected")

PERMISO_APROBAR_ROLES = "aprobar_roles_turno"


async def puede_aprobar_roles(db: AsyncSession, tenant_id: uuid.UUID, current_user: dict, servicio_id: uuid.UUID | None) -> bool:
    """Permiso real de aprobación: el perfil del usuario debe tener el permiso
    de acción, y si su rol de sistema no tiene alcance global, además debe ser
    jefe del servicio concreto del rol que se aprueba."""
    import json

    perfil_id = current_user.get("perfil_id")
    if not perfil_id:
        return False
    try:
        perfil_uuid = uuid.UUID(str(perfil_id))
    except (ValueError, TypeError):
        return False

    perfil = await db.scalar(
        select(PerfilUsuario).where(PerfilUsuario.id == perfil_uuid, PerfilUsuario.tenant_id == tenant_id, PerfilUsuario.is_active == True)
    )
    if not perfil or not perfil.rol_sistema_id:
        return False
    rol_sistema = await db.scalar(
        select(RolSistema).where(
            RolSistema.id == perfil.rol_sistema_id, RolSistema.tenant_id == tenant_id, RolSistema.is_active == True
        )
    )
    if not rol_sistema or not rol_sistema.permisos_accion:
        return False
    try:
        permisos = set(json.loads(rol_sistema.permisos_accion))
    except (ValueError, TypeError):
        permisos = set()
    if PERMISO_APROBAR_ROLES not in permisos:
        return False
    if rol_sistema.alcance_global:
        return True

    empleado_id = current_user.get("empleado_id")
    if not empleado_id or not servicio_id:
        return False
    try:
        empleado_uuid = uuid.UUID(str(empleado_id))
    except (ValueError, TypeError):
        return False
    empleado = await db.scalar(
        select(Empleado).where(Empleado.id == empleado_uuid, Empleado.tenant_id == tenant_id)
    )
    return bool(empleado and empleado.is_active and empleado.es_jefe_servicio and empleado.servicio_id == servicio_id)

# Nombres de actividad que App Hospitalario trata como consulta externa aunque
# la actividad no tenga marcado `requiere_consultorio` (mismo criterio que el sync).
_NOMBRES_CONSULTA_EXTERNA = {"consulta externa", "atencion ambulatoria", "atención ambulatoria"}


def _es_actividad_asistencial(act) -> bool:
    if act is None:
        return False
    if bool(getattr(act, "genera_agenda", False)):
        return True
    return False


def _hhmm_a_min(s: str | None) -> int | None:
    if not s or ":" not in str(s):
        return None
    try:
        h, m = str(s).split(":")[:2]
        return int(h) * 60 + int(m)
    except (ValueError, TypeError):
        return None


def _rango_min(hora_inicio: str | None, hora_fin: str | None) -> tuple[int, int] | None:
    """(inicio, fin) en minutos; si el turno cruza medianoche, fin += 24h."""
    a, b = _hhmm_a_min(hora_inicio), _hhmm_a_min(hora_fin)
    if a is None or b is None:
        return None
    if b <= a:
        b += 1440
    return (a, b)


def _rangos_solapan(r1: tuple[int, int], r2: tuple[int, int]) -> bool:
    return max(r1[0], r2[0]) < min(r1[1], r2[1])


def _dias_set(dias) -> set[int]:
    return {int(d) for d in (dias or []) if str(d).lstrip("-").isdigit() and 0 <= int(d) <= 6}


class ReglaNegocioError(Exception):
    """Operación bloqueada por regla de negocio -> HTTP 409."""


class PermisoError(Exception):
    """El usuario no tiene el permiso o el ámbito requerido -> HTTP 403."""


# ─── Carga ───────────────────────────────────────────────────────────────────

async def _validar_ambito(db, tenant_id, departamento_id, servicio_id) -> None:
    departamento = await db.scalar(select(Departamento).where(
        Departamento.id == departamento_id,
        Departamento.tenant_id == tenant_id,
        Departamento.is_active.is_(True),
    ))
    if not departamento:
        raise ReglaNegocioError("El departamento no existe o está inactivo.")
    servicio = await db.scalar(select(Servicio).where(
        Servicio.id == servicio_id,
        Servicio.tenant_id == tenant_id,
        Servicio.is_active.is_(True),
    ))
    if not servicio:
        raise ReglaNegocioError("El servicio no existe o está inactivo.")
    if servicio.departamento_id != departamento_id:
        raise ReglaNegocioError("El servicio seleccionado no pertenece al departamento.")


def _rol_stmt():
    return select(Rol).options(
        selectinload(Rol.empleados)
        .selectinload(RolEmpleado.actividades)
        .selectinload(RolActividad.turnos)
    )


async def obtener_rol_orm(db: AsyncSession, rol_id: uuid.UUID, tenant_id: uuid.UUID) -> Rol | None:
    res = await db.execute(_rol_stmt().where(Rol.id == rol_id, Rol.tenant_id == tenant_id))
    return res.scalar_one_or_none()


async def _catalogos(db: AsyncSession, tenant_id: uuid.UUID) -> dict:
    deps = dict((await db.execute(
        select(Departamento.id, Departamento.nombre).where(Departamento.tenant_id == tenant_id)
    )).all())
    servs = dict((await db.execute(
        select(Servicio.id, Servicio.nombre).where(Servicio.tenant_id == tenant_id)
    )).all())
    acts = {
        a.id: a for a in (await db.execute(
            select(Actividad).where(Actividad.tenant_id == tenant_id)
        )).scalars().all()
    }
    hors = {
        h.id: h for h in (await db.execute(
            select(HorarioGuardia).where(HorarioGuardia.tenant_id == tenant_id)
        )).scalars().all()
    }
    emps = {
        e.id: e for e in (await db.execute(
            select(Empleado).where(Empleado.tenant_id == tenant_id)
        )).scalars().all()
    }
    return {"deps": deps, "servs": servs, "acts": acts, "hors": hors, "emps": emps}


def _serializa_rol(rol: Rol, cat: dict, detalle: bool) -> dict:
    n_act = sum(len(re.actividades) for re in rol.empleados)
    n_turnos = sum(len(a.turnos) for re in rol.empleados for a in re.actividades)
    completa = bool(rol.empleados) and all(
        re.actividades and all(a.turnos for a in re.actividades) for re in rol.empleados
    )
    base = {
        "id": rol.id,
        "categoria_personal": rol.categoria_personal,
        "tipo_rol": rol.tipo_rol,
        "departamento_id": rol.departamento_id,
        "departamento_nombre": cat["deps"].get(rol.departamento_id),
        "servicio_id": rol.servicio_id,
        "servicio_nombre": cat["servs"].get(rol.servicio_id),
        "mes": rol.mes,
        "anio": rol.anio,
        "status": rol.status,
        "total_empleados": len(rol.empleados),
        "total_actividades": n_act,
        "total_turnos": n_turnos,
        "programacion_completa": completa,
        "created_by": rol.created_by,
        "submitted_at": rol.submitted_at,
        "reviewed_by": rol.reviewed_by,
        "reviewed_at": rol.reviewed_at,
        "rejection_reason": rol.rejection_reason,
        "created_at": rol.created_at,
    }
    if not detalle:
        return base

    empleados = []
    for re_ in rol.empleados:
        emp = cat["emps"].get(re_.empleado_id)
        actividades = []
        for a in re_.actividades:
            act = cat["acts"].get(a.actividad_id)
            turnos = []
            for t in a.turnos:
                hor = cat["hors"].get(t.horario_guardia_id)
                turnos.append({
                    "id": t.id,
                    "horario_guardia_id": t.horario_guardia_id,
                    "horario_nombre": getattr(hor, "nombre", None),
                    "hora_inicio": getattr(hor, "hora_inicio", None),
                    "hora_fin": getattr(hor, "hora_fin", None),
                    "dias_semana": t.dias_semana or [],
                })
            actividades.append({
                "id": a.id,
                "actividad_id": a.actividad_id,
                "actividad_nombre": getattr(act, "nombre", None),
                "requiere_consultorio": bool(getattr(act, "requiere_consultorio", False)),
                "turnos": turnos,
            })
        empleados.append({
            "id": re_.id,
            "empleado_id": re_.empleado_id,
            "empleado_nombre": getattr(emp, "nombre_completo", None),
            "dni": getattr(emp, "dni", None),
            "actividades": actividades,
        })
    base["empleados"] = empleados
    return base


async def serializar(db: AsyncSession, tenant_id: uuid.UUID, roles: list[Rol], detalle: bool = False) -> list[dict]:
    cat = await _catalogos(db, tenant_id)
    return [_serializa_rol(r, cat, detalle) for r in roles]


async def serializar_uno(db: AsyncSession, tenant_id: uuid.UUID, rol: Rol, detalle: bool = True) -> dict:
    cat = await _catalogos(db, tenant_id)
    result = _serializa_rol(rol, cat, detalle)
    if detalle:
        from app.sigarh.creacion_roles.valorizacion import estimar_rol
        result["valorizacion_guardias"] = await estimar_rol(db, tenant_id, rol, cat)
    return result


# ─── Diagnóstico de completitud (para el consumo de App Hospitalario) ─────────

async def diagnosticar_rol(db: AsyncSession, tenant_id: uuid.UUID, rol: Rol) -> list[dict]:
    """Revisa que el rol produzca cupos válidos al sincronizarse con la
    programación médica de App Hospitalario.

    Devuelve hallazgos ``{nivel, empleado, actividad, mensaje}``. Un ``"error"``
    impide enviar/aprobar el rol; una ``"advertencia"`` solo informa.
    """
    cat = await _catalogos(db, tenant_id)
    hallazgos: list[dict] = []

    def add(nivel: str, mensaje: str, empleado: str | None = None, actividad: str | None = None):
        hallazgos.append({"nivel": nivel, "empleado": empleado, "actividad": actividad, "mensaje": mensaje})

    if not rol.empleados:
        add("error", "El rol no tiene personal asignado.")
        return hallazgos

    es_medicos = rol.categoria_personal == "medicos"
    esp_por_empleado: dict[uuid.UUID, list[bool]] = {}
    if es_medicos:
        emp_ids = [re_.empleado_id for re_ in rol.empleados]
        filas = (await db.execute(
            select(EmpleadoEspecialidad.empleado_id, EmpleadoEspecialidad.validado)
            .where(EmpleadoEspecialidad.empleado_id.in_(emp_ids))
        )).all()
        for eid, validado in filas:
            esp_por_empleado.setdefault(eid, []).append(bool(validado))

    for re_ in rol.empleados:
        emp = cat["emps"].get(re_.empleado_id)
        nombre_emp = getattr(emp, "nombre_completo", None) or "Empleado sin nombre"
        if not emp or not emp.is_active:
            add("error", f"{nombre_emp}: trabajador inactivo o inexistente.", nombre_emp)
            continue
        if not re_.actividades:
            add("error", f"{nombre_emp}: no tiene actividades asignadas.", nombre_emp)
            continue

        tiene_asistencial = False
        franjas: list[tuple[str, set[int], tuple[int, int]]] = []  # (actividad, días, rango) asistenciales
        for a in re_.actividades:
            act = cat["acts"].get(a.actividad_id)
            nombre_act = getattr(act, "nombre", None) or "Actividad"
            asistencial = _es_actividad_asistencial(act)
            tiene_asistencial = tiene_asistencial or asistencial

            if not a.turnos:
                add("error", f"{nombre_emp} · {nombre_act}: la actividad no tiene turnos.", nombre_emp, nombre_act)
                continue

            for t in a.turnos:
                from calendar import monthrange
                from app.sigarh.rrhh.vigencia_laboral import impedimento_programacion
                fechas_invalidas = [dia for dia in range(1, monthrange(rol.anio, rol.mes)[1] + 1)
                                    if (date(rol.anio, rol.mes, dia).weekday() + 1) % 7 in _dias_set(t.dias_semana)
                                    and impedimento_programacion(emp, date(rol.anio, rol.mes, dia))]
                if fechas_invalidas:
                    add("error", f"{nombre_emp}: turno fuera de su vigencia laboral los dias {', '.join(map(str, fechas_invalidas))}.", nombre_emp, nombre_act)
                sin_horario = not t.horario_guardia_id
                sin_dias = not (t.dias_semana or [])
                if asistencial and sin_horario:
                    add("error", f"{nombre_emp} · {nombre_act}: un turno no tiene horario; no generará cupos.", nombre_emp, nombre_act)
                if asistencial and sin_dias:
                    add("error", f"{nombre_emp} · {nombre_act}: un turno no tiene días de la semana.", nombre_emp, nombre_act)
                if not asistencial and sin_horario:
                    add("advertencia", f"{nombre_emp} · {nombre_act}: un turno no tiene horario asignado.", nombre_emp, nombre_act)
                if asistencial and not sin_horario and not sin_dias:
                    hor = cat["hors"].get(t.horario_guardia_id)
                    rango = _rango_min(getattr(hor, "hora_inicio", None), getattr(hor, "hora_fin", None))
                    dset = _dias_set(t.dias_semana)
                    if rango and dset:
                        franjas.append((nombre_act, dset, rango))

        # Solape de franjas asistenciales del mismo médico dentro del rol.
        for i in range(len(franjas)):
            for j in range(i + 1, len(franjas)):
                n1, d1, r1 = franjas[i]
                n2, d2, r2 = franjas[j]
                if (d1 & d2) and _rangos_solapan(r1, r2):
                    detalle = f"'{n1}' y '{n2}'" if n1 != n2 else f"dos turnos de '{n1}'"
                    add("error", f"{nombre_emp}: {detalle} se solapan en día y horario.", nombre_emp)

        if es_medicos and tiene_asistencial:
            validados = esp_por_empleado.get(re_.empleado_id)
            if not validados:
                add("error", f"{nombre_emp}: el médico no tiene especialidad registrada; sus cupos no se sincronizarán con App Hospitalario.", nombre_emp)
            elif not any(validados):
                add("advertencia", f"{nombre_emp}: la especialidad del médico no está validada.", nombre_emp)

    hallazgos.extend(await _solapes_entre_roles(db, tenant_id, rol, cat))
    return hallazgos


async def _solapes_entre_roles(db: AsyncSession, tenant_id: uuid.UUID, rol: Rol, cat: dict) -> list[dict]:
    """Choques del rol contra la programación médica ya generada por OTROS roles.

    Compara cada franja asistencial que este rol produciría (por médico y fecha
    concreta del mes) contra las ``ProgramacionMedica`` activas de esos médicos
    que provienen de un turno distinto.
    """
    from app.hospital.consulta_externa.models import ProgramacionMedica

    hallazgos: list[dict] = []
    if not rol.empleados:
        return hallazgos

    turno_ids_propios = {t.id for re_ in rol.empleados for a in re_.actividades for t in a.turnos}
    emp_ids = [re_.empleado_id for re_ in rol.empleados]
    ultimo = monthrange(rol.anio, rol.mes)[1]

    progs = (await db.execute(
        select(ProgramacionMedica).where(
            ProgramacionMedica.tenant_id == tenant_id,
            ProgramacionMedica.medico_id.in_(emp_ids),
            ProgramacionMedica.estado == "activo",
            ProgramacionMedica.fecha.between(date(rol.anio, rol.mes, 1), date(rol.anio, rol.mes, ultimo)),
        )
    )).scalars().all()
    ajenas = [p for p in progs if p.origen_sigarh_turno_id not in turno_ids_propios]
    if not ajenas:
        return hallazgos

    # Servicio de origen de cada programación ajena, para el mensaje.
    otros_turnos = {p.origen_sigarh_turno_id for p in ajenas if p.origen_sigarh_turno_id}
    origen: dict[uuid.UUID, str] = {}
    if otros_turnos:
        rows = (await db.execute(
            select(RolTurno.id, Rol.mes, Rol.anio, Rol.servicio_id)
            .join(RolActividad, RolActividad.id == RolTurno.rol_actividad_id)
            .join(RolEmpleado, RolEmpleado.id == RolActividad.rol_empleado_id)
            .join(Rol, Rol.id == RolEmpleado.rol_id)
            .where(RolTurno.id.in_(otros_turnos))
        )).all()
        for tid_, mes_, anio_, serv_ in rows:
            origen[tid_] = cat["servs"].get(serv_) or f"rol {mes_:02d}/{anio_}"

    for re_ in rol.empleados:
        emp = cat["emps"].get(re_.empleado_id)
        nombre_emp = getattr(emp, "nombre_completo", None) or "Empleado"
        franjas_por_fecha: dict[date, list[tuple[int, int]]] = {}
        for a in re_.actividades:
            if not _es_actividad_asistencial(cat["acts"].get(a.actividad_id)):
                continue
            for t in a.turnos:
                hor = cat["hors"].get(t.horario_guardia_id)
                rango = _rango_min(getattr(hor, "hora_inicio", None), getattr(hor, "hora_fin", None))
                dset = _dias_set(t.dias_semana)
                if not rango or not dset:
                    continue
                for dia in range(1, ultimo + 1):
                    f = date(rol.anio, rol.mes, dia)
                    if (f.weekday() + 1) % 7 in dset:
                        franjas_por_fecha.setdefault(f, []).append(rango)

        vistos: set[str] = set()
        for p in ajenas:
            if p.medico_id != re_.empleado_id:
                continue
            r_exist = _rango_min(p.hora_inicio, p.hora_fin)
            if not r_exist:
                continue
            if any(_rangos_solapan(r, r_exist) for r in franjas_por_fecha.get(p.fecha, ())):
                quien = origen.get(p.origen_sigarh_turno_id, "otro rol aprobado")
                if quien not in vistos:
                    vistos.add(quien)
                    hallazgos.append({
                        "nivel": "error", "empleado": nombre_emp, "actividad": None,
                        "mensaje": f"{nombre_emp}: choca con la programación ya aprobada de '{quien}' (mismo día y franja horaria).",
                    })
    return hallazgos


def errores_bloqueantes(hallazgos: list[dict]) -> list[str]:
    return [h["mensaje"] for h in hallazgos if h["nivel"] == "error"]


# ─── Listado genérico ────────────────────────────────────────────────────────

async def listar_roles(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    *,
    status_in: list[str] | None = None,
    categoria: str | None = None,
    tipo: str | None = None,
    anio: int | None = None,
    mes: int | None = None,
) -> list[dict]:
    stmt = _rol_stmt().where(Rol.tenant_id == tenant_id)
    if status_in:
        stmt = stmt.where(Rol.status.in_(status_in))
    if categoria:
        stmt = stmt.where(Rol.categoria_personal == categoria)
    if tipo:
        stmt = stmt.where(Rol.tipo_rol == tipo)
    if anio:
        stmt = stmt.where(Rol.anio == anio)
    if mes:
        stmt = stmt.where(Rol.mes == mes)
    stmt = stmt.order_by(Rol.anio.desc(), Rol.mes.desc(), Rol.created_at.desc())
    roles = (await db.execute(stmt)).scalars().unique().all()
    return await serializar(db, tenant_id, roles, detalle=False)


# ─── CRUD cabecera ───────────────────────────────────────────────────────────

async def crear_rol(db: AsyncSession, tenant_id: uuid.UUID, data, usuario: str | None, usuario_id: uuid.UUID | None = None) -> dict:
    await _validar_ambito(db, tenant_id, data.departamento_id, data.servicio_id)
    # Regla de la variante médica ordinaria: no duplicar dep+serv+mes+anio
    if data.categoria_personal == "medicos" and data.tipo_rol == "ordinario":
        dup = await db.scalar(select(func.count()).select_from(Rol).where(
            Rol.tenant_id == tenant_id,
            Rol.categoria_personal == "medicos", Rol.tipo_rol == "ordinario",
            Rol.departamento_id == data.departamento_id, Rol.servicio_id == data.servicio_id,
            Rol.mes == data.mes, Rol.anio == data.anio,
            Rol.status != "rejected",
        ))
        if dup:
            raise ReglaNegocioError("Ya existe un rol médico ordinario para ese departamento, servicio y período.")

    rol = Rol(
        tenant_id=tenant_id,
        categoria_personal=data.categoria_personal,
        tipo_rol=data.tipo_rol,
        departamento_id=data.departamento_id,
        servicio_id=data.servicio_id,
        mes=data.mes,
        anio=data.anio,
        status="draft",
        created_by=usuario,
        created_by_id=usuario_id,
    )
    db.add(rol)
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, rol.id, tenant_id))


async def actualizar_rol(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID, data) -> dict | None:
    rol = await obtener_rol_orm(db, rol_id, tenant_id)
    if not rol:
        return None
    if rol.status not in EDITABLE:
        raise ReglaNegocioError("Solo se pueden editar roles en borrador o rechazados.")
    cambios = data.model_dump(exclude_unset=True)
    departamento_id = cambios.get("departamento_id", rol.departamento_id)
    servicio_id = cambios.get("servicio_id", rol.servicio_id)
    if departamento_id is None or servicio_id is None:
        raise ReglaNegocioError("El departamento y el servicio son obligatorios.")
    await _validar_ambito(db, tenant_id, departamento_id, servicio_id)
    for f, v in cambios.items():
        setattr(rol, f, v)
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, rol_id, tenant_id))


async def eliminar_rol(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID) -> bool:
    rol = await obtener_rol_orm(db, rol_id, tenant_id)
    if not rol:
        return False
    if rol.status not in EDITABLE:
        raise ReglaNegocioError("Solo se pueden eliminar roles en borrador o rechazados.")
    await db.delete(rol)
    await db.commit()
    return True


async def enviar_rol(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID) -> dict | None:
    rol = await obtener_rol_orm(db, rol_id, tenant_id)
    if not rol:
        return None
    if rol.status not in EDITABLE:
        raise ReglaNegocioError("El rol ya fue enviado.")
    errores = errores_bloqueantes(await diagnosticar_rol(db, tenant_id, rol))
    if errores:
        raise ReglaNegocioError("No se puede enviar el rol: " + " · ".join(errores[:8]))
    rol.status = "pending"
    rol.submitted_at = datetime.utcnow()
    rol.rejection_reason = None
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, rol_id, tenant_id))


# ─── Builder anidado ─────────────────────────────────────────────────────────

async def _rol_editable(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID) -> Rol:
    rol = await db.scalar(select(Rol).where(Rol.id == rol_id, Rol.tenant_id == tenant_id))
    if not rol:
        raise ReglaNegocioError("Rol no encontrado.")
    if rol.status not in EDITABLE:
        raise ReglaNegocioError("Solo se puede modificar la programación de roles en borrador o rechazados.")
    return rol


async def _rol_empleado(db: AsyncSession, tenant_id: uuid.UUID, rol_empleado_id: uuid.UUID) -> RolEmpleado:
    res = await db.execute(
        select(RolEmpleado).join(Rol, Rol.id == RolEmpleado.rol_id)
        .where(RolEmpleado.id == rol_empleado_id, Rol.tenant_id == tenant_id)
    )
    re_ = res.scalar_one_or_none()
    if not re_:
        raise ReglaNegocioError("Personal del rol no encontrado.")
    return re_


async def _rol_actividad(db: AsyncSession, tenant_id: uuid.UUID, rol_actividad_id: uuid.UUID) -> RolActividad:
    res = await db.execute(
        select(RolActividad)
        .join(RolEmpleado, RolEmpleado.id == RolActividad.rol_empleado_id)
        .join(Rol, Rol.id == RolEmpleado.rol_id)
        .where(RolActividad.id == rol_actividad_id, Rol.tenant_id == tenant_id)
    )
    ra = res.scalar_one_or_none()
    if not ra:
        raise ReglaNegocioError("Actividad del rol no encontrada.")
    return ra


async def _empleados_en_otro_rol_ordinario(
    db: AsyncSession, tenant_id: uuid.UUID, rol: Rol, empleado_ids: list[uuid.UUID]
) -> list[uuid.UUID]:
    """empleado_ids que ya pertenecen a otro rol 'ordinario' del mismo servicio y período."""
    if rol.tipo_rol != "ordinario" or not empleado_ids:
        return []
    return list((await db.execute(
        select(RolEmpleado.empleado_id)
        .join(Rol, Rol.id == RolEmpleado.rol_id)
        .where(
            Rol.tenant_id == tenant_id,
            Rol.id != rol.id,
            Rol.tipo_rol == "ordinario",
            Rol.servicio_id == rol.servicio_id,
            Rol.mes == rol.mes,
            Rol.anio == rol.anio,
            Rol.status != "rejected",
            RolEmpleado.empleado_id.in_(empleado_ids),
        )
    )).scalars().all())


async def categorias_de_empleados(db: AsyncSession, empleados: list[Empleado]) -> dict[uuid.UUID, str | None]:
    """Categoría de rol de turno (medicos/otros_profesionales/residentes/tecnicos/
    internos) de cada empleado. Manda el tipo de trabajador cuando identifica una
    etapa de formación (Residentado/Internado Médico); si no, manda el grupo
    ocupacional (la profesión). None si ninguno de los dos está clasificado."""
    tt_ids = {e.tipo_trabajador_id for e in empleados if e.tipo_trabajador_id}
    go_ids = {e.grupo_ocupacional_id for e in empleados if e.grupo_ocupacional_id}
    tt_cat = dict((await db.execute(
        select(TipoTrabajador.id, TipoTrabajador.categoria_personal).where(TipoTrabajador.id.in_(tt_ids))
    )).all()) if tt_ids else {}
    go_cat = dict((await db.execute(
        select(GrupoOcupacional.id, GrupoOcupacional.categoria_personal).where(GrupoOcupacional.id.in_(go_ids))
    )).all()) if go_ids else {}
    from app.sigarh.mantenimiento.models import Profesion
    profesion_ids = {e.profesion_id for e in empleados if e.profesion_id}
    profesion_cat = dict((await db.execute(select(
        Profesion.id, Profesion.categoria_personal
    ).where(Profesion.id.in_(profesion_ids)))).all()) if profesion_ids else {}
    return {
        e.id: tt_cat.get(e.tipo_trabajador_id) or profesion_cat.get(e.profesion_id) or go_cat.get(e.grupo_ocupacional_id)
        for e in empleados
    }


async def agregar_personal(db: AsyncSession, tenant_id: uuid.UUID, rol_id: uuid.UUID, empleado_ids: list[uuid.UUID]) -> dict:
    rol = await _rol_editable(db, tenant_id, rol_id)
    existentes = set((await db.execute(
        select(RolEmpleado.empleado_id).where(RolEmpleado.rol_id == rol_id)
    )).scalars().all())
    candidatos = (await db.execute(
        select(Empleado).where(Empleado.tenant_id == tenant_id, Empleado.id.in_(empleado_ids))
    )).scalars().all()
    validos = {e.id for e in candidatos}

    nuevos = [eid for eid in empleado_ids if eid in validos and eid not in existentes]
    if nuevos:
        categorias = await categorias_de_empleados(db, [e for e in candidatos if e.id in nuevos])
        incompatibles = [e for e in candidatos if e.id in nuevos and categorias.get(e.id) != rol.categoria_personal]
        if incompatibles:
            etq = ", ".join(f"{e.apellido_paterno} {e.nombres}".strip() for e in incompatibles)
            raise ReglaNegocioError(
                f"No corresponden a la categoría '{rol.categoria_personal}' de este rol: {etq}. "
                "Revisa su tipo de trabajador o grupo ocupacional en Mantenimiento."
            )
    chocan = await _empleados_en_otro_rol_ordinario(db, tenant_id, rol, nuevos)
    if chocan:
        nombres = (await db.execute(
            select(Empleado.apellido_paterno, Empleado.nombres).where(Empleado.id.in_(chocan))
        )).all()
        etq = ", ".join(f"{ap} {no}".strip() for ap, no in nombres) or "un empleado"
        raise ReglaNegocioError(
            f"{etq} ya pertenece a otro rol ordinario de este servicio para {rol.mes:02d}/{rol.anio}."
        )

    for eid in nuevos:
        db.add(RolEmpleado(rol_id=rol_id, empleado_id=eid))
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, rol_id, tenant_id))


async def quitar_personal(db: AsyncSession, tenant_id: uuid.UUID, rol_empleado_id: uuid.UUID) -> dict:
    re_ = await _rol_empleado(db, tenant_id, rol_empleado_id)
    await _rol_editable(db, tenant_id, re_.rol_id)
    rol_id = re_.rol_id
    await db.delete(re_)
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, rol_id, tenant_id))


async def agregar_actividades(db: AsyncSession, tenant_id: uuid.UUID, rol_empleado_id: uuid.UUID, actividad_ids: list[uuid.UUID]) -> dict:
    re_ = await _rol_empleado(db, tenant_id, rol_empleado_id)
    await _rol_editable(db, tenant_id, re_.rol_id)
    existentes = set((await db.execute(
        select(RolActividad.actividad_id).where(RolActividad.rol_empleado_id == rol_empleado_id)
    )).scalars().all())
    validos = set((await db.execute(
        select(Actividad.id).where(Actividad.tenant_id == tenant_id, Actividad.id.in_(actividad_ids))
    )).scalars().all())
    for aid in actividad_ids:
        if aid in validos and aid not in existentes:
            db.add(RolActividad(rol_empleado_id=rol_empleado_id, actividad_id=aid))
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, re_.rol_id, tenant_id))


async def quitar_actividad(db: AsyncSession, tenant_id: uuid.UUID, rol_actividad_id: uuid.UUID) -> dict:
    ra = await _rol_actividad(db, tenant_id, rol_actividad_id)
    re_ = await _rol_empleado(db, tenant_id, ra.rol_empleado_id)
    await _rol_editable(db, tenant_id, re_.rol_id)
    await db.delete(ra)
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, re_.rol_id, tenant_id))


async def agregar_turno(db: AsyncSession, tenant_id: uuid.UUID, rol_actividad_id: uuid.UUID, data) -> dict:
    ra = await _rol_actividad(db, tenant_id, rol_actividad_id)
    re_ = await _rol_empleado(db, tenant_id, ra.rol_empleado_id)
    await _rol_editable(db, tenant_id, re_.rol_id)
    if data.horario_guardia_id:
        ok = await db.scalar(select(func.count()).select_from(HorarioGuardia).where(
            HorarioGuardia.id == data.horario_guardia_id, HorarioGuardia.tenant_id == tenant_id
        ))
        if not ok:
            raise ReglaNegocioError("El horario de guardia no existe.")
    db.add(RolTurno(
        rol_actividad_id=rol_actividad_id,
        horario_guardia_id=data.horario_guardia_id,
        dias_semana=data.dias_semana,
    ))
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, re_.rol_id, tenant_id))


async def quitar_turno(db: AsyncSession, tenant_id: uuid.UUID, rol_turno_id: uuid.UUID) -> dict:
    res = await db.execute(
        select(RolTurno)
        .join(RolActividad, RolActividad.id == RolTurno.rol_actividad_id)
        .join(RolEmpleado, RolEmpleado.id == RolActividad.rol_empleado_id)
        .join(Rol, Rol.id == RolEmpleado.rol_id)
        .where(RolTurno.id == rol_turno_id, Rol.tenant_id == tenant_id)
    )
    t = res.scalar_one_or_none()
    if not t:
        raise ReglaNegocioError("Turno no encontrado.")
    ra = await _rol_actividad(db, tenant_id, t.rol_actividad_id)
    re_ = await _rol_empleado(db, tenant_id, ra.rol_empleado_id)
    await _rol_editable(db, tenant_id, re_.rol_id)
    await db.delete(t)
    await db.commit()
    return await serializar_uno(db, tenant_id, await obtener_rol_orm(db, re_.rol_id, tenant_id))
