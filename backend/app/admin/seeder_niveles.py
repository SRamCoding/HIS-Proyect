"""
Ejecutar con:
python -m app.admin.seeder_niveles
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.core.database import Base
from app.tenants.models import Tenant, TenantModule, Module
from app.auth.models import User
from app.admin.models import SystemRole, HospitalLevel, ModuleDependency, AuditLog


# ─── Módulos del Panel Administrativo (/app) ──────────────────────────────────
MODULES_APP = [
    {"code": "pacientes",           "name": "Pacientes"},
    {"code": "altas_pacientes",     "name": "Altas de Pacientes"},
    {"code": "consulta_externa",    "name": "Consulta Externa"},
    {"code": "archivo_clinico",     "name": "Archivo Clínico"},
    {"code": "agendamiento_citas",  "name": "Agendamiento de Citas"},
    {"code": "farmacia",            "name": "Farmacia"},
    {"code": "programacion_medica", "name": "Programación Médica"},
    {"code": "laboratorio",         "name": "Laboratorio"},
    {"code": "emergencia",          "name": "Emergencia"},
    {"code": "imagenologia",        "name": "Imagenología"},
    {"code": "hospitalizacion",     "name": "Hospitalización"},
    {"code": "caja_facturacion",    "name": "Caja y Facturación"},
    {"code": "sis_fua",             "name": "SIS / FUA"},
    {"code": "his",                 "name": "HIS"},
    {"code": "reportes",            "name": "Reportes"},
    {"code": "telemedicina",        "name": "Telemedicina"},
    {"code": "archivo",             "name": "Archivo"},
    {"code": "seguimiento_paciente","name": "Seguimiento Paciente"},
    {"code": "nutricion",           "name": "Nutrición"},
]

# ─── Módulos del Panel SIGARH (/sigarh) ───────────────────────────────────────
MODULES_SIGARH = [
    {"code": "sigarh_infraestructura",          "name": "Infraestructura"},
    {"code": "sigarh_infraestructura_hosp",     "name": "Infraestructura Hospitalaria"},
    {"code": "sigarh_config_farmacia",          "name": "Configuración Farmacia"},
    {"code": "sigarh_config_financiera",        "name": "Configuración Financiera"},
    {"code": "sigarh_imagenologia",             "name": "Imagenología"},
    {"code": "sigarh_laboratorio",              "name": "Laboratorio"},
    {"code": "sigarh_recursos_humanos",         "name": "Recursos Humanos"},
    {"code": "sigarh_mantenimiento",            "name": "Mantenimiento"},
    {"code": "sigarh_creacion_roles",           "name": "Creación de Roles"},
    {"code": "sigarh_roles_pendientes",         "name": "Roles Pendientes"},
    {"code": "sigarh_roles_aprobados",          "name": "Roles Aprobados"},
    {"code": "sigarh_nutricion",                "name": "Nutrición"},
    {"code": "sigarh_movimientos",              "name": "Movimientos"},
    {"code": "sigarh_general",                  "name": "General"},
]

# ─── Niveles Hospitalarios MINSA ──────────────────────────────────────────────
NIVELES = [
    {
        "code": "I-1",
        "name": "Puesto de Salud (sin médico)",
        "description": "Puesto de Salud sin médico",
        "color": "#6B7280",
        "sort_order": 1,
        "default_modules": {
            "app": [
                "pacientes", "consulta_externa", "farmacia",
                "sis_fua", "reportes", "telemedicina", "nutricion"
            ],
            "sigarh": [
                "sigarh_infraestructura", "sigarh_recursos_humanos",
                "sigarh_mantenimiento", "sigarh_general",
                "sigarh_creacion_roles", "sigarh_roles_pendientes",
                "sigarh_roles_aprobados"
            ]
        }
    },
    {
        "code": "I-2",
        "name": "Puesto de Salud (con médico)",
        "description": "Puesto de Salud con médico",
        "color": "#0EA5E9",
        "sort_order": 2,
        "default_modules": {
            "app": [
                "pacientes", "consulta_externa", "farmacia",
                "agendamiento_citas", "sis_fua", "reportes",
                "telemedicina", "nutricion", "his", "archivo_clinico"
            ],
            "sigarh": [
                "sigarh_infraestructura", "sigarh_recursos_humanos",
                "sigarh_mantenimiento", "sigarh_general",
                "sigarh_creacion_roles", "sigarh_roles_pendientes",
                "sigarh_roles_aprobados"
            ]
        }
    },
    {
        "code": "I-3",
        "name": "Centro de Salud sin internamiento",
        "description": "Centro de Salud sin internamiento",
        "color": "#3B82F6",
        "sort_order": 3,
        "default_modules": {
            "app": [
                "pacientes", "consulta_externa", "farmacia",
                "agendamiento_citas", "programacion_medica",
                "sis_fua", "his", "reportes", "telemedicina",
                "nutricion", "archivo_clinico"
            ],
            "sigarh": [
                "sigarh_infraestructura", "sigarh_recursos_humanos",
                "sigarh_mantenimiento", "sigarh_general",
                "sigarh_creacion_roles", "sigarh_roles_pendientes",
                "sigarh_roles_aprobados"
            ]
        }
    },
    {
        "code": "I-4",
        "name": "Centro de Salud con internamiento",
        "description": "Centro de Salud con internamiento",
        "color": "#8B5CF6",
        "sort_order": 4,
        "default_modules": {
            "app": [
                "pacientes", "consulta_externa", "farmacia",
                "agendamiento_citas", "programacion_medica",
                "hospitalizacion", "sis_fua", "his",
                "reportes", "telemedicina", "nutricion", "archivo_clinico"
            ],
            "sigarh": [
                "sigarh_infraestructura", "sigarh_infraestructura_hosp",
                "sigarh_recursos_humanos", "sigarh_mantenimiento",
                "sigarh_general", "sigarh_creacion_roles",
                "sigarh_roles_pendientes", "sigarh_roles_aprobados"
            ]
        }
    },
    {
        "code": "II-1",
        "name": "Hospital de Apoyo",
        "description": "Hospital de Apoyo",
        "color": "#F97316",
        "sort_order": 5,
        "default_modules": {
            "app": [
                "pacientes", "consulta_externa", "farmacia",
                "agendamiento_citas", "programacion_medica",
                "emergencia", "hospitalizacion", "laboratorio",
                "sis_fua", "his", "reportes", "telemedicina",
                "nutricion", "archivo_clinico", "caja_facturacion"
            ],
            "sigarh": [
                "sigarh_infraestructura", "sigarh_infraestructura_hosp",
                "sigarh_config_farmacia", "sigarh_recursos_humanos",
                "sigarh_mantenimiento", "sigarh_laboratorio",
                "sigarh_general", "sigarh_creacion_roles",
                "sigarh_roles_pendientes", "sigarh_roles_aprobados"
            ]
        }
    },
    {
        "code": "II-2",
        "name": "Hospital General",
        "description": "Hospital General",
        "color": "#EF4444",
        "sort_order": 6,
        "default_modules": {
            "app": [
                "pacientes", "consulta_externa", "farmacia",
                "agendamiento_citas", "programacion_medica",
                "emergencia", "hospitalizacion", "laboratorio",
                "sis_fua", "his", "reportes", "telemedicina",
                "nutricion", "archivo_clinico", "caja_facturacion"
            ],
            "sigarh": [
                "sigarh_infraestructura", "sigarh_infraestructura_hosp",
                "sigarh_config_farmacia", "sigarh_config_financiera",
                "sigarh_recursos_humanos", "sigarh_mantenimiento",
                "sigarh_laboratorio", "sigarh_general",
                "sigarh_creacion_roles", "sigarh_roles_pendientes",
                "sigarh_roles_aprobados", "sigarh_movimientos"
            ]
        }
    },
    {
        "code": "III-1",
        "name": "Hospital Nacional / Especializado",
        "description": "Hospital Nacional / Especializado",
        "color": "#16A34A",
        "sort_order": 7,
        "default_modules": {
            "app": [
                "pacientes", "altas_pacientes", "consulta_externa",
                "farmacia", "agendamiento_citas", "programacion_medica",
                "emergencia", "hospitalizacion", "laboratorio",
                "imagenologia", "sis_fua", "his", "reportes",
                "telemedicina", "nutricion", "archivo_clinico",
                "caja_facturacion", "seguimiento_paciente"
            ],
            "sigarh": [
                "sigarh_infraestructura", "sigarh_infraestructura_hosp",
                "sigarh_config_farmacia", "sigarh_config_financiera",
                "sigarh_imagenologia", "sigarh_laboratorio",
                "sigarh_recursos_humanos", "sigarh_mantenimiento",
                "sigarh_creacion_roles", "sigarh_roles_pendientes",
                "sigarh_roles_aprobados", "sigarh_nutricion",
                "sigarh_movimientos", "sigarh_general"
            ]
        }
    },
    {
        "code": "III-2",
        "name": "Instituto Nacional / INEN / INS",
        "description": "Instituto Nacional / INEN / INS",
        "color": "#1d4ed8",
        "sort_order": 8,
        "default_modules": {
            "app": [
                "pacientes", "altas_pacientes", "consulta_externa",
                "archivo_clinico", "agendamiento_citas", "farmacia",
                "programacion_medica", "emergencia", "hospitalizacion",
                "sis_fua", "his", "reportes", "telemedicina",
                "seguimiento_paciente", "nutricion"
            ],
            "sigarh": [
                "sigarh_infraestructura", "sigarh_infraestructura_hosp",
                "sigarh_config_farmacia", "sigarh_config_financiera",
                "sigarh_imagenologia", "sigarh_laboratorio",
                "sigarh_recursos_humanos", "sigarh_mantenimiento",
                "sigarh_creacion_roles", "sigarh_roles_pendientes",
                "sigarh_roles_aprobados", "sigarh_nutricion",
                "sigarh_movimientos", "sigarh_general"
            ]
        }
    },
]


async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

    async with AsyncSession() as db:
        # ─── Catálogo de módulos ───────────────────────────────────────────
        print("📦 Creando catálogo de módulos...")
        for m in MODULES_APP:
            mod = Module(code=m["code"], name=m["name"], category="app", is_active=True)
            db.add(mod)
        for m in MODULES_SIGARH:
            mod = Module(code=m["code"], name=m["name"], category="sigarh", is_active=True)
            db.add(mod)
        await db.flush()

        # ─── Niveles hospitalarios ─────────────────────────────────────────
        print("🏥 Creando niveles hospitalarios MINSA...")
        for n in NIVELES:
            level = HospitalLevel(
                code=n["code"],
                name=n["name"],
                description=n["description"],
                default_modules=n["default_modules"],
                sort_order=n["sort_order"],
                is_active=True,
            )
            db.add(level)

        await db.commit()
        print("✓ Niveles hospitalarios y módulos creados correctamente")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())