import json
import uuid
from datetime import date

import bcrypt
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import select, func, or_, text, delete as sa_delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.core.database import Base
from app.admin.auditoria.models import AuditLog
from app.sigarh.mantenimiento import models as m, schemas as s
from app.sigarh.mantenimiento.security import lista, es_admin_erp

REGISTROS = {
    "departamentos": (m.Departamento, s.DepartamentoCreate, s.DepartamentoResponse),
    "servicios": (m.Servicio, s.ServicioCreate, s.ServicioResponse),
    "dependencias": (m.Dependencia, s.DependenciaCreate, s.DependenciaResponse),
    "tipos-trabajador": (
        m.TipoTrabajador,
        s.TipoTrabajadorCreate,
        s.TipoTrabajadorResponse,
    ),
    "tipos-guardia": (m.TipoGuardia, s.TipoGuardiaCreate, s.TipoGuardiaResponse),
    "niveles-remunerativos": (
        m.NivelRemunerativo,
        s.NivelRemunerativoCreate,
        s.NivelRemunerativoResponse,
    ),
    "horarios-guardia": (
        m.HorarioGuardia,
        s.HorarioGuardiaCreate,
        s.HorarioGuardiaResponse,
    ),
    "grupos-ocupacionales": (
        m.GrupoOcupacional,
        s.GrupoOcupacionalCreate,
        s.GrupoOcupacionalResponse,
    ),
    "profesiones": (m.Profesion, s.ProfesionCreate, s.ProfesionResponse),
    "tipos-actividad": (
        m.TipoActividad,
        s.TipoActividadCreate,
        s.TipoActividadResponse,
    ),
    "actividades": (m.Actividad, s.ActividadCreate, s.ActividadResponse),
    "guardias-valorizadas": (
        m.GuardiaValorizada,
        s.GuardiaValorizadaCreate,
        s.GuardiaValorizadaResponse,
    ),
    "roles-sistema": (m.RolSistema, s.RolSistemaCreate, s.RolSistemaResponse),
    "perfiles-usuario": (
        m.PerfilUsuario,
        s.PerfilUsuarioCreate,
        s.PerfilUsuarioResponse,
    ),
    "usuarios": (m.UsuarioSigarh, s.UsuarioSigarhCreate, s.UsuarioSigarhResponse),
}
SEGURIDAD = {"usuarios", "perfiles-usuario", "roles-sistema"}
JSON_FIELDS = {
    "modulos_permitidos",
    "grupos_ocupacionales_permitidos",
    "permisos_accion",
    "modulos_acceso",
}
RELACIONES = {
    m.Servicio: ("departamento", "piso"),
    m.Dependencia: ("departamento", "servicio"),
    m.HorarioGuardia: ("tipo_guardia",),
    m.GuardiaValorizada: ("tipo_guardia", "grupo_ocupacional", "nivel_remunerativo"),
}


def serializar(item):
    data = {
        c.name: getattr(item, c.name)
        for c in item.__table__.columns
        if c.name not in {"password", "session_version"}
    }
    for field in JSON_FIELDS & data.keys():
        data[field] = lista(data[field])
    for rel in RELACIONES.get(type(item), ()):
        target = getattr(item, rel)
        data[f"{rel}_nombre"] = target.nombre if target else None
    return data


def snapshot(item):
    data = {
        c.name: getattr(item, c.name)
        for c in item.__table__.columns
        if c.name not in {"password", "session_version"}
    }
    return json.loads(json.dumps(data, default=str))


async def obtener(db, modelo, id, tenant_id, bloquear=False):
    query = select(modelo).where(modelo.id == id, modelo.tenant_id == tenant_id)
    for relation in RELACIONES.get(modelo, ()):
        query = query.options(selectinload(getattr(modelo, relation)))
    if bloquear:
        query = query.with_for_update()
    return await db.scalar(query.execution_options(populate_existing=True))


