import uuid
from datetime import date as date_type
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_db_central
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt, require_any_module_jwt
from app.hospital.admision.schemas import (
    PatientCreate, PatientUpdate, PatientResponse,
    PatientSearchResult, ClinicalRecordMovementCreate,
    UbigeoDepartamentoOut, UbigeoProvinciaOut, UbigeoDistritoOut,
    AltaItem, ListaEsperaCreate, ListaEsperaUpdate, ListaEsperaAtender, ListaEsperaResponse,
    AnuncioCreate, AnuncioUpdate, AnuncioResponse,
    MensajeCreate, MensajeResponse, DestinatarioOut,
)
from app.hospital.admision.service import (
    create_patient, get_patient_by_dni, get_patient_by_id,
    search_patients, update_patient, move_clinical_record,
    get_departamentos, get_provincias, get_distritos,
    list_altas,
    list_lista_espera, create_lista_espera, update_lista_espera, atender_lista_espera, cancelar_lista_espera,
    list_anuncios, create_anuncio, update_anuncio,
    list_inbox, list_enviados, enviar_mensaje, marcar_leido, list_destinatarios,
)

router = APIRouter()

MODULO_CODIGO = "admision"


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


def _to_response(patient) -> PatientResponse:
    return PatientResponse(
        id=patient.id,
        document_type=patient.document_type,
        dni=patient.dni,
        is_nn=patient.is_nn,
        first_name=patient.first_name,
        second_name=patient.second_name,
        last_name_paterno=patient.last_name_paterno,
        last_name_materno=patient.last_name_materno,
        full_name=patient.full_name,
        birth_date=patient.birth_date,
        gender=patient.gender,
        age=patient.age,
        marital_status=patient.marital_status,
        education_level=patient.education_level,
        occupation=patient.occupation,
        ethnicity=patient.ethnicity,
        language=patient.language,
        phone=patient.phone,
        phone_is_whatsapp=patient.phone_is_whatsapp,
        email=patient.email,
        address=patient.address,
        department_id=patient.department_id,
        province_id=patient.province_id,
        district_id=patient.district_id,
        populated_center=patient.populated_center,
        country=patient.country,
        birth_same_as_address=patient.birth_same_as_address,
        birth_department_id=patient.birth_department_id,
        birth_province_id=patient.birth_province_id,
        birth_district_id=patient.birth_district_id,
        birth_populated_center=patient.birth_populated_center,
        birth_country=patient.birth_country,
        insurance_type=patient.insurance_type,
        insurance_number=patient.insurance_number,
        is_active=patient.is_active,
        created_at=patient.created_at,
        record_number=patient.clinical_record.record_number if patient.clinical_record else None,
    )


@router.get("/buscar", response_model=list[PatientSearchResult], summary="Buscar pacientes")
async def buscar_pacientes(
    q: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("admision")),
):
    tenant_id = get_tenant_id(current_user, request)
    if len(q) < 2:
        raise HTTPException(400, detail="Ingresa al menos 2 caracteres")
    patients = await search_patients(db, tenant_id, q)
    return [
        PatientSearchResult(
            id=p.id,
            dni=p.dni,
            full_name=p.full_name,
            age=p.age,
            gender=p.gender,
            insurance_type=p.insurance_type,
            record_number=p.clinical_record.record_number if p.clinical_record else None,
        )
        for p in patients
    ]


@router.get("/dni/{dni}", response_model=PatientResponse, summary="Buscar por DNI")
async def buscar_por_dni(
    dni: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("admision")),
):
    tenant_id = get_tenant_id(current_user, request)
    patient = await get_patient_by_dni(db, tenant_id, dni)
    if not patient:
        raise HTTPException(404, detail=f"Paciente con DNI {dni} no encontrado")
    return _to_response(patient)



