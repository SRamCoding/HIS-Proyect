from typing import Literal
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=256)
    panel: Literal["admin", "app", "sigarh", "portal"]


class SessionResponse(BaseModel):
    """Respuesta de login/refresh/mfa-verify al NAVEGADOR: nunca lleva
    access_token/refresh_token en el body. Antes los devolvia igual (por
    "compatibilidad"), aunque el frontend ya no los leyera -- eso anulaba
    el punto entero de usar cookies httpOnly: cualquier script en el mismo
    origen (ej. via un XSS en otro modulo) podia simplemente llamar a
    fetch('/auth/refresh', {credentials:'include'}) el mismo y leer los
    tokens del JSON de respuesta, sin necesitar tocar la cookie httpOnly
    para nada. Los tokens viajan SOLO en las cookies (ver _set_auth_cookies
    en router.py); esta respuesta solo confirma la sesion con los datos no
    sensibles que la UI necesita mostrar."""
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


class MfaRequiredResponse(BaseModel):
    mfa_required: bool = True
    # True la primera vez (todavia no confirmo ningun codigo): el frontend
    # debe mostrar el QR/secreto para escanear. False en logins siguientes:
    # solo pide el codigo de 6 digitos.
    mfa_setup: bool
    otpauth_uri: str | None = None
    qr_png_base64: str | None = None
    secret: str | None = None


class MfaVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class RefreshRequest(BaseModel):
    # Opcional: si el navegador ya manda la cookie httpOnly del panel
    # correspondiente, el body puede venir vacio. Se mantiene el campo por
    # compatibilidad con cualquier cliente que todavia lo pase explicito.
    refresh_token: str | None = None
    # Que panel renovar: las cookies estan nombradas por panel (ver
    # PANELES_CON_COOKIE en auth/router.py) porque un mismo navegador puede
    # tener sesiones simultaneas en distintas pestañas (admin + un
    # hospital). Sin este dato, el backend no puede saber cual de las
    # cookies presentes usar.
    panel: str | None = None