async def listar(db, modelo, tenant_id, offset=0, limit=200, q=None, is_active=None):
    query = select(modelo).where(modelo.tenant_id == tenant_id)
    for relation in RELACIONES.get(modelo, ()):
        query = query.options(selectinload(getattr(modelo, relation)))
    if q:
        fields = [
            getattr(modelo, name)
            for name in ("nombre", "codigo", "username", "email")
            if hasattr(modelo, name)
        ]
        if fields:
            query = query.where(or_(*(field.ilike(f"%{q}%") for field in fields)))
    if is_active is not None:
        query = query.where(modelo.is_active == is_active)
    return (
        await db.scalars(
            query.order_by(modelo.created_at.desc(), modelo.id)
            .offset(offset)
            .limit(limit)
        )
    ).all()


async def listar_servicios(db, tenant_id):
    # Consumidor existente en Movimientos; conserva su contrato.
    return (
        await db.scalars(
            select(m.Servicio)
            .where(m.Servicio.tenant_id == tenant_id)
            .options(
                selectinload(m.Servicio.departamento),
                selectinload(m.Servicio.piso),
            )
            .order_by(m.Servicio.nombre)
        )
    ).all()


async def estructura_asistencial(db, tenant_id):
    from app.sigarh.rrhh.models import Especialidad

    units = (
        await db.scalars(
            select(m.UPSS)
            .where(m.UPSS.tenant_id == tenant_id)
            .order_by(m.UPSS.tipo_atencion, m.UPSS.nombre)
        )
    ).all()
    services = (
        await db.scalars(
            select(m.Servicio)
            .where(m.Servicio.tenant_id == tenant_id)
            .order_by(m.Servicio.nombre)
        )
    ).all()
    links = (
        await db.execute(
            select(m.ServicioUPSS.servicio_id, m.ServicioUPSS.upss_id)
            .join(m.Servicio, m.Servicio.id == m.ServicioUPSS.servicio_id)
            .where(m.Servicio.tenant_id == tenant_id)
        )
    ).all()
    specialty_links = (
        await db.execute(
            select(
                m.ServicioEspecialidad.servicio_id,
                Especialidad.id,
                Especialidad.nombre,
                Especialidad.is_active,
            )
            .join(m.Servicio, m.Servicio.id == m.ServicioEspecialidad.servicio_id)
            .join(
                Especialidad, Especialidad.id == m.ServicioEspecialidad.especialidad_id
            )
            .where(m.Servicio.tenant_id == tenant_id)
        )
    ).all()
    units_by_service = {}
    for service_id, unit_id in links:
        units_by_service.setdefault(service_id, []).append(unit_id)
    specialties_by_service = {}
    for service_id, specialty_id, name, active in specialty_links:
        specialties_by_service.setdefault(service_id, []).append(
            {
                "id": specialty_id,
                "nombre": name,
                "is_active": active,
            }
        )
    rows = [
        {
            **serializar(service),
            "upss_ids": units_by_service.get(service.id, []),
            "especialidades": specialties_by_service.get(service.id, []),
        }
        for service in services
    ]
    return {
        "upss": [
            {
                **serializar(unit),
                "servicios": [
                    service for service in rows if unit.id in service["upss_ids"]
                ],
            }
            for unit in units
        ],
        "servicios_sin_upss": [service for service in rows if not service["upss_ids"]],
    }


async def cambiar_estado_upss(db, tenant_id, id, active):
    unit = await db.scalar(
        select(m.UPSS).where(m.UPSS.id == id, m.UPSS.tenant_id == tenant_id)
    )
    if not unit:
        raise HTTPException(404, "UPSS no encontrada")
    unit.is_active = active
    await db.commit()
    return serializar(unit)


async def configurar_servicio(db, tenant_id, id, data):
    from app.sigarh.rrhh.models import Especialidad

    service = await referencia(db, m.Servicio, id, tenant_id, "servicio", activo=False)
    units = [
        await referencia(db, m.UPSS, value, tenant_id, "UPSS")
        for value in data.upss_ids
    ]
    specialties = [
        await referencia(db, Especialidad, value, tenant_id, "especialidad")
        for value in data.especialidad_ids
    ]
    await db.execute(sa_delete(m.ServicioUPSS).where(m.ServicioUPSS.servicio_id == id))
    await db.execute(
        sa_delete(m.ServicioEspecialidad).where(
            m.ServicioEspecialidad.servicio_id == id
        )
    )
    db.add_all([m.ServicioUPSS(servicio_id=id, upss_id=unit.id) for unit in units])
    db.add_all(
        [
            m.ServicioEspecialidad(servicio_id=id, especialidad_id=specialty.id)
            for specialty in specialties
        ]
    )
    await db.commit()
    return {"ok": True, "servicio_id": service.id}


