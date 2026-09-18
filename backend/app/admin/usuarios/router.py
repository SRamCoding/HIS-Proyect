import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.core.concurrency import gather_limitado
from app.admin.usuarios.schemas import UserListItem, UserCreate, UserUpdate
from app.admin.usuarios.service import (
    get_all_users, get_users_by_tenant, create_user,
    update_user, toggle_user, delete_user, obtener_cuenta,
)

logger = logging.getLogger(__name__)

router = APIRouter()


async def hospital_perfiles(tenant_id):
    from app.core.tenant_db import get_tenant_by_id
    hospital = await get_tenant_by_id(tenant_id)
    if not hospital or not hospital.is_active or not hospital.database_name:
        raise HTTPException(400, "Seleccione un hospital activo")
    return hospital


@router.get("/usuarios/perfiles-hospital/catalogo")
async def catalogo_perfiles(tenant_id: uuid.UUID, db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user)):
    from app.tenants.hospitales.models import TenantModule
    from app.tenants.modulos.models import Module
    from app.auth.hospital_access import RECURSOS
    await hospital_perfiles(tenant_id)
    modulos = (await db.scalars(select(Module).join(TenantModule, Module.code == TenantModule.module_code).where(
        TenantModule.tenant_id == tenant_id, TenantModule.is_active.is_(True), Module.is_active.is_(True),
        Module.category != "sigarh"))).all()
    codes = {m.code for m in modulos}
    return [{"code": m.code, "label": m.name} for m in modulos] + [r for r in RECURSOS if r["code"].split(".")[0] in codes]


@router.get("/usuarios/perfiles-hospital")
async def listar_perfiles_hospital(tenant_id: uuid.UUID, current_user: dict = Depends(get_admin_user)):
    from app.auth.models import PerfilHospital
    from app.core.tenant_db import get_tenant_sessionmaker
    hospital = await hospital_perfiles(tenant_id)
    async with get_tenant_sessionmaker(hospital.database_name)() as tdb:
        perfiles = (await tdb.scalars(select(PerfilHospital).where(PerfilHospital.tenant_id == tenant_id).order_by(PerfilHospital.nombre))).all()
        return [{"id": str(p.id), "nombre": p.nombre, "role": p.role, "modulos": p.modulos, "is_active": p.is_active} for p in perfiles]


from app.admin.usuarios.schemas import PerfilHospitalInput


@router.post("/usuarios/perfiles-hospital", status_code=201)
@router.put("/usuarios/perfiles-hospital/{perfil_id}")
async def guardar_perfil_hospital(data: PerfilHospitalInput, tenant_id: uuid.UUID,
    perfil_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user)):
    from app.auth.models import PerfilHospital, User
    from app.core.tenant_db import get_tenant_sessionmaker
    from app.admin.roles.models import SystemRole
    from app.admin.auditoria.service import create_audit_log
    hospital = await hospital_perfiles(tenant_id)
    rol = await db.scalar(select(SystemRole).where(SystemRole.name == data.role, SystemRole.panel == "app", SystemRole.is_active.is_(True)))
    if not rol:
        raise HTTPException(400, "Seleccione un rol hospitalario activo")
    from app.tenants.modulos.submodulos import permiso_incluye
    if isinstance(rol.allowed_modules, list) and any(not permiso_incluye(rol.allowed_modules, c) for c in data.modulos):
        raise HTTPException(400, "El perfil no puede exceder los módulos permitidos por el rol del sistema")
    catalogo = await catalogo_perfiles(tenant_id, db, current_user)
    if not set(data.modulos) <= {m["code"] for m in catalogo}:
        raise HTTPException(400, "El perfil contiene módulos que no están habilitados para este hospital")
    async with get_tenant_sessionmaker(hospital.database_name)() as tdb:
        from sqlalchemy import func
        duplicado = select(PerfilHospital.id).where(PerfilHospital.tenant_id == tenant_id,
            func.lower(func.trim(PerfilHospital.nombre)) == data.nombre.strip().lower())
        if perfil_id:
            duplicado = duplicado.where(PerfilHospital.id != perfil_id)
        if await tdb.scalar(duplicado):
            raise HTTPException(409, "Ya existe un perfil hospitalario con ese nombre")
        perfil = await tdb.scalar(select(PerfilHospital).where(PerfilHospital.id == perfil_id,
            PerfilHospital.tenant_id == tenant_id).with_for_update()) if perfil_id else None
        if perfil_id and not perfil:
            raise HTTPException(404, "Perfil no encontrado")
        if perfil and perfil.role != data.role and await tdb.scalar(select(User.id).where(User.perfil_hospital_id == perfil.id).limit(1)):
            raise HTTPException(400, "No cambie el rol de un perfil asignado; cree otro perfil")
        if not perfil:
            perfil = PerfilHospital(tenant_id=tenant_id)
            tdb.add(perfil)
        anteriores = {"nombre": perfil.nombre, "role": perfil.role, "modulos": perfil.modulos, "is_active": perfil.is_active} if perfil.id else None
        perfil.nombre, perfil.role, perfil.modulos, perfil.is_active = data.nombre, data.role, sorted(set(data.modulos)), data.is_active
        await tdb.commit()
        await tdb.refresh(perfil)
        resultado = {"id": str(perfil.id), **data.model_dump()}
    await create_audit_log(db, user_id=current_user["sub"], user_name=current_user.get("name"),
        tenant_id=hospital.id, tenant_name=hospital.name, action="hospital_profile_updated" if perfil_id else "hospital_profile_created",
        model="PerfilHospital", model_id=str(perfil.id), description=data.nombre, old_values=anteriores, new_values=data.model_dump())
    return resultado


