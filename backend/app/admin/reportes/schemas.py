# backend/app/admin/reportes/schemas.py
import uuid
from datetime import datetime
from pydantic import BaseModel


class MonthlyReportItem(BaseModel):
    month: str
    total_hospitals: int
    new_hospitals: int
    total_users: int


class HospitalModuleReportItem(BaseModel):
    hospital_name: str
    domain: str
    active_modules: list[str]
    total_modules: int


class ModuleCoverageItem(BaseModel):
    code: str
    name: str
    hospitals_with_module: int
    total_hospitals: int
    percentage: float


class HospitalMonthlySummary(BaseModel):
    id: uuid.UUID
    hospital_name: str
    domain: str
    is_active: bool
    pacientes_nuevos: int
    usuarios_count: int
    modules_count: int
    created_at: datetime
    disponible: bool = True


class HospitalRegistradoPeriodo(BaseModel):
    name: str
    domain: str
    created_at: datetime


class MonthlyReportResponse(BaseModel):
    month: str
    total_hospitales_activos: int
    pacientes_nuevos_total: int
    modules_coverage: list[ModuleCoverageItem]
    hospitales: list[HospitalMonthlySummary]
    hospitales_registrados_periodo: list[HospitalRegistradoPeriodo]
    usuarios_centrales_registrados: int
    hospitales_consultados: int = 0
    hospitales_totales: int = 0
    es_parcial: bool = False