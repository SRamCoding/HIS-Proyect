"""Importes del D.S. 232-2017-EF, artículos 3 a 5, para consulta y programación.

Transcripción contrastada con el anexo 7 de R.J. 000280-2022-MP-FN-JN-IMLCF.
No se suma el incremento histórico de 55% ni se presume derecho al pago.
"""
import uuid
from datetime import date
from decimal import Decimal
from sqlalchemy import select

FUENTE_URL = "https://cdn.www.gob.pe/uploads/document/file/6792759/5883027-r-j-n-000280-2022-mp-fn-jn-imlcf.pdf"
NAMESPACE = uuid.UUID("ecfb6930-8306-4c65-ae3a-806812fbe566")
VIGENCIA = date(2017, 8, 11)
TIPOS = (
    ("MINSA-GDO", "Guardia hospitalaria diurna ordinaria"),
    ("MINSA-GNO", "Guardia hospitalaria nocturna ordinaria"),
    ("MINSA-GDF", "Guardia hospitalaria diurna domingo/feriado"),
    ("MINSA-GNF", "Guardia hospitalaria nocturna domingo/feriado"),
)
MEDICOS = {
    "1": ("87.98", "117.30", "146.63", "175.96"),
    "2": ("92.21", "122.95", "153.68", "184.42"),
    "3": ("94.33", "125.77", "157.22", "188.65"),
    "4": ("98.81", "131.75", "164.69", "197.63"),
    "5": ("106.72", "142.29", "177.86", "213.44"),
}
ENFERMERIA = {
    "10": ("87.65", "116.87", "146.09", "175.31"),
    "11": ("90.06", "120.06", "150.09", "180.09"),
    "12": ("92.29", "123.04", "153.81", "184.56"),
    "13": ("94.47", "125.95", "157.45", "188.93"),
    "14": ("98.81", "131.75", "164.69", "197.63"),
}
OTROS = ("92.54", "123.38", "154.23", "185.07")
TECNICOS = ("36.67", "47.56", "59.45", "71.34")
AUXILIARES = ("34.71", "46.28", "57.85", "69.42")
FERIADOS_2026 = (
    (1, 1, "Año Nuevo"), (4, 2, "Jueves Santo"), (4, 3, "Viernes Santo"),
    (5, 1, "Día del Trabajo"), (6, 7, "Batalla de Arica y Día de la Bandera"),
    (6, 29, "San Pedro y San Pablo"), (7, 23, "Día de la Fuerza Aérea del Perú"),
    (7, 28, "Fiestas Patrias"), (7, 29, "Fiestas Patrias"), (8, 6, "Batalla de Junín"),
    (8, 30, "Santa Rosa de Lima"), (10, 8, "Combate de Angamos"),
    (11, 1, "Todos los Santos"), (12, 8, "Inmaculada Concepción"),
    (12, 9, "Batalla de Ayacucho"), (12, 25, "Navidad"),
)

def stable_id(tid, code):
    return uuid.uuid5(NAMESPACE, f"{tid}:{code}")

def importes_nivel(codigo):
    """Sin tarifa genérica: una profesión no identificada exige revisión."""
    prof, _, nivel = (codigo or "").partition("-")
    if prof == "MED":
        return MEDICOS.get(nivel)
    if prof == "ENF":
        return ENFERMERIA.get(nivel)
    if prof in {"OBS", "TME"}:
        niveles = ("I", "II", "III", "IV", "V") if prof == "OBS" else ("1", "2", "3", "4", "5")
        return ENFERMERIA[str(10 + niveles.index(nivel))] if nivel in niveles else None
    if prof in {"ODO", "QFA", "ISA", "VET", "BIO", "PSI", "NUT", "TSO"}:
        permitidos = {"I", "II", "III", "IV", "V"} if prof == "ODO" else {"IV", "V", "VI", "VII", "VIII"}
        return OTROS if nivel in permitidos else None
    # El catálogo de niveles contiene varias escalas. No equiparar SP/ST/SA.
    if prof == "TAS" and nivel in tuple("ST" + x for x in "ABCDEF"):
        return TECNICOS
    if prof == "AAS" and nivel in tuple("SA" + x for x in "ABCDEF"):
        return AUXILIARES
    return None

async def asegurar_guardias(db, tid, hospital_level):
    from app.sigarh.mantenimiento.models import TipoGuardia, HorarioGuardia, NivelRemunerativo, GuardiaValorizada
    from app.sigarh.rrhh.models import DiasFeriado
    hospitalario = (hospital_level or "").startswith(("II-", "III-"))
    tipos = {}
    for code, nombre in TIPOS:
        item = await db.scalar(select(TipoGuardia).where(TipoGuardia.tenant_id == tid, TipoGuardia.codigo == code))
        if not item:
            item = TipoGuardia(id=stable_id(tid, code), tenant_id=tid, codigo=code, nombre=nombre, horas=12,
                descripcion="D.S. 232-2017-EF. Requiere programación autorizada y ejecución efectiva.", is_active=hospitalario)
            db.add(item)
        tipos[code] = item.id
    await db.flush()
    for code, nombre, inicio, fin in (("MINSA-HD", "Guardia diurna 07:00–19:00", "07:00", "19:00"),
                                     ("MINSA-HN", "Guardia nocturna 19:00–07:00", "19:00", "07:00")):
        ident = stable_id(tid, code)
        if not await db.get(HorarioGuardia, ident):
            db.add(HorarioGuardia(id=ident, tenant_id=tid, nombre=nombre, hora_inicio=inicio, hora_fin=fin,
                tipo_guardia_id=tipos["MINSA-GDO" if code == "MINSA-HD" else "MINSA-GNO"],
                horas_totales=12, duracion_minutos=720, is_active=hospitalario))
    niveles = (await db.scalars(select(NivelRemunerativo).where(NivelRemunerativo.tenant_id == tid))).all()
    for nivel in niveles:
        valores = importes_nivel(nivel.codigo)
        if not valores:
            continue
        for (code, _), valor in zip(TIPOS, valores):
            existente = await db.scalar(select(GuardiaValorizada.id).where(
                GuardiaValorizada.tenant_id == tid, GuardiaValorizada.tipo_guardia_id == tipos[code],
                GuardiaValorizada.nivel_remunerativo_id == nivel.id,
                GuardiaValorizada.grupo_ocupacional_id.is_(None)))
            if not existente:
                db.add(GuardiaValorizada(id=stable_id(tid, code + ":" + nivel.codigo), tenant_id=tid,
                    tipo_guardia_id=tipos[code], nivel_remunerativo_id=nivel.id, valor=Decimal(valor), moneda="PEN",
                    vigencia_desde=VIGENCIA, is_active=hospitalario,
                    sustento="D.S. 232-2017-EF, arts. 3–5. Importes de la tabla publicada; referencia para programación. "
                    "Verificar régimen, plaza, autorización y ejecución antes de liquidar. Fuente: " + FUENTE_URL))
    for mes, dia, nombre in FERIADOS_2026:
        fecha = date(2026, mes, dia)
        if not await db.scalar(select(DiasFeriado.id).where(DiasFeriado.tenant_id == tid, DiasFeriado.fecha == fecha, DiasFeriado.tipo == "nacional")):
            db.add(DiasFeriado(id=stable_id(tid, "feriado:" + fecha.isoformat()), tenant_id=tid,
                fecha=fecha, nombre=nombre, tipo="nacional", is_active=True))
    await db.flush()
