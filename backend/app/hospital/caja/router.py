import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.caja import schemas, service

router = APIRouter()
caja_user = require_any_module_jwt("caja")


def tid(user):
    return uuid.UUID(user["tenant_id"])


@router.get("/catalogos/{kind}")
async def catalogos(kind: str, q: str = Query("", max_length=200), db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    return await service.catalogs(db, tid(user), kind, q)


@router.get("/cuentas/buscar")
async def buscar_cuentas(q: str = Query(min_length=2, max_length=200), db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    return await service.buscar_cuentas(db, tid(user), q)


@router.get("/cuentas/{numero_cuenta}")
async def cuenta(numero_cuenta: str, db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    return await service.cuenta_detalle(db, tid(user), numero_cuenta)


@router.get("/sesiones/mi-turno")
async def mi_turno(db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    sesion_id = None
    if user.get("empleado_id"):
        sesion = await service.sesion_activa_usuario(db, tid(user), uuid.UUID(user["empleado_id"]))
        sesion_id = sesion.id if sesion else None
    return await service.sesion_detalle(db, tid(user), sesion_id) if sesion_id else None


@router.get("/sesiones")
async def sesiones(estado: str | None = None, caja_id: uuid.UUID | None = None,
                   page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                   db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    return await service.list_sesiones(db, tid(user), {"estado": estado, "caja_id": caja_id}, page, page_size)


@router.post("/sesiones", status_code=201)
async def abrir_sesion(data: schemas.SesionAbrir, db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    return await service.abrir_sesion(db, tid(user), user, data)


@router.get("/sesiones/{sesion_id}")
async def sesion(sesion_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    return await service.sesion_detalle(db, tid(user), sesion_id)


@router.post("/sesiones/{sesion_id}/cerrar")
async def cerrar_sesion(sesion_id: uuid.UUID, data: schemas.SesionCerrar, db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    return await service.cerrar_sesion(db, tid(user), user, sesion_id, data)


@router.post("/sesiones/{sesion_id}/cobros", status_code=201)
async def crear_cobro(sesion_id: uuid.UUID, data: schemas.CobroCreate, db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    return await service.crear_cobro(db, tid(user), user, sesion_id, data)


@router.get("/cobros")
async def cobros(numero: str | None = Query(None, max_length=50), cuenta: str | None = Query(None, max_length=50),
                 estado: str | None = None, forma_pago: str | None = None, fecha: date | None = None,
                 page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                 db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    f = {"numero": numero, "cuenta": cuenta, "estado": estado, "forma_pago": forma_pago, "fecha": fecha}
    return await service.list_cobros(db, tid(user), f, page, page_size)


@router.get("/cobros/{cobro_id}")
async def cobro(cobro_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    return await service.cobro_detalle(db, tid(user), cobro_id)


@router.post("/cobros/{cobro_id}/anular")
async def anular_cobro(cobro_id: uuid.UUID, data: schemas.Anulacion, db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    return await service.anular_cobro(db, tid(user), user, cobro_id, data.motivo)


@router.get("/cobros/{cobro_id}/comprobante.pdf")
async def comprobante(cobro_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    return Response(await service.comprobante_pdf(db, tid(user), cobro_id), media_type="application/pdf",
                    headers={"Content-Disposition": 'inline; filename="comprobante-caja.pdf"', "Cache-Control": "no-store"})


@router.get("/reportes/cobros.csv")
async def exportar(numero: str | None = Query(None, max_length=50), cuenta: str | None = Query(None, max_length=50),
                   estado: str | None = None, forma_pago: str | None = None, fecha: date | None = None,
                   db: AsyncSession = Depends(get_db), user=Depends(caja_user)):
    f = {"numero": numero, "cuenta": cuenta, "estado": estado, "forma_pago": forma_pago, "fecha": fecha}
    return Response(await service.export_csv(db, tid(user), f), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="caja-cobros.csv"', "Cache-Control": "no-store"})
