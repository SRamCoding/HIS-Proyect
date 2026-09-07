# backend/app/sigarh/mantenimiento/service.py
import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.sigarh.mantenimiento.models import (
    Departamento, Servicio, Dependencia, TipoTrabajador, TipoGuardia,
    NivelRemunerativo, HorarioGuardia, GrupoOcupacional,
    TipoActividad, Actividad, GuardiaValorizada,
    RolSistema, PerfilUsuario
)


# ─── Helper genérico CRUD ────────────────────────────────────────────────────

async def listar(db: AsyncSession, modelo, tenant_id: uuid.UUID):
    result = await db.execute(
        select(modelo)
        .where(modelo.tenant_id == tenant_id)
        .order_by(modelo.created_at.desc())
    )
    return result.scalars().all()


async def obtener(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(modelo)
        .where(modelo.id == id, modelo.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def eliminar(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    item = await obtener(db, modelo, id, tenant_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True


# ─── Departamentos ────────────────────────────────────────────────────────────

async def crear_departamento(db: AsyncSession, tenant_id: uuid.UUID, data) -> Departamento:
    item = Departamento(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_departamento(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Departamento | None:
    item = await obtener(db, Departamento, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


# ─── Servicios ────────────────────────────────────────────────────────────────

async def listar_servicios(db: AsyncSession, tenant_id: uuid.UUID) -> list[Servicio]:
    result = await db.execute(
        select(Servicio)
        .where(Servicio.tenant_id == tenant_id)
        .options(selectinload(Servicio.departamento), selectinload(Servicio.piso))
        .order_by(Servicio.created_at.desc())
    )
    return result.scalars().all()


async def obtener_servicio(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Servicio | None:
    result = await db.execute(
        select(Servicio)
        .where(Servicio.id == id, Servicio.tenant_id == tenant_id)
        .options(selectinload(Servicio.departamento), selectinload(Servicio.piso))
    )
    return result.scalar_one_or_none()


async def crear_servicio(db: AsyncSession, tenant_id: uuid.UUID, data) -> Servicio:
    item = Servicio(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_servicio(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Servicio | None:
    item = await obtener(db, Servicio, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


# ─── Helper para catálogos simples ────────────────────────────────────────────

async def crud_crear(db: AsyncSession, modelo, tenant_id: uuid.UUID, data) -> any:
    item = modelo(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def crud_actualizar(db: AsyncSession, modelo, id: uuid.UUID, tenant_id: uuid.UUID, data) -> any:
    item = await obtener(db, modelo, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item





async def listar_horarios_guardia(db: AsyncSession, tenant_id: uuid.UUID):
    result = await db.execute(
        select(HorarioGuardia)
        .where(HorarioGuardia.tenant_id == tenant_id)
        .options(selectinload(HorarioGuardia.tipo_guardia))
        .order_by(HorarioGuardia.created_at.desc())
    )
    return result.scalars().all()


async def obtener_horario_guardia(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(HorarioGuardia)
        .where(HorarioGuardia.id == id, HorarioGuardia.tenant_id == tenant_id)
        .options(selectinload(HorarioGuardia.tipo_guardia))
    )
    return result.scalar_one_or_none()


async def crear_horario_guardia(db: AsyncSession, tenant_id: uuid.UUID, data):
    item = HorarioGuardia(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_horario_guardia(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data):
    item = await obtener(db, HorarioGuardia, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def listar_dependencias(db: AsyncSession, tenant_id: uuid.UUID):
    result = await db.execute(
        select(Dependencia)
        .where(Dependencia.tenant_id == tenant_id)
        .options(selectinload(Dependencia.departamento), selectinload(Dependencia.servicio))
        .order_by(Dependencia.created_at.desc())
    )
    return result.scalars().all()


async def obtener_dependencia(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(Dependencia)
        .where(Dependencia.id == id, Dependencia.tenant_id == tenant_id)
        .options(selectinload(Dependencia.departamento), selectinload(Dependencia.servicio))
    )
    return result.scalar_one_or_none()


async def crear_dependencia(db: AsyncSession, tenant_id: uuid.UUID, data):
    item = Dependencia(tenant_id=tenant_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def actualizar_dependencia(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data):
    item = await obtener(db, Dependencia, id, tenant_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item

# ─── Rol Sistema (con JSON de modulos y grupos ocupacionales) ─────────────

def _serializar_rol(item: RolSistema) -> dict:
    """Convierte los campos JSON (guardados como texto) a listas reales."""
    return {
        "id": item.id,
        "tenant_id": item.tenant_id,
        "codigo": item.codigo,
        "nombre": item.nombre,
        "panel": item.panel,
        "modulo_requerido": item.modulo_requerido,
        "modulos_permitidos": json.loads(item.modulos_permitidos) if item.modulos_permitidos else [],
        "grupos_ocupacionales_permitidos": json.loads(item.grupos_ocupacionales_permitidos) if item.grupos_ocupacionales_permitidos else [],
        "descripcion": item.descripcion,
        "is_active": item.is_active,
        "created_at": item.created_at,
    }


async def listar_roles(db: AsyncSession, tenant_id: uuid.UUID) -> list[dict]:
    items = await listar(db, RolSistema, tenant_id)
    return [_serializar_rol(i) for i in items]


async def obtener_rol(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> dict | None:
    item = await obtener(db, RolSistema, id, tenant_id)
    if not item:
        return None
    return _serializar_rol(item)


async def crear_rol(db: AsyncSession, tenant_id: uuid.UUID, data) -> dict:
    data_dict = data.model_dump()
    modulos = data_dict.pop("modulos_permitidos", [])
    grupos = data_dict.pop("grupos_ocupacionales_permitidos", [])
    rol = RolSistema(
        tenant_id=tenant_id,
        modulos_permitidos=json.dumps(modulos),
        grupos_ocupacionales_permitidos=json.dumps([str(g) for g in grupos]),
        **data_dict,
    )
    db.add(rol)
    await db.commit()
    await db.refresh(rol)
    return _serializar_rol(rol)


async def actualizar_rol(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> dict | None:
    item = await obtener(db, RolSistema, id, tenant_id)
    if not item:
        return None
    data_dict = data.model_dump(exclude_unset=True)
    if "modulos_permitidos" in data_dict:
        item.modulos_permitidos = json.dumps(data_dict.pop("modulos_permitidos"))
    if "grupos_ocupacionales_permitidos" in data_dict:
        item.grupos_ocupacionales_permitidos = json.dumps([str(g) for g in data_dict.pop("grupos_ocupacionales_permitidos")])
    for field, value in data_dict.items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return _serializar_rol(item)


# ─── Perfil Usuario (con JSON de módulos) ─────────────────────────────────

def _serializar_perfil(item: PerfilUsuario) -> dict:
    return {
        "id": item.id,
        "tenant_id": item.tenant_id,
        "nombre": item.nombre,
        "rol_sistema_id": item.rol_sistema_id,
        "modulos_acceso": json.loads(item.modulos_acceso) if item.modulos_acceso else [],
        "descripcion": item.descripcion,
        "is_active": item.is_active,
        "created_at": item.created_at,
    }

# ─── Validación de Perfil contra su Rol ────────────────────────────────────

async def _validar_perfil_contra_rol(db: AsyncSession, tenant_id: uuid.UUID, rol_sistema_id, modulos_acceso: list[str]):
    from sqlalchemy import func
    from app.tenants.hospitales.models import TenantModule

    rol = await obtener(db, RolSistema, rol_sistema_id, tenant_id)
    if not rol:
        raise ValueError("El rol seleccionado no existe")
    if not rol.is_active:
        raise ValueError("El rol seleccionado está inactivo")

    # El módulo requerido por el rol debe estar activo para este hospital
    if rol.modulo_requerido:
        activo = await db.scalar(
            select(func.count(TenantModule.id)).where(
                TenantModule.tenant_id == tenant_id,
                TenantModule.module_code == rol.modulo_requerido,
                TenantModule.is_active == True,
            )
        )
        if not activo:
            raise ValueError(
                f"El rol requiere el módulo '{rol.modulo_requerido}', que no está activo para este hospital"
            )

    # Los módulos elegidos deben estar dentro de lo permitido por el rol
    permitidos = json.loads(rol.modulos_permitidos) if rol.modulos_permitidos else []
    if permitidos:
        no_permitidos = [m for m in modulos_acceso if m not in permitidos]
        if no_permitidos:
            raise ValueError(
                f"Estos módulos no están permitidos por el rol seleccionado: {', '.join(no_permitidos)}"
            )

async def crear_perfil(db: AsyncSession, tenant_id: uuid.UUID, data) -> dict:
    data_dict = data.model_dump()
    modulos = data_dict.pop('modulos_acceso', [])
    rol_sistema_id = data_dict.get('rol_sistema_id')
    if rol_sistema_id:
        await _validar_perfil_contra_rol(db, tenant_id, rol_sistema_id, modulos)
    perfil = PerfilUsuario(
        tenant_id=tenant_id,
        modulos_acceso=json.dumps(modulos),
        **data_dict
    )
    db.add(perfil)
    await db.commit()
    await db.refresh(perfil)
    return _serializar_perfil(perfil)

async def listar_perfiles_usuario(db: AsyncSession, tenant_id: uuid.UUID) -> list[dict]:
    items = await listar(db, PerfilUsuario, tenant_id)
    return [_serializar_perfil(i) for i in items]


async def obtener_perfil_usuario(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> dict | None:
    item = await obtener(db, PerfilUsuario, id, tenant_id)
    if not item:
        return None
    return _serializar_perfil(item)


async def actualizar_perfil_usuario(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> dict | None:
    item = await obtener(db, PerfilUsuario, id, tenant_id)
    if not item:
        return None
    data_dict = data.model_dump(exclude_unset=True)

    rol_sistema_id = data_dict.get('rol_sistema_id', item.rol_sistema_id)
    modulos_acceso = data_dict.get(
        'modulos_acceso',
        json.loads(item.modulos_acceso) if item.modulos_acceso else []
    )
    if rol_sistema_id:
        await _validar_perfil_contra_rol(db, tenant_id, rol_sistema_id, modulos_acceso)

    if "modulos_acceso" in data_dict:
        item.modulos_acceso = json.dumps(data_dict.pop("modulos_acceso"))
    for field, value in data_dict.items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return _serializar_perfil(item)
