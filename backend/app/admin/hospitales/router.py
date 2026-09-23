import uuid
import bcrypt
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.dependencies import get_admin_user
from app.tenants.hospitales.models import Tenant, TenantModule
from app.tenants.hospitales.schemas import TenantCreate, TenantUpdate, TenantResponse
from app.tenants.hospitales.service import crear_tenant_rapido, get_tenant_by_domain, update_tenant_modules
from app.admin.hospitales.schemas import HospitalListItem, ModuleToggle, ActiveToggle, ReintentarAprovisionamiento
from app.admin.hospitales.service import get_all_hospitals, toggle_tenant_active
from app.admin.notificaciones.service import crear_notificacion

router = APIRouter()


async def _encolar_aprovisionamiento(
    db: AsyncSession, tenant: Tenant, hospital_level: str, active_modules: list[str],
    admin_name: str, admin_email: str, admin_password: str,
    sigarh_name: str, sigarh_email: str, sigarh_password: str,
    attempt_token: str,
) -> bool:
    """Hashea las credenciales y encola la tarea de Celery que hace el
    trabajo pesado de aprovisionar (o reintentar aprovisionar) un hospital.
    Compartido entre crear_hospital y reintentar_aprovisionamiento -- ambos
    necesitan exactamente el mismo manejo de fallo al encolar, aunque cada
    uno decide que responder al cliente (por eso esto devuelve bool en vez
    de levantar la excepcion HTTP directamente).

    `attempt_token` (el `provisioning_started_at` de ESTE intento, como
    string) viaja con la tarea para que, al terminar, pueda confirmar que
    sigue siendo el intento vigente antes de tocar el estado del hospital
    o de borrar su base fisica -- sin esto, detectar un "pendiente"
    atascado por tiempo y reintentarlo mientras la tarea vieja seguia
    corriendo de verdad dejaba dos intentos escribiendo sobre el mismo
    hospital sin que ninguno supiera del otro."""
    admin_password_hash = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
    sigarh_password_hash = bcrypt.hashpw(sigarh_password.encode(), bcrypt.gensalt()).decode()

    from workers.tasks import aprovisionar_hospital
    try:
        aprovisionar_hospital.delay(
            tenant_id=str(tenant.id),
            database_name=tenant.database_name,
            hospital_level=hospital_level,
            active_modules=active_modules,
            admin_name=admin_name, admin_email=admin_email, admin_password_hash=admin_password_hash,
            sigarh_name=sigarh_name, sigarh_email=sigarh_email, sigarh_password_hash=sigarh_password_hash,
            attempt_token=attempt_token,
        )
        return True
    except Exception as exc:
        # Si el broker no recibe el mensaje (RabbitMQ caido, por ejemplo), el
        # hospital quedaba en "pendiente" para siempre sin ninguna tarea
        # encolada -- lo dejamos en "error" de inmediato para que sea visible
        # y no un pendiente fantasma.
        logging.getLogger(__name__).exception(
            "No se pudo encolar el aprovisionamiento del hospital %s", tenant.id
        )
        tenant.provisioning_status = "error"
        tenant.provisioning_error = f"No se pudo encolar el aprovisionamiento: {exc}"[:2000]
        await db.commit()
        await crear_notificacion(
            f"Error al aprovisionar: {tenant.name}",
            "No se pudo encolar la tarea de aprovisionamiento",
            nivel="error",
        )
        return False


