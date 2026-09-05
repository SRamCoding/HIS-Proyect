CONTENIDO = '''"""
Ejecutar con:
python -m app.admin.seeder_niveles
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.core.database import Base
from app.tenants.hospitales.models import Tenant, TenantModule
from app.tenants.modulos.models import Module
from app.admin.roles.models import SystemRole
from app.admin.niveles_hospitalarios.models import HospitalLevel
from app.admin.modulos.models import ModuleDependency
from app.admin.auditoria.models import AuditLog

MODULES_APP = [
    {"code": "cobros",             "name": "Cobros"},
    {"code": "hospitalizacion",    "name": "Hospitalizacion"},
    {"code": "gestion_pacientes",  "name": "Gestion de Pacientes"},
    {"code": "consulta_externa",   "name": "Consulta Externa"},
    {"code": "emergencia",         "name": "Emergencia"},
    {"code": "laboratorio",        "name": "Laboratorio"},
    {"code": "imagenologia",       "name": "Imagenologia"},
    {"code": "farmacia",           "name": "Farmacia"},
    {"code": "caja",               "name": "Caja"},
    {"code": "archivo_clinico",    "name": "Archivo Clinico"},
    {"code": "sis",                "name": "SIS"},
    {"code": "his",                "name": "HIS"},
    {"code": "reportes",           "name": "Reportes"},
    {"code": "telemedicina",       "name": "Telemedicina"},
]

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
            "app": ["gestion_pacientes", "consulta_externa", "farmacia", "reportes", "telemedicina"],
            "sigarh": ["sigarh_infraestructura", "sigarh_recursos_humanos", "sigarh_mantenimiento",
                       "sigarh_general", "sigarh_creacion_roles", "sigarh_roles_pendientes", "sigarh_roles_aprobados"]
        }
    },
    {
        "code": "I-2", "name": "Puesto de Salud (con medico)",
        "description": "Puesto de Salud con medico", "color": "#0EA5E9", "sort_order": 2,
        "default_modules": {
            "app": ["gestion_pacientes", "consulta_externa", "farmacia", "reportes", "telemedicina", "his", "archivo_clinico"],
            "sigarh": ["sigarh_infraestructura", "sigarh_recursos_humanos", "sigarh_mantenimiento",
                       "sigarh_general", "sigarh_creacion_roles", "sigarh_roles_pendientes", "sigarh_roles_aprobados"]
        }
    },
    {
        "code": "I-3", "name": "Centro de Salud sin internamiento",
        "description": "Centro de Salud sin internamiento", "color": "#3B82F6", "sort_order": 3,
        "default_modules": {
            "app": ["gestion_pacientes", "consulta_externa", "farmacia", "sis", "his", "reportes", "telemedicina", "archivo_clinico"],
            "sigarh": ["sigarh_infraestructura", "sigarh_recursos_humanos", "sigarh_mantenimiento",
                       "sigarh_general", "sigarh_creacion_roles", "sigarh_roles_pendientes", "sigarh_roles_aprobados"]
        }
    },
    {
        "code": "I-4", "name": "Centro de Salud con internamiento",
        "description": "Centro de Salud con internamiento", "color": "#8B5CF6", "sort_order": 4,
        "default_modules": {
            "app": ["gestion_pacientes", "consulta_externa", "farmacia", "hospitalizacion", "sis", "his",
                    "reportes", "telemedicina", "archivo_clinico"],
            "sigarh": ["sigarh_infraestructura", "sigarh_infraestructura_hosp", "sigarh_recursos_humanos",
                       "sigarh_mantenimiento", "sigarh_general", "sigarh_creacion_roles",
                       "sigarh_roles_pendientes", "sigarh_roles_aprobados"]
        }
    },
    {
        "code": "II-1", "name": "Hospital de Apoyo",
        "description": "Hospital de Apoyo", "color": "#F97316", "sort_order": 5,
        "default_modules": {
            "app": ["gestion_pacientes", "consulta_externa", "farmacia", "emergencia", "hospitalizacion",
                    "laboratorio", "sis", "his", "reportes", "telemedicina", "archivo_clinico", "caja", "cobros"],
            "sigarh": ["sigarh_infraestructura", "sigarh_infraestructura_hosp", "sigarh_config_farmacia",
                       "sigarh_recursos_humanos", "sigarh_mantenimiento", "sigarh_laboratorio", "sigarh_general",
                       "sigarh_creacion_roles", "sigarh_roles_pendientes", "sigarh_roles_aprobados"]
        }
    },
    {
        "code": "II-2", "name": "Hospital General",
        "description": "Hospital General", "color": "#EF4444", "sort_order": 6,
        "default_modules": {
            "app": ["gestion_pacientes", "consulta_externa", "farmacia", "emergencia", "hospitalizacion",
                    "laboratorio", "sis", "his", "reportes", "telemedicina", "archivo_clinico", "caja", "cobros"],
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
            "app": ["gestion_pacientes", "consulta_externa", "farmacia", "emergencia", "hospitalizacion",
                    "laboratorio", "imagenologia", "sis", "his", "reportes", "telemedicina", "archivo_clinico",
                    "caja", "cobros"],
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
            "app": ["gestion_pacientes", "consulta_externa", "archivo_clinico", "farmacia", "emergencia",
                    "hospitalizacion", "sis", "his", "reportes", "telemedicina"],
            "sigarh": ["sigarh_infraestructura", "sigarh_infraestructura_hosp", "sigarh_config_farmacia",
                       "sigarh_config_financiera", "sigarh_imagenologia", "sigarh_laboratorio",
                       "sigarh_recursos_humanos", "sigarh_mantenimiento", "sigarh_creacion_roles",
                       "sigarh_roles_pendientes", "sigarh_roles_aprobados", "sigarh_nutricion",
                       "sigarh_movimientos", "sigarh_general"]
        }
    },
]


async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

    async with AsyncSession() as db:
        print("Creando catalogo de modulos...")
        for m in MODULES_APP:
            mod = Module(code=m["code"], name=m["name"], category="app", is_active=True)
            db.add(mod)
        for m in MODULES_SIGARH:
            mod = Module(code=m["code"], name=m["name"], category="sigarh", is_active=True)
            db.add(mod)
        await db.flush()

        print("Creando niveles hospitalarios MINSA...")
        for n in NIVELES:
            level = HospitalLevel(
                code=n["code"], name=n["name"], description=n["description"],
                default_modules=n["default_modules"], sort_order=n["sort_order"], is_active=True,
            )
            db.add(level)

        await db.commit()
        print("Niveles hospitalarios y modulos creados correctamente")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
'''

with open("app/admin/seeder_niveles.py", "w", encoding="utf-8") as f:
    f.write(CONTENIDO)

print("seeder_niveles.py reescrito correctamente en UTF-8")