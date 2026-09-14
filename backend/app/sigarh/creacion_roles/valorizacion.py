"""Estimación de guardias programadas. Las marcaciones no autorizan un pago."""
import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select
from app.sigarh.mantenimiento.models import TipoGuardia, GuardiaValorizada, NivelRemunerativo, Profesion
from app.sigarh.mantenimiento.service import seleccionar_tarifa
from app.sigarh.rrhh.models import DiasFeriado, RegistroAsistencia
from app.sigarh.rrhh.vigencia_laboral import impedimento_programacion

def tipo_por_fecha(codigo, fecha, feriados):
    if codigo not in {"MINSA-GDO", "MINSA-GNO", "MINSA-GDF", "MINSA-GNF"}:
        return None
    nocturna = codigo in {"MINSA-GNO", "MINSA-GNF"}
    festivo = fecha.weekday() == 6 or fecha in feriados
    return "MINSA-G" + ("NF" if nocturna and festivo else "NO" if nocturna else "DF" if festivo else "DO")

def intervalo(fecha, horario):
    try:
        inicio = datetime.combine(fecha, datetime.strptime(horario.hora_inicio, "%H:%M").time())
        fin = datetime.combine(fecha, datetime.strptime(horario.hora_fin, "%H:%M").time())
    except (ValueError, AttributeError, TypeError):
        return None
    if fin <= inicio:
        fin += timedelta(days=1)
    return inicio, fin

