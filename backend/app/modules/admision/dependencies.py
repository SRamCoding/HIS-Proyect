from fastapi import Depends
from app.tenants.entitlements import require_module

# Shortcut para usar en otros módulos que necesiten verificar admision
admision_required = Depends(require_module("pacientes"))