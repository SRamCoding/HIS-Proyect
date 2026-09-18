"""Esquemas de respuesta del dashboard del panel hospitalario (Escritorio).

Documentan el contrato que consume frontend/components/DashboardGeneral.vue.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel


class KpisResumen(BaseModel):
    camas_total: int
    camas_ocupadas: int
    citas_hoy_total: int
    citas_hoy_pendientes: int
    citas_hoy_atendidas: int
    emergencias_en_atencion: int
    lab_pendientes: int
    recetas_pendientes: int


class PuntoSerieSemana(BaseModel):
    label: str        # "16/09"
    ingresos: int      # hospitalizacion
    altas: int         # hospitalizacion
    citas: int         # consulta_externa
    emergencias: int   # emergencia


class PuntoActividadHora(BaseModel):
    label: str    # "00:00"
    valor: int


class PacienteReciente(BaseModel):
    id: uuid.UUID
    nombre: str
    dni: str | None
    edad: int
    created_at: datetime


class DashboardResponse(BaseModel):
    fecha: str
    kpis: KpisResumen
    serie_semana: list[PuntoSerieSemana]
    actividad_por_hora: list[PuntoActividadHora]
    pacientes_recientes: list[PacienteReciente]


class KpisMedico(BaseModel):
    citas_hoy_total: int
    citas_hoy_pendientes: int
    citas_hoy_atendidas: int
    jornadas_mes: int
    pacientes_semana: int


class PuntoSerieMedico(BaseModel):
    label: str
    citas: int


class ProximaCita(BaseModel):
    id: uuid.UUID
    hora: str
    paciente: str
    estado: str


class DashboardMedicoResponse(BaseModel):
    fecha: str
    kpis: KpisMedico
    serie_semana: list[PuntoSerieMedico]
    proximas_citas: list[ProximaCita]
