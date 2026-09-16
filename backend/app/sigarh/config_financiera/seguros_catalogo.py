"""Catálogo estándar de fuentes de financiamiento (aseguradoras) reconocidas
en el sistema de salud peruano: SIS, EsSalud, Sanidad de las Fuerzas Armadas,
Sanidad PNP, EPS (seguros privados), SOAT y Particular. Son las categorías de
"financiador" que ya usa el Formato HIS-MINSA y el propio SIS para clasificar
la atención -- no una lista inventada para este proyecto.

Es una plantilla editable, igual que asegurar_departamentos(): siembra el
nombre y si exige FUA (documento propio del SIS), nunca un precio. El precio
de cada combinación tarifa+seguro es un dato real de negocio de cada hospital
y debe configurarse manualmente en Tarifario -- eso no se inventa aquí.
"""
import uuid
from sqlalchemy import select

SEGUROS = (
    ("SIS", "SIS - Seguro Integral de Salud", "Público", True,
     "Seguro público subsidiado/semicontributivo administrado por el Pliego SIS. Requiere Formato Único de Atención (FUA) para el reembolso."),
    ("ESSALUD", "EsSalud - Seguro Social de Salud", "Público", False,
     "Seguro Social de Salud (EsSalud), régimen contributivo por planilla."),
    ("FFAA", "Sanidad de las Fuerzas Armadas", "Público", False,
     "Cobertura de salud del personal militar y sus derechohabientes."),
    ("PNP", "Sanidad de la Policía Nacional del Perú", "Público", False,
     "Cobertura de salud del personal policial y sus derechohabientes."),
    ("EPS", "EPS - Entidad Prestadora de Salud", "Privado", False,
     "Seguros privados complementarios al régimen contributivo (Ley N.° 26790)."),
    ("SOAT", "SOAT - Seguro Obligatorio de Accidentes de Tránsito", "Privado", False,
     "Cobertura obligatoria para víctimas de accidentes de tránsito."),
    ("PARTICULAR", "Particular", "Privado", False,
     "Pago directo del paciente, sin seguro de por medio."),
)


def seguro_id(tid: uuid.UUID, codigo: str) -> uuid.UUID:
    """UUID determinístico por tenant+código -- reintentar la siembra no duplica filas."""
    return uuid.uuid5(uuid.UUID("f4c1a6b2-9e3d-4a7c-8b1e-2d5f6a9c0e17"), f"{tid}:{codigo}")


async def asegurar_seguros_estandar(db, tid: uuid.UUID) -> int:
    """Crea los seguros estándar que falten en este hospital. Idempotente:
    si el hospital ya tiene un seguro con ese código, no lo toca (puede haberlo
    editado). Devuelve cuántos se crearon."""
    from app.sigarh.config_financiera.models import Seguro

    existentes = {s.codigo for s in (await db.scalars(
        select(Seguro).where(Seguro.tenant_id == tid, Seguro.codigo.in_([c for c, *_ in SEGUROS]))
    )).all()}
    creados = 0
    for codigo, nombre, tipo_entidad, requiere_fua, notas in SEGUROS:
        if codigo in existentes:
            continue
        db.add(Seguro(id=seguro_id(tid, codigo), tenant_id=tid, codigo=codigo, nombre=nombre,
            tipo_entidad=tipo_entidad, requiere_fua=requiere_fua, notas=notas, is_active=True))
        creados += 1
    await db.flush()
    return creados
