import uuid
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.hemodialisis import schemas, service

router = APIRouter()
hd_user = require_any_module_jwt("hemodialisis")


def tid(user):
    return uuid.UUID(user["tenant_id"])


# ─── Hemodialis: programa de pacientes ──────────────────────────────────────

@router.get("/hemodialis")
async def pacientes(estado: str | None = None, q: str = "", db: AsyncSession = Depends(get_db), user=Depends(hd_user)):
    return await service.list_pacientes(db, tid(user), estado, q)


@router.post("/hemodialis", status_code=201)
async def crear_paciente(data: schemas.PacienteCreateIn, db: AsyncSession = Depends(get_db), user=Depends(hd_user)):
    return await service.crear_paciente(db, tid(user), user, data)


@router.get("/hemodialis/{paciente_id}")
async def paciente(paciente_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(hd_user)):
    return await service.get_paciente(db, tid(user), paciente_id)


@router.patch("/hemodialis/{paciente_id}")
async def actualizar_paciente(paciente_id: uuid.UUID, data: schemas.PacienteUpdateIn,
                               db: AsyncSession = Depends(get_db), user=Depends(hd_user)):
    return await service.update_paciente(db, tid(user), user, paciente_id, data)


@router.post("/hemodialis/{paciente_id}/estado")
async def cambiar_estado_paciente(paciente_id: uuid.UUID, data: schemas.PacienteEstadoIn,
                                   db: AsyncSession = Depends(get_db), user=Depends(hd_user)):
    return await service.cambiar_estado_paciente(db, tid(user), user, paciente_id, data)


# ─── Sesiones ────────────────────────────────────────────────────────────

@router.get("/sesiones")
async def sesiones(paciente_hemodialisis_id: uuid.UUID | None = None, fecha: date | None = None,
                    estado: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(hd_user)):
    return await service.list_sesiones(db, tid(user), paciente_hemodialisis_id, fecha, estado)


@router.post("/sesiones", status_code=201)
async def crear_sesion(data: schemas.SesionCreateIn, db: AsyncSession = Depends(get_db), user=Depends(hd_user)):
    return await service.crear_sesion(db, tid(user), user, data)


@router.post("/sesiones/{sesion_id}/estado")
async def cambiar_estado_sesion(sesion_id: uuid.UUID, data: schemas.SesionEstadoIn,
                                 db: AsyncSession = Depends(get_db), user=Depends(hd_user)):
    return await service.cambiar_estado_sesion(db, tid(user), user, sesion_id, data)
