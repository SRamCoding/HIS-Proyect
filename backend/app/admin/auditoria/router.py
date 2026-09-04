# backend/app/admin/auditoria/router.py
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.admin.auditoria.schemas import AuditLogResponse
from app.admin.auditoria.service import get_audit_logs

router = APIRouter()


@router.get("/auditoria", response_model=list[AuditLogResponse], summary="Auditoría del ERP")
async def auditoria_erp(
    limit: int = 100,
    only_global: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_audit_logs(db, only_global=only_global, limit=limit)


@router.get("/auditoria/hospital/{tenant_id}", response_model=list[AuditLogResponse], summary="Auditoría por hospital")
async def auditoria_hospital(
    tenant_id: uuid.UUID,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    return await get_audit_logs(db, tenant_id=tenant_id, limit=limit)