@router.get("/dni-lookup/{dni}", summary="Consultar DNI en servicio externo (autocompletado)")
async def consultar_dni_externo(
    dni: str,
    current_user: dict = Depends(require_module_jwt("admision")),
):
    from app.hospital.admision.service import lookup_dni_externo
    datos = await lookup_dni_externo(dni)
    if not datos:
        raise HTTPException(404, detail="No se encontraron datos para ese DNI en el servicio externo")
    return {
        "first_name": datos.get("nombres", ""),
        "last_name_paterno": datos.get("apellidoPaterno", ""),
        "last_name_materno": datos.get("apellidoMaterno", ""),
    }


# --- Rutas de submodulos nuevos: Altas, Lista Espera, Anuncios, Mensajito.   ---
# --- IMPORTANTE: van ANTES de "/{patient_id}" mas abajo, porque si no esa   ---
# --- ruta generica intercepta estos paths y nunca llegan aqui (FastAPI/     ---
# --- Starlette matchea por orden de declaracion).                          ---

# --- Altas (vista de solo lectura sobre Hospitalizacion + AtencionEmergencia) ---
@router.get("/altas", response_model=list[AltaItem], summary="Listar altas (hospitalizacion + emergencia)")
async def listar_altas(
    request: Request,
    fecha_desde: date_type | None = None,
    fecha_hasta: date_type | None = None,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    from app.hospital.admision.service import list_altas
    tenant_id = get_tenant_id(current_user, request)
    return await list_altas(db, tenant_id, fecha_desde, fecha_hasta, q)


# --- Lista de Espera ---
@router.get("/lista-espera", response_model=list[ListaEsperaResponse], summary="Listar lista de espera")
async def listar_lista_espera(
    request: Request,
    estado: str | None = None,
    servicio_id: uuid.UUID | None = None,
    especialidad_id: uuid.UUID | None = None,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    return await list_lista_espera(db, tenant_id, estado, servicio_id, especialidad_id, q)


@router.post("/lista-espera", response_model=ListaEsperaResponse, status_code=201, summary="Registrar en lista de espera")
async def crear_lista_espera(
    data: ListaEsperaCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    return await create_lista_espera(db, tenant_id, data, current_user)


@router.patch("/lista-espera/{item_id}", response_model=ListaEsperaResponse, summary="Editar registro de lista de espera")
async def editar_lista_espera(
    item_id: uuid.UUID,
    data: ListaEsperaUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    return await update_lista_espera(db, tenant_id, item_id, data, current_user)


@router.post("/lista-espera/{item_id}/atender", response_model=ListaEsperaResponse, summary="Marcar atendido (enlaza cita)")
async def atender_lista_espera_endpoint(
    item_id: uuid.UUID,
    data: ListaEsperaAtender,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    return await atender_lista_espera(db, tenant_id, item_id, data.cita_id, current_user)


@router.post("/lista-espera/{item_id}/cancelar", response_model=ListaEsperaResponse, summary="Cancelar registro de lista de espera")
async def cancelar_lista_espera_endpoint(
    item_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    return await cancelar_lista_espera(db, tenant_id, item_id, current_user)


# --- Anuncios ---
@router.get("/anuncios", response_model=list[AnuncioResponse], summary="Listar anuncios")
async def listar_anuncios(
    request: Request,
    incluir_inactivos: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    return await list_anuncios(db, tenant_id, incluir_inactivos)


@router.post("/anuncios", response_model=AnuncioResponse, status_code=201, summary="Publicar anuncio")
async def crear_anuncio(
    data: AnuncioCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    return await create_anuncio(db, tenant_id, data, current_user)


@router.patch("/anuncios/{anuncio_id}", response_model=AnuncioResponse, summary="Editar o desactivar anuncio")
async def editar_anuncio(
    anuncio_id: uuid.UUID,
    data: AnuncioUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    return await update_anuncio(db, tenant_id, anuncio_id, data, current_user)


# --- Mensajito ---
@router.get("/mensajito/destinatarios", response_model=list[DestinatarioOut], summary="Catalogo de destinatarios")
async def catalogo_destinatarios(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    users = await list_destinatarios(db, tenant_id)
    return [DestinatarioOut(id=u.id, name=u.name, role=u.role) for u in users]


@router.get("/mensajito/inbox", response_model=list[MensajeResponse], summary="Bandeja de entrada")
async def bandeja_entrada(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    return await list_inbox(db, tenant_id, current_user)


@router.get("/mensajito/enviados", response_model=list[MensajeResponse], summary="Mensajes enviados")
async def mensajes_enviados(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    return await list_enviados(db, tenant_id, current_user)


@router.post("/mensajito", response_model=MensajeResponse, status_code=201, summary="Enviar mensaje")
async def enviar_mensaje_endpoint(
    data: MensajeCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    return await enviar_mensaje(db, tenant_id, data, current_user)


@router.post("/mensajito/{mensaje_id}/leido", summary="Marcar mensaje como leido")
async def marcar_mensaje_leido(
    mensaje_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    tenant_id = get_tenant_id(current_user, request)
    await marcar_leido(db, tenant_id, mensaje_id, current_user)
    return {"ok": True}


@router.post("/", response_model=PatientResponse, status_code=201, summary="Registrar paciente")
async def registrar_paciente(
    data: PatientCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("admision")),
):
    tenant_id = get_tenant_id(current_user, request)
    if data.dni:
        existing = await get_patient_by_dni(db, tenant_id, data.dni)
        if existing:
            raise HTTPException(400, detail=f"Ya existe un paciente con documento {data.dni}")
    patient = await create_patient(db, tenant_id, data)
    return _to_response(patient)


@router.get("/{patient_id}", response_model=PatientResponse, summary="Obtener paciente")
async def obtener_paciente(
    patient_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("admision")),
):
    tenant_id = get_tenant_id(current_user, request)
    patient = await get_patient_by_id(db, tenant_id, patient_id)
    if not patient:
        raise HTTPException(404, detail="Paciente no encontrado")
    return _to_response(patient)


@router.patch("/{patient_id}", response_model=PatientResponse, summary="Actualizar paciente")
async def actualizar_paciente(
    patient_id: uuid.UUID,
    data: PatientUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt("admision")),
):
    tenant_id = get_tenant_id(current_user, request)
    patient = await update_patient(db, tenant_id, patient_id, data)
    if not patient:
        raise HTTPException(404, detail="Paciente no encontrado")
    return _to_response(patient)


@router.post("/historia-clinica/mover", summary="Mover historia clinica")
async def mover_historia_clinica(
    data: ClinicalRecordMovementCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_module_jwt("admision", "archivo_clinico")),
):
    tenant_id = get_tenant_id(current_user, request)
    try:
        movement = await move_clinical_record(
            db, tenant_id, data.clinical_record_id, data.to_location,
            f"{(current_user.get('name') or 'Usuario')[:210]} ({current_user['sub']})", data.notes,
        )
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc
    return {"ok": True, "movement_id": str(movement.id)}


# --- Ubigeo en cascada (para los selects de Domicilio/Nacimiento del formulario) ---
@router.get("/ubigeo/departamentos", response_model=list[UbigeoDepartamentoOut], summary="Listar departamentos")
async def listar_departamentos(
    db: AsyncSession = Depends(get_db_central),
    current_user: dict = Depends(require_module_jwt("admision")),
):
    return await get_departamentos(db)


@router.get("/ubigeo/provincias/{departamento_id}", response_model=list[UbigeoProvinciaOut], summary="Listar provincias de un departamento")
async def listar_provincias(
    departamento_id: str,
    db: AsyncSession = Depends(get_db_central),
    current_user: dict = Depends(require_module_jwt("admision")),
):
    return await get_provincias(db, departamento_id)


@router.get("/ubigeo/distritos/{provincia_id}", response_model=list[UbigeoDistritoOut], summary="Listar distritos de una provincia")
async def listar_distritos(
    provincia_id: str,
    db: AsyncSession = Depends(get_db_central),
    current_user: dict = Depends(require_module_jwt("admision")),
):
    return await get_distritos(db, provincia_id)