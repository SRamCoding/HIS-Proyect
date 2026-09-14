"""UPSS de la NTS 021-MINSA/DGSP-V.03 y configuración base por categoría."""

import uuid

FUENTE = "MINSA"
NORMA = "NTS N.° 021-MINSA/DGSP-V.03 - Anexo 03"
FUENTE_URL = "https://www.minsa.gob.pe/Recursos/OTRANS/08Proyectos/2022/NTS%20021%20CATEGOR%C3%8DAS%20DE%20ES.pdf"
NAMESPACE = uuid.UUID("bf3859d2-c366-4098-9cdf-5af20114c121")

UPSS = [
    ("UPSS-CE", "Consulta Externa", "atencion_directa"),
    ("UPSS-HOSP", "Hospitalización", "atencion_directa"),
    ("UPSS-EMER", "Emergencia", "atencion_directa"),
    ("UPSS-CO", "Centro Obstétrico", "atencion_directa"),
    ("UPSS-CQ", "Centro Quirúrgico", "atencion_directa"),
    ("UPSS-UCI", "Unidad de Cuidados Intensivos", "atencion_directa"),
    ("UPSS-FARM", "Farmacia", "atencion_soporte"),
    ("UPSS-PC", "Patología Clínica", "atencion_soporte"),
    ("UPSS-NUT", "Nutrición y Dietética", "atencion_soporte"),
    ("UPSS-DI", "Diagnóstico por Imágenes", "atencion_soporte"),
    ("UPSS-MR", "Medicina de Rehabilitación", "atencion_soporte"),
    ("UPSS-CEST", "Central de Esterilización", "atencion_soporte"),
    ("UPSS-BS", "Centro de Hemoterapia y Banco de Sangre", "atencion_soporte"),
    ("UPSS-AP", "Anatomía Patológica", "atencion_soporte"),
    ("UPSS-HD", "Hemodiálisis", "atencion_soporte"),
]

_BASIC = {"UPSS-CE"}
_HOSPITAL = {code for code, _, _ in UPSS} - {"UPSS-UCI", "UPSS-HD"}
RECOMENDADAS = {
    "I-1": _BASIC,
    "I-2": _BASIC,
    "I-3": _BASIC | {"UPSS-PC"},
    "I-4": _BASIC | {"UPSS-FARM", "UPSS-PC"},
    "II-1": _HOSPITAL,
    "II-2": _HOSPITAL | {"UPSS-UCI"},
    "II-E": _HOSPITAL | {"UPSS-UCI"},
    "III-1": set(code for code, _, _ in UPSS),
    "III-2": set(code for code, _, _ in UPSS),
    "III-E": set(code for code, _, _ in UPSS),
}

# Servicios asistenciales base. Su activación es hospitalaria; la NTS regula UPSS,
# no obliga a que todas las IPRESS usen idénticos nombres organizacionales.
SERVICIOS = [
    ("SRV-MED", "Medicina", ["UPSS-CE", "UPSS-HOSP"]),
    ("SRV-CIR", "Cirugía", ["UPSS-CE", "UPSS-HOSP", "UPSS-CQ"]),
    ("SRV-PED", "Pediatría", ["UPSS-CE", "UPSS-HOSP", "UPSS-EMER"]),
    (
        "SRV-GIN",
        "Ginecología y Obstetricia",
        ["UPSS-CE", "UPSS-HOSP", "UPSS-CO", "UPSS-CQ"],
    ),
    ("SRV-ANE", "Anestesiología", ["UPSS-CQ", "UPSS-UCI"]),
    ("SRV-EME", "Medicina de Emergencias", ["UPSS-EMER"]),
    ("SRV-UCI", "Cuidados Intensivos", ["UPSS-UCI"]),
    ("SRV-DIA", "Apoyo Diagnóstico", ["UPSS-PC", "UPSS-DI", "UPSS-AP"]),
    ("SRV-REH", "Rehabilitación", ["UPSS-MR"]),
]

ESPECIALIDADES_SERVICIO = {
    "SRV-MED": [
        "CARDIOLOGÍA",
        "DERMATOLOGÍA",
        "ENDOCRINOLOGÍA",
        "GASTROENTEROLOGÍA",
        "GERIATRÍA",
        "HEMATOLOGÍA",
        "MEDICINA INTERNA",
        "NEFROLOGÍA",
        "NEUMOLOGÍA",
        "NEUROLOGÍA",
        "PSIQUIATRÍA",
        "REUMATOLOGÍA",
    ],
    "SRV-CIR": [
        "CIRUGÍA GENERAL",
        "CIRUGÍA ONCOLÓGICA",
        "CIRUGÍA PEDIÁTRICA",
        "CIRUGÍA PLÁSTICA",
        "NEUROCIRUGÍA",
        "OFTALMOLOGÍA",
        "ORTOPEDIA Y TRAUMATOLOGÍA",
        "OTORRINOLARINGOLOGÍA",
        "UROLOGÍA",
    ],
    "SRV-PED": ["PEDIATRÍA", "ADOLESCENTOLOGÍA"],
    "SRV-GIN": ["GINECOLOGÍA Y OBSTETRICIA"],
    "SRV-ANE": ["ANESTESIOLOGÍA"],
    "SRV-EME": ["MEDICINA DE EMERGENCIAS Y DESASTRES"],
    "SRV-UCI": ["MEDICINA INTENSIVA"],
    "SRV-DIA": ["ANATOMÍA PATOLÓGICA", "PATOLOGÍA CLÍNICA", "RADIOLOGÍA"],
    "SRV-REH": ["MEDICINA FÍSICA Y DE REHABILITACIÓN"],
}


def stable_id(kind: str, tenant_id: uuid.UUID, code: str) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, f"{kind}:{tenant_id}:{code}")
