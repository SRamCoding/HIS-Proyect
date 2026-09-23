"""Lógica de agregación del dashboard SIGARH.

Un único punto de entrada -`get_dashboard`- que arma todo el payload que
consume el escritorio (pages/sigarh/index.vue).
"""
import uuid
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.sigarh.rrhh.models import Empleado, RegistroAsistencia, Justificacion
from app.sigarh.movimientos.models import CambioTurno, Papeleta
from app.sigarh.infraestructura_hosp.models import Cama
from app.tenants.modulos.submodulos import permiso_incluye

# Mismo criterio que admin/auditoria y admin/reportes: el contenedor corre
# en UTC puro, asi que date.today() "cambia de dia" entre las 19:00 y
# medianoche hora de Lima -- "Asistencia Hoy" podia mostrar 0 durante esa
# ventana aunque si hubiera asistencia marcada para el dia real en Lima, y
# el corte de "mes actual" se adelantaba un dia en la ultima noche del mes.
_ZONA_LIMA = timezone(timedelta(hours=-5))

# Vacaciones y licencias no tienen tabla propia en uso: "Tramitar Licencia" y
# "Justificación y Vacaciones" (movimientos) escriben en sigarh_justificaciones
# (rrhh), discriminando por `tipo`. Las clases Vacacion/Licencia de
# movimientos.models existen pero nunca reciben datos — leerlas aquí hacía que
# estos KPIs mostraran siempre 0 aunque hubiera vacaciones/licencias reales.

MESES_ES = ["ene", "feb", "mar", "abr", "may", "jun",
            "jul", "ago", "sep", "oct", "nov", "dic"]

ASISTENCIA_PRESENTE = ("presente", "tardanza", "justificado")


async def _count(db: AsyncSession, stmt) -> int:
    return (await db.scalar(stmt)) or 0


def _tiene_modulo(activos: list[str], modulo_base: str) -> bool:
    """True si `activos` concede el modulo completo o CUALQUIER submodulo
    suyo -- a diferencia de permiso_incluye (que exige el codigo exacto o
    su padre inmediato), esto responde "el usuario tiene ALGO de acceso a
    este modulo", que es lo que hace falta para decidir si mostrar la
    seccion del Escritorio en absoluto."""
    return any(m == modulo_base or m.startswith(f"{modulo_base}.") for m in activos)


def _rango_meses(hoy: date, cantidad: int) -> list[tuple[date, date]]:
    """Devuelve [(inicio_mes, inicio_mes_siguiente)] para los últimos `cantidad` meses."""
    rangos: list[tuple[date, date]] = []
    anio, mes = hoy.year, hoy.month
    # retroceder hasta el mes más antiguo
    for _ in range(cantidad - 1):
        mes -= 1
        if mes == 0:
            mes, anio = 12, anio - 1
    for _ in range(cantidad):
        inicio = date(anio, mes, 1)
        if mes == 12:
            fin = date(anio + 1, 1, 1)
        else:
            fin = date(anio, mes + 1, 1)
        rangos.append((inicio, fin))
        mes += 1
        if mes == 13:
            mes, anio = 1, anio + 1
    return rangos


def _rango_semanas(hoy: date, cantidad: int) -> list[tuple[date, date]]:
    """Devuelve [(lunes, domingo)] para las últimas `cantidad` semanas (incluida la actual)."""
    lunes_actual = hoy - timedelta(days=hoy.weekday())
    rangos: list[tuple[date, date]] = []
    for i in range(cantidad - 1, -1, -1):
        lunes = lunes_actual - timedelta(weeks=i)
        rangos.append((lunes, lunes + timedelta(days=6)))
    return rangos