async def asegurar_estructura_asistencial(db, tenant_id, hospital_level):
    """Siembra UPSS, servicios y relaciones para un hospital recién creado."""
    from app.sigarh.mantenimiento.upss_catalogo import (
        UPSS,
        SERVICIOS,
        ESPECIALIDADES_SERVICIO,
        RECOMENDADAS,
        FUENTE,
        NORMA,
        FUENTE_URL,
        stable_id,
    )
    from app.sigarh.rrhh.models import Especialidad

    if await db.scalar(select(m.UPSS.id).where(m.UPSS.tenant_id == tenant_id).limit(1)):
        return
    recommended = RECOMENDADAS.get(hospital_level, set())
    for code, name, care_type in UPSS:
        db.add(
            m.UPSS(
                id=stable_id("upss", tenant_id, code),
                tenant_id=tenant_id,
                codigo=code,
                nombre=name,
                tipo_atencion=care_type,
                fuente=FUENTE,
                norma=NORMA,
                fuente_url=FUENTE_URL,
                recomendada_nivel=code in recommended,
                is_active=code in recommended,
            )
        )
    for code, name, unit_codes in SERVICIOS:
        db.add(
            m.Servicio(
                id=stable_id("service", tenant_id, code),
                tenant_id=tenant_id,
                codigo=code,
                nombre=name,
                descripcion="Servicio asistencial base vinculado a UPSS",
                tiempo_atencion_min=15,
                es_base=True,
                is_active=any(value in recommended for value in unit_codes),
            )
        )
    await db.flush()
    specialties = {
        (e.nombre, e.tipo): e
        for e in (
            await db.scalars(
                select(Especialidad).where(Especialidad.tenant_id == tenant_id)
            )
        ).all()
    }
    for code, _, unit_codes in SERVICIOS:
        service_id = stable_id("service", tenant_id, code)
        db.add_all(
            [
                m.ServicioUPSS(
                    servicio_id=service_id, upss_id=stable_id("upss", tenant_id, value)
                )
                for value in unit_codes
            ]
        )
        db.add_all(
            [
                m.ServicioEspecialidad(
                    servicio_id=service_id,
                    especialidad_id=specialties[(name, "especialidad")].id,
                )
                for name in ESPECIALIDADES_SERVICIO.get(code, [])
                if (name, "especialidad") in specialties
            ]
        )
    await db.flush()


async def referencia(db, modelo, id, tenant_id, campo, activo=True):
    if id is None:
        return None
    query = select(modelo).where(modelo.id == id, modelo.tenant_id == tenant_id)
    if activo and hasattr(modelo, "is_active"):
        query = query.where(modelo.is_active.is_(True))
    item = await db.scalar(query)
    if not item:
        raise HTTPException(422, f"{campo}: no existe en este hospital o está inactivo")
    return item


async def modulos_habilitados(db, tenant_id):
    # TenantModule/Module son catálogos centrales (contratación de módulos
    # por hospital); nunca viven en la BD física del tenant, así que esta
    # consulta va siempre contra la BD central, sin importar qué BD trae la
    # sesión `db` inyectada (física para /sigarh/*, ver core/database.py).
    from app.tenants.hospitales.models import TenantModule
    from app.tenants.modulos.models import Module
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as central:
        return (await central.scalars(select(Module).join(TenantModule, TenantModule.module_code == Module.code).where(
            TenantModule.tenant_id == tenant_id, TenantModule.is_active.is_(True), Module.is_active.is_(True),
            Module.code.startswith("sigarh_"),
        ).order_by(Module.name))).all()


