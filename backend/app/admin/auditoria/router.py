# backend/app/admin/auditoria/router.py
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.auditoria.schemas import AuditLogResponse
from app.admin.auditoria.service import get_audit_logs, get_audit_summary, LIMIT_MAXIMO

router = APIRouter()


@router.get("/auditoria", summary="Auditoría del ERP")
async def auditoria_erp(
    limit: int = Query(50, ge=1, le=LIMIT_MAXIMO),
    offset: int = Query(0, ge=0),
    q: str | None = None,
    action: str | None = None,
    only_global: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    items, total = await get_audit_logs(db, only_global=only_global, limit=limit, offset=offset, q=q, action=action)
    return {"items": [AuditLogResponse.model_validate(i) for i in items], "total": total}


@router.get("/auditoria/hospital/{tenant_id}", summary="Auditoría por hospital")
async def auditoria_hospital(
    tenant_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=LIMIT_MAXIMO),
    offset: int = Query(0, ge=0),
    q: str | None = None,
    action: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    items, total = await get_audit_logs(db, tenant_id=tenant_id, limit=limit, offset=offset, q=q, action=action)
    return {"items": [AuditLogResponse.model_validate(i) for i in items], "total": total}


@router.get("/auditoria/resumen", summary="Agregados de auditoría (global o por hospital)")
async def auditoria_resumen(
    tenant_id: uuid.UUID | None = None,
    only_global: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_audit_summary(db, tenant_id=tenant_id, only_global=only_global)


@router.get("/auditoria/fallback", summary="Eventos de auditoría pendientes de recuperar")
async def auditoria_fallback_estado(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    """Cuantos eventos quedaron atrapados porque AuditLog no los acepto en
    su momento (ver app/core/audit.py). Un fallo de auditoria no debe
    quedar invisible: si esto no vuelve a 0 solo, hay que mirar por que la
    escritura sigue fallando. `pendientes_emergencia` solo deberia
    aparecer si la BD central estuvo totalmente inalcanzable en algun
    momento (ver _FALLBACK_ARCHIVO_ULTIMO_RECURSO)."""
    from sqlalchemy import func
    from app.core.audit import _FALLBACK_ARCHIVO_ULTIMO_RECURSO
    from app.admin.auditoria.models import AuditLogFallback

    pendientes = await db.scalar(select(func.count()).select_from(AuditLogFallback))
    pendientes_emergencia = 0
    if _FALLBACK_ARCHIVO_ULTIMO_RECURSO.exists():
        with open(_FALLBACK_ARCHIVO_ULTIMO_RECURSO, "r", encoding="utf-8") as f:
            pendientes_emergencia = sum(1 for linea in f if linea.strip())
    return {"pendientes": pendientes, "pendientes_emergencia": pendientes_emergencia}


@router.post("/auditoria/fallback/reintentar", summary="Reintentar eventos de auditoría pendientes")
async def auditoria_fallback_reintentar(current_user: dict = Depends(get_admin_user)):
    from app.core.audit import reintentar_fallback_pendiente
    return await reintentar_fallback_pendiente()