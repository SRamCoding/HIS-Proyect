"""Siembra datos de prueba para Configuración Farmacia (almacenes + medicamentos).

Uso:  python -m scripts.seed_config_farmacia [tenant_id]
Si no se pasa tenant_id, usa el tenant con empleados registrados.
"""
import asyncio
import sys
import uuid

import main  # noqa: F401  (carga todos los modelos para resolver FKs)
from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal
from app.sigarh.config_farmacia import service as svc
from app.sigarh.config_farmacia.schemas import AlmacenCreate, MedicamentoCreate
from app.sigarh.config_farmacia.models import Almacen, Medicamento
from app.sigarh.infraestructura.models import Catalogo


TIPOS_PRODUCTO = ["Medicamento", "Insumo médico", "Material de curación", "Reactivo de laboratorio"]

ALMACENES = [
    ("FAR-001", "Farmacia Principal", "farmacia", "sismed", "Piso 1, ala norte", True),
    ("FAR-002", "Farmacia de Emergencia", "farmacia", "sismed", "Emergencia, planta baja", True),
    ("FAR-003", "Farmacia de Hospitalización", "farmacia", "mixto", "Piso 3", True),
    ("ALM-001", "Almacén Central de Medicamentos", "almacen_central", "sismed", "Sótano - depósito 1", False),
    ("ALM-002", "Almacén de Insumos", "almacen_central", "donaciones", "Sótano - depósito 2", False),
    ("DIS-001", "Dispensación Consulta Externa", "dispensacion", "sismed", "Consulta externa, módulo 4", True),
    ("DIS-002", "Dispensación Programas Sociales", "dispensacion", "donaciones", "Consulta externa, módulo 7", True),
    ("LAB-001", "Almacén de Laboratorio Clínico", "laboratorio", "mixto", "Laboratorio, piso 2", False),
    ("FAR-004", "Farmacia de Centro Quirúrgico", "farmacia", "sismed", "Centro quirúrgico, piso 4", True),
    ("ALM-003", "Almacén de Cadena de Frío", "almacen_central", "sismed", "Sótano - cámara refrigerada", False),
]

# (codigo, comercial, generico, dci, presentacion, unidad, concentracion, forma, via, atc,
#  reg_sanitario, laboratorio, pais, condicion_venta, precio, requiere_receta, controlado,
#  digemid, sismed, precio_sismed, min_stock, cadena_frio, tmin, tmax)
MEDICAMENTOS = [
    ("MED-0001", "Panadol 500 mg", "Paracetamol", "Paracetamol", "Caja x 100 tabletas", "tableta", "500 mg", "tableta", "oral", "N02BE01",
     "EN-12345", "GlaxoSmithKline", "Perú", "sin_receta", 0.15, False, False, False, True, 0.12, 50, False, None, None),
    ("MED-0002", "Amoxil 500 mg", "Amoxicilina", "Amoxicilina", "Caja x 21 cápsulas", "capsula", "500 mg", "capsula", "oral", "J01CA04",
     "EN-22811", "Pfizer", "EE.UU.", "receta_simple", 0.40, True, False, True, True, 0.35, 30, False, None, None),
    ("MED-0003", "Tramal 100 mg/2 mL", "Tramadol", "Tramadol", "Ampolla 2 mL", "ampolla", "100 mg/2 mL", "ampolla", "intravenosa", "N02AX02",
     "EN-30012", "Grünenthal", "Alemania", "control_medico", 1.20, True, True, True, True, 1.10, 20, False, None, None),
    ("MED-0004", "Insulina NPH Humana", "Insulina isófana", "Insulina humana", "Frasco 10 mL (100 UI/mL)", "frasco_ampolla", "100 UI/mL", "frasco_ampolla", "subcutanea", "A10AC01",
     "EN-40233", "Novo Nordisk", "Dinamarca", "receta_retenida", 18.00, True, False, True, True, 16.50, 15, True, 2, 8),
    ("MED-0005", "Salbutamol Inhalador", "Salbutamol", "Salbutamol", "Inhalador 200 dosis", "inhalador", "100 mcg/dosis", "inhalador", "inhalada", "R03AC02",
     "EN-51002", "AstraZeneca", "Reino Unido", "receta_simple", 6.50, True, False, False, True, 6.00, 12, False, None, None),
    ("MED-0006", "Suero Fisiológico 0.9%", "Cloruro de sodio", "Cloruro de sodio", "Bolsa 1000 mL", "solucion", "0.9%", "solucion", "intravenosa", "B05CB01",
     "EN-60777", "Baxter", "Colombia", "sin_receta", 2.30, False, False, False, True, 2.00, 60, False, None, None),
    ("MED-0007", "Diclofenaco Gel 1%", "Diclofenaco", "Diclofenaco", "Tubo 30 g", "gel", "1%", "gel", "topica", "M02AA15",
     "EN-70991", "Medifarma", "Perú", "sin_receta", 3.10, False, False, False, True, 2.80, 25, False, None, None),
    ("MED-0008", "Morfina 10 mg/mL", "Morfina", "Morfina", "Ampolla 1 mL", "ampolla", "10 mg/mL", "ampolla", "intravenosa", "N02AA01",
     "EN-80145", "Farmindustria", "Perú", "control_medico", 2.90, True, True, True, True, 2.70, 10, False, None, None),
    ("MED-0009", "Ceftriaxona 1 g", "Ceftriaxona", "Ceftriaxona", "Vial polvo para inyección", "polvo_reconstituir", "1 g", "frasco_ampolla", "intravenosa", "J01DD04",
     "EN-90322", "Roche", "Suiza", "receta_simple", 1.80, True, False, True, True, 1.60, 30, False, None, None),
    ("MED-0010", "Loratadina 10 mg", "Loratadina", "Loratadina", "Caja x 10 tabletas", "tableta", "10 mg", "tableta", "oral", "R06AX13",
     "EN-10233", "Portugal S.A.", "Portugal", "sin_receta", 0.25, False, False, False, True, 0.20, 40, False, None, None),
    ("MED-0011", "Vacuna Antitetánica (dT)", "Toxoide diftérico y tetánico", "Toxoide tetánico", "Vial 0.5 mL monodosis", "frasco_ampolla", "0.5 mL", "frasco_ampolla", "intramuscular", "J07AM51",
     "EN-11888", "Sanofi Pasteur", "Francia", "receta_simple", 4.20, True, False, True, True, 3.90, 18, True, 2, 8),
    ("MED-0012", "Alcohol Yodado 10%", "Povidona yodada", "Povidona yodada", "Frasco 120 mL", "solucion", "10%", "solucion", "topica", "D08AG02",
     "EN-12099", "Drokasa", "Perú", "sin_receta", 4.90, False, False, False, False, None, 35, False, None, None),
]