async def usado(db, modelo, id):
    """Comprueba referencias antes de modificar o borrar; no permite cascadas silenciosas."""
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if any(
                fk.target_fullname == f"{modelo.__tablename__}.id"
                for fk in column.foreign_keys
            ):
                if await db.scalar(select(column).where(column == id).limit(1)):
                    return True
    return False


async def validar_relaciones(db, modelo, tenant_id, values):
    from app.sigarh.rrhh.models import Empleado
    from app.sigarh.infraestructura.models import Catalogo
    from app.sigarh.infraestructura_hosp.models import Piso

    targets = {
        "departamento_id": m.Departamento,
        "servicio_id": m.Servicio,
        "piso_id": Piso,
        "tipo_guardia_id": m.TipoGuardia,
        "grupo_ocupacional_id": m.GrupoOcupacional,
        "profesion_id": m.Profesion,
        "nivel_remunerativo_id": m.NivelRemunerativo,
        "tipo_actividad_id": m.TipoActividad,
        "rol_sistema_id": m.RolSistema,
        "perfil_id": m.PerfilUsuario,
        "empleado_id": Empleado,
        "tipo_grupo_id": Catalogo,
    }
    refs = {}
    for field, target in targets.items():
        if field in values:
            refs[field] = await referencia(db, target, values[field], tenant_id, field)
    if (
        refs.get("tipo_grupo_id")
        and refs["tipo_grupo_id"].categoria != "tipos_grupo_ocupacional"
    ):
        raise HTTPException(
            422, "El tipo de grupo debe pertenecer a tipos_grupo_ocupacional"
        )
    if modelo is m.Dependencia and refs.get("servicio_id"):
        if (
            not values.get("departamento_id")
            or refs["servicio_id"].departamento_id != values["departamento_id"]
        ):
            raise HTTPException(
                422, "El servicio no pertenece al departamento seleccionado"
            )
    if modelo is m.RolSistema:
        from app.tenants.modulos.submodulos import modulo_padre
        habilitados = {module.code for module in await modulos_habilitados(db, tenant_id)}
        elegidos = set(values["modulos_permitidos"])
        requerido = values.get("modulo_requerido")
        # Un código puede venir con submódulo (ej. "sigarh_recursos_humanos.empleados"):
        # basta con que el módulo padre esté habilitado para el hospital.
        no_habilitados = {c for c in elegidos if modulo_padre(c) not in habilitados}
        if no_habilitados or (requerido and requerido not in habilitados):
            raise HTTPException(422, "Los módulos deben existir y estar habilitados para SIGARH en este hospital")
        if requerido and requerido not in elegidos:
            raise HTTPException(
                422, "El módulo requerido debe estar incluido entre los permitidos"
            )
        if (
            values["permisos_accion"]
            and not any(modulo_padre(c) == "sigarh_mantenimiento" for c in elegidos)
            and (
                set(values["permisos_accion"])
                & {"administrar_seguridad", "administrar_mantenimiento"}
            )
        ):
            raise HTTPException(422, "Administrar requiere el módulo Mantenimiento")
        if (
            "aprobar_roles_turno" in values["permisos_accion"]
            and not any(modulo_padre(c) == "sigarh_roles_pendientes" for c in elegidos)
        ):
            raise HTTPException(
                422, "Aprobar turnos requiere el módulo Roles Pendientes"
            )
        for group in values["grupos_ocupacionales_permitidos"]:
            await referencia(
                db, m.GrupoOcupacional, group, tenant_id, "grupo ocupacional permitido"
            )
    if modelo is m.PerfilUsuario:
        from app.tenants.modulos.submodulos import modulo_padre, permiso_incluye
        rol = refs["rol_sistema_id"]
        habilitados = {module.code for module in await modulos_habilitados(db, tenant_id)}
        if rol.panel != "sigarh" or (rol.modulo_requerido and rol.modulo_requerido not in habilitados):
            raise HTTPException(422, "El rol no es válido para SIGARH o su módulo requerido está deshabilitado")
        # Un código de modulos_acceso puede venir con submódulo (ej.
        # "sigarh_recursos_humanos.empleados"): es válido si el rol lo cubre
        # (código exacto o su módulo padre) y ese módulo padre está habilitado
        # para el hospital. Antes esto era una resta de sets por código exacto,
        # que rechazaba cualquier submódulo fino aunque el rol lo permitiera.
        concedidos_rol = set(lista(rol.modulos_permitidos))
        no_validos = {
            c for c in values["modulos_acceso"]
            if not permiso_incluye(concedidos_rol, c) or modulo_padre(c) not in habilitados
        }
        if no_validos:
            raise HTTPException(422, "Los módulos deben estar permitidos por el rol y habilitados en el hospital")
    if modelo is m.UsuarioSigarh:
        perfil = refs["perfil_id"]
        rol = await referencia(
            db, m.RolSistema, perfil.rol_sistema_id, tenant_id, "rol del perfil"
        )
        if not rol or rol.panel != "sigarh":
            raise HTTPException(422, "El perfil requiere un rol SIGARH activo")
        grupos = set(lista(rol.grupos_ocupacionales_permitidos))
        empleado = refs.get("empleado_id")
        if grupos and (
            not empleado or str(empleado.grupo_ocupacional_id) not in grupos
        ):
            raise HTTPException(
                422, "Seleccione un empleado del grupo ocupacional permitido por el rol"
            )


