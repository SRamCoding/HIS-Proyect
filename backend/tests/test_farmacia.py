"""Pruebas HTTP/PostgreSQL del inventario farmacéutico."""
import unittest, uuid
from datetime import date
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.sigarh.config_farmacia.models import Almacen, Medicamento
from app.sigarh.config_financiera.models import Caja as CajaFisica
from app.hospital.caja.models import CajaSesion, Cobro, CobroItem
from app.hospital.admision.models import Patient, ClinicalRecord
from app.sigarh.rrhh.models import Empleado

class FarmaciaTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.store,self.pharmacy,self.med=uuid.uuid4(),uuid.uuid4(),uuid.uuid4()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id,module_code="farmacia"))
            db.add_all([Almacen(id=self.store,tenant_id=self.tenant_id,codigo="ALM-T",nombre="Almacén Test",tipo="almacen"),Almacen(id=self.pharmacy,tenant_id=self.tenant_id,codigo="FAR-T",nombre="Farmacia Test",tipo="farmacia"),Medicamento(id=self.med,tenant_id=self.tenant_id,codigo_interno="MED-T",nombre_comercial="Medicamento Test",unidad="TABLETA",numero_registro_sanitario="RS-T")])
            await db.commit()
        self.claims["role"]="farmacia";from app.core.security import create_access_token
        self.client.headers["Authorization"]="Bearer "+create_access_token(self.claims)
    def body(self,tipo,ambito,origin=None,dest=None,qty="10"):
        return {"tipo":tipo,"ambito":ambito,"concepto":"COMPRA" if tipo=="INGRESO" else "DISTRIBUCION","almacen_origen_id":str(origin) if origin else None,"almacen_destino_id":str(dest) if dest else None,"confirmar":True,"items":[{"medicamento_id":str(self.med),"numero_lote":"LT-001","fecha_vencimiento":"2035-12-31","cantidad":qty,"precio_unitario":"2.5000"}]}
    async def test_inventory_transfer_reports_and_cancel(self):
        r=await self.client.post("/app/farmacia/movimientos",json=self.body("INGRESO","ALMACEN",dest=self.store));self.assertEqual(r.status_code,201,r.text)
        r=await self.client.post("/app/farmacia/movimientos",json=self.body("SALIDA","ALMACEN",origin=self.store,dest=self.pharmacy,qty="4"));self.assertEqual(r.status_code,201,r.text);mid=r.json()["id"]
        stock=(await self.client.get("/app/farmacia/saldos")).json(); amounts={x["almacen_id"]:x["stock"] for x in stock};self.assertEqual(amounts[str(self.store)],6.0);self.assertEqual(amounts[str(self.pharmacy)],4.0)
        for path in ("ici-diario/datos","idi-diario/datos"):
            r=await self.client.get("/app/farmacia/reportes/"+path);self.assertEqual(r.status_code,200,r.text);self.assertTrue(r.json())
        r=await self.client.get("/app/farmacia/reportes/kardex.pdf");self.assertEqual(r.status_code,200);self.assertTrue(r.content.startswith(b"%PDF"))
        r=await self.client.post(f"/app/farmacia/movimientos/{mid}/anular",json={"motivo":"Error comprobado en prueba"});self.assertEqual(r.status_code,200,r.text)
        stock=(await self.client.get("/app/farmacia/saldos")).json();amounts={x["almacen_id"]:x["stock"] for x in stock};self.assertEqual(amounts[str(self.store)],10.0);self.assertNotIn(str(self.pharmacy),amounts)
    async def test_rejects_negative_stock_and_foreign_master(self):
        r=await self.client.post("/app/farmacia/movimientos",json=self.body("SALIDA","FARMACIA",origin=self.pharmacy));self.assertEqual(r.status_code,409,r.text)
        body=self.body("INGRESO","ALMACEN",dest=self.store);body["items"][0]["medicamento_id"]=str(uuid.uuid4())
        r=await self.client.post("/app/farmacia/movimientos",json=body);self.assertEqual(r.status_code,422,r.text)

    async def test_venta_no_se_marca_pagada_sin_cobro_real_en_caja(self):
        # Una venta de farmacia NO debe quedar "pagada" solo por confirmarse --
        # el pago real se registra en Caja (CobroItem origen='FARMACIA') y el
        # estado se calcula leyendo esos cobros, igual que Laboratorio/Imagen.
        pid = await self.client_patient()
        body = self.body("SALIDA", "FARMACIA", origin=self.pharmacy, qty="4")
        body["concepto"], body["patient_id"], body["fuente_financiamiento"] = "VENTA", str(pid), "PARTICULAR"
        await self.client.post("/app/farmacia/movimientos", json=self.body("INGRESO", "ALMACEN", dest=self.store))
        await self.client.post("/app/farmacia/movimientos", json=self.body("SALIDA", "ALMACEN", origin=self.store, dest=self.pharmacy))
        r = await self.client.post("/app/farmacia/movimientos", json=body)
        self.assertEqual(r.status_code, 201, r.text)
        venta = r.json()
        self.assertEqual(venta["estado_pago"], "pendiente")
        self.assertEqual(float(venta["monto_cobrado"]), 0)

        async with self.session() as db:
            caja_id, sesion_id, cobro_id, cajero_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
            db.add(Empleado(id=cajero_id, tenant_id=self.tenant_id, dni="99998888", nombres="Cajero",
                apellido_paterno="De", apellido_materno="Prueba"))
            db.add(CajaFisica(id=caja_id, tenant_id=self.tenant_id, nombre="Caja Farmacia Test"))
            db.add(CajaSesion(id=sesion_id, tenant_id=self.tenant_id, caja_id=caja_id, cajero_id=cajero_id,
                numero="CS-FARM-TEST-1", estado="abierta", registrado_por="Prueba"))
            db.add(Cobro(id=cobro_id, tenant_id=self.tenant_id, caja_sesion_id=sesion_id, numero="CB-FARM-TEST-1",
                numero_cuenta="CUENTA-TEST", forma_pago="EFECTIVO", monto=venta["total"], registrado_por="Prueba"))
            db.add(CobroItem(tenant_id=self.tenant_id, cobro_id=cobro_id, origen="FARMACIA",
                origen_id=venta["id"], descripcion="Venta de prueba", monto=venta["total"]))
            await db.commit()

        r = await self.client.get(f"/app/farmacia/movimientos/{venta['id']}")
        self.assertEqual(r.json()["estado_pago"], "pagado")
        self.assertAlmostEqual(float(r.json()["monto_pendiente"]), 0, places=2)

    async def client_patient(self):
        async with self.session() as db:
            patient = Patient(tenant_id=self.tenant_id, dni="87651234", first_name="Paciente",
                last_name_paterno="Prueba", last_name_materno="Farmacia", birth_date=date(1990, 1, 1), gender="M")
            db.add(patient)
            await db.flush()
            return patient.id


def load_tests(loader,tests,pattern):
    return unittest.TestSuite(FarmaciaTests(n) for n in FarmaciaTests.__dict__ if n.startswith("test_"))
