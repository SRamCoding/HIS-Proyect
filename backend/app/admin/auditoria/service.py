# backend/app/admin/auditoria/service.py
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.admin.auditoria.models import AuditLog


async def get_audit_logs(
    db: AsyncSession,
    tenant_id: uuid.UUID | None = None,
    only_global: bool = False,
    limit: int = 100,
) -> list[AuditLog]:
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if only_global:
        query = query.where(AuditLog.tenant_id.is_(None))
    elif tenant_id:
        query = query.where(AuditLog.tenant_id == tenant_id)
    result = await db.execute(query)
    return result.scalars().all()


async def create_audit_log(
    db: AsyncSession,
    user_id: uuid.UUID | None,
    user_name: str | None,
    tenant_id: uuid.UUID | None,
    tenant_name: str | None,
    action: str,
    model: str | None = None,
    model_id: str | None = None,
    description: str | None = None,
    old_values: dict | None = None,
    new_values: dict | None = None,
    ip_address: str | None = None,
) -> None:
    log = AuditLog(
        user_id=user_id,
        user_name=user_name,
        tenant_id=tenant_id,
        tenant_name=tenant_name,
        action=action,
        model=model,
        model_id=model_id,
        description=description,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
    )
    db.add(log)
    await db.commit()