@router.get("/usuarios/empleados-disponibles")
async def empleados_disponibles(tenant_id: uuid.UUID, current_user: dict = Depends(get_admin_user)):
    from app.core.tenant_db import get_tenant_by_id, get_tenant_sessionmaker
    from app.sigarh.rrhh.models import Empleado
    hospital = await get_tenant_by_id(tenant_id)
    if not hospital or not hospital.is_active or not hospital.database_name:
        raise HTTPException(400, detail="Seleccione un hospital activo")
    async with get_tenant_sessionmaker(hospital.database_name)() as db:
        empleados = (await db.scalars(select(Empleado).where(Empleado.tenant_id == tenant_id, Empleado.is_active == True).order_by(Empleado.apellido_paterno))).all()
        return [{"id": str(e.id), "nombre": e.nombre_completo} for e in empleados]


@router.get("/usuarios", response_model=list[UserListItem], summary="Listar todos los usuarios")
async def listar_usuarios(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_all_users(db)


async def _roles_por_lote(session, perfil_ids: set) -> dict:
    """Nombre de rol para varias cuentas SIGARH en UNA sola tanda de
    consultas (2, sin importar cuantos perfiles sean), en vez de dos
    consultas POR CADA cuenta (_rol_nombre_sigarh de antes). Con muchas
    cuentas SIGARH en un hospital, eso significaba cientos de consultas
    solo para armar el listado."""
    if not perfil_ids:
        return {}
    from app.sigarh.mantenimiento.models import PerfilUsuario, RolSistema

    perfiles = (await session.scalars(
        select(PerfilUsuario).where(PerfilUsuario.id.in_(perfil_ids))
    )).all()
    rol_ids = {p.rol_sistema_id for p in perfiles if p.rol_sistema_id}
    roles = (await session.scalars(
        select(RolSistema).where(RolSistema.id.in_(rol_ids))
    )).all() if rol_ids else []
    nombre_por_rol = {r.id: r.nombre for r in roles}
    return {p.id: nombre_por_rol.get(p.rol_sistema_id, "SIGARH") for p in perfiles}


def _filtro_texto(*columnas, q: str | None):
    from sqlalchemy import or_
    if not q:
        return None
    termino = f"%{q.strip()}%"
    return or_(*[c.ilike(termino) for c in columnas])


async def _tenants_relevantes(db: AsyncSession, tenant_id: uuid.UUID | None) -> dict:
    from app.tenants.hospitales.models import Tenant
    tenants_query = select(Tenant).where(Tenant.id == tenant_id) if tenant_id else select(Tenant)
    return {str(t.id): t for t in (await db.scalars(tenants_query)).all()}


async def _reunir_todas_las_cuentas(
    db: AsyncSession, tenant_id: uuid.UUID | None, vista: str | None = None,
    q: str | None = None, is_active: bool | None = None, cap: int | None = None,
) -> tuple[list[dict], list[str]]:
    """Reune cuentas (central + cada hospital con base física) en una sola
    lista en memoria, con el rol SIGARH ya resuelto en lote. La usa el
    listado paginado (`/usuarios/con-hospital`) -- el resumen
    (`/usuarios/resumen`) ya NO pasa por aca: usa `_resumen_todas_las_
    cuentas`, que calcula sus agregados (total/activos/roles) con
    COUNT/SUM/DISTINCT en cada fuente, sin traer una sola cuenta.

    `q`/`is_active`/`vista` se empujan como WHERE a cada consulta (central y
    a cada base de hospital) en vez de filtrar en Python despues de traer
    todo -- antes CUALQUIER busqueda, filtro o vista traia el catalogo
    completo de cuentas igual, y no ahorraban nada del lado del servidor.
    Es importante que ESTOS MISMOS filtros (sobre todo `vista == "hospital"`,
    que debe excluir panel="portal" ademas de "admin") se apliquen ANTES de
    `cap`, no despues: si el filtro por panel se aplicara en Python sobre el
    resultado ya acotado, una base cuyas primeras `cap` filas (por fecha)
    fueran todas panel="portal" iba a devolver una pagina vacia o incompleta
    aunque existieran cuentas app/sigarh validas mas atras en esa misma base.

    `cap`, cuando se pasa (el listado paginado lo hace), acota con
    LIMIT/ORDER BY created_at cuantas filas se piden a CADA fuente. Alcanza
    con que cada fuente entregue sus propias top-`cap` mas recientes (ya
    filtradas por panel/busqueda/estado): en el peor caso, una pagina global
    completa viene de una sola fuente, y esa fuente ya la cubre con su
    propio top-`cap`. Con esto una base de un hospital con miles de cuentas
    ya no se descarga entera solo para mostrar una pagina de 50. No hay
    forma de paginar con un solo LIMIT/OFFSET de Postgres a traves de varias
    bases distintas sin un índice materializado aparte, que es un cambio más
    grande que esto; lo que se gana aqui es dejar de mover TODA la fila de
    cada cuenta cuando no hace falta.

    Si `vista == "admin"`, ni siquiera se intenta tocar ninguna base física
    de hospital: una cuenta panel="admin" SOLO puede vivir en la BD
    central (create_tenant nunca crea cuentas admin dentro de un hospital),
    así que recorrer cada hospital para esta vista era trabajo puro
    desperdiciado -- antes se hacía igual y el filtro por panel se aplicaba
    recién al final, sobre datos que nunca iban a servir."""
    from app.auth.models import User
    from app.sigarh.mantenimiento.models import UsuarioSigarh
    from app.core.tenant_db import get_tenant_sessionmaker
    from app.tenants.hospitales.models import Tenant

    central_query = (
        select(User, Tenant.name.label("tenant_name"))
        .outerjoin(Tenant, User.tenant_id == Tenant.id)
        .where(User.is_superadmin.is_(False))  # excluir la cuenta admin fundacional
    )
    if tenant_id:
        central_query = central_query.where(User.tenant_id == tenant_id)
    if vista == "admin":
        central_query = central_query.where(User.panel == "admin")
    elif vista == "hospital":
        # "hospital" = cuentas hospitalarias (app + sigarh), NUNCA admin NI
        # portal (User.panel admite "admin"/"app"/"portal", ver schemas.py::
        # PANELES). `!= "admin"` dejaba pasar "portal" igual.
        central_query = central_query.where(User.panel == "app")
    if is_active is not None:
        central_query = central_query.where(User.is_active == is_active)
    filtro = _filtro_texto(User.name, User.email, q=q)
    if filtro is not None:
        central_query = central_query.where(filtro)
    if cap:
        central_query = central_query.order_by(User.created_at.desc()).limit(cap)
    result = await db.execute(central_query)
    rows = result.all()
    items = [
        {
            "id": str(u.id),
            "name": u.name,
                    "perfil_hospital_id": str(u.perfil_hospital_id) if u.perfil_hospital_id else None,
                    "empleado_id": str(u.empleado_id) if u.empleado_id else None,
            "email": u.email,
            "role": u.role,
            "panel": u.panel,
            "is_active": u.is_active,
            "tenant_name": tenant_name or "—",
            "tenant_id": str(u.tenant_id) if u.tenant_id else None,
            "created_at": u.created_at.strftime("%d/%m/%Y"),
            "_created_at_raw": u.created_at,
            "account_type": "user",
        }
        for u, tenant_name in rows
    ]

    if vista == "admin":
        return items, []

    # Cuentas SIGARH que viven en la BD central (hospitales sin base física propia).
    sigarh_query = select(UsuarioSigarh)
    if tenant_id:
        sigarh_query = sigarh_query.where(UsuarioSigarh.tenant_id == tenant_id)
    if is_active is not None:
        sigarh_query = sigarh_query.where(UsuarioSigarh.is_active == is_active)
    filtro = _filtro_texto(UsuarioSigarh.username, UsuarioSigarh.email, q=q)
    if filtro is not None:
        sigarh_query = sigarh_query.where(filtro)
    if cap:
        sigarh_query = sigarh_query.order_by(UsuarioSigarh.created_at.desc()).limit(cap)
    sigarh_central = (await db.scalars(sigarh_query)).all()
    tenants_por_id = await _tenants_relevantes(db, tenant_id)
    sigarh_central_validos = [
        (u, tenants_por_id.get(str(u.tenant_id)))
        for u in sigarh_central
    ]
    sigarh_central_validos = [(u, t) for u, t in sigarh_central_validos if t and not t.database_name]
    roles_central = await _roles_por_lote(db, {u.perfil_id for u, _ in sigarh_central_validos if u.perfil_id})
    for u, tenant in sigarh_central_validos:
        items.append({
            "id": str(u.id),
            "name": u.username,
            "email": u.email,
            "role": roles_central.get(u.perfil_id, "SIGARH"),
            "panel": "sigarh",
            "is_active": u.is_active,
            "tenant_name": tenant.name,
            "tenant_id": str(tenant.id),
            "created_at": u.created_at.strftime("%d/%m/%Y"),
            "_created_at_raw": u.created_at,
            "account_type": "sigarh",
        })

    # Hospitales con base de datos física propia: sus usuarios de panel "app"
    # y sus cuentas SIGARH se crean directamente ahí (ver create_tenant), no en
    # la BD central, así que hay que ir a buscarlas a cada base. Se piden en
    # paralelo (antes era secuencial: uno por uno) y cada hospital se aísla
    # con su propio try/except -- si UNO no responde, ya no tumba la pantalla
    # completa de Usuarios para todos los demás hospitales.
    tenants_con_bd = [t for t in tenants_por_id.values() if t.database_name and t.is_active]

    async def _usuarios_de(tenant) -> tuple[list[dict], bool]:
        try:
            TenantSession = get_tenant_sessionmaker(tenant.database_name)
            async with TenantSession() as tdb:
                encontrados = []
                tenant_users_q = select(User)
                if vista == "hospital":
                    tenant_users_q = tenant_users_q.where(User.panel == "app")
                if is_active is not None:
                    tenant_users_q = tenant_users_q.where(User.is_active == is_active)
                filtro_u = _filtro_texto(User.name, User.email, q=q)
                if filtro_u is not None:
                    tenant_users_q = tenant_users_q.where(filtro_u)
                if cap:
                    tenant_users_q = tenant_users_q.order_by(User.created_at.desc()).limit(cap)
                tenant_users = (await tdb.scalars(tenant_users_q)).all()
                for u in tenant_users:
                    encontrados.append({
                        "id": str(u.id), "name": u.name, "email": u.email,
                        "role": u.role, "panel": u.panel, "is_active": u.is_active,
                        "tenant_name": tenant.name, "tenant_id": str(tenant.id),
                        "created_at": u.created_at.strftime("%d/%m/%Y"), "_created_at_raw": u.created_at,
                        "account_type": "user",
                    })
                tenant_sigarh_q = select(UsuarioSigarh)
                if is_active is not None:
                    tenant_sigarh_q = tenant_sigarh_q.where(UsuarioSigarh.is_active == is_active)
                filtro_s = _filtro_texto(UsuarioSigarh.username, UsuarioSigarh.email, q=q)
                if filtro_s is not None:
                    tenant_sigarh_q = tenant_sigarh_q.where(filtro_s)
                if cap:
                    tenant_sigarh_q = tenant_sigarh_q.order_by(UsuarioSigarh.created_at.desc()).limit(cap)
                tenant_sigarh_users = (await tdb.scalars(tenant_sigarh_q)).all()
                roles_hospital = await _roles_por_lote(tdb, {u.perfil_id for u in tenant_sigarh_users if u.perfil_id})
                for u in tenant_sigarh_users:
                    encontrados.append({
                        "id": str(u.id), "name": u.username, "email": u.email,
                        "role": roles_hospital.get(u.perfil_id, "SIGARH"), "panel": "sigarh",
                        "is_active": u.is_active, "tenant_name": tenant.name, "tenant_id": str(tenant.id),
                        "created_at": u.created_at.strftime("%d/%m/%Y"), "_created_at_raw": u.created_at,
                        "account_type": "sigarh",
                    })
                return encontrados, True
        except Exception:
            logger.exception("No se pudo consultar usuarios del hospital %s", tenant.name)
            return [], False

    resultados = await gather_limitado([_usuarios_de(t) for t in tenants_con_bd])
    hospitales_no_disponibles = []
    for tenant, (encontrados, disponible) in zip(tenants_con_bd, resultados):
        items.extend(encontrados)
        if not disponible:
            hospitales_no_disponibles.append(tenant.name)

    return items, hospitales_no_disponibles


async def _contar_todas_las_cuentas(
    db: AsyncSession, tenant_id: uuid.UUID | None, vista: str | None,
    q: str | None, is_active: bool | None,
) -> int:
    """Total real de cuentas que matchean los mismos filtros que
    `_reunir_todas_las_cuentas`, pero via COUNT (una fila de resultado por
    fuente) -- nunca trae las cuentas en si. Lo usa el listado paginado
    para no depender de `len(items)` sobre una lista ya acotada por `cap`."""
    from sqlalchemy import func
    from app.auth.models import User
    from app.sigarh.mantenimiento.models import UsuarioSigarh
    from app.tenants.hospitales.models import Tenant
    from app.core.tenant_db import get_tenant_sessionmaker

    central_q = select(func.count(User.id)).where(User.is_superadmin.is_(False))
    if tenant_id:
        central_q = central_q.where(User.tenant_id == tenant_id)
    if vista == "admin":
        central_q = central_q.where(User.panel == "admin")
    elif vista == "hospital":
        # Mismo criterio que en _reunir_todas_las_cuentas: "hospital" es
        # app + sigarh, nunca portal.
        central_q = central_q.where(User.panel == "app")
    if is_active is not None:
        central_q = central_q.where(User.is_active == is_active)
    filtro = _filtro_texto(User.name, User.email, q=q)
    if filtro is not None:
        central_q = central_q.where(filtro)
    total = await db.scalar(central_q) or 0

    if vista == "admin":
        return total

    sigarh_central_q = (
        select(func.count(UsuarioSigarh.id))
        .join(Tenant, UsuarioSigarh.tenant_id == Tenant.id)
        .where(Tenant.database_name.is_(None))
    )
    if tenant_id:
        sigarh_central_q = sigarh_central_q.where(UsuarioSigarh.tenant_id == tenant_id)
    if is_active is not None:
        sigarh_central_q = sigarh_central_q.where(UsuarioSigarh.is_active == is_active)
    filtro = _filtro_texto(UsuarioSigarh.username, UsuarioSigarh.email, q=q)
    if filtro is not None:
        sigarh_central_q = sigarh_central_q.where(filtro)
    total += await db.scalar(sigarh_central_q) or 0

    tenants_por_id = await _tenants_relevantes(db, tenant_id)
    tenants_con_bd = [t for t in tenants_por_id.values() if t.database_name and t.is_active]

    async def _contar_en(tenant) -> int:
        try:
            TenantSession = get_tenant_sessionmaker(tenant.database_name)
            async with TenantSession() as tdb:
                users_q = select(func.count(User.id))
                if vista == "hospital":
                    users_q = users_q.where(User.panel == "app")
                if is_active is not None:
                    users_q = users_q.where(User.is_active == is_active)
                filtro_u = _filtro_texto(User.name, User.email, q=q)
                if filtro_u is not None:
                    users_q = users_q.where(filtro_u)
                sigarh_q = select(func.count(UsuarioSigarh.id))
                if is_active is not None:
                    sigarh_q = sigarh_q.where(UsuarioSigarh.is_active == is_active)
                filtro_s = _filtro_texto(UsuarioSigarh.username, UsuarioSigarh.email, q=q)
                if filtro_s is not None:
                    sigarh_q = sigarh_q.where(filtro_s)
                return (await tdb.scalar(users_q) or 0) + (await tdb.scalar(sigarh_q) or 0)
        except Exception:
            logger.exception("No se pudo contar usuarios del hospital %s", tenant.name)
            return 0

    conteos = await gather_limitado([_contar_en(t) for t in tenants_con_bd])
    return total + sum(conteos)


def _query_roles_sigarh():
    """Nombres de rol DISTINTOS entre cuentas SIGARH (resueltos via perfil ->
    rol de sistema, con "SIGARH" de respaldo si no tiene perfil o el perfil
    no tiene rol asignado). Nunca trae las cuentas en si, solo el pequeño
    conjunto de nombres de rol distintos que existen."""
    from sqlalchemy import func
    from app.sigarh.mantenimiento.models import UsuarioSigarh, PerfilUsuario, RolSistema
    return (
        select(func.coalesce(RolSistema.nombre, "SIGARH"))
        .select_from(UsuarioSigarh)
        .outerjoin(PerfilUsuario, UsuarioSigarh.perfil_id == PerfilUsuario.id)
        .outerjoin(RolSistema, PerfilUsuario.rol_sistema_id == RolSistema.id)
        .distinct()
    )


async def _resumen_todas_las_cuentas(
    db: AsyncSession, tenant_id: uuid.UUID | None, vista: str | None,
) -> dict:
    """Agregados (total, activos, inactivos, roles unicos) para el mismo
    universo de cuentas que _reunir_todas_las_cuentas/_contar_todas_las_
    cuentas, pero SIN traer una sola cuenta a memoria: cada fuente aporta un
    COUNT/SUM y un SELECT DISTINCT de a lo sumo un puñado de nombres de rol.
    Antes /usuarios/resumen llamaba a _reunir_todas_las_cuentas sin `cap` --
    es decir, con el catalogo COMPLETO de cuentas de TODOS los hospitales --
    solo para sumarlas y sacar un set() de roles en Python. La mejora de
    paginacion de /usuarios/con-hospital nunca alcanzaba a este endpoint,
    que la pantalla de Usuarios pide en cada carga junto al listado."""
    from sqlalchemy import func, case
    from app.auth.models import User
    from app.sigarh.mantenimiento.models import UsuarioSigarh
    from app.tenants.hospitales.models import Tenant
    from app.core.tenant_db import get_tenant_sessionmaker

    activos_expr = func.sum(case((User.is_active.is_(True), 1), else_=0))

    central_q = select(func.count(User.id), activos_expr).where(User.is_superadmin.is_(False))
    roles_central_q = select(User.role).where(User.is_superadmin.is_(False)).distinct()
    if tenant_id:
        central_q = central_q.where(User.tenant_id == tenant_id)
        roles_central_q = roles_central_q.where(User.tenant_id == tenant_id)
    if vista == "admin":
        central_q = central_q.where(User.panel == "admin")
        roles_central_q = roles_central_q.where(User.panel == "admin")
    elif vista == "hospital":
        central_q = central_q.where(User.panel == "app")
        roles_central_q = roles_central_q.where(User.panel == "app")
    total_c, activos_c = (await db.execute(central_q)).one()
    total = total_c or 0
    activos = activos_c or 0
    roles: set[str] = set((await db.scalars(roles_central_q)).all())

    if vista == "admin":
        return {
            "total": total, "activos": activos, "inactivos": total - activos,
            "roles_unicos": len(roles), "hospitales_no_disponibles": [], "es_parcial": False,
        }

    sigarh_activos_expr = func.sum(case((UsuarioSigarh.is_active.is_(True), 1), else_=0))
    sigarh_central_q = (
        select(func.count(UsuarioSigarh.id), sigarh_activos_expr)
        .join(Tenant, UsuarioSigarh.tenant_id == Tenant.id)
        .where(Tenant.database_name.is_(None))
    )
    roles_sigarh_central_q = _query_roles_sigarh().join(Tenant, UsuarioSigarh.tenant_id == Tenant.id).where(
        Tenant.database_name.is_(None)
    )
    if tenant_id:
        sigarh_central_q = sigarh_central_q.where(UsuarioSigarh.tenant_id == tenant_id)
        roles_sigarh_central_q = roles_sigarh_central_q.where(UsuarioSigarh.tenant_id == tenant_id)
    total_sc, activos_sc = (await db.execute(sigarh_central_q)).one()
    total += total_sc or 0
    activos += activos_sc or 0
    roles |= set((await db.scalars(roles_sigarh_central_q)).all())

    tenants_por_id = await _tenants_relevantes(db, tenant_id)
    tenants_con_bd = [t for t in tenants_por_id.values() if t.database_name and t.is_active]

    async def _resumen_en(tenant) -> tuple[int, int, set[str], bool]:
        try:
            TenantSession = get_tenant_sessionmaker(tenant.database_name)
            async with TenantSession() as tdb:
                users_q = select(func.count(User.id), activos_expr)
                roles_u_q = select(User.role).distinct()
                if vista == "hospital":
                    users_q = users_q.where(User.panel == "app")
                    roles_u_q = roles_u_q.where(User.panel == "app")
                total_u, activos_u = (await tdb.execute(users_q)).one()
                roles_t: set[str] = set((await tdb.scalars(roles_u_q)).all())

                sigarh_q = select(func.count(UsuarioSigarh.id), sigarh_activos_expr)
                total_s, activos_s = (await tdb.execute(sigarh_q)).one()
                roles_t |= set((await tdb.scalars(_query_roles_sigarh())).all())

                return (total_u or 0) + (total_s or 0), (activos_u or 0) + (activos_s or 0), roles_t, True
        except Exception:
            logger.exception("No se pudo calcular el resumen de usuarios del hospital %s", tenant.name)
            return 0, 0, set(), False

    resultados = await gather_limitado([_resumen_en(t) for t in tenants_con_bd])
    hospitales_no_disponibles = []
    for tenant, (total_t, activos_t, roles_t, disponible) in zip(tenants_con_bd, resultados):
        total += total_t
        activos += activos_t
        roles |= roles_t
        if not disponible:
            hospitales_no_disponibles.append(tenant.name)

    return {
        "total": total,
        "activos": activos,
        "inactivos": total - activos,
        "roles_unicos": len(roles),
        "hospitales_no_disponibles": hospitales_no_disponibles,
        "es_parcial": len(hospitales_no_disponibles) > 0,
    }


@router.get("/usuarios/con-hospital", summary="Usuarios con datos de hospital, de todos los paneles")
async def usuarios_con_hospital(
    tenant_id: uuid.UUID | None = None,
    vista: str | None = Query(None, pattern="^(admin|hospital)$"),
    q: str | None = None,
    is_active: bool | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    """Si se pasa `tenant_id`, solo consulta ESE hospital (y las cuentas
    centrales que ya le pertenecen) en vez de recorrer todos -- la pantalla
    de Usuarios lo usa cuando el admin ya eligió un hospital puntual, para
    no pagar el costo de tocar cada base física solo para mostrar una.

    `q`/`is_active` se filtran en SQL en cada fuente (ver
    `_reunir_todas_las_cuentas`), y `limit`/`offset` acotan lo que cada
    fuente entrega (`cap = offset + limit` alcanza para un top-N global
    correcto, ver esa misma nota). Antes esto traia el catalogo COMPLETO de
    cuentas de TODOS los hospitales a memoria en cada llamada -- buscar o
    paginar no reducia nada del trabajo real, solo lo que bajaba al
    navegador. `total` ya no sale de `len(items)` (que ahora viene acotado)
    sino de `_contar_todas_las_cuentas`, que solo pide COUNT(*) por fuente,
    nunca las filas.

    Sigue siendo honesto decir que un LIMIT/OFFSET unico de Postgres a
    traves de varias bases fisicas distintas no existe sin un índice
    materializado aparte -- eso es un cambio mas grande que esto. Lo que se
    gana aqui es que ni la busqueda ni la paginacion siguen pagando el
    costo de traer TODO solo para descartarlo despues."""
    cap = offset + limit
    items, hospitales_no_disponibles = await _reunir_todas_las_cuentas(
        db, tenant_id, vista, q=q, is_active=is_active, cap=cap,
    )

    # vista == "admin"/"hospital" ya vienen filtradas por panel dentro de
    # _reunir_todas_las_cuentas (empujado a SQL en cada fuente, antes de
    # aplicar `cap`) -- antes este filtro se aplicaba ACA, en Python, DESPUES
    # de que cada fuente ya habia sido acotada a sus top-`cap` mas recientes
    # sin importar el panel. Si esas primeras `cap` filas de una base eran
    # todas panel="portal", las cuentas app/sigarh reales quedaban fuera del
    # resultado sin llegar siquiera a este filtro -- una pagina podia salir
    # vacia (o con menos cuentas de las que en realidad existian) aunque
    # hubiera cuentas validas mas atras en esa misma base.

    items.sort(key=lambda it: it["_created_at_raw"], reverse=True)
    pagina = items[offset:offset + limit]
    for it in pagina:
        del it["_created_at_raw"]

    total = await _contar_todas_las_cuentas(db, tenant_id, vista, q, is_active)

    return {
        "items": pagina,
        "total": total,
        "hospitales_no_disponibles": hospitales_no_disponibles,
        "es_parcial": len(hospitales_no_disponibles) > 0,
    }


@router.get("/usuarios/resumen", summary="Agregados de usuarios (total, activos, inactivos, roles)")
async def usuarios_resumen(
    tenant_id: uuid.UUID | None = None,
    vista: str | None = Query(None, pattern="^(admin|hospital)$"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await _resumen_todas_las_cuentas(db, tenant_id, vista)


@router.get("/usuarios/hospital/{tenant_id}", response_model=list[UserListItem], summary="Usuarios por hospital")
async def usuarios_por_hospital(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_users_by_tenant(db, tenant_id)


@router.get("/usuarios/{user_id}", summary="Obtener una cuenta por id")
async def obtener_usuario(
    user_id: uuid.UUID,
    tenant_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    cuenta = await obtener_cuenta(db, user_id, tenant_id)
    if not cuenta:
        raise HTTPException(404, detail="Usuario no encontrado")
    return cuenta


@router.post("/usuarios", response_model=UserListItem, status_code=201, summary="Crear usuario")
async def crear_usuario(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await create_user(db, data, current_user)


@router.patch("/usuarios/{user_id}", response_model=UserListItem, summary="Actualizar usuario")
async def actualizar_usuario(
    user_id: uuid.UUID,
    data: UserUpdate,
    tenant_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    user = await update_user(db, user_id, data, current_user, tenant_id)
    if not user:
        raise HTTPException(404, detail="Usuario no encontrado")
    return user


@router.patch("/usuarios/{user_id}/toggle", summary="Activar/desactivar usuario")
async def toggle_usuario(
    user_id: uuid.UUID,
    is_active: bool,
    tenant_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    user = await toggle_user(db, user_id, is_active, current_user, tenant_id)
    if not user:
        raise HTTPException(404, detail="Usuario no encontrado")
    # UsuarioSigarh no tiene name/role/panel como User; devolvemos la forma
    # correcta según el tipo de cuenta en vez de forzar un solo response_model.
    from app.sigarh.mantenimiento.models import UsuarioSigarh
    if isinstance(user, UsuarioSigarh):
        return {
            "id": str(user.id), "name": user.username, "email": user.email,
            "role": "SIGARH", "panel": "sigarh", "tenant_id": str(user.tenant_id),
            "is_active": user.is_active, "created_at": user.created_at,
        }
    return UserListItem.model_validate(user)


@router.delete("/usuarios/{user_id}", summary="Eliminar usuario")
async def eliminar_usuario(
    user_id: uuid.UUID,
    tenant_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    ok = await delete_user(db, user_id, current_user, tenant_id)
    if not ok:
        raise HTTPException(404, detail="Usuario no encontrado")
    return {"ok": True}
