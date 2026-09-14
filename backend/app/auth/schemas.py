from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str
    panel: str  # admin, app, sigarh, portal


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    id: str
    name: str
    email: str
    role: str
    panel: str
    tenant_id: str | None = None
    tenant_name: str | None = None
    active_modules: list[str] = []
    permisos_accion: list[str] = []
    perfil_id: str | None = None
    perfil_hospital_id: str | None = None
    empleado_id: str | None = None
    alcance_global: bool = False


class RefreshRequest(BaseModel):
    refresh_token: str
