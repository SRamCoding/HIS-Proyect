import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.archivo_clinico.schemas import (
    DigitalizarRequest, HistoriaOut, HistoriasPage, MovimientosPage, PersonalArchivoOut,
)
from app.hospital.archivo_clinico import service

router = APIRouter()

MODULO_CODIGO = "archivo_clinico"

# La dependencia compartida delega en require_module_jwt y exige hospital del JWT.
archivo_user = require_any_module_jwt(MODULO_CODIGO)


@router.get("/historias", response_model=HistoriasPage)
async def listar_historias(
    q: str | None = Query(default=None, max_length=200),
    location: str | None = Query(default=None, max_length=50),
    is_digitized: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(archivo_user),
):
    return await service.list_historias(db, uuid.UUID(current_user["tenant_id"]),
        q, location, is_digitized, page, page_size)


@router.get("/historias/{record_id}/movimientos", response_model=MovimientosPage)
async def listar_movimientos(
    record_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(archivo_user),
):
    result = await service.list_movimientos(db, uuid.UUID(current_user["tenant_id"]),
                                           record_id, page, page_size)
    if result is None:
        raise HTTPException(404, detail="Historia clínica no encontrada")
    return result


@router.patch("/historias/{record_id}/digitalizar", response_model=HistoriaOut)
async def digitalizar_historia(
    record_id: uuid.UUID,
    data: DigitalizarRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(archivo_user),
):
    result = await service.set_digitalizada(db, uuid.UUID(current_user["tenant_id"]),
                                           record_id, data.is_digitized)
    if result is None:
        raise HTTPException(404, detail="Historia clínica no encontrada")
    return result


# Nota: no hay endpoints separados /hc-electronica, /historias-clinicas ni
# /movimientos-hc -- las 3 paginas del menu con esos nombres son vistas del
# mismo recurso real (/historias, /historias/{id}/movimientos), filtradas o
# tituladas distinto en el frontend (ver ArchivoClinicoPanel.vue).


@router.get("/personal-archivo", response_model=list[PersonalArchivoOut], summary="Personal con rol de archivo en este hospital")
async def personal_archivo(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(archivo_user),
):
    return await service.list_personal_archivo(db, uuid.UUID(current_user["tenant_id"]))
