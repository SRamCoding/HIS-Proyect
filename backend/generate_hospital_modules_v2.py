"""
Genera la estructura completa (carpetas + archivos) de los 13 modulos
del panel hospitalario (app) que faltan, con sus submodulos reales,
dentro de backend/app/hospital/.

Ejecutar desde la carpeta backend/:
    python generate_hospital_modules_v2.py

No sobreescribe archivos que ya existan (borra la carpeta antes si
quieres regenerar un modulo desde cero).
"""
import os

# codigo_modulo -> (nombre_modulo, [(slug_submodulo, nombre_submodulo), ...])
MODULOS = {
    "cobros": ("Cobros", [
        ("cobro-por-paciente", "Cobro por Paciente"),
        ("mi-caja", "Mi Caja"),
    ]),
    "hospitalizacion": ("Hospitalizacion", [
        ("hospitalizaciones", "Hospitalizaciones"),
        ("panel-camas", "Panel de Camas"),
        ("seguimiento-paciente", "Seguimiento Paciente"),
        ("censo-diario", "Censo Diario"),
        ("interconsultas", "Interconsultas"),
        ("consentimientos", "Consentimientos Informados"),
    ]),
    "consulta_externa": ("Consulta Externa", [
        ("admision", "Admision Consulta Externa"),
        ("programacion-medica", "Programacion Medica"),
        ("calendario-medico", "Calendario Medico"),
        ("triaje", "Triaje"),
        ("atenciones-medicas", "Atenciones Medicas"),
        ("bandeja-electronica", "Bandeja Electronica"),
    ]),
    "emergencia": ("Emergencia", [
        ("admisiones", "Admisiones"),
        ("observacion", "Observacion"),
        ("referencias", "Referencias"),
    ]),
    "laboratorio": ("Laboratorio", [
        ("ordenes", "Ordenes de Laboratorio"),
    ]),
    "imagenologia": ("Imagenologia", [
        ("atenciones", "Atenciones"),
        ("tickets", "Tickets"),
        ("hospitalizados", "Hospitalizados"),
        ("reimpresiones", "Reimpresiones"),
    ]),
    "farmacia": ("Farmacia", [
        ("recetas-medicas", "Recetas Medicas"),
        ("recetas-farmacotecnia", "Recetas Farmacotecnia"),
        ("ventas-despacho", "Ventas / Despacho"),
        ("notas-ingreso", "Notas de Ingreso"),
        ("kardex-movimientos", "Kardex / Movimientos"),
        ("notas-salida", "Notas de Salida"),
        ("saldos", "Saldos Farmacia"),
        ("reportes", "Reportes"),
        ("panel-digemid", "Panel DIGEMID"),
        ("ici-diario", "ICI Diario"),
    ]),
    "caja": ("Caja", [
        ("comprobantes-pago", "Comprobantes de Pago"),
        ("cuentas", "Cuentas"),
    ]),
    "archivo_clinico": ("Archivo Clinico", [
        ("hc-electronica", "HC Electronica"),
        ("historias-clinicas", "Historias Clinicas"),
        ("movimientos-hc", "Movimientos de H.C."),
        ("personal-archivo", "Personal de Archivo"),
    ]),
    "sis": ("SIS", [
        ("formato-fua", "Formato FUA"),
        ("afiliaciones", "Afiliaciones SIS"),
    ]),
    "his": ("HIS", [
        ("registro-microred", "Registro HIS de la MicroRed"),
        ("formato-his", "Formato HIS"),
    ]),
    "reportes": ("Reportes", [
        ("reporte-medico", "Reporte por Medico"),
        ("reportes-hospitalizacion", "Reportes de Hospitalizacion"),
    ]),
    "telemedicina": ("Telemedicina", [
        ("resumen-teleconsultas", "Resumen Teleconsultas"),
        ("guia-rapida-minsa", "Guia Rapida MINSA"),
    ]),
}

BASE_DIR = os.path.join("app", "hospital")


def write_if_missing(path, content):
    if os.path.exists(path):
        print(f"  (ya existe, se omite) {path}")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  creado: {path}")


def crear_modulo(codigo: str, nombre: str, submodulos: list):
    carpeta = os.path.join(BASE_DIR, codigo)
    os.makedirs(carpeta, exist_ok=True)
    print(f"Modulo: {codigo} ({nombre})")

    write_if_missing(os.path.join(carpeta, "__init__.py"), "")

    submodulos_comentario = "\n".join(f"# - {slug}: {nom}" for slug, nom in submodulos)
    write_if_missing(os.path.join(carpeta, "models.py"), f'''"""
Modelos de {nombre}.
Submodulos de este modulo:
{submodulos_comentario}

TODO: definir las tablas reales de cada submodulo.
Recuerda: todo modelo debe tener tenant_id para aislamiento multi-tenant.
"""
# import uuid
# from datetime import datetime
# from sqlalchemy import String, Boolean, DateTime
# from sqlalchemy.orm import Mapped, mapped_column
# from sqlalchemy.dialects.postgresql import UUID
# from app.core.database import Base
''')

    write_if_missing(os.path.join(carpeta, "schemas.py"), f'''"""
Schemas Pydantic de {nombre}.
TODO: definir los schemas reales de cada submodulo.
"""
# import uuid
# from datetime import datetime
# from pydantic import BaseModel
''')

    write_if_missing(os.path.join(carpeta, "service.py"), f'''"""
Logica de negocio de {nombre}.
TODO: implementar las funciones reales de cada submodulo.
"""
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
''')

    # Genera un endpoint placeholder por submodulo, todos bajo el mismo gate de modulo
    endpoints = ""
    for slug, nom in submodulos:
        func_name = "estado_" + slug.replace("-", "_")
        endpoints += f'''

@router.get("/{slug}", summary="Estado de {nom} (placeholder)")
async def {func_name}(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant=Depends(require_module_jwt(MODULO_CODIGO)),
    current_user: dict = Depends(get_current_user),
):
    return {{
        "modulo": MODULO_CODIGO,
        "submodulo": "{slug}",
        "nombre": "{nom}",
        "tenant_id": str(get_tenant_id(current_user, request)),
        "status": "pendiente de implementar",
    }}
'''

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
{endpoints}''')


def main():
    if not os.path.isdir("app"):
        print("ERROR: ejecuta este script desde la carpeta backend/ (donde esta la carpeta app/)")
        return

    os.makedirs(BASE_DIR, exist_ok=True)

    for codigo, (nombre, submodulos) in MODULOS.items():
        crear_modulo(codigo, nombre, submodulos)

    print("\nListo. Revisa app/hospital/ y agrega los imports en main.py.")


if __name__ == "__main__":
    main()