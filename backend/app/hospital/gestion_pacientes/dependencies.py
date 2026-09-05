# backend/app/modules/admision/dependencies.py
from fastapi import Depends
from app.tenants.entitlements import require_module_jwt

# Shortcut para usar en otros módulos que necesiten verificar admisión
admision_required = Depends(require_module_jwt("gestion_pacientes"))