@router.get("/hospitales", response_model=list[HospitalListItem], summary="Listar hospitales")
async def listar_hospitales(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    tenants = await get_all_hospitals(db)
    return [
        HospitalListItem(
            id=t.id, name=t.name, domain=t.domain,
            hospital_level=t.hospital_level, is_active=t.is_active,
            active_modules=t.active_module_codes, created_at=t.created_at,
            provisioning_status=t.provisioning_status, provisioning_error=t.provisioning_error,
        )
        for t in tenants
    ]


@router.post("/hospitales", response_model=TenantResponse, status_code=201, summary="Crear hospital")
async def crear_hospital(
    data: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    existing = await get_tenant_by_domain(db, data.domain)
    if existing:
        raise HTTPException(400, detail=f"Ya existe un hospital con el dominio '{data.domain}'")
    tenant = await crear_tenant_rapido(db, data)
    # Nombre/correo (nunca contraseña) de los usuarios iniciales, para poder
    # precargar el formulario de reintento si el aprovisionamiento falla.
    tenant.admin_name, tenant.admin_email = data.admin_name, data.admin_email
    tenant.sigarh_name, tenant.sigarh_email = data.sigarh_name, data.sigarh_email
    await db.commit()
    # Si falla el encolado, _encolar_aprovisionamiento ya deja el hospital en
    # "error" y notifica -- el registro SI se creo (commit ya hecho en
    # crear_tenant_rapido), asi que igual se responde 201 con el tenant tal
    # como quedo, en vez de un 500 que sugeriria que nada se guardo.
    await _encolar_aprovisionamiento(
        db, tenant, data.hospital_level, data.active_modules,
        data.admin_name, data.admin_email, data.admin_password,
        data.sigarh_name, data.sigarh_email, data.sigarh_password,
        attempt_token=tenant.provisioning_started_at.isoformat(),
    )
    return tenant


@router.get("/hospitales/{tenant_id}", summary="Obtener hospital por ID")
async def obtener_hospital(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    result = await db.execute(
        select(Tenant)
        .options(selectinload(Tenant.modules))
        .where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(404, detail="Hospital no encontrado")
    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "logo_url": tenant.logo_url,
        "domain": tenant.domain,
        "hospital_level": tenant.hospital_level,
        "ruc": tenant.ruc,
        "phone": tenant.phone,
        "email": tenant.email,
        "address": tenant.address,
        "mission": tenant.mission,
        "vision": tenant.vision,
        "values": tenant.values,
        "is_active": tenant.is_active,
        "active_modules": tenant.active_module_codes,
        "created_at": tenant.created_at.isoformat(),
        "provisioning_status": tenant.provisioning_status,
        "provisioning_error": tenant.provisioning_error,
        "admin_name": tenant.admin_name,
        "admin_email": tenant.admin_email,
        "sigarh_name": tenant.sigarh_name,
        "sigarh_email": tenant.sigarh_email,
    }


@router.patch("/hospitales/{tenant_id}", summary="Actualizar hospital")
async def actualizar_hospital(
    tenant_id: uuid.UUID,
    data: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(404, detail="Hospital no encontrado")
    # TenantUpdate es la lista blanca de campos editables (hereda de TenantBase);
    # antes se aceptaba un dict libre y se aplicaba con setattr a cualquier
    # atributo del modelo, incluidos campos internos como schema_name. is_active
    # SI esta en la lista blanca (el formulario de edicion lo envia junto con el
    # resto de la identidad), pero domain/active_modules tienen su propio flujo.
    cambios = data.model_dump(exclude_unset=True, exclude={"active_modules", "domain"})
    if cambios.get("hospital_level"):
        # Antes se guardaba el codigo tal cual, sin comprobar que exista o
        # siga activo -- un typo, o un nivel que se desactivo despues,
        # dejaba al hospital apuntando a un codigo invalido sin ningun
        # aviso (el mismo chequeo que ya hace crear_tenant_rapido al crear
        # un hospital, aca faltaba al editarlo).
        from app.admin.niveles_hospitalarios.models import HospitalLevel
        nivel_valido = await db.scalar(select(HospitalLevel.id).where(
            HospitalLevel.code == cambios["hospital_level"],
            HospitalLevel.is_active.is_(True),
        ))
        if not nivel_valido:
            raise HTTPException(422, detail="El nivel hospitalario no existe o está inactivo")
    for field, value in cambios.items():
        setattr(tenant, field, value)
    await db.commit()
    return {"ok": True}


@router.patch("/hospitales/{tenant_id}/toggle", summary="Activar/desactivar hospital")
async def toggle_hospital(
    tenant_id: uuid.UUID,
    data: ActiveToggle,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    tenant = await toggle_tenant_active(db, tenant_id, data.is_active)
    if not tenant:
        raise HTTPException(404, detail="Hospital no encontrado")
    await crear_notificacion(
        f"Hospital {'activado' if data.is_active else 'desactivado'}: {tenant.name}",
        nivel="alerta" if not data.is_active else "info",
        link=f"/admin/hospitales/{tenant.id}",
    )
    return {"ok": True, "is_active": tenant.is_active}


@router.post("/hospitales/{tenant_id}/reintentar-aprovisionamiento", summary="Reintentar aprovisionamiento fallido")
async def reintentar_aprovisionamiento(
    tenant_id: uuid.UUID,
    data: ReintentarAprovisionamiento,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(404, detail="Hospital no encontrado")

    active_modules = list((await db.scalars(
        select(TenantModule.module_code).where(TenantModule.tenant_id == tenant_id)
    )).all())

    # UPDATE condicionado al estado actual (no "leer, decidir en Python,
    # escribir"): dos solicitudes de reintento simultaneas podian pasar
    # ambas el chequeo de `provisioning_status != "error"` antes de que
    # cualquiera alcanzara a cambiarlo, y las dos terminaban encolando una
    # tarea para el mismo hospital. Con el WHERE en el propio UPDATE, solo
    # UNA de las dos puede afectar la fila -- la otra ve rowcount == 0.
    #
    # provisioning_started_at se renueva AQUI (no en el objeto `tenant` ya
    # cargado, que el UPDATE crudo no actualiza en memoria): ese nuevo valor
    # es el token de intento que la tarea usara para confirmar que sigue
    # siendo vigente antes de tocar nada.
    nuevo_intento = datetime.utcnow()
    resultado = await db.execute(
        update(Tenant)
        .where(Tenant.id == tenant_id, Tenant.provisioning_status == "error")
        .values(
            provisioning_status="pendiente", provisioning_error=None, provisioning_started_at=nuevo_intento,
            admin_name=data.admin_name, admin_email=data.admin_email,
            sigarh_name=data.sigarh_name, sigarh_email=data.sigarh_email,
        )
    )
    await db.commit()
    if resultado.rowcount == 0:
        raise HTTPException(400, detail="Solo se puede reintentar un hospital que quedó en estado de error")

    ok = await _encolar_aprovisionamiento(
        db, tenant, tenant.hospital_level, active_modules,
        data.admin_name, data.admin_email, data.admin_password,
        data.sigarh_name, data.sigarh_email, data.sigarh_password,
        attempt_token=nuevo_intento.isoformat(),
    )
    if not ok:
        # Aqui si corresponde un error real: a diferencia de crear_hospital,
        # el reintento no tiene ningun otro efecto que reportar como exito
        # parcial -- si no se pudo encolar, la accion completa fallo.
        raise HTTPException(500, detail="No se pudo encolar el reintento. Intenta nuevamente en unos minutos.")
    return {"ok": True}


@router.put("/hospitales/modulos", summary="Actualizar módulos de un hospital")
async def actualizar_modulos(
    data: ModuleToggle,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: dict = Depends(get_admin_user),
):
    tenant = await db.get(Tenant, data.tenant_id)
    await update_tenant_modules(db, redis, data.tenant_id, data.module_codes)
    await crear_notificacion(
        f"Módulos actualizados: {tenant.name if tenant else data.tenant_id}",
        f"{len(data.module_codes)} módulos activos",
        nivel="info",
        link=f"/admin/hospitales/{data.tenant_id}",
    )
    return {"ok": True, "message": "Módulos actualizados correctamente"}
