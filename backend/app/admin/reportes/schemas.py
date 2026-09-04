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
