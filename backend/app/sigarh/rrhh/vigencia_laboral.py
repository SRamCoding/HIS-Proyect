"""Vigencia operativa por fechas registradas, independiente del regimen."""
def impedimento_programacion(empleado, fecha):
    if not empleado or not empleado.is_active:
        return "El trabajador esta inactivo o no existe."
    if empleado.fecha_ingreso and fecha < empleado.fecha_ingreso:
        return "La fecha programada es anterior al ingreso del trabajador."
    if empleado.fecha_cese and fecha > empleado.fecha_cese:
        return "La fecha programada es posterior al cese del trabajador."
    return None


def validar_fechas_laborales(values, empleado=None):
    def valor(key):
        return values[key] if key in values else getattr(empleado, key, None)
    ingreso, nacimiento = valor("fecha_ingreso"), valor("fecha_nacimiento")
    if ingreso and nacimiento and ingreso <= nacimiento:
        return "La fecha de ingreso debe ser posterior al nacimiento."
    for key, label in (("fecha_cese", "cese"), ("fecha_nombramiento", "nombramiento")):
        fecha = valor(key)
        if ingreso and fecha and fecha < ingreso:
            return f"La fecha de {label} no puede ser anterior al ingreso."
    return None
