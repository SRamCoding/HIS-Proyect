import uuid
from datetime import datetime
from pydantic import BaseModel, Field

# Los limites de longitud reflejan las columnas de HospitalLevel
# (code String(10), name String(255), color String(20)) -- sin esto, un
# valor demasiado largo pasaba la validacion de Pydantic y reventaba
# como un error crudo de Postgres (DataError) en lugar de un 422 claro.


class HospitalLevelCreate(BaseModel):
    code: str = Field(min_length=1, max_length=10)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    color: str | None = Field(default=None, max_length=20)
    default_modules: dict = {}
    default_roles: dict = {}
    sort_order: int = 0
    is_active: bool = True


class HospitalLevelUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=10)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    color: str | None = Field(default=None, max_length=20)
    default_modules: dict | None = None
    default_roles: dict | None = None
    sort_order: int | None = None
    is_active: bool | None = None


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
