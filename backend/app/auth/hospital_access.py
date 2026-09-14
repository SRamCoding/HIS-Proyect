"""Accesos efectivos: perfil actual y módulos habilitados por el hospital."""
import uuid
from fastapi import HTTPException
from sqlalchemy import select
from app.auth.models import PerfilHospital

MEDICO_MODULOS = {"consulta_externa.programacion", "consulta_externa.atenciones"}

async def validar_rol_hospital(central, role):
    from app.admin.roles.models import SystemRole
    rol = await central.scalar(select(SystemRole).where(SystemRole.name == role,
        SystemRole.panel == 'app', SystemRole.is_active.is_(True)))
    if not rol:
        raise HTTPException(403, "El rol hospitalario está inactivo o no existe")
    return rol


def limitar_por_rol(contexto, rol):
    from app.tenants.modulos.submodulos import permiso_incluye
    if isinstance(rol.allowed_modules, list):
        contexto['active_modules'] = [c for c in contexto['active_modules'] if permiso_incluye(rol.allowed_modules, c)]
    return contexto
RECURSOS = [
    {"code": "consulta_externa.programacion", "label": "Programación médica (lectura)"},
    {"code": "consulta_externa.atenciones", "label": "Atenciones médicas y órdenes clínicas"},
    {"code": "consulta_externa.confirmacion", "label": "Confirmación de citas"},
    {"code": "consulta_externa.triaje", "label": "Registro de triaje"},
    {"code": "consulta_externa.agendamiento", "label": "Agendamiento y gestión de agendas"},
]

def permiso_recurso(path, method, modulo):
    if modulo != "consulta_externa":
        return modulo
    ruta = path.split("/consulta-externa/", 1)[-1]
    if ruta.startswith("programacion-medica"):
        return "consulta_externa.programacion" if method == "GET" else "consulta_externa.agendamiento"
    if ruta.startswith("citas"):
        if "confirmar" in ruta:
            return "consulta_externa.confirmacion"
        return "consulta_externa.atenciones" if method == "GET" else "consulta_externa.agendamiento"
    if ruta == "triaje/pendientes":
        return "consulta_externa.atenciones" if method == "GET" else "consulta_externa.triaje"
    if ruta.startswith("triaje"):
        return "consulta_externa.atenciones" if method == "GET" and ruta != "triaje" else "consulta_externa.triaje"
    if ruta.startswith(("estado-citas-medico", "paciente-consulta", "atenciones-medicas", "farmacia", "laboratorio", "imagenologia", "hospitalizacion", "referencias")):
        return "consulta_externa.atenciones"
    if ruta.startswith("interconsultas") and "/programar/" not in ruta and ruta != "interconsultas/pendientes":
        return "consulta_externa.atenciones"
    return "consulta_externa"

async def contexto_hospital(db, usuario, hospital, habilitados):
    from app.sigarh.rrhh.models import Empleado
    from app.tenants.modulos.submodulos import modulo_padre
    perfil = None
    if usuario.perfil_hospital_id:
        perfil = await db.scalar(select(PerfilHospital).where(
            PerfilHospital.id == usuario.perfil_hospital_id,
            PerfilHospital.tenant_id == hospital.id, PerfilHospital.is_active.is_(True)))
        if not perfil or perfil.role != usuario.role:
            raise HTTPException(403, "El perfil hospitalario está inactivo o no corresponde al rol")
    elif usuario.role != "administrador":
        raise HTTPException(403, "Asigne un perfil hospitalario a esta cuenta desde Admin > Usuarios")
    empleado = None
    if usuario.empleado_id:
        empleado = await db.scalar(select(Empleado).where(Empleado.id == usuario.empleado_id,
            Empleado.tenant_id == hospital.id, Empleado.is_active.is_(True)))
        if not empleado:
            raise HTTPException(403, "El empleado vinculado está inactivo o pertenece a otro hospital")
    if usuario.role == "medico" and not empleado:
        raise HTTPException(403, "Vincule la cuenta médica a un empleado del hospital")
    permisos = set(perfil.modulos) if perfil else set(habilitados)
    if usuario.role == "medico":
        permisos &= MEDICO_MODULOS
    permisos = sorted(c for c in permisos if modulo_padre(c) in habilitados)
    return {"sub": str(usuario.id), "name": usuario.name, "email": usuario.email,
        "role": usuario.role, "panel": usuario.panel, "tenant_id": str(hospital.id),
        "active_modules": permisos, "perfil_hospital_id": str(perfil.id) if perfil else None,
        "empleado_id": str(empleado.id) if empleado else None}

async def validar_perfil(db, tid, perfil_id, role, empleado_id, panel):
    if panel != "app":
        if perfil_id:
            raise HTTPException(400, "El perfil hospitalario solo corresponde al panel hospitalario")
        return
    if not perfil_id:
        if role != "administrador":
            raise HTTPException(400, "Seleccione un perfil hospitalario para este usuario")
        return
    perfil = await db.scalar(select(PerfilHospital).where(PerfilHospital.id == perfil_id,
        PerfilHospital.is_active.is_(True)))
    if not perfil or (tid and perfil.tenant_id != tid) or perfil.role != role:
        raise HTTPException(400, "Seleccione un perfil activo del hospital que corresponda al rol")
    if role == "medico":
        from app.sigarh.rrhh.models import Empleado
        from app.sigarh.mantenimiento.models import Profesion
        empleado = await db.get(Empleado, empleado_id) if empleado_id else None
        profesion = await db.get(Profesion, empleado.profesion_id) if empleado and empleado.profesion_id else None
        if not empleado or not profesion or profesion.codigo != "MED":
            raise HTTPException(400, "La cuenta médica debe vincularse a un empleado con profesión Médico Cirujano")

async def verificar_ambito_medico(request, user):
    """Impide abrir citas/agendas ajenas, incluso con un UUID conocido."""
    if user.get("role") != "medico":
        return
    from app.core.tenant_db import get_tenant_by_id, get_tenant_sessionmaker
    from app.hospital.consulta_externa.models import Cita, ProgramacionMedica
    tid = uuid.UUID(user["tenant_id"])
    empleado_id = uuid.UUID(user["empleado_id"])
    hospital = await get_tenant_by_id(tid)
    async with get_tenant_sessionmaker(hospital.database_name)() as db:
        cid = request.path_params.get("cita_id")
        pid = request.path_params.get("prog_id") or request.path_params.get("programacion_id")
        try:
            if cid:
                cita = await db.scalar(select(Cita).where(Cita.id == uuid.UUID(str(cid)), Cita.tenant_id == tid))
                pid = cita.programacion_medica_id if cita else None
                if not pid:
                    raise HTTPException(404, "Cita no encontrada")
            if pid:
                prog = await db.scalar(select(ProgramacionMedica).where(ProgramacionMedica.id == uuid.UUID(str(pid)),
                    ProgramacionMedica.tenant_id == tid, ProgramacionMedica.medico_id == empleado_id))
                if not prog:
                    raise HTTPException(404, "Programación no encontrada")
        except ValueError:
            raise HTTPException(422, "Identificador inválido")
