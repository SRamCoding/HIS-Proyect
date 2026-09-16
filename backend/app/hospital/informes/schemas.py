"""
Informes no define schemas Pydantic propios: todos los endpoints son GET con
parametros de query (fecha_desde/fecha_hasta y filtros opcionales) y devuelven
listas/diccionarios construidos directamente en service.py -- igual que
Formato HIS, que tampoco usa un schema de salida para sus reportes.
"""
