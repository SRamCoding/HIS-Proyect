"""Catálogo base de profesiones del sector salud peruano."""

import uuid

NAMESPACE = uuid.UUID("8db4a31c-198e-4bf2-9c67-95da058239f5")
FUENTE = "MINSA / Decreto Legislativo N.° 1153"
FUENTE_URL = "https://www.congreso.gob.pe/Docs/DGP/DIDP/files/decreto_legislativo_1153.pdf"

GRUPOS = [
    ("GO-PS", "Profesional de la Salud", "otros_profesionales"),
    ("GO-TA", "Técnico Asistencial de la Salud", "tecnicos"),
    ("GO-AA", "Auxiliar Asistencial de la Salud", "tecnicos"),
    ("GO-ADM", "Personal Administrativo", None),
]

# Código, nombre, grupo, código de colegio profesional MINSA/FHIR y colegio.
PROFESIONES = [
    ("MED", "Médico Cirujano", "GO-PS", "01", "Colegio Médico del Perú", "medicos"),
    ("ODO", "Cirujano Dentista", "GO-PS", "03", "Colegio Odontológico del Perú", "otros_profesionales"),
    ("QFA", "Químico Farmacéutico", "GO-PS", "02", "Colegio Químico Farmacéutico del Perú", "otros_profesionales"),
    ("ENF", "Enfermero", "GO-PS", "06", "Colegio de Enfermeros del Perú", "otros_profesionales"),
    ("OBS", "Obstetra", "GO-PS", "05", "Colegio de Obstetras del Perú", "otros_profesionales"),
    ("BIO", "Biólogo", "GO-PS", "04", "Colegio de Biólogos del Perú", "otros_profesionales"),
    ("VET", "Médico Veterinario", "GO-PS", None, "Colegio Médico Veterinario del Perú", "otros_profesionales"),
    ("ISA", "Ingeniero Sanitario", "GO-PS", None, "Colegio de Ingenieros del Perú", "otros_profesionales"),
    ("PSI", "Psicólogo", "GO-PS", "08", "Colegio de Psicólogos del Perú", "otros_profesionales"),
    ("NUT", "Nutricionista", "GO-PS", "10", "Colegio de Nutricionistas del Perú", "otros_profesionales"),
    ("TSO", "Trabajador Social", "GO-PS", "07", "Colegio de Trabajadores Sociales del Perú", "otros_profesionales"),
    ("TME", "Tecnólogo Médico", "GO-PS", "09", "Colegio Tecnólogo Médico del Perú", "otros_profesionales"),
    ("QMC", "Químico", "GO-PS", None, None, "otros_profesionales"),
    ("TES", "Técnico Especializado en Fisioterapia, Laboratorio y Rayos X", "GO-TA", "00", None, "tecnicos"),
    ("TAS", "Técnico Asistencial de la Salud", "GO-TA", "00", None, "tecnicos"),
    ("AAS", "Auxiliar Asistencial de la Salud", "GO-AA", "00", None, "tecnicos"),
    ("ADM", "Profesional Administrativo", "GO-ADM", "00", None, None),
]


def stable_id(kind: str, tenant_id: uuid.UUID, code: str) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, f"{kind}:{tenant_id}:{code}")


async def asegurar_catalogo_personal(db, tenant_id):
    from sqlalchemy import select
    from app.sigarh.mantenimiento.models import GrupoOcupacional, Profesion

    grupos = {}
    for code, name, category in GRUPOS:
        grupo = await db.scalar(select(GrupoOcupacional).where(
            GrupoOcupacional.tenant_id == tenant_id,
            GrupoOcupacional.codigo == code,
        ))
        if not grupo:
            grupo = GrupoOcupacional(
                id=stable_id("group", tenant_id, code), tenant_id=tenant_id,
                codigo=code, nombre=name, categoria_personal=category,
                descripcion="Grupo ocupacional base del sector salud", is_active=True,
            )
            db.add(grupo)
        grupos[code] = grupo.id
    await db.flush()
    for code, name, group_code, college_code, college, category in PROFESIONES:
        if await db.scalar(select(Profesion.id).where(
            Profesion.tenant_id == tenant_id, Profesion.codigo == code,
        )):
            continue
        db.add(Profesion(
            id=stable_id("profession", tenant_id, code), tenant_id=tenant_id,
            grupo_ocupacional_id=grupos[group_code], codigo=code, nombre=name,
            codigo_colegio=college_code, colegio_profesional=college,
            categoria_personal=category, fuente=FUENTE, fuente_url=FUENTE_URL,
            es_base=True, is_active=True,
        ))
    await db.flush()
