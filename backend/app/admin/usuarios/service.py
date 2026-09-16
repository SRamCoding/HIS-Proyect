import uuid
import bcrypt
from contextlib import asynccontextmanager
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.auth.models import User


async def _es_ultimo_administrador(user: User, work_db: AsyncSession) -> bool:
    """True si `user` es administrador activo y, sin él, su ámbito (su
    hospital si es panel "app", o el ERP central si es panel "admin") se
    queda sin ningún administrador activo. `panel` ya delimita el ámbito
    correcto: en la BD física de un hospital solo hay cuentas app/portal de
    ESE hospital; en la central solo hay cuentas admin.

    SELECT ... FOR UPDATE sobre TODOS los administradores activos del
    ámbito (no solo "los otros"): un simple conteo aqui y una escritura
    despues, sin bloqueo, deja una ventana real -- dos peticiones que
    desactivan a los dos unicos administradores de un hospital al mismo
    tiempo pueden contar cada una "el otro sigue activo" antes de que
    cualquiera confirme, y las dos pasan. Al bloquear las filas de TODOS
    los administradores del ambito (no solo la del otro), dos operaciones
    concurrentes sobre el mismo ambito chocan por el mismo lock: la segunda
    espera a que la primera confirme y entonces re-lee el estado ya
    actualizado, viendo correctamente que ya no queda ningun otro activo."""
    if user.role != "administrador" or not user.is_active:
        return False
    activos = (await work_db.execute(
        select(User.id).where(
            User.panel == user.panel,
            User.role == "administrador",
            User.is_active.is_(True),
        ).with_for_update()
    )).scalars().all()
    otros = [uid for uid in activos if uid != user.id]
    return len(otros) == 0


async def get_all_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


async def get_users_by_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> list[User]:
    result = await db.execute(
        select(User).where(User.tenant_id == tenant_id).order_by(User.name)
    )
    return result.scalars().all()


