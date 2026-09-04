from pydantic import BaseModel


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
