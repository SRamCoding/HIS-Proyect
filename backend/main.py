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