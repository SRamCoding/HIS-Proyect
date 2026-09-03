import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.sigarh.rrhh.models import (
    Empleado, Especialidad, EmpleadoEspecialidad,
    DiasFeriado, MotivoJustificacion, Tolerancia,
    RegistroAsistencia, Justificacion
)
from app.sigarh.rrhh.schemas import (
    EmpleadoCreate, EmpleadoUpdate,
    EmpleadoEspecialidadCreate,
)


# ─── Empleados ────────────────────────────────────────────────────────────────

async def listar_empleados(db: AsyncSession, tenant_id: uuid.UUID) -> list[Empleado]:
    result = await db.execute(
        select(Empleado)
        .where(Empleado.tenant_id == tenant_id)
        .order_by(Empleado.apellido_paterno)
    )
    return result.scalars().all()


async def obtener_empleado(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> Empleado | None:
    result = await db.execute(
        select(Empleado)
        .options(selectinload(Empleado.especialidades))
        .where(Empleado.id == id, Empleado.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def obtener_empleado_por_dni(db: AsyncSession, dni: str, tenant_id: uuid.UUID) -> Empleado | None:
    result = await db.execute(
        select(Empleado)
        .where(Empleado.dni == dni, Empleado.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def crear_empleado(db: AsyncSession, tenant_id: uuid.UUID, data: EmpleadoCreate) -> Empleado:
    empleado = Empleado(tenant_id=tenant_id, **data.model_dump())
    db.add(empleado)
    await db.commit()
    await db.refresh(empleado)
    return empleado


async def actualizar_empleado(
    db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data: EmpleadoUpdate
) -> Empleado | None:
    empleado = await obtener_empleado(db, id, tenant_id)
    if not empleado:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(empleado, field, value)
    await db.commit()
    await db.refresh(empleado)
    return empleado


async def eliminar_empleado(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    empleado = await obtener_empleado(db, id, tenant_id)
    if not empleado:
        return False
    await db.delete(empleado)
    await db.commit()
    return True


# ─── Especialidades del empleado ──────────────────────────────────────────────

async def agregar_especialidad(
    db: AsyncSession,
    empleado_id: uuid.UUID,
    data: EmpleadoEspecialidadCreate,
) -> EmpleadoEspecialidad:
    esp = EmpleadoEspecialidad(
        empleado_id=empleado_id,
        **data.model_dump()
    )
    db.add(esp)
    await db.commit()
    await db.refresh(esp)
    return esp


async def eliminar_especialidad(db: AsyncSession, id: uuid.UUID) -> bool:
    result = await db.execute(
        select(EmpleadoEspecialidad).where(EmpleadoEspecialidad.id == id)
    )
    esp = result.scalar_one_or_none()
    if not esp:
        return False
    await db.delete(esp)
    await db.commit()
    return True


# ─── Catálogo de Especialidades ───────────────────────────────────────────────

async def listar_especialidades(db: AsyncSession, tenant_id: uuid.UUID) -> list[Especialidad]:
    result = await db.execute(
        select(Especialidad)
        .where(Especialidad.tenant_id == tenant_id)
        .order_by(Especialidad.nombre)
    )
    return result.scalars().all()


async def crear_especialidad(db: AsyncSession, tenant_id: uuid.UUID, data) -> Especialidad:
    esp = Especialidad(tenant_id=tenant_id, **data.model_dump())
    db.add(esp)
    await db.commit()
    await db.refresh(esp)
    return esp


async def actualizar_especialidad(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Especialidad | None:
    result = await db.execute(
        select(Especialidad).where(Especialidad.id == id, Especialidad.tenant_id == tenant_id)
    )
    esp = result.scalar_one_or_none()
    if not esp:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(esp, field, value)
    await db.commit()
    await db.refresh(esp)
    return esp


async def eliminar_especialidad_catalogo(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Especialidad).where(Especialidad.id == id, Especialidad.tenant_id == tenant_id)
    )
    esp = result.scalar_one_or_none()
    if not esp:
        return False
    await db.delete(esp)
    await db.commit()
    return True


# ─── Días Feriados ────────────────────────────────────────────────────────────

async def listar_feriados(db: AsyncSession, tenant_id: uuid.UUID) -> list[DiasFeriado]:
    result = await db.execute(
        select(DiasFeriado)
        .where(DiasFeriado.tenant_id == tenant_id)
        .order_by(DiasFeriado.fecha)
    )
    return result.scalars().all()


async def crear_feriado(db: AsyncSession, tenant_id: uuid.UUID, data) -> DiasFeriado:
    feriado = DiasFeriado(tenant_id=tenant_id, **data.model_dump())
    db.add(feriado)
    await db.commit()
    await db.refresh(feriado)
    return feriado


async def actualizar_feriado(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> DiasFeriado | None:
    result = await db.execute(
        select(DiasFeriado).where(DiasFeriado.id == id, DiasFeriado.tenant_id == tenant_id)
    )
    feriado = result.scalar_one_or_none()
    if not feriado:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(feriado, field, value)
    await db.commit()
    await db.refresh(feriado)
    return feriado


async def eliminar_feriado(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(DiasFeriado).where(DiasFeriado.id == id, DiasFeriado.tenant_id == tenant_id)
    )
    feriado = result.scalar_one_or_none()
    if not feriado:
        return False
    await db.delete(feriado)
    await db.commit()
    return True


# ─── Motivos Justificación ────────────────────────────────────────────────────

async def listar_motivos(db: AsyncSession, tenant_id: uuid.UUID) -> list[MotivoJustificacion]:
    result = await db.execute(
        select(MotivoJustificacion)
        .where(MotivoJustificacion.tenant_id == tenant_id)
        .order_by(MotivoJustificacion.nombre)
    )
    return result.scalars().all()


async def crear_motivo(db: AsyncSession, tenant_id: uuid.UUID, data) -> MotivoJustificacion:
    motivo = MotivoJustificacion(tenant_id=tenant_id, **data.model_dump())
    db.add(motivo)
    await db.commit()
    await db.refresh(motivo)
    return motivo


async def actualizar_motivo(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> MotivoJustificacion | None:
    result = await db.execute(
        select(MotivoJustificacion).where(MotivoJustificacion.id == id, MotivoJustificacion.tenant_id == tenant_id)
    )
    motivo = result.scalar_one_or_none()
    if not motivo:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(motivo, field, value)
    await db.commit()
    await db.refresh(motivo)
    return motivo


async def eliminar_motivo(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(MotivoJustificacion).where(MotivoJustificacion.id == id, MotivoJustificacion.tenant_id == tenant_id)
    )
    motivo = result.scalar_one_or_none()
    if not motivo:
        return False
    await db.delete(motivo)
    await db.commit()
    return True


# ─── Tolerancias ──────────────────────────────────────────────────────────────

async def listar_tolerancias(db: AsyncSession, tenant_id: uuid.UUID) -> list[Tolerancia]:
    result = await db.execute(
        select(Tolerancia)
        .where(Tolerancia.tenant_id == tenant_id)
        .order_by(Tolerancia.nombre)
    )
    return result.scalars().all()


async def crear_tolerancia(db: AsyncSession, tenant_id: uuid.UUID, data) -> Tolerancia:
    tolerancia = Tolerancia(tenant_id=tenant_id, **data.model_dump())
    db.add(tolerancia)
    await db.commit()
    await db.refresh(tolerancia)
    return tolerancia


async def actualizar_tolerancia(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data) -> Tolerancia | None:
    result = await db.execute(
        select(Tolerancia).where(Tolerancia.id == id, Tolerancia.tenant_id == tenant_id)
    )
    tolerancia = result.scalar_one_or_none()
    if not tolerancia:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tolerancia, field, value)
    await db.commit()
    await db.refresh(tolerancia)
    return tolerancia


async def eliminar_tolerancia(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Tolerancia).where(Tolerancia.id == id, Tolerancia.tenant_id == tenant_id)
    )
    tolerancia = result.scalar_one_or_none()
    if not tolerancia:
        return False
    await db.delete(tolerancia)
    await db.commit()
    return True


# ─── Registro Asistencia ──────────────────────────────────────────────────────

async def listar_asistencia(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    fecha: date | None = None,
    empleado_id: uuid.UUID | None = None,
) -> list[RegistroAsistencia]:
    query = select(RegistroAsistencia).where(RegistroAsistencia.tenant_id == tenant_id)
    if fecha:
        query = query.where(RegistroAsistencia.fecha == fecha)
    if empleado_id:
        query = query.where(RegistroAsistencia.empleado_id == empleado_id)
    query = query.order_by(RegistroAsistencia.fecha.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def crear_asistencia(db: AsyncSession, tenant_id: uuid.UUID, data) -> RegistroAsistencia:
    asistencia = RegistroAsistencia(tenant_id=tenant_id, **data.model_dump())
    db.add(asistencia)
    await db.commit()
    await db.refresh(asistencia)
    return asistencia


# ─── Justificaciones ──────────────────────────────────────────────────────────

async def listar_justificaciones(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    empleado_id: uuid.UUID | None = None,
    estado: str | None = None,
) -> list[Justificacion]:
    query = select(Justificacion).where(Justificacion.tenant_id == tenant_id)
    if empleado_id:
        query = query.where(Justificacion.empleado_id == empleado_id)
    if estado:
        query = query.where(Justificacion.estado == estado)
    query = query.order_by(Justificacion.fecha_inicio.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def crear_justificacion(db: AsyncSession, tenant_id: uuid.UUID, data) -> Justificacion:
    justificacion = Justificacion(tenant_id=tenant_id, **data.model_dump())
    db.add(justificacion)
    await db.commit()
    await db.refresh(justificacion)
    return justificacion


async def actualizar_justificacion(db: AsyncSession, id: uuid.UUID, tenant_id: uuid.UUID, data: dict) -> Justificacion | None:
    result = await db.execute(
        select(Justificacion).where(Justificacion.id == id, Justificacion.tenant_id == tenant_id)
    )
    justificacion = result.scalar_one_or_none()
    if not justificacion:
        return None
    for field, value in data.items():
        if hasattr(justificacion, field):
            setattr(justificacion, field, value)
    await db.commit()
    await db.refresh(justificacion)
    return justificacion