"""Plantilla operativa de actividades, editable según cartera del hospital.

Los códigos son internos del ERP, no un nomenclador oficial MINSA.
Marco de programación: R.M. 432-2025-MINSA / D.A. 378-MINSA/DGAIN-2025.
"""
import uuid
from sqlalchemy import select

FUENTE_URL = "https://www.gob.pe/institucion/minsa/normas-legales/6922180-432-2025-minsa"
NAMESPACE = uuid.UUID("347698cf-084a-4eab-a587-44d781f898a9")
TIPOS = (
    ("TA-AMB", "Atención ambulatoria"),
    ("TA-HOS", "Atención hospitalaria"),
    ("TA-EME", "Atención de emergencia"),
    ("TA-PRO", "Procedimientos diagnósticos y terapéuticos"),
    ("TA-NAS", "Trabajo no asistencial"),
)
# Código, nombre, tipo, requiere consultorio, genera agenda de consulta externa,
# actividad hospitalaria (inactiva en plantillas del primer nivel).
ACTIVIDADES = (
    ("ACT-CE", "Consulta externa", "TA-AMB", True, True, False),
    ("ACT-IC", "Interconsulta", "TA-HOS", False, False, True),
    ("ACT-VM", "Visita médica", "TA-HOS", False, False, True),
    ("ACT-HO", "Atención en hospitalización", "TA-HOS", False, False, True),
    ("ACT-EM", "Atención de emergencia", "TA-EME", False, False, True),
    ("ACT-PD", "Procedimientos diagnósticos", "TA-PRO", False, False, False),
    ("ACT-PT", "Procedimientos terapéuticos", "TA-PRO", False, False, False),
    ("ACT-GE", "Gestión", "TA-NAS", False, False, False),
    ("ACT-DO", "Docencia", "TA-NAS", False, False, False),
    ("ACT-IN", "Investigación", "TA-NAS", False, False, False),
)

async def asegurar_actividades(db, tid, hospital_level):
    from app.sigarh.mantenimiento.models import TipoActividad, Actividad
    hospitalario = (hospital_level or "").startswith(("II-", "III-"))
    tipos = {}
    for code, nombre in TIPOS:
        item = await db.scalar(select(TipoActividad).where(TipoActividad.tenant_id == tid, TipoActividad.codigo == code))
        if not item:
            item = TipoActividad(id=uuid.uuid5(NAMESPACE, f"{tid}:tipo:{code}"), tenant_id=tid,
                codigo=code, nombre=nombre, is_active=True)
            db.add(item)
        tipos[code] = item.id
    await db.flush()
    for code, nombre, tipo, consultorio, agenda, hospital in ACTIVIDADES:
        if not await db.scalar(select(Actividad.id).where(Actividad.tenant_id == tid, Actividad.codigo == code)):
            db.add(Actividad(id=uuid.uuid5(NAMESPACE, f"{tid}:actividad:{code}"), tenant_id=tid,
                codigo=code, nombre=nombre, tipo_actividad_id=tipos[tipo], requiere_consultorio=consultorio,
                genera_agenda=agenda, is_active=hospitalario or not hospital))
    await db.flush()
