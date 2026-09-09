import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context
from app.admin.roles.models import SystemRole
from app.admin.niveles_hospitalarios.models import HospitalLevel
from app.admin.modulos.models import ModuleDependency
from app.admin.auditoria.models import AuditLog
from app.core.config import settings
from app.core.database import Base
from app.hospital.laboratorio.models import LabCorrelativo, LabCupo, LabMovimiento, LabMovimientoItem, LabFichaCovid
from app.hospital.admision.models import Patient, ClinicalRecord, ClinicalRecordMovement
from app.hospital.consulta_externa.models import ProgramacionMedica, Cita, Triaje, AtencionMedica, AtencionDiagnostico, Receta, RecetaItem, Hospitalizacion, OrdenLaboratorio, OrdenLaboratorioItem, OrdenImagen, OrdenImagenItem, Interconsulta, Referencia
from app.hospital.emergencia.models import AdmisionEmergencia, TriajeEmergencia, AtencionEmergencia, EmergenciaDiagnostico
from app.shared.ubigeo.models import UbigeoDepartamento, UbigeoProvincia, UbigeoDistrito
# Importar todos los modelos para que Alembic los detecte
from app.tenants.hospitales.models import Tenant, TenantModule
from app.tenants.modulos.models import Module
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
from app.sigarh.config_farmacia.models import Almacen, Medicamento, ProveedorFarmacia, CatalogoFarmacia
from app.hospital.farmacia.models import (FarmaciaCorrelativo, FarmaciaLote,
    FarmaciaMovimiento, FarmaciaMovimientoItem, FarmaciaDispensacion,
    FarmaciaDispensacionItem, FarmacotecniaOrden, FarmaciaVenta)
from app.sigarh.config_financiera.models import Seguro, PlanSeguro, Caja, Tarifario
from app.sigarh.imagenologia.models import ExamenImagenologia
from app.sigarh.laboratorio.models import ExamenLaboratorio
from app.sigarh.general.models import DiagnosticoCIE10, Paquete, TiempoProcedimiento
from app.sigarh.nutricion.models import RacionNutricion, CambioTurnoNutricion


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
