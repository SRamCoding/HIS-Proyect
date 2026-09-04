from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.admin.router import router as admin_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import register_exception_handlers
from app.auth.router import router as auth_router
from app.tenants.router import router as tenants_router
from app.modules.admision.router import router as admision_router
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    print(f"🏥 {settings.APP_NAME} iniciando en modo {settings.APP_ENV}")
    yield
    print("🏥 Cerrando servidor...")


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


# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(tenants_router, prefix="/admin/tenants", tags=["admin"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(admision_router, prefix="/app/admision", tags=["admision"])
app.include_router(sigarh_mant_router, prefix="/sigarh/mantenimiento", tags=["sigarh-mantenimiento"])
app.include_router(sigarh_rrhh_router, prefix="/sigarh/rrhh", tags=["sigarh-rrhh"])
app.include_router(sigarh_mov_router, prefix="/sigarh/movimientos", tags=["sigarh-movimientos"])
app.include_router(sigarh_infra_router, prefix="/sigarh/infraestructura", tags=["sigarh-infraestructura"])
app.include_router(sigarh_infra_hosp_router, prefix="/sigarh/infraestructura-hosp", tags=["sigarh-infraestructura-hosp"])
app.include_router(sigarh_farmacia_router, prefix="/sigarh/config-farmacia", tags=["sigarh-config-farmacia"])
app.include_router(sigarh_financiera_router, prefix="/sigarh/config-financiera", tags=["sigarh-config-financiera"])
app.include_router(sigarh_img_router, prefix="/sigarh/imagenologia", tags=["sigarh-imagenologia"])
app.include_router(sigarh_lab_router, prefix="/sigarh/laboratorio", tags=["sigarh-laboratorio"])
app.include_router(sigarh_general_router,   prefix="/sigarh/general",   tags=["SIGARH - General"])
app.include_router(sigarh_nutricion_router, prefix="/sigarh/nutricion", tags=["SIGARH - Nutrición"])