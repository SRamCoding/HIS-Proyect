"""Catálogo único de submódulos de SIGARH.

Es la fuente de verdad de qué pantallas/recursos viven dentro de cada módulo
(hoy esa jerarquía solo existía hardcodeada en el nav del frontend). La usan:
  - GET /sigarh/mantenimiento/modulos-catalogo, para que la pantalla de
    creación de roles arme el árbol módulo -> submódulos.
  - permiso_incluye(), para resolver si un rol tiene acceso a un submódulo
    puntual.

Código de un submódulo: "<modulo>.<submodulo>", ej. "sigarh_recursos_humanos.empleados".

Compatibilidad hacia atrás: un rol con el código del módulo padre a secas
(sin punto) sigue teniendo acceso a TODOS sus submódulos. Ningún rol existente
pierde acceso al introducir este catálogo — hoy modulos_permitidos solo
contiene códigos de módulo completos, y seguirá funcionando igual.

Esta es la Fase 1 del trabajo (catálogo + regla de compatibilidad). Los
routers de SIGARH todavía protegen cada endpoint a nivel de módulo completo;
migrarlos a submódulo puntual es la Fase 3, módulo por módulo.
"""

SUBMODULOS_POR_MODULO: dict[str, list[dict[str, str]]] = {
    "sigarh_recursos_humanos": [
        {"code": "empleados", "label": "Empleados"},
        {"code": "especialidades", "label": "Especialidades"},
        {"code": "feriados", "label": "Días Feriados"},
        {"code": "asistencia", "label": "Registro de Asistencia"},
        {"code": "tolerancias", "label": "Tolerancias"},
        {"code": "motivos_justificacion", "label": "Motivos de Justificación"},
        {"code": "justificaciones", "label": "Justificaciones e Inasistencias"},
    ],
    "sigarh_movimientos": [
        {"code": "vacaciones", "label": "Justificación y Vacaciones"},
        {"code": "licencias_tramitar", "label": "Tramitar Licencia"},
        {"code": "licencias_estado", "label": "Estado Licencia"},
        {"code": "cambio_turno_tramitar", "label": "Tramitar Cambio de Turno"},
        {"code": "cambio_turno_estado", "label": "Estado Cambio Turno"},
        {"code": "papeletas_tramitar", "label": "Tramitar Papeleta"},
        {"code": "papeletas_estado", "label": "Estado de Papeletas"},
    ],
    "sigarh_creacion_roles": [
        {"code": "medicos", "label": "Médicos"},
        {"code": "otros_profesionales", "label": "Otros Profesionales de la Salud"},
        {"code": "residentes", "label": "Residentes"},
        {"code": "tecnicos", "label": "Técnicos"},
        {"code": "internos", "label": "Internos"},
    ],
    "sigarh_roles_pendientes": [
        {"code": "bandeja", "label": "Bandeja de Roles"},
        {"code": "solicitudes", "label": "Solicitudes de Modificación"},
    ],
    "sigarh_roles_aprobados": [
        {"code": "roles_aprobados", "label": "Roles Aprobados"},
    ],
    "sigarh_infraestructura": [
        {"code": "catalogos", "label": "Catálogos"},
        {"code": "consultorios", "label": "Consultorios"},
    ],
    "sigarh_infraestructura_hosp": [
        {"code": "pisos", "label": "Pisos"},
        {"code": "salas", "label": "Salas"},
        {"code": "camas", "label": "Camas"},
    ],
    "sigarh_config_farmacia": [
        {"code": "almacenes", "label": "Almacenes / Farmacias"},
        {"code": "medicamentos", "label": "Medicamentos e Insumos"},
    ],
    "sigarh_config_financiera": [
        {"code": "seguros", "label": "Seguros"},
        {"code": "cajas", "label": "Cajas"},
        {"code": "tarifario", "label": "Tarifario"},
    ],
    "sigarh_laboratorio": [
        {"code": "examenes", "label": "Exámenes de Laboratorio"},
    ],
    "sigarh_imagenologia": [
        {"code": "examenes", "label": "Exámenes de Imagenología"},
    ],
    "sigarh_nutricion": [
        {"code": "raciones", "label": "Registro de Raciones"},
        {"code": "reportes", "label": "Generar Reportes"},
        {"code": "entrega", "label": "Entrega de Raciones"},
        {"code": "cambio_turno", "label": "Cambios de Turno"},
    ],
    "sigarh_general": [
        {"code": "cie10", "label": "Diagnósticos CIE-10"},
        {"code": "paquetes", "label": "Paquetes"},
        {"code": "tiempos", "label": "Tiempos Procedimientos"},
    ],
    "sigarh_mantenimiento": [
        {"code": "usuarios", "label": "Usuarios"},
        {"code": "departamentos", "label": "Departamentos"},
        {"code": "servicios", "label": "Servicios"},
        {"code": "dependencias", "label": "Dependencias"},
        {"code": "tipos_trabajador", "label": "Tipos de Trabajador"},
        {"code": "tipos_guardia", "label": "Tipos de Guardia"},
        {"code": "niveles_remunerativos", "label": "Niveles Remunerativos"},
        {"code": "horarios_guardia", "label": "Horarios de Guardia"},
        {"code": "tipos_actividad", "label": "Tipos de Actividad"},
        {"code": "actividades", "label": "Actividades"},
        {"code": "guardias_valorizadas", "label": "Guardias Valorizadas"},
        {"code": "roles_sistema", "label": "Roles del Sistema"},
        {"code": "perfiles_usuario", "label": "Perfiles de Usuario"},
        {"code": "grupos_ocupacionales", "label": "Grupos Ocupacionales"},
    ],
}


def submodulos_de(modulo_code: str) -> list[dict[str, str]]:
    return SUBMODULOS_POR_MODULO.get(modulo_code, [])


def modulo_padre(codigo: str) -> str:
    """'sigarh_recursos_humanos.empleados' -> 'sigarh_recursos_humanos'.
    Un código sin punto (el módulo completo) se devuelve tal cual."""
    return codigo.split(".", 1)[0]


def permiso_incluye(permisos_concedidos: list[str], codigo_requerido: str) -> bool:
    """¿'permisos_concedidos' cubre 'codigo_requerido'?

    Compatibilidad hacia atrás: tener el módulo padre completo (sin submódulo)
    da acceso a todos sus submódulos. Un rol más fino puede en cambio listar
    submódulos puntuales (ej. 'sigarh_recursos_humanos.empleados') sin el
    código del módulo padre.
    """
    if codigo_requerido in permisos_concedidos:
        return True
    padre = modulo_padre(codigo_requerido)
    return padre != codigo_requerido and padre in permisos_concedidos