async def validar_unicidad(db, modelo, tenant_id, values, item=None):
    for field in ("nombre", "codigo", "username", "email"):
        value = values.get(field)
        if not value or not hasattr(modelo, field):
            continue
        query = select(modelo.id).where(
            func.lower(func.trim(getattr(modelo, field))) == value.strip().lower()
        )
        if modelo is not m.UsuarioSigarh:
            query = query.where(modelo.tenant_id == tenant_id)
        if item:
            query = query.where(modelo.id != item.id)
        if await db.scalar(query.limit(1)):
            raise HTTPException(409, f"Ya existe un registro con ese {field}")
    if modelo is m.UsuarioSigarh:
        # El login comparte correo/usuario; tampoco se permiten colisiones entre columnas.
        query = select(m.UsuarioSigarh.id).where(
            or_(
                func.lower(m.UsuarioSigarh.email) == values["username"],
                func.lower(m.UsuarioSigarh.username) == values["email"],
            )
        )
        if item:
            query = query.where(m.UsuarioSigarh.id != item.id)
        if await db.scalar(query.limit(1)):
            raise HTTPException(409, "El identificador de acceso ya está ocupado")
    if modelo is m.GuardiaValorizada and values["is_active"]:
        query = select(modelo.id).where(
            modelo.tenant_id == tenant_id,
            modelo.is_active.is_(True),
            modelo.tipo_guardia_id == values["tipo_guardia_id"],
            modelo.grupo_ocupacional_id == values["grupo_ocupacional_id"],
            modelo.nivel_remunerativo_id == values["nivel_remunerativo_id"],
            or_(
                modelo.vigencia_hasta.is_(None),
                modelo.vigencia_hasta >= values["vigencia_desde"],
            ),
        )
        if values["vigencia_hasta"]:
            query = query.where(
                or_(
                    modelo.vigencia_desde.is_(None),
                    modelo.vigencia_desde <= values["vigencia_hasta"],
                )
            )
        if item:
            query = query.where(modelo.id != item.id)
        if await db.scalar(query.limit(1)):
            raise HTTPException(
                409, "Existe una tarifa para esa combinación con vigencia superpuesta"
            )


async def bloquear_escritura(db, tenant_id):
    # Serializa validación + escritura incluso entre procesos de la API.
    await db.execute(
        text("SELECT pg_advisory_xact_lock(hashtextextended(:clave, 0))"),
        {"clave": "mantenimiento-identidades"},
    )


