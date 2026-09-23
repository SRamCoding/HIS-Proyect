from pydantic import BaseModel


class SaludSistema(BaseModel):
    redis_ok: bool
    celery_ok: bool
    celery_workers_activos: int
    verificado_en: str


class DashboardStats(BaseModel):
    total_hospitals: int
    active_hospitals: int
    total_users: int
    active_users: int
    active_module_assignments: int
    audit_events_24h: int
    modules_distribution: dict[str, int]
    hospitals_by_month: list[dict]
    users_by_panel: dict[str, int]
    hospitals_by_level: list[dict]
    top_hospitals_by_modules: list[dict]
    audit_events_by_hour: list[dict]
    audit_actions: dict[str, int]
    usuarios_hospitales_consultados: int
    usuarios_hospitales_totales: int
    usuarios_es_parcial: bool
    actualizado_en: str
    hospitales_con_error: int
    hospitales_pendientes: int
    auditoria_fallback_pendientes: int
    usuarios_recientes: list[dict]
