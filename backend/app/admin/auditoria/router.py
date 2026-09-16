# backend/app/admin/auditoria/router.py
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.auditoria.schemas import AuditLogResponse
from app.admin.auditoria.service import get_audit_logs, get_audit_summary

router = APIRouter()


@router.get("/auditoria", summary="Auditoría del ERP")
async def auditoria_erp(
    limit: int = 50,
    offset: int = 0,
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
    limit: int = 50,
    offset: int = 0,
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