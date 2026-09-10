"""API de catálogos; permisos explícitos y contratos consistentes en todas las rutas."""
import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.sigarh.mantenimiento import service as svc
from app.sigarh.mantenimiento.schemas import esquema_parcial
from app.sigarh.mantenimiento.security import es_admin_erp, exigir_permiso
from app.tenants.hospitales.models import Tenant, TenantModule

router = APIRouter()


def get_tenant_id(user, request):
    value = user.get("tenant_id")
    if es_admin_erp(user):
        value = request.headers.get("X-Tenant-ID") or value
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        raise HTTPException(403, "Seleccione un hospital válido")


async def autorizar(request, db, user, recurso, escritura=False):
    tid = get_tenant_id(user, request)
    hospital = await db.scalar(select(Tenant.id).where(Tenant.id == tid, Tenant.is_active.is_(True)))
    modulo = await db.scalar(select(TenantModule.id).where(
        TenantModule.tenant_id == tid, TenantModule.module_code == "sigarh_mantenimiento", TenantModule.is_active.is_(True),
    ))
    if not hospital or not modulo:
        raise HTTPException(403, "Hospital o módulo Mantenimiento inactivo")
    if not es_admin_erp(user):
        if user.get("panel") != "sigarh" or not user.get("active_modules"):
            raise HTTPException(403, "Acceso restringido a SIGARH")
        if recurso in svc.SEGURIDAD:
            exigir_permiso(user, "administrar_seguridad")
        elif escritura:
            exigir_permiso(user, "administrar_mantenimiento")
        if escritura or recurso in svc.SEGURIDAD:
            if "sigarh_mantenimiento" not in user.get("active_modules", []):
                raise HTTPException(403, "Su perfil no permite Mantenimiento")
    return tid


def ip(request):
    return request.client.host if request.client else None


# Rutas auxiliares antes de los identificadores dinámicos.
@router.get("/modulos-catalogo")
async def modulos(request: Request, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    tid = await autorizar(request, db, user, "roles-sistema")
    return [{"id": str(m.id), "code": m.code, "name": m.name, "category": m.category, "is_active": m.is_active}
            for m in await svc.modulos_habilitados(db, tid)]


@router.get("/personal-catalogo")
async def personal(request: Request, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from app.sigarh.rrhh.models import Empleado
    tid = await autorizar(request, db, user, "usuarios")
    empleados = (await db.scalars(select(Empleado).where(Empleado.tenant_id == tid, Empleado.is_active.is_(True)).order_by(Empleado.apellido_paterno))).all()
    return [{"id": str(e.id), "nombre": e.nombre_completo, "grupo_ocupacional_id": str(e.grupo_ocupacional_id) if e.grupo_ocupacional_id else None} for e in empleados]


@router.get("/guardias-valorizadas/resolver")
async def tarifa(request: Request, tipo_guardia_id: uuid.UUID, fecha: date,
                 grupo_id: uuid.UUID | None = None, nivel_id: uuid.UUID | None = None,
                 db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    tid = await autorizar(request, db, user, "guardias-valorizadas")
    item = await svc.resolver_tarifa(db, tid, tipo_guardia_id, grupo_id, nivel_id, fecha)
    return {"id": str(item.id), "valor": str(item.valor), "moneda": item.moneda}


def registrar(recurso, modelo, entrada, salida):
    # entrada/parcial son clases Pydantic resueltas en tiempo de ejecución (una
    # por recurso); FastAPI las usa igual como anotación, pero un type checker
    # estático no puede verificarlas -> se silencia con type: ignore abajo.
    parcial = esquema_parcial(entrada)

    async def listar_items(request: Request, offset: int = Query(0, ge=0), limit: int = Query(200, ge=1, le=500),
                           q: str | None = Query(None, max_length=255), is_active: bool | None = None,
                           db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
        tid = await autorizar(request, db, current_user, recurso)
        return [svc.serializar(i) for i in await svc.listar(db, modelo, tid, offset, limit, q, is_active)]

    async def crear_item(request: Request, data: entrada, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):  # type: ignore[valid-type]
        tid = await autorizar(request, db, current_user, recurso, True)
        return await svc.guardar(db, recurso, tid, data, current_user, ip=ip(request))

    async def obtener_item(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
        tid = await autorizar(request, db, current_user, recurso)
        item = await svc.obtener(db, modelo, id, tid)
        if not item:
            raise HTTPException(404, "Registro no encontrado")
        return svc.serializar(item)

    async def actualizar_item(request: Request, id: uuid.UUID, data: parcial, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):  # type: ignore[valid-type]
        tid = await autorizar(request, db, current_user, recurso, True)
        return await svc.guardar(db, recurso, tid, data, current_user, id, ip(request))

    async def eliminar_item(request: Request, id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
        tid = await autorizar(request, db, current_user, recurso, True)
        return await svc.eliminar(db, recurso, tid, id, current_user, ip(request))

    router.add_api_route(f"/{recurso}", listar_items, methods=["GET"], response_model=list[salida], name=f"listar_{recurso}")
    router.add_api_route(f"/{recurso}", crear_item, methods=["POST"], response_model=salida, status_code=201, name=f"crear_{recurso}")
    router.add_api_route(f"/{recurso}/{{id}}", obtener_item, methods=["GET"], response_model=salida, name=f"obtener_{recurso}")
    router.add_api_route(f"/{recurso}/{{id}}", actualizar_item, methods=["PATCH"], response_model=salida, name=f"actualizar_{recurso}")
    router.add_api_route(f"/{recurso}/{{id}}", eliminar_item, methods=["DELETE"], name=f"eliminar_{recurso}")


for recurso, configuracion in svc.REGISTROS.items():
    registrar(recurso, *configuracion)