async def get_dashboard(db: AsyncSession, tenant_id: uuid.UUID, active_modules: list[str] | None = None) -> dict:
    """`active_modules` viene del JWT de la sesion (mismo campo que ya usa
    require_module_jwt en el resto de routers SIGARH). Antes este endpoint
    no exigia ningun modulo y devolvia KPIs de RRHH/movimientos/camas del
    hospital COMPLETO sin importar el perfil de quien preguntara -- una
    cuenta con acceso solo a Camas podia ver conteos de empleados,
    solicitudes pendientes, etc. que su perfil no deberia mostrarle. Cada
    seccion ahora se calcula (y se expone) solo si el perfil tiene ALGO de
    acceso al modulo dueño de esos datos; si no, esa parte del payload
    queda en su valor vacio/cero y `acceso.*` avisa al frontend para que
    oculte la seccion en vez de mostrar un cero que parece un dato real.
    `active_modules=None` (compatibilidad con llamadores que no lo pasen)
    se trata como "sin modulos" -- todo oculto, nunca "todo visible" por
    defecto."""
    activos = active_modules or []
    acceso_rrhh = _tiene_modulo(activos, "sigarh_recursos_humanos")
    acceso_movimientos = _tiene_modulo(activos, "sigarh_movimientos")
    acceso_camas = permiso_incluye(activos, "sigarh_infraestructura_hosp.camas")

    hoy = datetime.now(_ZONA_LIMA).date()
    inicio_mes = hoy.replace(day=1)

    def emp(*extra):
        return select(func.count(Empleado.id)).where(Empleado.tenant_id == tenant_id, *extra)

    # ── Empleados / asistencia (requiere sigarh_recursos_humanos) ──────────
    total_empleados = empleados_activos = empleados_inactivos = 0
    genero_m = genero_f = 0
    asistencia_hoy = ausentes_hoy = 0
    porcentaje_asistencia = 0.0
    empleados_por_mes: list[dict] = []
    asistencia_semanal: list[dict] = []

    if acceso_rrhh:
        total_empleados = await _count(db, emp())
        empleados_activos = await _count(db, emp(Empleado.is_active.is_(True)))
        empleados_inactivos = total_empleados - empleados_activos

        genero_m = await _count(db, emp(Empleado.sexo == "M"))
        genero_f = await _count(db, emp(Empleado.sexo == "F"))

        asistencia_hoy = await _count(db, select(func.count(RegistroAsistencia.id)).where(
            RegistroAsistencia.tenant_id == tenant_id,
            RegistroAsistencia.fecha == hoy,
            RegistroAsistencia.estado.in_(ASISTENCIA_PRESENTE),
        ))
        ausentes_hoy = await _count(db, select(func.count(RegistroAsistencia.id)).where(
            RegistroAsistencia.tenant_id == tenant_id,
            RegistroAsistencia.fecha == hoy,
            RegistroAsistencia.estado == "ausente",
        ))
        # min(...,100): sin registro unico tenant_id+empleado_id+fecha en
        # RegistroAsistencia, un duplicado (o un empleado desactivado el
        # mismo dia que ya tenia un registro "presente") puede inflar el
        # numerador por encima de empleados_activos -- la barra visual del
        # frontend ya se limitaba a 100%, pero el numero en texto no.
        porcentaje_asistencia = min(round(asistencia_hoy / empleados_activos * 100, 1), 100.0) if empleados_activos else 0.0

        for inicio, fin in _rango_meses(hoy, 6):
            valor = await _count(db, emp(
                Empleado.created_at >= datetime.combine(inicio, time.min),
                Empleado.created_at < datetime.combine(fin, time.min),
            ))
            empleados_por_mes.append({"label": MESES_ES[inicio.month - 1], "anio": inicio.year, "valor": valor})

        for lunes, domingo in _rango_semanas(hoy, 5):
            presentes = await _count(db, select(func.count(RegistroAsistencia.id)).where(
                RegistroAsistencia.tenant_id == tenant_id,
                RegistroAsistencia.fecha >= lunes, RegistroAsistencia.fecha <= domingo,
                RegistroAsistencia.estado.in_(ASISTENCIA_PRESENTE),
            ))
            ausentes = await _count(db, select(func.count(RegistroAsistencia.id)).where(
                RegistroAsistencia.tenant_id == tenant_id,
                RegistroAsistencia.fecha >= lunes, RegistroAsistencia.fecha <= domingo,
                RegistroAsistencia.estado == "ausente",
            ))
            asistencia_semanal.append({
                "label": lunes.strftime("%d/%m"),
                "presentes": presentes, "ausentes": ausentes, "total": presentes + ausentes,
            })

    def justif(tipo, *extra):
        return select(func.count(Justificacion.id)).where(
            Justificacion.tenant_id == tenant_id, Justificacion.tipo == tipo, *extra)

    # "Por revisar en RRHH" en la UI -- se gatea con RRHH, no con
    # movimientos, aunque Justificacion tambien registre tipo=vacacion/
    # licencia (esos conteos puntuales SI van con movimientos, ver abajo).
    justificaciones_pendientes = 0
    if acceso_rrhh:
        justificaciones_pendientes = await _count(db, select(func.count(Justificacion.id)).where(
            Justificacion.tenant_id == tenant_id, Justificacion.estado == "pendiente"))

    # ── Movimientos (requiere sigarh_movimientos) ───────────────────────────
    mov_mes = {"vacaciones": 0, "licencias": 0, "papeletas": 0, "cambios_turno": 0}
    pendientes = {"vacaciones": 0, "licencias": 0, "papeletas": 0, "cambios_turno": 0}
    solicitudes_pendientes = 0
    en_vacaciones = en_licencia = 0
    tendencias_solicitudes: list[dict] = []
    ultimas_vacaciones: list[dict] = []
    ultimas_licencias: list[dict] = []

    if acceso_movimientos:
        mov_mes = {
            "vacaciones": await _count(db, justif("vacacion", Justificacion.fecha_inicio >= inicio_mes)),
            "licencias": await _count(db, justif("licencia", Justificacion.fecha_tramite >= inicio_mes)),
            "papeletas": await _count(db, select(func.count(Papeleta.id)).where(
                Papeleta.tenant_id == tenant_id, Papeleta.fecha_tramite >= inicio_mes)),
            "cambios_turno": await _count(db, select(func.count(CambioTurno.id)).where(
                CambioTurno.tenant_id == tenant_id, CambioTurno.fecha_original >= inicio_mes)),
        }

        pendientes = {
            "vacaciones": await _count(db, justif("vacacion", Justificacion.estado == "pendiente")),
            "licencias": await _count(db, justif("licencia", Justificacion.estado == "pendiente")),
            "papeletas": await _count(db, select(func.count(Papeleta.id)).where(
                Papeleta.tenant_id == tenant_id, Papeleta.estado == "pendiente")),
            "cambios_turno": await _count(db, select(func.count(CambioTurno.id)).where(
                CambioTurno.tenant_id == tenant_id, CambioTurno.estado == "pendiente")),
        }
        solicitudes_pendientes = sum(pendientes.values())

        en_vacaciones = await _count(db, select(func.count(func.distinct(Justificacion.empleado_id))).where(
            Justificacion.tenant_id == tenant_id, Justificacion.tipo == "vacacion",
            Justificacion.estado == "aprobado",
            Justificacion.fecha_inicio <= hoy,
            Justificacion.fecha_fin >= hoy,
        ))
        en_licencia = await _count(db, select(func.count(func.distinct(Justificacion.empleado_id))).where(
            Justificacion.tenant_id == tenant_id, Justificacion.tipo == "licencia",
            Justificacion.estado == "aprobado",
            Justificacion.fecha_inicio <= hoy,
            Justificacion.fecha_fin >= hoy,
        ))

        for inicio, fin in _rango_meses(hoy, 6):
            v = await _count(db, justif("vacacion", Justificacion.fecha_inicio >= inicio, Justificacion.fecha_inicio < fin))
            l = await _count(db, justif("licencia", Justificacion.fecha_tramite >= inicio, Justificacion.fecha_tramite < fin))
            p = await _count(db, select(func.count(Papeleta.id)).where(
                Papeleta.tenant_id == tenant_id, Papeleta.fecha_tramite >= inicio, Papeleta.fecha_tramite < fin))
            c = await _count(db, select(func.count(CambioTurno.id)).where(
                CambioTurno.tenant_id == tenant_id, CambioTurno.fecha_original >= inicio, CambioTurno.fecha_original < fin))
            tendencias_solicitudes.append({
                "label": MESES_ES[inicio.month - 1], "anio": inicio.year,
                "vacaciones": v, "licencias": l, "papeletas": p, "cambios_turno": c,
                "total": v + l + p + c,
            })

        res_vac = await db.execute(
            select(Justificacion, Empleado)
            .join(Empleado, Empleado.id == Justificacion.empleado_id)
            .where(Justificacion.tenant_id == tenant_id, Justificacion.tipo == "vacacion")
            .order_by(Justificacion.created_at.desc()).limit(5)
        )
        ultimas_vacaciones = [
            {
                "id": str(v.id),
                "empleado_nombre": e.nombre_completo,
                "tipo": v.tipo,
                "fecha_inicio": str(v.fecha_inicio),
                "fecha_fin": str(v.fecha_fin),
                "estado": v.estado,
            }
            for v, e in res_vac.all()
        ]

        res_lic = await db.execute(
            select(Justificacion, Empleado)
            .join(Empleado, Empleado.id == Justificacion.empleado_id)
            .where(Justificacion.tenant_id == tenant_id, Justificacion.tipo == "licencia")
            .order_by(Justificacion.created_at.desc()).limit(5)
        )
        ultimas_licencias = [
            {
                "id": str(l.id),
                "empleado_nombre": e.nombre_completo,
                "fecha_tramite": str(l.fecha_tramite),
                "fecha_inicio": str(l.fecha_inicio),
                "fecha_fin": str(l.fecha_fin),
                "estado": l.estado,
            }
            for l, e in res_lic.all()
        ]

    # ── Camas (requiere sigarh_infraestructura_hosp.camas) ─────────────────
    camas_total = camas_disp = camas_ocup = camas_mant = camas_res = 0
    if acceso_camas:
        def cama(*extra):
            return select(func.count(Cama.id)).where(Cama.tenant_id == tenant_id, *extra)

        camas_total = await _count(db, cama())
        camas_disp = await _count(db, cama(Cama.estado == "DISPONIBLE"))
        camas_ocup = await _count(db, cama(Cama.estado == "OCUPADA"))
        camas_mant = await _count(db, cama(Cama.estado == "MANTENIMIENTO"))
        camas_res = await _count(db, cama(Cama.estado == "RESERVADA"))

    return {
        "fecha": str(hoy),
        "acceso": {
            "rrhh": acceso_rrhh,
            "movimientos": acceso_movimientos,
            "camas": acceso_camas,
        },
        "kpis": {
            "total_empleados": total_empleados,
            "empleados_activos": empleados_activos,
            "empleados_inactivos": empleados_inactivos,
            "asistencia_hoy": asistencia_hoy,
            "ausentes_hoy": ausentes_hoy,
            "porcentaje_asistencia": porcentaje_asistencia,
            "solicitudes_pendientes": solicitudes_pendientes,
            "justificaciones_pendientes": justificaciones_pendientes,
        },
        "movimientos_mes": mov_mes,
        "pendientes": pendientes,
        "camas": {
            "total": camas_total,
            "disponibles": camas_disp,
            "ocupadas": camas_ocup,
            "mantenimiento": camas_mant,
            "reservadas": camas_res,
            "porcentaje_ocupacion": round(camas_ocup / camas_total * 100, 1) if camas_total else 0.0,
        },
        "distribucion_genero": {
            "masculino": genero_m,
            "femenino": genero_f,
            "sin_registrar": max(total_empleados - genero_m - genero_f, 0),
        },
        "distribucion_estado": {
            "activos": empleados_activos,
            "inactivos": empleados_inactivos,
            "en_vacaciones": en_vacaciones,
            "en_licencia": en_licencia,
        },
        "empleados_por_mes": empleados_por_mes,
        "asistencia_semanal": asistencia_semanal,
        "tendencias_solicitudes": tendencias_solicitudes,
        "ultimas_vacaciones": ultimas_vacaciones,
        "ultimas_licencias": ultimas_licencias,
    }
