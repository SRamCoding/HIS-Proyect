# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import register_exception_handlers
from app.auth.router import router as auth_router

# ── Admin (submódulos independientes) ─────────────────────────
from app.admin.dashboard.router import router as admin_dashboard_router
from app.admin.hospitales.router import router as admin_hospitales_router
from app.admin.usuarios.router import router as admin_usuarios_router
from app.admin.niveles_hospitalarios.router import router as admin_niveles_router
from app.admin.roles.router import router as admin_roles_router
from app.admin.auditoria.router import router as admin_auditoria_router
from app.admin.modulos.router import router as admin_modulos_router
from app.admin.reportes.router import router as admin_reportes_router

# ── SIGARH ──────────────────────────────────────────────────
from app.sigarh.mantenimiento.router import router as sigarh_mant_router
from app.sigarh.rrhh.router import router as sigarh_rrhh_router
from app.sigarh.movimientos.router import router as sigarh_mov_router
from app.sigarh.infraestructura.router import router as sigarh_infra_router
from app.sigarh.infraestructura_hosp.router import router as sigarh_infra_hosp_router
from app.sigarh.config_farmacia.router import router as sigarh_farmacia_router
from app.sigarh.config_financiera.router import router as sigarh_financiera_router
from app.sigarh.imagenologia.router import router as sigarh_img_router
from app.sigarh.laboratorio.router import router as sigarh_lab_router
from app.sigarh.general.router import router as sigarh_general_router
from app.sigarh.nutricion.router import router as sigarh_nutricion_router
from app.sigarh.dashboard.router import router as sigarh_dashboard_router
from app.sigarh.creacion_roles.router import router as sigarh_creacion_roles_router
from app.sigarh.roles_pendientes.router import router as sigarh_roles_pendientes_router
from app.sigarh.roles_aprobados.router import router as sigarh_roles_aprobados_router

