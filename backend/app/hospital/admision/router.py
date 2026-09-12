import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_db_central
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt, require_any_module_jwt
from app.hospital.admision.schemas import (
    PatientCreate, PatientUpdate, PatientResponse,
    PatientSearchResult, ClinicalRecordMovementCreate,
    UbigeoDepartamentoOut, UbigeoProvinciaOut, UbigeoDistritoOut,
)
from app.hospital.admision.service import (
    create_patient, get_patient_by_dni, get_patient_by_id,
    search_patients, update_patient, move_clinical_record,
    get_departamentos, get_provincias, get_distritos,
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


# --- Placeholders nuevos: Citados, Agendamientos, Anuncios, Programaciones, ---
# --- Lista Espera, Mensajito. IMPORTANTE: van ANTES de "/{patient_id}" mas   ---
# --- abajo, porque si no esa ruta generica intercepta estos paths y nunca   ---
# --- llegan aqui (FastAPI/Starlette matchea por orden de declaracion).      ---

@router.get("/citados", summary="Estado de Citados (placeholder)")
async def estado_citados(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "citados",
        "nombre": "Citados",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


@router.get("/anuncios", summary="Estado de Anuncios (placeholder)")
async def estado_anuncios(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "anuncios",
        "nombre": "Anuncios",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


@router.get("/lista-espera", summary="Estado de Lista Espera (placeholder)")
async def estado_lista_espera(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "lista-espera",
        "nombre": "Lista Espera",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


@router.get("/mensajito", summary="Estado de Mensajito (placeholder)")
async def estado_mensajito(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_module_jwt(MODULO_CODIGO)),
):
    return {
        "modulo": MODULO_CODIGO,
        "submodulo": "mensajito",
        "nombre": "Mensajito",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }


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