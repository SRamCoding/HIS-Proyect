import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.hospitalizacion import schemas, service

router = APIRouter()
hosp_user = require_any_module_jwt("hospitalizacion")
# Seguimiento Paciente es el único item de nav del módulo "seguimiento" — necesita
# listar/ver hospitalizaciones y sus notas de evolución sin el módulo "hospitalizacion" completo.
seguimiento_user = require_any_module_jwt("hospitalizacion", "seguimiento")


def tid(user):
    return uuid.UUID(user["tenant_id"])


# --- Panel de Camas ---
@router.get("/pisos", response_model=list[schemas.PisoOut])
async def listar_pisos(db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.get_pisos(db, tid(user))


@router.get("/panel-camas", response_model=list[schemas.CamaConPacienteOut])
async def panel_camas(piso_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.get_panel_camas(db, tid(user), piso_id)


@router.get("/camas-disponibles")
async def camas_disponibles(servicio_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.camas_disponibles(db, tid(user), servicio_id)


@router.get("/catalogos/{kind}")
async def catalogos(kind: str, q: str = Query("", max_length=200), db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.catalogs(db, tid(user), kind, q)


# --- Admisión desde Emergencia ---
@router.get("/emergencia-pendientes")
async def destinos_pendientes(destino: str = "HOSPITALIZACION", db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.destinos_emergencia_pendientes(db, tid(user), destino)


@router.post("/hospitalizaciones/admitir-emergencia", status_code=201)
async def admitir_desde_emergencia(data: schemas.AdmisionDesdeEmergencia, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.admitir_desde_emergencia(db, tid(user), user, data)


# --- Hospitalizaciones ---
@router.get("/hospitalizaciones")
async def hospitalizaciones(q: str | None = None, estado: str | None = None, origen: str | None = None,
                            page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                            db: AsyncSession = Depends(get_db), user=Depends(seguimiento_user)):
    f = {"q": q, "estado": estado, "origen": origen}
    return await service.list_hospitalizaciones(db, tid(user), f, page, page_size)


@router.get("/hospitalizaciones/{hosp_id}")
async def hospitalizacion(hosp_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(seguimiento_user)):
    return await service.hospitalizacion_detalle(db, tid(user), hosp_id)


@router.post("/hospitalizaciones/{hosp_id}/alta")
async def dar_alta(hosp_id: uuid.UUID, data: schemas.AltaHospitalizacion, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.dar_alta(db, tid(user), user, hosp_id, data)


# --- Seguimiento del paciente (notas de evolución) ---
@router.get("/hospitalizaciones/{hosp_id}/notas")
async def notas(hosp_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(seguimiento_user)):
    return await service.listar_notas(db, tid(user), hosp_id)


@router.post("/hospitalizaciones/{hosp_id}/notas", status_code=201)
async def crear_nota(hosp_id: uuid.UUID, data: schemas.NotaEvolucionCreate, db: AsyncSession = Depends(get_db), user=Depends(seguimiento_user)):
    return await service.crear_nota(db, tid(user), user, hosp_id, data)


# --- Interconsultas intrahospitalarias ---
@router.get("/interconsultas")
async def todas_interconsultas(estado: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.listar_todas_interconsultas(db, tid(user), estado)


@router.post("/interconsultas/admitir-emergencia", status_code=201)
async def admitir_interconsulta_desde_emergencia(data: schemas.AdmitirInterconsultaEmergencia, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.admitir_interconsulta_desde_emergencia(db, tid(user), user, data)


@router.get("/hospitalizaciones/{hosp_id}/interconsultas")
async def interconsultas(hosp_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.listar_interconsultas(db, tid(user), hosp_id)


@router.post("/hospitalizaciones/{hosp_id}/interconsultas", status_code=201)
async def crear_interconsulta(hosp_id: uuid.UUID, data: schemas.InterconsultaHospCreate, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.crear_interconsulta(db, tid(user), user, hosp_id, data)


# --- Consentimientos informados ---
@router.get("/consentimientos")
async def todos_consentimientos(estado: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.listar_todos_consentimientos(db, tid(user), estado)


@router.get("/hospitalizaciones/{hosp_id}/consentimientos")
async def consentimientos(hosp_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.listar_consentimientos(db, tid(user), hosp_id)


@router.post("/hospitalizaciones/{hosp_id}/consentimientos", status_code=201)
async def crear_consentimiento(hosp_id: uuid.UUID, data: schemas.ConsentimientoCreate, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.crear_consentimiento(db, tid(user), user, hosp_id, data)


@router.post("/consentimientos/{consentimiento_id}/revocar")
async def revocar_consentimiento(consentimiento_id: uuid.UUID, data: schemas.ConsentimientoRevocar, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.revocar_consentimiento(db, tid(user), user, consentimiento_id, data)


@router.get("/consentimientos/{consentimiento_id}/comprobante.pdf")
async def consentimiento_pdf(consentimiento_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return Response(await service.consentimiento_pdf(db, tid(user), consentimiento_id), media_type="application/pdf",
                    headers={"Content-Disposition": 'inline; filename="consentimiento.pdf"', "Cache-Control": "no-store"})


# --- Censo diario ---
@router.get("/censo-diario")
async def censo_diario(fecha: date | None = None, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return await service.censo_diario(db, tid(user), fecha or date.today())


@router.get("/censo-diario/reporte.pdf")
async def censo_pdf(fecha: date | None = None, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return Response(await service.censo_pdf(db, tid(user), fecha or date.today()), media_type="application/pdf",
                    headers={"Content-Disposition": 'inline; filename="censo-diario.pdf"', "Cache-Control": "no-store"})


@router.get("/censo-diario/reporte.csv")
async def censo_csv(fecha: date | None = None, db: AsyncSession = Depends(get_db), user=Depends(hosp_user)):
    return Response(await service.export_censo_csv(db, tid(user), fecha or date.today()), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="censo-diario.csv"', "Cache-Control": "no-store"})
