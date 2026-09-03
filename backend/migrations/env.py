import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context
from app.admin.models import SystemRole, HospitalLevel, ModuleDependency, AuditLog
from app.core.config import settings
from app.core.database import Base
from app.modules.admision.models import Patient, ClinicalRecord, ClinicalRecordMovement
# Importar todos los modelos para que Alembic los detecte
from app.tenants.models import Tenant, TenantModule, Module
from app.auth.models import User
from app.sigarh.mantenimiento.models import (
    Departamento, Servicio, TipoTrabajador, TipoGuardia,
    NivelRemunerativo, HorarioGuardia, GrupoOcupacional,
    TipoActividad, Actividad, GuardiaValorizada,
    RolSistema, PerfilUsuario, Dependencia, UsuarioSigarh
)
from app.sigarh.rrhh.models import (
    Empleado, Especialidad, EmpleadoEspecialidad,
    DiasFeriado, MotivoJustificacion, Tolerancia,
    RegistroAsistencia, Justificacion
)

from app.sigarh.movimientos.models import Vacacion, Licencia, CambioTurno, Papeleta
from app.sigarh.infraestructura.models import Catalogo, Consultorio
from app.sigarh.infraestructura_hosp.models import Piso, Sala, Cama
from app.sigarh.config_farmacia.models import Almacen, Medicamento
from app.sigarh.config_financiera.models import Seguro, PlanSeguro, Caja, Tarifario
from app.sigarh.imagenologia.models import ExamenImagenologia
from app.sigarh.laboratorio.models import ExamenLaboratorio



config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()