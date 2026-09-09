# backend/app/admin/seeder_niveles.py
"""
Ejecutar con:
docker compose exec backend python -m app.admin.seeder_niveles
"""
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.core.database import Base
from app.tenants.hospitales.models import Tenant, TenantModule
from app.tenants.modulos.models import Module
from app.admin.roles.models import SystemRole
from app.admin.niveles_hospitalarios.models import HospitalLevel
from app.admin.modulos.models import ModuleDependency
from app.admin.auditoria.models import AuditLog

# Catalogo EXACTO — no debe tener mas ni menos modulos que estos 27.
MODULES_APP = [
    {"code": "admision",           "name": "Admisión"},
    {"code": "consulta_externa",   "name": "Consulta externa"},
    {"code": "hospitalizacion",    "name": "Hospitalización"},
    {"code": "emergencia",         "name": "Emergencia"},
    {"code": "archivo_clinico",    "name": "Archivo Clínico"},
    {"code": "caja",               "name": "Caja"},
    {"code": "farmacia",           "name": "Farmacia"},
    {"code": "servicio_social",    "name": "Servicio Social"},
    {"code": "facturacion",        "name": "Facturación"},
    {"code": "fact_config",        "name": "Fact - Config"},
    {"code": "seguridad",          "name": "Seguridad"},
    {"code": "general",            "name": "General"},
    {"code": "laboratorio",        "name": "Laboratorio"},
    {"code": "imagenes",           "name": "Imagenes"},
    {"code": "sis",                "name": "SIS"},
    {"code": "his",                "name": "HIS"},
    {"code": "seguimiento",        "name": "Seguimiento"},
    {"code": "epidemiologia",      "name": "Epidemiologia"},
    {"code": "telesalud",          "name": "TeleSalud"},
    {"code": "procedimientos",     "name": "Procedimientos"},
    {"code": "auditoria",          "name": "Auditoria"},
    {"code": "hemodialisis",       "name": "Hemodialisis"},
    {"code": "banco_sangre",       "name": "Banco de Sangre"},
    {"code": "informes",           "name": "Informes"},
    {"code": "salud_ambiental",    "name": "Salud Ambiental"},
    {"code": "medicina_fisica",    "name": "Medicina Fisica"},
    {"code": "firma_electronica",  "name": "Firma Electronica"},
]

# Set de codigos permitidos, calculado del catalogo de arriba.
# Cualquier modulo category='app' en la BD que NO este en este set se
# considera basura de versiones anteriores del seeder y se BORRA.
# (Seguro de hacer porque esta BD todavia no tiene tenants con modulos
# asignados. Si en el futuro ya hay tenants, cambiar el DELETE por un
# is_active=False para no romper referencias.)
ALLOWED_APP_CODES = {m["code"] for m in MODULES_APP}

MODULES_SIGARH = [
    {"code": "sigarh_infraestructura",          "name": "Infraestructura"},
    {"code": "sigarh_infraestructura_hosp",     "name": "Infraestructura Hospitalaria"},
    {"code": "sigarh_config_farmacia",          "name": "Configuracion Farmacia"},
    {"code": "sigarh_config_financiera",        "name": "Configuracion Financiera"},
    {"code": "sigarh_imagenologia",             "name": "Imagenologia"},
    {"code": "sigarh_laboratorio",              "name": "Laboratorio"},
    {"code": "sigarh_recursos_humanos",         "name": "Recursos Humanos"},
    {"code": "sigarh_mantenimiento",            "name": "Mantenimiento"},
    {"code": "sigarh_creacion_roles",           "name": "Creacion de Roles"},
    {"code": "sigarh_roles_pendientes",         "name": "Roles Pendientes"},
    {"code": "sigarh_roles_aprobados",          "name": "Roles Aprobados"},
    {"code": "sigarh_nutricion",                "name": "Nutricion"},
    {"code": "sigarh_movimientos",              "name": "Movimientos"},
    {"code": "sigarh_general",                  "name": "General"},
]

