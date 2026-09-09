"""Esquemas de respuesta del dashboard SIGARH.

Documentan el contrato que consume el frontend (pages/sigarh/index.vue).
"""
from pydantic import BaseModel


class KpisResumen(BaseModel):
    total_empleados: int
    empleados_activos: int
    empleados_inactivos: int
    asistencia_hoy: int          # presente + tardanza + justificado
    ausentes_hoy: int
    porcentaje_asistencia: float  # asistencia_hoy / empleados_activos * 100
    solicitudes_pendientes: int   # vacaciones + licencias + papeletas + cambios de turno
    justificaciones_pendientes: int


class ConteoMovimientos(BaseModel):
    vacaciones: int
    licencias: int
    papeletas: int
    cambios_turno: int


class ResumenCamas(BaseModel):
    total: int
    disponibles: int
    ocupadas: int
    mantenimiento: int
    reservadas: int
    porcentaje_ocupacion: float


class DistribucionGenero(BaseModel):
    masculino: int
    femenino: int
    sin_registrar: int


class DistribucionEstado(BaseModel):
    activos: int
    inactivos: int
    en_vacaciones: int
    en_licencia: int


class PuntoEmpleadosMes(BaseModel):
    label: str        # "abr"
    anio: int
    valor: int        # empleados dados de alta ese mes


class PuntoAsistenciaSemana(BaseModel):
    label: str        # "01/09"
    presentes: int
    ausentes: int
    total: int


class PuntoTendenciaSolicitudes(BaseModel):
    label: str        # "abr"
    anio: int
    vacaciones: int
    licencias: int
    papeletas: int
    cambios_turno: int
    total: int


class UltimaVacacion(BaseModel):
    id: str
    empleado_nombre: str
    tipo: str
    fecha_inicio: str
    fecha_fin: str
    estado: str


class UltimaLicencia(BaseModel):
    id: str
    empleado_nombre: str
    fecha_tramite: str
    fecha_inicio: str
    fecha_fin: str
    estado: str


class DashboardResponse(BaseModel):
    fecha: str
    kpis: KpisResumen
    movimientos_mes: ConteoMovimientos
    pendientes: ConteoMovimientos
    camas: ResumenCamas
    distribucion_genero: DistribucionGenero
    distribucion_estado: DistribucionEstado
    empleados_por_mes: list[PuntoEmpleadosMes]
    asistencia_semanal: list[PuntoAsistenciaSemana]
    tendencias_solicitudes: list[PuntoTendenciaSolicitudes]
    ultimas_vacaciones: list[UltimaVacacion]
    ultimas_licencias: list[UltimaLicencia]