# ── Panel Hospitalario (app) ────────────────────────────────
from app.hospital.admision.router import router as hosp_admision_router
from app.hospital.hospitalizacion.router import router as hosp_hospitalizacion_router
from app.hospital.consulta_externa.router import router as hosp_consulta_externa_router
from app.hospital.emergencia.router import router as hosp_emergencia_router
from app.hospital.laboratorio.router import router as hosp_laboratorio_router
from app.hospital.imagenes.router import router as hosp_imagenes_router
from app.hospital.farmacia.router import router as hosp_farmacia_router
from app.hospital.caja.router import router as hosp_caja_router
from app.hospital.referencias.router import router as hosp_referencias_router
from app.hospital.auditoria.router import router as hosp_auditoria_router
from app.hospital.general.router import router as hosp_general_router
from app.hospital.fact_config.router import router as hosp_fact_config_router
from app.hospital.seguridad.router import router as hosp_seguridad_router
from app.hospital.archivo_clinico.router import router as hosp_archivo_clinico_router
from app.hospital.sis.router import router as hosp_sis_router
from app.hospital.his.router import router as hosp_his_router
from app.hospital.informes.router import router as hosp_informes_router
from app.hospital.telesalud.router import router as hosp_telesalud_router
from app.hospital.banco_sangre.router import router as hosp_banco_sangre_router
from app.hospital.hemodialisis.router import router as hosp_hemodialisis_router
from app.hospital.medicina_fisica.router import router as hosp_medicina_fisica_router
from app.hospital.firma_electronica.router import router as hosp_firma_electronica_router
from app.hospital.salud_ambiental.router import router as hosp_salud_ambiental_router
from app.hospital.epidemiologia.router import router as hosp_epidemiologia_router
from app.hospital.servicio_social.router import router as hosp_servicio_social_router
from app.hospital.procedimientos.router import router as hosp_procedimientos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    print(f" {settings.APP_NAME} iniciando en modo {settings.APP_ENV}")
    yield
    print(" Cerrando servidor...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.get("/health", tags=["sistema"])
async def health_check():
    return {
        "ok": True,
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
    }


# ── Routers ────────────────────────────────────────────────
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Admin — cada submódulo registrado por separado, mismo patrón que SIGARH
app.include_router(admin_dashboard_router, prefix="/admin", tags=["admin-dashboard"])
app.include_router(admin_hospitales_router, prefix="/admin", tags=["admin-hospitales"])
app.include_router(admin_usuarios_router, prefix="/admin", tags=["admin-usuarios"])
app.include_router(admin_niveles_router, prefix="/admin", tags=["admin-niveles-hospitalarios"])
app.include_router(admin_roles_router, prefix="/admin", tags=["admin-roles"])
app.include_router(admin_auditoria_router, prefix="/admin", tags=["admin-auditoria"])
app.include_router(admin_modulos_router, prefix="/admin", tags=["admin-modulos"])
app.include_router(admin_reportes_router, prefix="/admin", tags=["admin-reportes"])

# SIGARH
app.include_router(sigarh_mant_router, prefix="/sigarh/mantenimiento", tags=["sigarh-mantenimiento"])
app.include_router(sigarh_rrhh_router, prefix="/sigarh/rrhh", tags=["sigarh-rrhh"])
app.include_router(sigarh_mov_router, prefix="/sigarh/movimientos", tags=["sigarh-movimientos"])
app.include_router(sigarh_infra_router, prefix="/sigarh/infraestructura", tags=["sigarh-infraestructura"])
app.include_router(sigarh_infra_hosp_router, prefix="/sigarh/infraestructura-hosp", tags=["sigarh-infraestructura-hosp"])
app.include_router(sigarh_farmacia_router, prefix="/sigarh/config-farmacia", tags=["sigarh-config-farmacia"])
app.include_router(sigarh_financiera_router, prefix="/sigarh/config-financiera", tags=["sigarh-config-financiera"])
app.include_router(sigarh_img_router, prefix="/sigarh/imagenologia", tags=["sigarh-imagenologia"])
app.include_router(sigarh_lab_router, prefix="/sigarh/laboratorio", tags=["sigarh-laboratorio"])
app.include_router(sigarh_general_router, prefix="/sigarh/general", tags=["SIGARH - General"])
app.include_router(sigarh_nutricion_router, prefix="/sigarh/nutricion", tags=["SIGARH - Nutrición"])
app.include_router(sigarh_dashboard_router, prefix="/sigarh", tags=["SIGARH - Dashboard"])
app.include_router(sigarh_creacion_roles_router, prefix="/sigarh/creacion-roles", tags=["SIGARH - Creación de Roles"])
app.include_router(sigarh_roles_pendientes_router, prefix="/sigarh/roles-pendientes", tags=["SIGARH - Roles Pendientes"])
app.include_router(sigarh_roles_aprobados_router, prefix="/sigarh/roles-aprobados", tags=["SIGARH - Roles Aprobados"])

# Panel Hospitalario (app)
app.include_router(hosp_admision_router, prefix="/app/admision", tags=["app-admision"])
app.include_router(hosp_hospitalizacion_router, prefix="/app/hospitalizacion", tags=["app-hospitalizacion"])
app.include_router(hosp_consulta_externa_router, prefix="/app/consulta-externa", tags=["app-consulta-externa"])
app.include_router(hosp_emergencia_router, prefix="/app/emergencia", tags=["app-emergencia"])
app.include_router(hosp_laboratorio_router, prefix="/app/laboratorio", tags=["app-laboratorio"])
app.include_router(hosp_imagenes_router, prefix="/app/imagenes", tags=["app-imagenes"])
app.include_router(hosp_farmacia_router, prefix="/app/farmacia", tags=["app-farmacia"])
app.include_router(hosp_caja_router, prefix="/app/caja", tags=["app-caja"])
app.include_router(hosp_referencias_router, prefix="/app/referencias", tags=["app-referencias"])
app.include_router(hosp_auditoria_router, prefix="/app/auditoria", tags=["app-auditoria"])
app.include_router(hosp_general_router, prefix="/app/general", tags=["app-general"])
app.include_router(hosp_fact_config_router, prefix="/app/fact-config", tags=["app-fact-config"])
app.include_router(hosp_seguridad_router, prefix="/app/seguridad", tags=["app-seguridad"])
app.include_router(hosp_archivo_clinico_router, prefix="/app/archivo-clinico", tags=["app-archivo-clinico"])
app.include_router(hosp_sis_router, prefix="/app/sis", tags=["app-sis"])
app.include_router(hosp_his_router, prefix="/app/his", tags=["app-his"])
app.include_router(hosp_informes_router, prefix="/app/informes", tags=["app-informes"])
app.include_router(hosp_telesalud_router, prefix="/app/telesalud", tags=["app-telesalud"])
app.include_router(hosp_banco_sangre_router, prefix="/app/banco-sangre", tags=["app-banco-sangre"])
app.include_router(hosp_hemodialisis_router, prefix="/app/hemodialisis", tags=["app-hemodialisis"])
app.include_router(hosp_medicina_fisica_router, prefix="/app/medicina-fisica", tags=["app-medicina-fisica"])
app.include_router(hosp_firma_electronica_router, prefix="/app/firma-electronica", tags=["app-firma-electronica"])
app.include_router(hosp_salud_ambiental_router, prefix="/app/salud-ambiental", tags=["app-salud-ambiental"])
app.include_router(hosp_epidemiologia_router, prefix="/app/epidemiologia", tags=["app-epidemiologia"])
app.include_router(hosp_servicio_social_router, prefix="/app/servicio-social", tags=["app-servicio-social"])
app.include_router(hosp_procedimientos_router, prefix="/app/procedimientos", tags=["app-procedimientos"])