NIVELES = [
    {
        "code": "I-1", "name": "Puesto de Salud (sin medico)",
        "description": "Puesto de Salud sin medico", "color": "#6B7280", "sort_order": 1,
        "default_modules": {
            "app": ["admision", "consulta_externa", "farmacia", "informes"],
            "sigarh": ["sigarh_infraestructura", "sigarh_recursos_humanos", "sigarh_mantenimiento",
                       "sigarh_general", "sigarh_creacion_roles", "sigarh_roles_pendientes", "sigarh_roles_aprobados"]
        }
    },
    {
        "code": "I-2", "name": "Puesto de Salud (con medico)",
        "description": "Puesto de Salud con medico", "color": "#0EA5E9", "sort_order": 2,
        "default_modules": {
            "app": ["admision", "consulta_externa", "farmacia", "informes", "telesalud", "his", "archivo_clinico"],
            "sigarh": ["sigarh_infraestructura", "sigarh_recursos_humanos", "sigarh_mantenimiento",
                       "sigarh_general", "sigarh_creacion_roles", "sigarh_roles_pendientes", "sigarh_roles_aprobados"]
        }
    },
    {
        "code": "I-3", "name": "Centro de Salud sin internamiento",
        "description": "Centro de Salud sin internamiento", "color": "#3B82F6", "sort_order": 3,
        "default_modules": {
            "app": ["admision", "consulta_externa", "farmacia", "sis", "his", "informes", "telesalud",
                    "archivo_clinico", "servicio_social", "general"],
            "sigarh": ["sigarh_infraestructura", "sigarh_recursos_humanos", "sigarh_mantenimiento",
                       "sigarh_general", "sigarh_creacion_roles", "sigarh_roles_pendientes", "sigarh_roles_aprobados"]
        }
    },
    {
        "code": "I-4", "name": "Centro de Salud con internamiento",
        "description": "Centro de Salud con internamiento", "color": "#8B5CF6", "sort_order": 4,
        "default_modules": {
            "app": ["admision", "consulta_externa", "farmacia", "hospitalizacion", "sis", "his",
                    "informes", "telesalud", "archivo_clinico", "servicio_social", "general",
                    "seguridad", "caja"],
            "sigarh": ["sigarh_infraestructura", "sigarh_infraestructura_hosp", "sigarh_recursos_humanos",
                       "sigarh_mantenimiento", "sigarh_general", "sigarh_creacion_roles",
                       "sigarh_roles_pendientes", "sigarh_roles_aprobados"]
        }
    },
    {
        "code": "II-1", "name": "Hospital de Apoyo",
        "description": "Hospital de Apoyo", "color": "#F97316", "sort_order": 5,
        "default_modules": {
            "app": ["admision", "consulta_externa", "farmacia", "emergencia", "hospitalizacion",
                    "laboratorio", "sis", "his", "informes", "telesalud", "archivo_clinico", "caja",
                    "servicio_social", "facturacion", "fact_config", "seguridad", "general",
                    "seguimiento", "procedimientos", "auditoria"],
            "sigarh": ["sigarh_infraestructura", "sigarh_infraestructura_hosp", "sigarh_config_farmacia",
                       "sigarh_recursos_humanos", "sigarh_mantenimiento", "sigarh_laboratorio", "sigarh_general",
                       "sigarh_creacion_roles", "sigarh_roles_pendientes", "sigarh_roles_aprobados"]
        }
    },
    {
        "code": "II-2", "name": "Hospital General",
        "description": "Hospital General", "color": "#EF4444", "sort_order": 6,
        "default_modules": {
            "app": ["admision", "consulta_externa", "farmacia", "emergencia", "hospitalizacion",
                    "laboratorio", "sis", "his", "informes", "telesalud", "archivo_clinico", "caja",
                    "servicio_social", "facturacion", "fact_config", "seguridad", "general",
                    "seguimiento", "epidemiologia", "procedimientos", "auditoria",
                    "hemodialisis", "banco_sangre", "salud_ambiental", "medicina_fisica",
                    "firma_electronica"],
            "sigarh": ["sigarh_infraestructura", "sigarh_infraestructura_hosp", "sigarh_config_farmacia",
                       "sigarh_config_financiera", "sigarh_recursos_humanos", "sigarh_mantenimiento",
                       "sigarh_laboratorio", "sigarh_general", "sigarh_creacion_roles", "sigarh_roles_pendientes",
                       "sigarh_roles_aprobados", "sigarh_movimientos"]
        }
    },
    {
        "code": "III-1", "name": "Hospital Nacional / Especializado",
        "description": "Hospital Nacional / Especializado", "color": "#16A34A", "sort_order": 7,
        "default_modules": {
            "app": ["admision", "consulta_externa", "farmacia", "emergencia", "hospitalizacion",
                    "laboratorio", "imagenes", "sis", "his", "informes", "telesalud", "archivo_clinico",
                    "caja", "servicio_social", "facturacion", "fact_config", "seguridad", "general",
                    "seguimiento", "epidemiologia", "procedimientos", "auditoria",
                    "hemodialisis", "banco_sangre", "salud_ambiental", "medicina_fisica",
                    "firma_electronica"],
            "sigarh": ["sigarh_infraestructura", "sigarh_infraestructura_hosp", "sigarh_config_farmacia",
                       "sigarh_config_financiera", "sigarh_imagenologia", "sigarh_laboratorio",
                       "sigarh_recursos_humanos", "sigarh_mantenimiento", "sigarh_creacion_roles",
                       "sigarh_roles_pendientes", "sigarh_roles_aprobados", "sigarh_nutricion",
                       "sigarh_movimientos", "sigarh_general"]
        }
    },
    {
        "code": "III-2", "name": "Instituto Nacional / INEN / INS",
        "description": "Instituto Nacional / INEN / INS", "color": "#1d4ed8", "sort_order": 8,
        "default_modules": {
            "app": ["admision", "consulta_externa", "archivo_clinico", "farmacia", "emergencia",
                    "hospitalizacion", "sis", "his", "informes", "telesalud", "servicio_social",
                    "facturacion", "fact_config", "seguridad", "general", "seguimiento", "epidemiologia",
                    "procedimientos", "auditoria", "hemodialisis", "banco_sangre",
                    "salud_ambiental", "medicina_fisica", "firma_electronica"],
            "sigarh": ["sigarh_infraestructura", "sigarh_infraestructura_hosp", "sigarh_config_farmacia",
                       "sigarh_config_financiera", "sigarh_imagenologia", "sigarh_laboratorio",
                       "sigarh_recursos_humanos", "sigarh_mantenimiento", "sigarh_creacion_roles",
                       "sigarh_roles_pendientes", "sigarh_roles_aprobados", "sigarh_nutricion",
                       "sigarh_movimientos", "sigarh_general"]
        }
    },
]