async def seed(tenant_id: uuid.UUID):
    async with AsyncSessionLocal() as db:
        # ── tipos de producto (Infraestructura → Catálogos) ──
        existentes = {
            n for (n,) in (await db.execute(
                select(Catalogo.nombre).where(Catalogo.tenant_id == tenant_id, Catalogo.categoria == "tipos_producto")
            )).all()
        }
        for i, nombre in enumerate(TIPOS_PRODUCTO, 1):
            if nombre not in existentes:
                db.add(Catalogo(tenant_id=tenant_id, categoria="tipos_producto", codigo=f"TP{i:02d}", nombre=nombre, is_active=True))
        await db.commit()
        tipos = dict((await db.execute(
            select(Catalogo.nombre, Catalogo.id).where(Catalogo.tenant_id == tenant_id, Catalogo.categoria == "tipos_producto")
        )).all())
        tp_med = tipos.get("Medicamento")
        tp_ins = tipos.get("Insumo médico")

        # ── almacenes ──
        ya_alm = {a.codigo for a in (await db.execute(select(Almacen).where(Almacen.tenant_id == tenant_id))).scalars()}
        n_alm = 0
        for cod, nom, tipo, fte, ubic, desp in ALMACENES:
            if cod in ya_alm:
                continue
            await svc.crear_almacen(db, tenant_id, AlmacenCreate(
                codigo=cod, nombre=nom, tipo=tipo, fuente_financiamiento=fte,
                ubicacion_fisica=ubic, despacha_recetas=desp, is_active=True,
            ))
            n_alm += 1

        # ── medicamentos ──
        ya_med = {m.codigo_interno for m in (await db.execute(select(Medicamento).where(Medicamento.tenant_id == tenant_id))).scalars()}
        n_med = 0
        for row in MEDICAMENTOS:
            (cod, com, gen, dci, pres, uni, conc, forma, via, atc, rs, lab, pais, cv,
             precio, rec, ctrl, dig, sis, psis, mins, frio, tmin, tmax) = row
            if cod in ya_med:
                continue
            await svc.crear_medicamento(db, tenant_id, MedicamentoCreate(
                codigo_interno=cod, nombre_comercial=com, nombre_generico=gen, dci=dci,
                presentacion=pres, unidad=uni, concentracion=conc, forma_farmaceutica=forma,
                via_administracion=via, codigo_atc=atc, numero_registro_sanitario=rs,
                laboratorio_fabricante=lab, pais_origen=pais, condicion_venta=cv,
                tipo_producto_id=(tp_ins if "Suero" in com or "Alcohol" in com else tp_med),
                precio_referencia=precio, requiere_receta=rec, controlado=ctrl,
                fiscalizado_digemid=dig, reporte_sismed=sis, precio_referencia_sismed=psis,
                stock_minimo_alerta=mins, requiere_cadena_frio=frio,
                temperatura_min=tmin, temperatura_max=tmax, is_active=True,
            ))
            n_med += 1

        print(f"Tenant {tenant_id}")
        print(f"  tipos_producto: {len(tipos)}  |  almacenes nuevos: {n_alm}  |  medicamentos nuevos: {n_med}")
        tot_alm = await db.scalar(text("select count(*) from sigarh_almacenes where tenant_id=:t"), {"t": str(tenant_id)})
        tot_med = await db.scalar(text("select count(*) from sigarh_medicamentos where tenant_id=:t"), {"t": str(tenant_id)})
        print(f"  totales -> almacenes: {tot_alm}  medicamentos: {tot_med}")


async def _main():
    if len(sys.argv) > 1:
        tid = uuid.UUID(sys.argv[1])
    else:
        async with AsyncSessionLocal() as db:
            row = (await db.execute(text("select distinct tenant_id from sigarh_empleados limit 1"))).first()
        if not row:
            print("No hay tenant con empleados. Pasa el tenant_id como argumento.")
            return
        tid = row[0]
    await seed(tid)


if __name__ == "__main__":
    asyncio.run(_main())