async def auditar(user, tenant_id, item, action, before=None, ip=None):
    # AuditLog es una tabla central (la revisa Admin ERP en Auditoría), nunca
    # vive en la BD física del tenant: se escribe en su propia sesión central,
    # independiente de `db` (física para /sigarh/*, ver core/database.py).
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as central:
        central.add(AuditLog(user_id=uuid.UUID(user["sub"]), user_name=user.get("name"),
            tenant_id=tenant_id, action=action, model=type(item).__name__, model_id=str(item.id),
            description=f"Mantenimiento: {action}", old_values=before,
            new_values=None if action == "deleted" else snapshot(item), ip_address=ip))
        await central.commit()


async def guardar(db, recurso, tenant_id, data, user, id=None, ip=None):
    modelo, schema, _ = REGISTROS[recurso]
    await bloquear_escritura(db, tenant_id)
    item = await obtener(db, modelo, id, tenant_id, bloquear=True) if id else None
    if id and not item:
        raise HTTPException(404, "Registro no encontrado")
    before = snapshot(item) if item else None
    supplied = data.model_dump(exclude_unset=True)
    if modelo is m.Profesion and item and item.es_base:
        protected = set(supplied) - {"is_active", "descripcion"}
        if any(supplied[key] != getattr(item, key) for key in protected):
            raise HTTPException(409, "Las profesiones base conservan su denominacion y clasificacion; puedes desactivarlas.")
    values = (
        {key: getattr(item, key) for key in schema.model_fields if hasattr(item, key)}
        if item
        else {}
    )
    for key in JSON_FIELDS & values.keys():
        values[key] = lista(values[key])
    if modelo is m.UsuarioSigarh and item:
        # El hash nunca pasa por el contrato de una contraseña nueva.
        values["password"] = "placeholder-seguro-interno"
        if not supplied.get("password"):
            supplied.pop("password", None)
    if (
        modelo is m.HorarioGuardia
        and item
        and {"hora_inicio", "hora_fin"} & supplied.keys()
    ):
        values["horas_totales"] = None
        values["duracion_minutos"] = None
    values.update(supplied)
    try:
        values = schema.model_validate(values).model_dump()
    except ValidationError as exc:
        raise HTTPException(
            422,
            " · ".join(
                f"{'.'.join(map(str, e['loc']))}: {e['msg']}"
                for e in exc.errors(include_input=False)
            ),
        )
    if modelo is m.UsuarioSigarh and item and "password" not in supplied:
        values.pop("password", None)
    changed = {
        key
        for key, value in values.items()
        if not item
        or (lista(getattr(item, key)) if key in JSON_FIELDS else getattr(item, key))
        != value
    }
    if item and not es_admin_erp(user):
        own = (modelo is m.UsuarioSigarh and str(item.id) == user.get("sub")) or (
            modelo is m.PerfilUsuario and str(item.id) == user.get("perfil_id")
        )
        if modelo is m.RolSistema and user.get("perfil_id"):
            perfil = await db.scalar(
                select(m.PerfilUsuario).where(
                    m.PerfilUsuario.id == uuid.UUID(user["perfil_id"])
                )
            )
            own = bool(perfil and perfil.rol_sistema_id == item.id)
        critical = {
            "is_active",
            "perfil_id",
            "rol_sistema_id",
            "modulos_acceso",
            "permisos_accion",
            "modulos_permitidos",
            "alcance_global",
            "empleado_id",
        }
        if own and changed & critical:
            raise HTTPException(
                409,
                "Otra persona administradora debe modificar sus propias autorizaciones",
            )
    # Desactivar seguridad siempre debe ser posible aun con referencias antiguas inválidas.
    solo_baja = item and supplied == {"is_active": False}
    if not solo_baja:
        await validar_relaciones(db, modelo, tenant_id, values)
        await validar_unicidad(db, modelo, tenant_id, values, item)
    if (
        item
        and recurso not in SEGURIDAD
        and changed - {"descripcion"}
        and await usado(db, modelo, item.id)
    ):
        raise HTTPException(
            409,
            "El catálogo ya está utilizado. Conserve el registro y cree una nueva versión",
        )
    if (
        item
        and modelo is m.GuardiaValorizada
        and item.vigencia_desde
        and item.vigencia_desde <= date.today()
    ):
        if changed - {"vigencia_hasta"}:
            raise HTTPException(
                409,
                "La tarifa ya inició su vigencia; cierre su período y cree una nueva tarifa",
            )
        if values.get("vigencia_hasta") and values["vigencia_hasta"] < date.today():
            raise HTTPException(409, "No se puede cerrar una tarifa retroactivamente")
    if item is None:
        item = modelo(id=uuid.uuid4(), tenant_id=tenant_id)
        db.add(item)
    if "password" in values:
        values["password"] = bcrypt.hashpw(
            values["password"].encode(), bcrypt.gensalt()
        ).decode()
    for key, value in values.items():
        setattr(
            item, key, json.dumps(value, default=str) if key in JSON_FIELDS else value
        )
    if (
        modelo is m.UsuarioSigarh
        and id
        and changed
        & {"password", "perfil_id", "empleado_id", "is_active", "username", "email"}
    ):
        item.session_version += 1
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "Los datos duplican un registro o tienen una relación inválida")
    await auditar(user, tenant_id, item, "updated" if id else "created", before, ip)
    return serializar(await obtener(db, modelo, item.id, tenant_id))


