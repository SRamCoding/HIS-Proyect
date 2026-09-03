import uuid
from datetime import datetime
from pydantic import BaseModel


# ─── Dashboard ────────────────────────────────────────────────────────────────

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


# ─── Hospitales ───────────────────────────────────────────────────────────────

class HospitalListItem(BaseModel):
    id: uuid.UUID
    name: str
    domain: str
    hospital_level: str | None
    is_active: bool
    active_modules: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ModuleToggle(BaseModel):
    tenant_id: uuid.UUID
    module_codes: list[str]


# ─── Niveles Hospitalarios ────────────────────────────────────────────────────

class HospitalLevelCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    color: str | None = None
    default_modules: list[str] = []
    default_roles: list[str] = []
    sort_order: int = 0


class HospitalLevelResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    description: str | None = None
    color: str | None = None
    default_modules: dict | None = None
    sort_order: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

# ─── Dependencias de Módulos ──────────────────────────────────────────────────

class ModuleDependencyCreate(BaseModel):
    module_code: str
    depends_on_code: str
    is_required: bool = True


class ModuleDependencyResponse(ModuleDependencyCreate):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── System Roles ─────────────────────────────────────────────────────────────

class SystemRoleCreate(BaseModel):
    name: str
    label: str
    panel: str
    required_module: str | None = None
    allowed_modules: list[str] = []
    sort_order: int = 0


class SystemRoleResponse(SystemRoleCreate):
    id: uuid.UUID
    is_active: bool

    model_config = {"from_attributes": True}


# ─── Usuarios ─────────────────────────────────────────────────────────────────

class UserListItem(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: str
    panel: str
    tenant_id: uuid.UUID | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str
    panel: str
    tenant_id: uuid.UUID | None = None


# ─── Auditoría ────────────────────────────────────────────────────────────────

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_name: str | None
    tenant_name: str | None
    action: str
    model: str | None
    description: str | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Reportes ─────────────────────────────────────────────────────────────────

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