async def create_user(db: AsyncSession, data, creador: dict) -> User:
    if data.panel != "admin":
        from app.tenants.hospitales.models import Tenant
        from app.core.tenant_db import get_tenant_sessionmaker
        hospital = await db.get(Tenant, data.tenant_id) if data.tenant_id else None
        if not hospital or not hospital.is_active or not hospital.database_name:
            raise HTTPException(400, detail="Seleccione un hospital activo con base de datos")
        async with get_tenant_sessionmaker(hospital.database_name)() as hospital_db:
            if await hospital_db.scalar(select(User.id).where(User.email == data.email)):
                raise HTTPException(400, detail="El correo ya existe en este hospital")
            user = User(name=data.name, email=data.email,
                        password=bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode(),
                        role=data.role, panel=data.panel, tenant_id=None, is_active=data.is_active)
            hospital_db.add(user)
            await hospital_db.commit()
            await hospital_db.refresh(user)
        return user
    if data.tenant_id:
        raise HTTPException(400, detail="Una cuenta admin no pertenece a un hospital")
    existente = await db.scalar(select(User.id).where(User.email == data.email))
    if existente:
        raise HTTPException(400, detail=f"Ya existe un usuario con el correo {data.email}")

    if data.tenant_id:
        from app.tenants.hospitales.models import Tenant
        if not await db.scalar(select(Tenant.id).where(Tenant.id == data.tenant_id)):
            raise HTTPException(400, detail="El hospital indicado no existe")

    hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
    user = User(
        name=data.name,
        email=data.email,
        password=hashed,
        role=data.role,
        panel=data.panel,
        tenant_id=data.tenant_id,
        is_active=data.is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    from app.admin.notificaciones.service import crear_notificacion
    await crear_notificacion(
        f"Cuenta admin creada: {user.name}",
        f"Correo: {user.email}",
        nivel="info",
    )
    return user


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await db.scalar(select(User).where(User.id == user_id))


async def _locate_user(db: AsyncSession, user_id: uuid.UUID):
    """Busca un User en la BD central; si no está ahí, lo busca en la BD
    física de cada hospital con base propia (ver create_tenant). Devuelve
    (user, sesion_de_trabajo, sesion_es_de_tenant, "user"). La sesión de
    tenant, si se abre, queda a cargo del llamador (cerrarla cuando termine)."""
    user = await get_user_by_id(db, user_id)
    if user:
        return user, db, False, "user"

    from app.tenants.hospitales.models import Tenant
    from app.core.tenant_db import get_tenant_sessionmaker

    tenants = (await db.scalars(
        select(Tenant).where(Tenant.database_name.is_not(None), Tenant.is_active.is_(True))
    )).all()
    for tenant in tenants:
        TenantSession = get_tenant_sessionmaker(tenant.database_name)
        tdb = TenantSession()
        try:
            found = await tdb.scalar(select(User).where(User.id == user_id))
        except Exception:
            await tdb.close()
            raise
        if found:
            return found, tdb, True, "user"
        await tdb.close()
    return None, None, False, None


async def _locate_cuenta(db: AsyncSession, user_id: uuid.UUID):
    """Como _locate_user, pero además busca en UsuarioSigarh (central y por
    hospital) si no se encontró como User. Devuelve (cuenta, sesion, es_tenant, tipo)
    con tipo en {"user", "sigarh"}."""
    found, work_db, es_tenant, tipo = await _locate_user(db, user_id)
    if found:
        return found, work_db, es_tenant, tipo

    from app.sigarh.mantenimiento.models import UsuarioSigarh
    from app.tenants.hospitales.models import Tenant
    from app.core.tenant_db import get_tenant_sessionmaker

    sigarh_user = await db.scalar(select(UsuarioSigarh).where(UsuarioSigarh.id == user_id))
    if sigarh_user:
        return sigarh_user, db, False, "sigarh"

    tenants = (await db.scalars(
        select(Tenant).where(Tenant.database_name.is_not(None), Tenant.is_active.is_(True))
    )).all()
    for tenant in tenants:
        TenantSession = get_tenant_sessionmaker(tenant.database_name)
        tdb = TenantSession()
        try:
            found_sigarh = await tdb.scalar(select(UsuarioSigarh).where(UsuarioSigarh.id == user_id))
        except Exception:
            await tdb.close()
            raise
        if found_sigarh:
            return found_sigarh, tdb, True, "sigarh"
        await tdb.close()
    return None, None, False, None


async def _locate_cuenta_directa(db: AsyncSession, user_id: uuid.UUID, tenant_id: uuid.UUID):
    """Como _locate_cuenta, pero va directo a la BD física de UN hospital ya
    conocido en vez de recorrer todos -- la lista de usuarios ya trae
    tenant_id en cada fila, así que editar/activar/eliminar una cuenta no
    tiene por qué escanear cada hospital para encontrarla (y, en una
    instalación con muchos hospitales, una base ajena caída o lenta ya no
    puede demorar ni interrumpir la operación sobre otra cuenta)."""
    from app.tenants.hospitales.models import Tenant
    from app.core.tenant_db import get_tenant_sessionmaker
    from app.sigarh.mantenimiento.models import UsuarioSigarh

    tenant = await db.get(Tenant, tenant_id)
    if not tenant or not tenant.database_name:
        return None, None, False, None

    TenantSession = get_tenant_sessionmaker(tenant.database_name)
    tdb = TenantSession()
    try:
        user = await tdb.get(User, user_id)
        if user:
            return user, tdb, True, "user"
        sigarh = await tdb.get(UsuarioSigarh, user_id)
        if sigarh:
            return sigarh, tdb, True, "sigarh"
    except Exception:
        await tdb.close()
        raise
    await tdb.close()
    return None, None, False, None


@asynccontextmanager
async def _cuenta_localizada(db: AsyncSession, user_id: uuid.UUID, tenant_id: uuid.UUID | None = None):
    """Como _locate_cuenta, pero garantiza el cierre de la sesión hospitalaria
    (si se abrió una) al salir del bloque `async with`, incluso si el cuerpo
    lanza una excepción. Antes cada llamador repetía `if es_tenant: await
    work_db.close()` en cada punto de salida por separado -- fácil de
    olvidar en un camino nuevo, y en efecto faltaba en `_locate_user`/
    `_locate_cuenta` mismos cuando la consulta fallaba a mitad de camino.

    Si el llamador ya sabe en qué hospital vive la cuenta (`tenant_id`), se
    va directo ahí -- el escaneo completo (_locate_cuenta) queda solo como
    respaldo para cuando de verdad no se sabe dónde buscar."""
    if tenant_id:
        user, work_db, es_tenant, tipo = await _locate_cuenta_directa(db, user_id, tenant_id)
    else:
        user, work_db, es_tenant, tipo = await _locate_cuenta(db, user_id)
    try:
        yield user, work_db, es_tenant, tipo
    finally:
        if es_tenant:
            await work_db.close()


async def obtener_cuenta(db: AsyncSession, user_id: uuid.UUID, tenant_id: uuid.UUID | None = None) -> dict | None:
    """Trae una cuenta (User o UsuarioSigarh) por su id, ya lista para la
    pantalla de edicion. Si se conoce `tenant_id` (la lista ya lo trae en
    cada fila), va directo a esa base fisica en vez de recorrer TODOS los
    hospitales buscando donde vive la cuenta -- antes editar un usuario
    siempre descargaba /usuarios/con-hospital completo solo para encontrar
    uno por id."""
    if tenant_id:
        from app.tenants.hospitales.models import Tenant
        from app.core.tenant_db import get_tenant_sessionmaker
        from app.sigarh.mantenimiento.models import UsuarioSigarh
        tenant = await db.get(Tenant, tenant_id)
        if not tenant:
            return None
        if tenant.database_name:
            TenantSession = get_tenant_sessionmaker(tenant.database_name)
            async with TenantSession() as tdb:
                user = await tdb.get(User, user_id)
                if user:
                    return _serializar_user(user, tenant_id=str(tenant.id))
                sigarh = await tdb.get(UsuarioSigarh, user_id)
                if sigarh:
                    return await _serializar_sigarh(tdb, sigarh, tenant_id=str(tenant.id))
                return None
        user = await db.scalar(select(User).where(User.id == user_id, User.tenant_id == tenant_id))
        if user:
            return _serializar_user(user, tenant_id=str(tenant_id))
        sigarh = await db.scalar(select(UsuarioSigarh).where(UsuarioSigarh.id == user_id, UsuarioSigarh.tenant_id == tenant_id))
        if sigarh:
            return await _serializar_sigarh(db, sigarh, tenant_id=str(tenant_id))
        return None

    async with _cuenta_localizada(db, user_id) as (cuenta, work_db, es_tenant, tipo):
        if not cuenta:
            return None
        if tipo == "sigarh":
            return await _serializar_sigarh(work_db, cuenta, tenant_id=str(cuenta.tenant_id))
        return _serializar_user(cuenta, tenant_id=str(cuenta.tenant_id) if cuenta.tenant_id else None)


def _serializar_user(user: User, tenant_id: str | None) -> dict:
    return {
        "id": str(user.id), "name": user.name, "email": user.email,
        "role": user.role, "panel": user.panel, "is_active": user.is_active,
        "tenant_id": tenant_id, "account_type": "user",
    }


async def _serializar_sigarh(session: AsyncSession, sigarh, tenant_id: str | None) -> dict:
    from app.sigarh.mantenimiento.models import PerfilUsuario, RolSistema
    role_name = "SIGARH"
    if sigarh.perfil_id:
        perfil = await session.scalar(select(PerfilUsuario).where(PerfilUsuario.id == sigarh.perfil_id))
        if perfil and perfil.rol_sistema_id:
            rol = await session.scalar(select(RolSistema).where(RolSistema.id == perfil.rol_sistema_id))
            if rol:
                role_name = rol.nombre
    return {
        "id": str(sigarh.id), "name": sigarh.username, "email": sigarh.email,
        "role": role_name, "panel": "sigarh", "is_active": sigarh.is_active,
        "tenant_id": tenant_id, "account_type": "sigarh",
    }


async def update_user(db: AsyncSession, user_id: uuid.UUID, data, actor: dict, tenant_id: uuid.UUID | None = None) -> User | None:
    async with _cuenta_localizada(db, user_id, tenant_id) as (user, work_db, es_tenant, tipo):
        if not user:
            return None
        if tipo == "sigarh":
            raise HTTPException(400, detail="Las cuentas SIGARH se editan desde SIGARH → Mantenimiento → Usuarios")
        cambios = data.model_dump(exclude_unset=True, exclude={"password"})
        if es_tenant:
            if cambios.get("panel", user.panel) == "admin":
                raise HTTPException(400, detail="Una cuenta hospitalaria no puede convertirse en admin")
            if "tenant_id" in cambios:
                if cambios["tenant_id"] is not None:
                    from app.tenants.hospitales.models import Tenant
                    hospital = await db.scalar(select(Tenant).where(Tenant.database_name == work_db.bind.url.database))
                    if not hospital or hospital.id != cambios["tenant_id"]:
                        raise HTTPException(400, detail="No se puede trasladar una cuenta a otro hospital")
                cambios.pop("tenant_id")
        if data.email and data.email != user.email:
            existente = await work_db.scalar(select(User.id).where(User.email == data.email, User.id != user_id))
            if existente:
                raise HTTPException(400, detail=f"Ya existe un usuario con el correo {data.email}")
        if cambios.get("tenant_id"):
            from app.tenants.hospitales.models import Tenant
            if not await db.scalar(select(Tenant.id).where(Tenant.id == cambios["tenant_id"])):
                raise HTTPException(400, detail="El hospital indicado no existe")

        panel_final = cambios.get("panel", user.panel)
        role_final = cambios.get("role", user.role)
        if panel_final == "admin" and role_final != "administrador":
            raise HTTPException(400, detail="Las cuentas del panel admin deben tener el rol 'administrador'")

        activo_final = cambios.get("is_active", user.is_active)
        # La proteccion de la cuenta fundacional (is_superadmin) antes solo
        # vivia en toggle_user/delete_user; este PATCH general podia
        # desactivarla o sacarla de rol/panel administrador sin pasar por
        # ese chequeo -- bastaba con que existiera otro admin activo para
        # que _es_ultimo_administrador no lo bloqueara.
        if tipo == "user" and getattr(user, "is_superadmin", False):
            if not activo_final:
                raise HTTPException(400, detail="La cuenta administradora fundacional no se puede desactivar")
            if panel_final != "admin" or role_final != "administrador":
                raise HTTPException(400, detail="La cuenta administradora fundacional no puede cambiar de panel ni de rol")
        # Cambiar de panel tambien saca a la cuenta de su ambito actual, aunque
        # el rol siga diciendo "administrador" -- sin este chequeo, mover el
        # unico admin de un hospital a panel "app" esquivaba la proteccion
        # (el rol y el estado no cambiaban, solo el panel).
        dejara_de_ser_admin = (
            role_final != "administrador" or not activo_final or panel_final != user.panel
        )
        if dejara_de_ser_admin and await _es_ultimo_administrador(user, work_db):
            raise HTTPException(
                400,
                "No puedes quitarle el rol de administrador ni desactivar al último administrador activo",
            )

        for field, value in cambios.items():
            setattr(user, field, value)
        if data.password:
            user.password = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
            # UPDATE atomico calculado en SQL, no "user.session_version += 1"
            # en Python: ese patron es lectura-y-luego-escritura sobre el
            # valor que el ORM tenia en memoria, y una operacion concurrente
            # (otro cambio de contraseña, un logout) que tambien incrementa
            # puede perderse. El logout ya usa este mismo patron (ver
            # auth/router.py); aqui quedaba inconsistente.
            await work_db.execute(
                update(User).where(User.id == user.id).values(session_version=User.session_version + 1)
            )

        await work_db.commit()
        await work_db.refresh(user)
        return user


async def toggle_user(db: AsyncSession, user_id: uuid.UUID, is_active: bool, actor: dict, tenant_id: uuid.UUID | None = None):
    async with _cuenta_localizada(db, user_id, tenant_id) as (user, work_db, es_tenant, tipo):
        if not user:
            return None
        if str(user.id) == str(actor.get("sub")) and not is_active:
            raise HTTPException(400, detail="No puedes desactivar tu propia cuenta")
        if not is_active and tipo == "user" and getattr(user, "is_superadmin", False):
            raise HTTPException(400, detail="La cuenta administradora fundacional no se puede desactivar")
        if not is_active and tipo == "user" and await _es_ultimo_administrador(user, work_db):
            raise HTTPException(400, detail="No puedes desactivar al último administrador activo")
        user.is_active = is_active
        await work_db.commit()
        await work_db.refresh(user)
        return user


async def delete_user(db: AsyncSession, user_id: uuid.UUID, actor: dict, tenant_id: uuid.UUID | None = None) -> bool:
    async with _cuenta_localizada(db, user_id, tenant_id) as (user, work_db, es_tenant, tipo):
        if not user:
            return False
        if str(user.id) == str(actor.get("sub")):
            raise HTTPException(400, detail="No puedes eliminar tu propia cuenta")
        if tipo == "user" and getattr(user, "is_superadmin", False):
            raise HTTPException(400, detail="La cuenta administradora fundacional no se puede eliminar")
        if tipo == "user" and await _es_ultimo_administrador(user, work_db):
            raise HTTPException(400, detail="No puedes eliminar al último administrador activo")
        await work_db.delete(user)
        await work_db.commit()
        return True
