"""Controles de programación ordinaria médica. Véase data/jornadas/README.md."""
from calendar import monthrange
from datetime import datetime, date, timedelta


def intervalos(rol, empleado_id, horarios, actividades):
    resultado = []
    for re in rol.empleados:
        if re.empleado_id != empleado_id:
            continue
        for actividad in re.actividades:
            act = actividades.get(actividad.actividad_id)
            for turno in actividad.turnos:
                hor = horarios.get(turno.horario_guardia_id)
                if not hor or not act:
                    continue
                try:
                    inicio = datetime.strptime(hor.hora_inicio, '%H:%M').time()
                    fin = datetime.strptime(hor.hora_fin, '%H:%M').time()
                except (TypeError, ValueError):
                    continue
                for dia in range(1, monthrange(rol.anio, rol.mes)[1] + 1):
                    fecha = date(rol.anio, rol.mes, dia)
                    if (fecha.weekday() + 1) % 7 not in (turno.dias_semana or []):
                        continue
                    a, b = datetime.combine(fecha, inicio), datetime.combine(fecha, fin)
                    if b <= a:
                        b += timedelta(days=1)
                    resultado.append((a, b, bool(hor.tipo_guardia_id), bool(act.genera_agenda), rol.tipo_rol))
    return resultado


def revisar_intervalos(franjas, mes, anio, limite, feriados=frozenset()):
    errores = []
    # Un turno repetido en varias actividades no debe desaparecer del diagnóstico.
    franjas = sorted(franjas)
    for anterior, siguiente in zip(franjas, franjas[1:]):
        if siguiente[0] < anterior[1]:
            errores.append('Tiene actividades o roles con horarios superpuestos.')
            break
    del_mes = [f for f in franjas if (f[0].year, f[0].month) == (anio, mes)]
    ordinarios = [f for f in del_mes if not f[4].startswith('complementario') and f[4] != 'reten']
    minutos = sum(int((f[1] - f[0]).total_seconds() / 60) for f in ordinarios)
    if minutos > limite * 60:
        errores.append(f'Acumula {minutos / 60:g} horas ordinarias; su jornada documentada permite {limite:g} horas mensuales.')
    guardias = [f for f in ordinarios if f[2]]
    if sum((f[1] - f[0]).total_seconds() / 3600 for f in guardias) > 60:
        errores.append('Supera 60 horas de guardia ordinaria mensual. Una excepción requiere autorización y validación específicas.')
    for a, b, guardia, agenda, tipo in del_mes:
        horas = (b - a).total_seconds() / 3600
        if agenda and horas > 4:
            errores.append('Consulta externa supera cuatro horas continuas. Separe las actividades de gestión clínica del turno de seis horas.')
        if guardia and horas > 12:
            errores.append('La guardia supera doce horas. La ampliación excepcional requiere autorización específica.')
        if tipo.startswith('complementario') or tipo == 'reten':
            errores.append('Servicios complementarios y retén requieren reglas y autorizaciones específicas; no se pueden aprobar como jornada ordinaria.')
    # Descanso postguardia en el siguiente día laborable (D.S. 019-83-PCM,
    # art. 14), junto con restricciones previas de R.M. 118-2014, art. 23.
    for a, b, guardia, agenda, tipo in franjas:
        if not guardia or b.date() == a.date():
            continue
        descanso = b.date()
        while descanso.weekday() >= 5 or descanso in feriados:
            descanso += timedelta(days=1)
        for c, d, *_ in franjas:
            if (c, d) == (a, b):
                continue
            if c.date() == descanso or (c.date() == a.date() and d.hour > 12 and d <= a):
                errores.append(f'Incumple descanso postguardia o restricción previa a guardia nocturna del {a:%d/%m/%Y}.')
                break
    return list(dict.fromkeys(errores))