async def estimar_rol(db, tid, rol, cat):
    tipos = {t.id: t for t in (await db.scalars(select(TipoGuardia).where(TipoGuardia.tenant_id == tid, TipoGuardia.is_active.is_(True)))).all()}
    por_codigo = {t.codigo: t.id for t in tipos.values()}
    tarifas = (await db.scalars(select(GuardiaValorizada).where(GuardiaValorizada.tenant_id == tid, GuardiaValorizada.is_active.is_(True)))).all()
    niveles = {n.id: n for n in (await db.scalars(select(NivelRemunerativo).where(NivelRemunerativo.tenant_id == tid, NivelRemunerativo.is_active.is_(True)))).all()}
    profesiones = {p.id: p for p in (await db.scalars(select(Profesion).where(Profesion.tenant_id == tid, Profesion.is_active.is_(True)))).all()}
    feriados = set((await db.scalars(select(DiasFeriado.fecha).where(DiasFeriado.tenant_id == tid, DiasFeriado.is_active.is_(True)))).all())
    primero = date(rol.anio, rol.mes, 1)
    ultimo = date(rol.anio, rol.mes, calendar.monthrange(rol.anio, rol.mes)[1])
    # El calendario nacional 2026 se contrastó con gob.pe/feriados. Otros años requieren revisión.
    asistencia = (await db.scalars(select(RegistroAsistencia).where(RegistroAsistencia.tenant_id == tid,
        RegistroAsistencia.fecha >= primero, RegistroAsistencia.fecha <= ultimo))).all()
    filas, total = [], Decimal("0.00")
    for re in rol.empleados:
        emp = cat["emps"].get(re.empleado_id)
        programados = {}
        for act in re.actividades:
            for turno in act.turnos:
                hor = cat["hors"].get(turno.horario_guardia_id)
                for dia in range(1, ultimo.day + 1):
                    fecha = date(rol.anio, rol.mes, dia)
                    if (fecha.weekday() + 1) % 7 in (turno.dias_semana or []):
                        # Varias actividades en el mismo horario constituyen una sola guardia.
                        programados[(fecha, turno.horario_guardia_id)] = hor
        intervalos = {k: intervalo(k[0], h) for k, h in programados.items()}
        for key, hor in sorted(programados.items(), key=lambda x: (x[0][0], str(x[0][1]))):
            fecha, hid = key
            motivo = impedimento_programacion(emp, fecha)
            nivel = niveles.get(getattr(emp, "nivel_remunerativo_id", None))
            prof = profesiones.get(getattr(emp, "profesion_id", None))
            if not motivo and (not nivel or not prof or nivel.profesion_codigo != prof.codigo):
                motivo = "Completar profesión y nivel remunerativo compatibles en el empleado."
            if not motivo and getattr(emp, "vinculo_laboral_codigo", None) not in {"276_NOMBRADO", "276_CONTRATADO"}:
                motivo = "Revisar el sustento de aplicación del D.Leg. 1153 para este vínculo laboral."
            if not motivo and rol.tipo_rol in {"reten", "complementario", "complementario_con_actividad", "turnos"}:
                motivo = "Esta modalidad requiere una regla específica; no se aplica la tarifa hospitalaria ordinaria."
            iv = intervalos[key]
            if not motivo and (not hor or not hor.is_active or not iv or iv[1] - iv[0] != timedelta(hours=12)):
                motivo = "Seleccionar un horario de guardia activo de 12 horas."
            if not motivo and any(k != key and other and iv[0] < other[1] and other[0] < iv[1] for k, other in intervalos.items()):
                motivo = "Existen horarios superpuestos para este empleado; revisar la programación."
            codigo = tipo_por_fecha(getattr(tipos.get(getattr(hor, "tipo_guardia_id", None)), "codigo", None), fecha, feriados)
            if not motivo and not codigo:
                motivo = "El horario no está asociado a un tipo hospitalario MINSA."
            if not motivo and rol.anio != 2026:
                motivo = "Revisar el calendario nacional de feriados de este año antes de valorizar."
            if not motivo and ((codigo.endswith(("DO", "DF")) and hor.hora_inicio != "07:00") or
                               (codigo.endswith(("NO", "NF")) and hor.hora_inicio != "19:00")):
                motivo = "Revisar la modalidad diurna/nocturna y las horas del horario."
            tarifa = None
            if not motivo:
                candidatas = [t for t in tarifas if t.tipo_guardia_id == por_codigo.get(codigo)
                    and t.vigencia_desde and t.vigencia_desde <= fecha
                    and (not t.vigencia_hasta or t.vigencia_hasta >= fecha)
                    and (not t.grupo_ocupacional_id or t.grupo_ocupacional_id == emp.grupo_ocupacional_id)
                    and (not t.nivel_remunerativo_id or t.nivel_remunerativo_id == emp.nivel_remunerativo_id)]
                try:
                    tarifa = seleccionar_tarifa(candidatas)
                    if tarifa.moneda != "PEN":
                        motivo, tarifa = "La tarifa debe estar expresada en soles.", None
                except HTTPException as exc:
                    motivo = exc.detail
            if tarifa:
                total += tarifa.valor
            registros = [a for a in asistencia if a.empleado_id == re.empleado_id and a.fecha == fecha and a.horario_guardia_id == hid]
            marcaciones = bool(len(registros) == 1 and registros[0].estado in {"presente", "tardanza"}
                and registros[0].hora_entrada_real and registros[0].hora_salida_real)
            filas.append({"empleado": getattr(emp, "nombre_completo", "Empleado"), "fecha": fecha.isoformat(),
                "horario": getattr(hor, "nombre", "Sin horario"), "tipo": codigo,
                "valor": str(tarifa.valor) if tarifa else None, "tarifa_id": str(tarifa.id) if tarifa else None,
                "sustento": tarifa.sustento if tarifa else None, "pendiente": motivo,
                "asistencia": "Marcaciones registradas; requiere calificación" if marcaciones else "Sin marcaciones completas"})
    return {"total_estimado": str(total), "moneda": "PEN", "pendientes": sum(bool(f["pendiente"]) for f in filas),
        "detalle": filas, "nota": "Estimación de este rol. No constituye liquidación ni autorización de pago. "
        "RR. HH. debe consolidar roles, validar ejecución, vínculo, plaza, presupuesto y resolución. "
        "Retén, guardias comunitarias y servicios complementarios requieren reglas propias."}
