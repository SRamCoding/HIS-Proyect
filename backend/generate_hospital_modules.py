"""
Genera la estructura completa (carpetas + archivos) de los modulos
del panel hospitalario (app) dentro de backend/app/hospital/.

Ejecutar desde la carpeta backend/:
    python generate_hospital_modules.py

No sobreescribe archivos que ya existan.
"""
import os

# Codigo de modulo -> nombre legible (mismo codigo que en seeder_niveles.py MODULES_APP)
MODULOS = [
    ("altas_pacientes",     "Altas de Pacientes"),
    ("consulta_externa",    "Consulta Externa"),
    ("archivo_clinico",     "Archivo Clinico"),
    ("agendamiento_citas",  "Agendamiento de Citas"),
    ("farmacia",            "Farmacia"),
    ("programacion_medica", "Programacion Medica"),
    ("laboratorio",         "Laboratorio"),
    ("emergencia",          "Emergencia"),
    ("imagenologia",        "Imagenologia"),
    ("hospitalizacion",     "Hospitalizacion"),
    ("caja_facturacion",    "Caja y Facturacion"),
    ("sis_fua",             "SIS / FUA"),
    ("his",                 "HIS"),
    ("reportes",            "Reportes"),
    ("telemedicina",        "Telemedicina"),
    ("archivo",             "Archivo"),
    ("seguimiento_paciente","Seguimiento Paciente"),
    ("nutricion",           "Nutricion Pacientes"),
]

BASE_DIR = os.path.join("app", "hospital")


def write_if_missing(path, content):
    if os.path.exists(path):
        print(f"  (ya existe, se omite) {path}")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  creado: {path}")


def crear_modulo(codigo: str, nombre: str):
    carpeta = os.path.join(BASE_DIR, codigo)
    os.makedirs(carpeta, exist_ok=True)
    print(f"Modulo: {codigo} ({nombre})")

    write_if_missing(os.path.join(carpeta, "__init__.py"), "")

    write_if_missing(os.path.join(carpeta, "models.py"), f'''"""
Modelos de {nombre}.
TODO: definir las tablas reales de este modulo.
Recuerda: todo modelo debe tener tenant_id para aislamiento multi-tenant.
"""
# import uuid
# from datetime import datetime
# from sqlalchemy import String, Boolean, DateTime
# from sqlalchemy.orm import Mapped, mapped_column
# from sqlalchemy.dialects.postgresql import UUID
# from app.core.database import Base
#
# class EjemploModelo(Base):
#     __tablename__ = "hospital_{codigo}_ejemplo"
#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
''')

    write_if_missing(os.path.join(carpeta, "schemas.py"), f'''"""
Schemas Pydantic de {nombre}.
TODO: definir los schemas reales de este modulo.
"""
# import uuid
# from datetime import datetime
# from pydantic import BaseModel
#
# class EjemploCreate(BaseModel):
#     nombre: str
#
# class EjemploResponse(EjemploCreate):
#     id: uuid.UUID
#     tenant_id: uuid.UUID
#     created_at: datetime
#     model_config = {{"from_attributes": True}}
''')

    write_if_missing(os.path.join(carpeta, "service.py"), f'''"""
Logica de negocio de {nombre}.
TODO: implementar las funciones reales de este modulo.
"""
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
''')

    write_if_missing(os.path.join(carpeta, "router.py"), f'''import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.tenants.entitlements import require_module_jwt

router = APIRouter()

MODULO_CODIGO = "{codigo}"


def get_tenant_id(current_user: dict, request: Request) -> uuid.UUID:
    tid = current_user.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tid:
        raise HTTPException(403, detail="Sin tenant asignado")
    return uuid.UUID(str(tid))


@router.get("/", summary="Estado del modulo {nombre} (placeholder)")
async def estado_modulo(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    """Endpoint placeholder: confirma que el modulo esta activo para el tenant."""
    return {{
        "modulo": MODULO_CODIGO,
        "nombre": "{nombre}",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }}
''')


def main():
    if not os.path.isdir("app"):
        print("ERROR: ejecuta este script desde la carpeta backend/ (donde esta la carpeta app/)")
        return

    os.makedirs(BASE_DIR, exist_ok=True)
    write_if_missing(os.path.join(BASE_DIR, "__init__.py"), "")

    for codigo, nombre in MODULOS:
        crear_modulo(codigo, nombre)

    print("\nListo. Revisa app/hospital/ y agrega los imports en main.py (ver instrucciones).")


if __name__ == "__main__":
    main()