from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.tenants.hospitales.models import Tenant

router = APIRouter()

LIMITE_POR_GRUPO = 5


@router.get("/buscar", summary="Búsqueda global (hospitales y cuentas admin)")
async def buscar(
    q: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    """Busca por nombre/dominio en hospitales y por nombre/correo en cuentas
    admin de la BD central. No busca en las cuentas App/SIGARH de cada
    hospital (viven en bases físicas separadas): recorrer todas para una
    caja de busqueda global seria caro y lento -- mismo criterio ya usado
    en el dashboard, que aclara "BD central" en sus tarjetas de usuarios en
    vez de mezclar ámbitos distintos."""
    termino = q.strip()
    if len(termino) < 2:
        return {"hospitales": [], "usuarios": []}

    patron = f"%{termino}%"
    hospitales = (await db.scalars(
        select(Tenant)
        .where(or_(Tenant.name.ilike(patron), Tenant.domain.ilike(patron)))
        .order_by(Tenant.name)
        .limit(LIMITE_POR_GRUPO)
    )).all()
    usuarios = (await db.scalars(
        select(User)
        .where(User.is_superadmin.is_(False))
        .where(or_(User.name.ilike(patron), User.email.ilike(patron)))
        .order_by(User.name)
        .limit(LIMITE_POR_GRUPO)
    )).all()

    return {
        "hospitales": [{"id": str(h.id), "name": h.name, "domain": h.domain} for h in hospitales],
        "usuarios": [
            {"id": str(u.id), "name": u.name, "email": u.email, "tenant_id": str(u.tenant_id) if u.tenant_id else None}
            for u in usuarios
        ],
    }
