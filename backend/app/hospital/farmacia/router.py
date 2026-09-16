import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.farmacia import schemas, service

router = APIRouter()
pharmacy_user = require_any_module_jwt("farmacia")


def tid(u):
    return uuid.UUID(u["tenant_id"])


@router.get("/catalogos/{kind}")
async def catalogos(kind: str, q: str = "", db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.catalogs(db, tid(user), kind, q)


@router.get("/recetas")
async def recetas(estado: str | None = None, q: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.list_recipes(db, tid(user), estado, q)


@router.get("/recetas/{rid}")
async def receta(rid: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.recipe_detail(db, tid(user), rid)


@router.post("/recetas/{rid}/dispensar", status_code=201)
async def dispensar(rid: uuid.UUID, data: schemas.DispensarIn, db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.dispense(db, tid(user), user, rid, data)


@router.get("/movimientos")
async def movimientos(tipo: str | None = None, ambito: str | None = None, almacen_id: uuid.UUID | None = None,
                      fecha_desde: date | None = None, fecha_hasta: date | None = None, q: str | None = None,
                      concepto: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                      db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.list_movements(db, tid(user), tipo, ambito, almacen_id, fecha_desde, fecha_hasta, q, page, page_size, concepto)


@router.post("/movimientos", status_code=201)
async def crear_movimiento(data: schemas.MovimientoIn, db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.create_movement(db, tid(user), user, data)


@router.get("/movimientos/{mid}")
async def movimiento(mid: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.movement_detail(db, tid(user), mid)


@router.post("/movimientos/{mid}/anular")
async def anular_movimiento(mid: uuid.UUID, data: schemas.AnulacionIn, db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.cancel_movement(db, tid(user), user, mid, data.motivo)


@router.get("/saldos")
async def saldos(almacen_id: uuid.UUID | None = None, q: str | None = None, dias_vencimiento: int = Query(90, ge=0, le=730),
                 db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.list_stock(db, tid(user), almacen_id, q, dias_vencimiento)


@router.get("/farmacotecnia")
async def farmacotecnia(estado: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.list_farmacotecnia(db, tid(user), estado)


@router.post("/farmacotecnia", status_code=201)
async def crear_farmacotecnia(data: schemas.FarmacotecniaIn, db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.create_farmacotecnia(db, tid(user), user, data)


@router.patch("/farmacotecnia/{oid}")
async def estado_farmacotecnia(oid: uuid.UUID, data: schemas.FarmacotecniaEstado, db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.update_farmacotecnia_estado(db, tid(user), user, oid, data)


@router.get("/reportes/{kind}/datos")
async def reporte(kind: str, fecha_desde: date | None = None, fecha_hasta: date | None = None,
                  almacen_id: uuid.UUID | None = None, q: str | None = None,
                  db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return await service.report(db, tid(user), kind, fecha_desde, fecha_hasta, almacen_id, q)


@router.get("/reportes/{kind}.csv")
async def reporte_csv(kind: str, fecha_desde: date | None = None, fecha_hasta: date | None = None,
                      almacen_id: uuid.UUID | None = None, q: str | None = None,
                      db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return Response(await service.csv_report(db, tid(user), kind, fecha_desde, fecha_hasta, almacen_id, q),
        media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="farmacia-{kind}.csv"', "Cache-Control": "no-store"})


@router.get("/reportes/{kind}.pdf")
async def reporte_pdf(kind: str, fecha_desde: date | None = None, fecha_hasta: date | None = None,
                      almacen_id: uuid.UUID | None = None, q: str | None = None,
                      db: AsyncSession = Depends(get_db), user=Depends(pharmacy_user)):
    return Response(await service.pdf_report(db, tid(user), kind, fecha_desde, fecha_hasta, almacen_id, q),
        media_type="application/pdf", headers={"Content-Disposition": f'inline; filename="farmacia-{kind}.pdf"', "Cache-Control": "no-store"})
