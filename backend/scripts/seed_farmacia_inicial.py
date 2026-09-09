"""Carga idempotente de datos iniciales para probar Farmacia en un tenant."""
import asyncio
import sys
import uuid

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.sigarh.config_farmacia.models import (
    Almacen,
    CatalogoFarmacia,
    Medicamento,
    ProveedorFarmacia,
)


ALMACENES = [
    ("ALM-CEN", "Almacén Central de Medicamentos", "ALMACEN", False, "Almacén central"),
    ("FAR-PRI", "Farmacia Principal", "FARMACIA", True, "Consulta externa"),
    ("FAR-EME", "Farmacia de Emergencia", "FARMACIA", True, "Emergencia"),
    ("FAR-HOS", "Farmacia de Hospitalización", "FARMACIA", True, "Hospitalización"),
    ("FAR-QX", "Farmacia de Centro Quirúrgico", "FARMACIA", True, "Centro quirúrgico"),
]

MEDICAMENTOS = [
    ("MED-0001", "PARACETAMOL 500 mg TABLETA", "Paracetamol", "500 mg", "TABLETA", "ORAL", "N02BE01", 0.12, False, False),
    ("MED-0002", "AMOXICILINA 500 mg CÁPSULA", "Amoxicilina", "500 mg", "CÁPSULA", "ORAL", "J01CA04", 0.35, True, False),
    ("MED-0003", "CEFTRIAXONA 1 g INYECTABLE", "Ceftriaxona", "1 g", "POLVO PARA INYECTABLE", "IV/IM", "J01DD04", 4.50, True, False),
    ("MED-0004", "CLORURO DE SODIO 0.9% 1000 mL", "Cloruro de sodio", "0.9%", "SOLUCIÓN INYECTABLE", "IV", "B05XA03", 4.20, True, False),
    ("MED-0005", "OMEPRAZOL 20 mg CÁPSULA", "Omeprazol", "20 mg", "CÁPSULA", "ORAL", "A02BC01", 0.18, True, False),
    ("MED-0006", "METAMIZOL SÓDICO 1 g/2 mL", "Metamizol sódico", "1 g/2 mL", "SOLUCIÓN INYECTABLE", "IV/IM", "N02BB02", 0.80, True, False),
    ("MED-0007", "SALBUTAMOL 100 mcg/dosis INHALADOR", "Salbutamol", "100 mcg/dosis", "AEROSOL", "INHALATORIA", "R03AC02", 8.50, True, False),
    ("MED-0008", "INSULINA HUMANA REGULAR 100 UI/mL", "Insulina humana", "100 UI/mL", "SOLUCIÓN INYECTABLE", "SUBCUTÁNEA", "A10AB01", 28.00, True, True),
    ("MED-0009", "LOSARTÁN 50 mg TABLETA", "Losartán", "50 mg", "TABLETA", "ORAL", "C09CA01", 0.16, True, False),
    ("MED-0010", "METFORMINA 850 mg TABLETA", "Metformina", "850 mg", "TABLETA", "ORAL", "A10BA02", 0.14, True, False),
    ("MED-0011", "DEXAMETASONA 4 mg/mL INYECTABLE", "Dexametasona", "4 mg/mL", "SOLUCIÓN INYECTABLE", "IV/IM", "H02AB02", 1.20, True, False),
    ("MED-0012", "AZITROMICINA 500 mg TABLETA", "Azitromicina", "500 mg", "TABLETA", "ORAL", "J01FA10", 1.10, True, False),
]

CATALOGOS = {
    "CONCEPTO_MOVIMIENTO": [("COMPRA", "Compra"), ("DISTRIBUCION", "Distribución"), ("DEVOLUCION", "Devolución"), ("AJUSTE", "Ajuste de inventario")],
    "TIPO_DOCUMENTO": [("OC", "Orden de compra"), ("PECOSA", "PECOSA"), ("GR", "Guía de remisión"), ("FACTURA", "Factura")],
    "FUENTE_FINANCIAMIENTO": [("SIS", "Seguro Integral de Salud"), ("PARTICULAR", "Particular"), ("DONACION", "Donación"), ("ESTRATEGIA", "Estrategia sanitaria")],
}


async def main(tenant_id: uuid.UUID):
    created = {"almacenes": 0, "medicamentos": 0, "proveedores": 0, "catalogos": 0}
    async with AsyncSessionLocal() as db:
        for codigo, nombre, tipo, despacha, ubicacion in ALMACENES:
            exists = await db.scalar(select(Almacen.id).where(Almacen.tenant_id == tenant_id, Almacen.codigo == codigo))
            if not exists:
                db.add(Almacen(tenant_id=tenant_id, codigo=codigo, nombre=nombre, tipo=tipo, despacha_recetas=despacha, ubicacion_fisica=ubicacion, fuente_financiamiento="SISMED"))
                created["almacenes"] += 1

        for codigo, nombre, dci, concentracion, forma, via, atc, precio, receta, frio in MEDICAMENTOS:
            exists = await db.scalar(select(Medicamento.id).where(Medicamento.tenant_id == tenant_id, Medicamento.codigo_interno == codigo))
            if not exists:
                db.add(Medicamento(tenant_id=tenant_id, codigo_interno=codigo, nombre_comercial=nombre, dci=dci, nombre_generico=dci, presentacion="UNIDAD", unidad="UNIDAD", concentracion=concentracion, forma_farmaceutica=forma, via_administracion=via, codigo_atc=atc, numero_registro_sanitario="DEMO-POR-VALIDAR", laboratorio_fabricante="POR CONFIGURAR", pais_origen="POR CONFIGURAR", condicion_venta="CON RECETA" if receta else "SIN RECETA", precio_referencia=precio, requiere_receta=receta, requiere_cadena_frio=frio, reporte_sismed=True, stock_minimo_alerta=10))
                created["medicamentos"] += 1

        supplier = await db.scalar(select(ProveedorFarmacia.id).where(ProveedorFarmacia.tenant_id == tenant_id, ProveedorFarmacia.ruc == "00000000000"))
        if not supplier:
            db.add(ProveedorFarmacia(tenant_id=tenant_id, ruc="00000000000", razon_social="PROVEEDOR DEMOSTRACIÓN - REEMPLAZAR", registro_digemid="DEMO-POR-VALIDAR"))
            created["proveedores"] += 1

        for categoria, values in CATALOGOS.items():
            for codigo, nombre in values:
                exists = await db.scalar(select(CatalogoFarmacia.id).where(CatalogoFarmacia.tenant_id == tenant_id, CatalogoFarmacia.categoria == categoria, CatalogoFarmacia.codigo == codigo))
                if not exists:
                    db.add(CatalogoFarmacia(tenant_id=tenant_id, categoria=categoria, codigo=codigo, nombre=nombre))
                    created["catalogos"] += 1
        await db.commit()
    print(created)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python scripts/seed_farmacia_inicial.py TENANT_UUID")
    asyncio.run(main(uuid.UUID(sys.argv[1])))
