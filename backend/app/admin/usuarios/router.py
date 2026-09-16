import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.usuarios.schemas import UserListItem, UserCreate, UserUpdate
from app.admin.usuarios.service import (
    get_all_users, get_users_by_tenant, create_user,
    update_user, toggle_user, delete_user,
)

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


async def _rol_nombre_sigarh(session, perfil_id) -> str:
    from app.sigarh.mantenimiento.models import PerfilUsuario, RolSistema
    if not perfil_id:
        return "SIGARH"
    perfil = await session.scalar(select(PerfilUsuario).where(PerfilUsuario.id == perfil_id))
    if not perfil or not perfil.rol_sistema_id:
        return "SIGARH"
    rol = await session.scalar(select(RolSistema).where(RolSistema.id == perfil.rol_sistema_id))
    return rol.nombre if rol else "SIGARH"


@router.get("/usuarios/con-hospital", summary="Usuarios con datos de hospital, de todos los paneles")
async def usuarios_con_hospital(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    from app.auth.models import User
    from app.sigarh.mantenimiento.models import UsuarioSigarh
    from app.tenants.hospitales.models import Tenant
    from app.core.tenant_db import get_tenant_sessionmaker

    result = await db.execute(
        select(User, Tenant.name.label("tenant_name"))
        .outerjoin(Tenant, User.tenant_id == Tenant.id)
        .where(User.email != "admin@erp.local")  # excluir super admin
        .order_by(User.created_at.desc())
    )
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
            "account_type": "user",
        }
        for u, tenant_name in rows
    ]

    # Cuentas SIGARH que viven en la BD central (hospitales sin base física propia).
    sigarh_central = (await db.scalars(select(UsuarioSigarh))).all()
    tenants_por_id = {str(t.id): t for t in (await db.scalars(select(Tenant))).all()}
    for u in sigarh_central:
        tenant = tenants_por_id.get(str(u.tenant_id))
        if not tenant or tenant.database_name:
            continue  # los de hospitales con BD física se leen de ahí, más abajo
        items.append({
            "id": str(u.id),
            "name": u.username,
            "email": u.email,
            "role": await _rol_nombre_sigarh(db, u.perfil_id),
            "panel": "sigarh",
            "is_active": u.is_active,
            "tenant_name": tenant.name,
            "tenant_id": str(tenant.id),
            "created_at": u.created_at.strftime("%d/%m/%Y"),
            "account_type": "sigarh",
        })

    # Hospitales con base de datos física propia: sus usuarios de panel "app"
    # y sus cuentas SIGARH se crean directamente ahí (ver create_tenant), no en
    # la BD central, así que hay que ir a buscarlas a cada base.
    tenants_con_bd = [t for t in tenants_por_id.values() if t.database_name and t.is_active]
    for tenant in tenants_con_bd:
        TenantSession = get_tenant_sessionmaker(tenant.database_name)
        async with TenantSession() as tdb:
            tenant_users = (await tdb.scalars(select(User))).all()
            for u in tenant_users:
                items.append({
                    "id": str(u.id),
                    "name": u.name,
                    "perfil_hospital_id": str(u.perfil_hospital_id) if u.perfil_hospital_id else None,
                    "empleado_id": str(u.empleado_id) if u.empleado_id else None,
                    "email": u.email,
                    "role": u.role,
                    "panel": u.panel,
                    "is_active": u.is_active,
                    "tenant_name": tenant.name,
                    "tenant_id": str(tenant.id),
                    "created_at": u.created_at.strftime("%d/%m/%Y"),
                    "account_type": "user",
                })

            tenant_sigarh_users = (await tdb.scalars(select(UsuarioSigarh))).all()
            for u in tenant_sigarh_users:
                items.append({
                    "id": str(u.id),
                    "name": u.username,
                    "email": u.email,
                    "role": await _rol_nombre_sigarh(tdb, u.perfil_id),
                    "panel": "sigarh",
                    "is_active": u.is_active,
                    "tenant_name": tenant.name,
                    "tenant_id": str(tenant.id),
                    "created_at": u.created_at.strftime("%d/%m/%Y"),
                    "account_type": "sigarh",
                })

    return items


@router.get("/usuarios/hospital/{tenant_id}", response_model=list[UserListItem], summary="Usuarios por hospital")
async def usuarios_por_hospital(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_users_by_tenant(db, tenant_id)


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
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    user = await update_user(db, user_id, data, current_user)
    if not user:
        raise HTTPException(404, detail="Usuario no encontrado")
    return user


@router.patch("/usuarios/{user_id}/toggle", summary="Activar/desactivar usuario")
async def toggle_usuario(
    user_id: uuid.UUID,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    user = await toggle_user(db, user_id, is_active, current_user)
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
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    ok = await delete_user(db, user_id, current_user)
    if not ok:
        raise HTTPException(404, detail="Usuario no encontrado")
    return {"ok": True}