async def eliminar(db, recurso, tenant_id, id, user, ip=None):
    modelo = REGISTROS[recurso][0]
    await bloquear_escritura(db, tenant_id)
    item = await obtener(db, modelo, id, tenant_id, bloquear=True)
    if not item:
        raise HTTPException(404, "Registro no encontrado")
    if modelo is m.Profesion and item.es_base:
        raise HTTPException(409, "Las profesiones base se desactivan; no se eliminan.")
    if recurso in SEGURIDAD:
        raise HTTPException(
            409,
            "Las cuentas y permisos se desactivan; no se eliminan para conservar auditoría",
        )
    if await usado(db, modelo, id):
        raise HTTPException(
            409, "No puede eliminar un catálogo utilizado por otros registros"
        )
    if (
        modelo is m.GuardiaValorizada
        and item.vigencia_desde
        and item.vigencia_desde <= date.today()
    ):
        raise HTTPException(409, "Una tarifa con vigencia iniciada debe conservarse")
    before = snapshot(item)
    await db.delete(item)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "El catálogo está siendo utilizado y no puede eliminarse")
    await auditar(user, tenant_id, item, "deleted", before, ip)
    return {"ok": True}


async def resolver_tarifa(db, tenant_id, tipo_guardia_id, grupo_id, nivel_id, fecha):
    """Prioridad explícita: grupo+nivel, grupo, nivel, general; nunca usa Float."""
    rows = (
        await db.scalars(
            select(m.GuardiaValorizada).where(
                m.GuardiaValorizada.tenant_id == tenant_id,
                m.GuardiaValorizada.is_active.is_(True),
                m.GuardiaValorizada.tipo_guardia_id == tipo_guardia_id,
                m.GuardiaValorizada.vigencia_desde <= fecha,
                or_(
                    m.GuardiaValorizada.vigencia_hasta.is_(None),
                    m.GuardiaValorizada.vigencia_hasta >= fecha,
                ),
                or_(
                    m.GuardiaValorizada.grupo_ocupacional_id.is_(None),
                    m.GuardiaValorizada.grupo_ocupacional_id == grupo_id,
                ),
                or_(
                    m.GuardiaValorizada.nivel_remunerativo_id.is_(None),
                    m.GuardiaValorizada.nivel_remunerativo_id == nivel_id,
                ),
            )
        )
    ).all()
    ranked = sorted(
        rows,
        key=lambda r: 2 * bool(r.grupo_ocupacional_id) + bool(r.nivel_remunerativo_id),
        reverse=True,
    )
    if not ranked:
        raise HTTPException(404, "No existe tarifa vigente")
    score = lambda r: 2 * bool(r.grupo_ocupacional_id) + bool(r.nivel_remunerativo_id)
    if len(ranked) > 1 and score(ranked[0]) == score(ranked[1]):
        raise HTTPException(409, "Hay tarifas ambiguas; revise las vigencias")
    return ranked[0]