async def get_or_create_module(db, code: str, name: str, category: str, is_active: bool = True):
    result = await db.execute(select(Module).where(Module.code == code))
    existing = result.scalar_one_or_none()
    if existing:
        existing.name = name
        existing.category = category
        existing.is_active = is_active
        return existing
    mod = Module(code=code, name=name, category=category, is_active=is_active)
    db.add(mod)
    return mod


async def purge_extra_app_modules(db, allowed_codes: set[str]):
    result = await db.execute(select(Module).where(Module.category == "app"))
    all_app_modules = result.scalars().all()
    borrados = []
    for mod in all_app_modules:
        if mod.code not in allowed_codes:
            borrados.append(mod.code)
            await db.delete(mod)
    if borrados:
        print(f"  - Modulos 'app' eliminados del catalogo ({len(borrados)}): {', '.join(sorted(borrados))}")
    else:
        print("  - No habia modulos 'app' fuera del catalogo, nada que eliminar.")


async def get_or_create_level(db, n: dict):
    result = await db.execute(select(HospitalLevel).where(HospitalLevel.code == n["code"]))
    existing = result.scalar_one_or_none()
    if existing:
        existing.name = n["name"]
        existing.description = n["description"]
        existing.color = n["color"]
        existing.sort_order = n["sort_order"]
        existing.default_modules = n["default_modules"]
        existing.is_active = True
        return existing
    level = HospitalLevel(
        code=n["code"], name=n["name"], description=n["description"],
        default_modules=n["default_modules"], sort_order=n["sort_order"], is_active=True,
    )
    db.add(level)
    return level


async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

    async with AsyncSession() as db:
        print("Creando/actualizando catalogo de modulos (app)...")
        for m in MODULES_APP:
            await get_or_create_module(db, m["code"], m["name"], "app")
        await db.flush()

        print("Purgando modulos 'app' que no pertenecen al catalogo (27 permitidos)...")
        await purge_extra_app_modules(db, ALLOWED_APP_CODES)

        print("Creando/actualizando catalogo de modulos (sigarh)...")
        for m in MODULES_SIGARH:
            await get_or_create_module(db, m["code"], m["name"], "sigarh")
        await db.flush()

        print("Creando/actualizando niveles hospitalarios MINSA...")
        for n in NIVELES:
            await get_or_create_level(db, n)

        await db.commit()
        print("Niveles hospitalarios y modulos creados/actualizados correctamente")
        print(f"Total modulos 'app' activos en catalogo: {len(MODULES_APP)}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())