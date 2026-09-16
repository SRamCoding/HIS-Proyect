import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.laboratorio import schemas, service

router = APIRouter()
lab_user = require_any_module_jwt("laboratorio")
# Ficha Covid: mismo registro clinico, accesible tambien desde Consulta Externa
# (el clinico puede llenarla ahi mismo sin necesitar el modulo Laboratorio activo) --
# sin duplicar la tabla ni el servicio, solo el gate de acceso es mas amplio.
covid_user = require_any_module_jwt("laboratorio", "consulta_externa")


def filters(q: str | None = Query(None, max_length=200),
            numero: str | None = Query(None, max_length=50),
            historia: str | None = Query(None, max_length=50),
            cuenta: str | None = Query(None, max_length=50),
            apellido: str | None = Query(None, max_length=100),
            materno: str | None = Query(None, max_length=100),
            dni: str | None = Query(None, max_length=30),
            fecha: date | None = None, estado: str | None = Query(None, max_length=30),
            tipos: list[schemas.TipoServicio] | None = Query(None)):
    return locals()


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/catalogos/{kind}")
async def catalogos(kind: str, q: str = Query("", max_length=200), db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.catalogs(db, tid(user), kind, q)


@router.get("/pacientes")
async def pacientes(q: str = Query(min_length=2, max_length=200), db: AsyncSession = Depends(get_db), user=Depends(covid_user)):
    return await service.patients(db, tid(user), q)


@router.get("/pacientes/{pid}/historial")
async def historial(pid: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.patient_history(db, tid(user), pid)


@router.get("/ordenes")
async def ordenes(f=Depends(filters), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                  db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.list_orders(db, tid(user), f, page, page_size)


@router.post("/ordenes", status_code=201)
async def crear_orden(data: schemas.OrdenCreate, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.create_order(db, tid(user), user, data)


@router.get("/ordenes/{oid}")
async def orden(oid: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.order_detail(db, tid(user), oid)


@router.get("/movimientos")
async def movimientos(f=Depends(filters), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                      db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.list_movements(db, tid(user), f, page, page_size)


@router.post("/movimientos", status_code=201)
async def crear_movimiento(data: schemas.MovimientoCreate, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.save_movement(db, tid(user), user, data)


@router.get("/movimientos/{mid}")
async def movimiento(mid: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.movement_detail(db, tid(user), mid)


@router.patch("/movimientos/{mid}")
async def editar_movimiento(mid: uuid.UUID, data: schemas.MovimientoUpdate, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.save_movement(db, tid(user), user, data, mid)


@router.put("/movimientos/{mid}/resultados")
async def resultados(mid: uuid.UUID, data: schemas.ResultadosEntrada, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.save_results(db, tid(user), user, mid, data)


@router.post("/movimientos/{mid}/{action}")
async def accion(mid: uuid.UUID, action: str, data: schemas.Accion, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.transition(db, tid(user), user, mid, action, data)


@router.get("/movimientos/{mid}/auditoria")
async def auditoria(mid: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.audits(db, tid(user), mid)


@router.get("/movimientos/{mid}/ticket.pdf")
async def ticket(mid: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return Response(await service.movement_pdf(db, tid(user), mid, "ticket"), media_type="application/pdf",
                    headers={"Content-Disposition": 'inline; filename="ticket-laboratorio.pdf"', "Cache-Control": "no-store"})


@router.get("/movimientos/{mid}/resultados.pdf")
async def informe(mid: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return Response(await service.movement_pdf(db, tid(user), mid, "resultados"), media_type="application/pdf",
                    headers={"Content-Disposition": 'inline; filename="resultados-laboratorio.pdf"', "Cache-Control": "no-store"})


@router.get("/cupos")
async def cupos(fecha: date | None = None, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.list_cupos(db, tid(user), fecha)


@router.post("/cupos", status_code=201)
async def crear_cupo(data: schemas.CupoEntrada, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.save_cupo(db, tid(user), user, data, True)


@router.put("/cupos")
async def editar_cupo(data: schemas.CupoEntrada, db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return await service.save_cupo(db, tid(user), user, data, False)


@router.get("/ficha-covid")
async def fichas(f=Depends(filters), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                 db: AsyncSession = Depends(get_db), user=Depends(covid_user)):
    return await service.list_covid(db, tid(user), f, page, page_size)


@router.post("/ficha-covid", status_code=201)
async def crear_ficha(data: schemas.CovidEntrada, db: AsyncSession = Depends(get_db), user=Depends(covid_user)):
    return await service.save_covid(db, tid(user), user, data)


@router.patch("/ficha-covid/{cid}")
async def editar_ficha(cid: uuid.UUID, data: schemas.CovidUpdate, db: AsyncSession = Depends(get_db), user=Depends(covid_user)):
    return await service.save_covid(db, tid(user), user, data, cid)


@router.get("/ficha-covid/{cid}/reporte.pdf")
async def ficha_pdf(cid: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(covid_user)):
    return Response(await service.covid_pdf(db, tid(user), cid), media_type="application/pdf",
                    headers={"Content-Disposition": 'inline; filename="ficha-covid.pdf"', "Cache-Control": "no-store"})


@router.get("/reportes/{kind}.csv")
async def exportar(kind: str, f=Depends(filters), db: AsyncSession = Depends(get_db), user=Depends(lab_user)):
    return Response(await service.export_csv(db, tid(user), kind, f), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="laboratorio-{kind}.csv"', "Cache-Control": "no-store"})
