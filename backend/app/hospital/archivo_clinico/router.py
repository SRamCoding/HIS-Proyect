import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from typing import Literal
from starlette.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_db_central
from app.tenants.entitlements import require_any_module_jwt
from app.hospital.archivo_clinico.schemas import (
    DigitalizarRequest, HistoriaOut, HistoriasPage, MovimientosPage, PersonalArchivoOut,
)
from app.hospital.archivo_clinico import service

router = APIRouter()

MODULO_CODIGO = "archivo_clinico"

# La dependencia compartida delega en require_module_jwt y exige hospital del JWT.
archivo_user = require_any_module_jwt(MODULO_CODIGO)


@router.get("/historias/{record_id}/pdf", summary="Exportar ficha o expediente clínico en PDF")
async def exportar_historia_pdf(
    record_id: uuid.UUID,
    request: Request,
    alcance: Literal["completa", "ficha"] = "completa",
    db: AsyncSession = Depends(get_db),
    central: AsyncSession = Depends(get_db_central),
    current_user: dict = Depends(archivo_user),
):
    from app.hospital.archivo_clinico.pdf import collect, render
    from app.tenants.hospitales.models import Tenant
    from app.admin.auditoria.models import AuditLog

    tid = uuid.UUID(current_user["tenant_id"])
    record, patient, entries, lookup = await collect(db, tid, record_id, alcance == "completa")
    hospital = await central.get(Tenant, tid)
    if hospital is None:
        raise HTTPException(404, "Hospital no encontrado")
    institution = {k: getattr(hospital, k) for k in ("name", "ruc", "address", "phone", "logo_url")}
    pdf = await run_in_threadpool(render, record, patient, entries, lookup, institution, alcance == "completa")
    central.add(AuditLog(user_id=uuid.UUID(current_user["sub"]), user_name=current_user.get("name"),
        tenant_id=tid, tenant_name=hospital.name, action="hc_pdf_exportada", model="ClinicalRecord",
        model_id=str(record_id), description=f"Exportación de HC: {alcance}",
        ip_address=request.client.host if request.client else None))
    await central.flush()
    return Response(pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'attachment; filename="HC-{record_id}-{alcance}.pdf"',
        "Cache-Control": "no-store, private", "Pragma": "no-cache",
        "X-Content-Type-Options": "nosniff",
    })


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
