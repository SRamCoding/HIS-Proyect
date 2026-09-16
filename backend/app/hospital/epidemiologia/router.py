import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.epidemiologia import schemas, service

router = APIRouter()
epi_user = require_any_module_jwt("epidemiologia")


def tid(user):
    return uuid.UUID(user["tenant_id"])


async def _crear_ficha_tipada(tipo_ficha: str, data: schemas.FichaCreateIn, db: AsyncSession, user: dict):
    from fastapi import HTTPException
    if data.tipo_ficha != tipo_ficha:
        raise HTTPException(400, detail=f"tipo_ficha debe ser {tipo_ficha} en este endpoint")
    return await service.crear_ficha(db, tid(user), user, data)


# ─── Ficha Covid ─────────────────────────────────────────────────────────

@router.get("/ficha-covid")
async def ficha_covid_listar(estado_envio: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(epi_user)):
    return await service.list_fichas(db, tid(user), "COVID", estado_envio)


@router.post("/ficha-covid", status_code=201)
async def ficha_covid_crear(data: schemas.FichaCreateIn, db: AsyncSession = Depends(get_db), user=Depends(epi_user)):
    return await _crear_ficha_tipada("COVID", data, db, user)


# ─── Ficha Cáncer ────────────────────────────────────────────────────────

@router.get("/ficha-cancer")
async def ficha_cancer_listar(estado_envio: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(epi_user)):
    return await service.list_fichas(db, tid(user), "CANCER", estado_envio)


@router.post("/ficha-cancer", status_code=201)
async def ficha_cancer_crear(data: schemas.FichaCreateIn, db: AsyncSession = Depends(get_db), user=Depends(epi_user)):
    return await _crear_ficha_tipada("CANCER", data, db, user)


# ─── Ficha Diabetes ──────────────────────────────────────────────────────

@router.get("/ficha-diabetes")
async def ficha_diabetes_listar(estado_envio: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(epi_user)):
    return await service.list_fichas(db, tid(user), "DIABETES", estado_envio)


@router.post("/ficha-diabetes", status_code=201)
async def ficha_diabetes_crear(data: schemas.FichaCreateIn, db: AsyncSession = Depends(get_db), user=Depends(epi_user)):
    return await _crear_ficha_tipada("DIABETES", data, db, user)


# ─── Ficha Dengue ────────────────────────────────────────────────────────

@router.get("/ficha-dengue")
async def ficha_dengue_listar(estado_envio: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(epi_user)):
    return await service.list_fichas(db, tid(user), "DENGUE", estado_envio)


@router.post("/ficha-dengue", status_code=201)
async def ficha_dengue_crear(data: schemas.FichaCreateIn, db: AsyncSession = Depends(get_db), user=Depends(epi_user)):
    return await _crear_ficha_tipada("DENGUE", data, db, user)


# ─── Ficha Leptospirosis ─────────────────────────────────────────────────

@router.get("/ficha-leptospirosis")
async def ficha_leptospirosis_listar(estado_envio: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(epi_user)):
    return await service.list_fichas(db, tid(user), "LEPTOSPIROSIS", estado_envio)


@router.post("/ficha-leptospirosis", status_code=201)
async def ficha_leptospirosis_crear(data: schemas.FichaCreateIn, db: AsyncSession = Depends(get_db), user=Depends(epi_user)):
    return await _crear_ficha_tipada("LEPTOSPIROSIS", data, db, user)


# ─── Ficha individual (compartido por tipo) ──────────────────────────────

@router.get("/fichas/{ficha_id}")
async def obtener_ficha(ficha_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(epi_user)):
    return await service.get_ficha(db, tid(user), ficha_id)


@router.post("/fichas/{ficha_id}/marcar-enviado")
async def marcar_enviado(ficha_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(epi_user)):
    return await service.marcar_enviado(db, tid(user), user, ficha_id)
