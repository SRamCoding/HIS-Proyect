"""Laboratorio: pruebas HTTP con PostgreSQL y rollback por caso."""
import unittest
import uuid
from datetime import date
from pathlib import Path
from sqlalchemy import select, update
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import Patient, ClinicalRecord
from app.sigarh.laboratorio.models import ExamenLaboratorio
from app.sigarh.mantenimiento.models import Servicio
from app.sigarh.rrhh.models import Empleado
from app.hospital.laboratorio.models import LabMovimiento, LabMovimientoItem
from app.sigarh.config_financiera.models import Caja as CajaFisica
from app.hospital.caja.models import CajaSesion, Cobro, CobroItem


class LaboratorioTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="laboratorio"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))
            self.other_pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.other_record))
            self.staff, self.exam, self.service = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
            self.other_exam = uuid.uuid4()
            db.add(Empleado(id=self.staff, tenant_id=self.tenant_id, dni="99999999", nombres="Profesional",
                apellido_paterno="Prueba", apellido_materno="Laboratorio"))
            db.add(Servicio(id=self.service, tenant_id=self.tenant_id, nombre="Laboratorio de prueba"))
            db.add(ExamenLaboratorio(id=self.exam, tenant_id=self.tenant_id, codigo="TEST-LAB",
                nombre="Examen sintético", precio=18.1234, tipo_muestra="Muestra sintética",
                unidad_medida="U", valores_referencia="Referencia configurada por el hospital"))
            db.add(ExamenLaboratorio(id=self.other_exam, tenant_id=self.other_tenant, nombre="Otro hospital"))
            await db.commit()
        self.prefix = "/app/laboratorio"

    async def post(self, path, data, status=201):
        r = await self.client.post(self.prefix+path, json=data)
        self.assertEqual(r.status_code, status, r.text)
        return r.json()

    def order_body(self):
        return {"patient_id":str(self.pid), "tipo_servicio":"APOYO_DIAGNOSTICO",
            "servicio_id":str(self.service), "medico_id":str(self.staff),
            "fuente_financiamiento":"SIS", "numero_cuenta":"CUENTA-TEST",
            "examen_ids":[str(self.exam)]}

    async def order(self):
        return await self.post("/ordenes", self.order_body())

    async def movement(self, order=None, cupos=2):
        if cupos is not None:
            await self.post("/cupos", {"fecha":"2030-01-01", "cupos":cupos})
        o = order or await self.order()
        return await self.post("/movimientos", self.movement_body(o["id"]))

    def movement_body(self, oid):
        return {"orden_id":oid,"fecha":"2030-01-01","toma_examen_id":str(self.staff),
            "items":[{"examen_id":str(self.exam),"cantidad":2,"precio":"18.1234"}]}

    async def test_lab_full_flow_results_pdf_csv_audit(self):
        o = await self.order()
        m = await self.movement(o)
        self.assertEqual(str(m["total"]), "36.2468")
        r = await self.client.get(self.prefix+f"/movimientos/{m['id']}/resultados.pdf")
        self.assertEqual(r.status_code,409)
        m = await self.post(f"/movimientos/{m['id']}/tomar-muestra",{"version":m["version"]},200)
        r = await self.client.put(self.prefix+f"/movimientos/{m['id']}/resultados",json={
            "version":m["version"],"items":[{"item_id":m["items"][0]["id"],"valores":[
                {"parametro":"Parámetro sintético","valor":"Resultado de prueba","unidad":"U","referencia":"Solo prueba"}]}]})
        self.assertEqual(r.status_code,200,r.text)
        m = await self.post(f"/movimientos/{m['id']}/validar",{"version":r.json()["version"]},200)
        self.assertEqual(m["estado"],"atendido")
        for kind in ("ticket","resultados"):
            r = await self.client.get(self.prefix+f"/movimientos/{m['id']}/{kind}.pdf")
            self.assertEqual(r.status_code,200,r.text[:100])
            self.assertTrue(r.content.startswith(b"%PDF"))
            path=Path("/tmp/laboratorio-pdf-qa");path.mkdir(parents=True,exist_ok=True)
            (path/f"laboratorio-{kind}-qa.pdf").write_bytes(r.content)
        r=await self.client.get(self.prefix+f"/movimientos/{m['id']}/auditoria")
        self.assertEqual(len(r.json()),4)
        r=await self.client.get(self.prefix+"/reportes/movimientos.csv",params={"cuenta":"CUENTA-TEST"})
        self.assertEqual(r.status_code,200,r.text)
        self.assertIn("CUENTA-TEST",r.text)
        r=await self.client.get(self.prefix+f"/ordenes/{o['id']}")
        self.assertEqual(r.json()["estado"],"completada")
        r=await self.client.get(self.prefix+f"/pacientes/{self.pid}/historial")
        self.assertEqual(len(r.json()),1)

    async def test_lab_cupos_duplicate_exhaustion_and_release(self):
        m=await self.movement(cupos=1)
        await self.post("/cupos",{"fecha":"2030-01-01","cupos":2},409)
        second=await self.order()
        await self.post("/movimientos",self.movement_body(second["id"]),409)
        r=await self.client.put(self.prefix+"/cupos",json={"fecha":"2030-01-01","cupos":0})
        self.assertEqual(r.status_code,409,r.text)
        await self.post(f"/movimientos/{m['id']}/anular",{"version":m["version"],"motivo":"Prueba de liberación"},200)
        await self.post("/movimientos",self.movement_body(second["id"]))
        r=await self.client.get(self.prefix+"/cupos",params={"fecha":"2030-01-01"})
        self.assertEqual(r.json()[0]["disponibles"],0)

    async def test_lab_tenant_foreign_keys_and_visibility(self):
        for field,value in (("patient_id",str(self.other_pid)),("medico_id",str(uuid.uuid4())),
                            ("examen_ids",[str(self.other_exam)])):
            body=self.order_body();body[field]=value
            await self.post("/ordenes",body,404)
        o=await self.order()
        from app.core.security import create_access_token
        self.client.headers["Authorization"]="Bearer "+create_access_token(self.claims|{"tenant_id":str(self.other_tenant)})
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.other_tenant,module_code="laboratorio"));await db.commit()
        r=await self.client.get(self.prefix+f"/ordenes/{o['id']}")
        self.assertEqual(r.status_code,404)
        r=await self.client.get(self.prefix+"/ordenes")
        self.assertEqual(r.json()["total"],0)
        r=await self.client.get(self.prefix+f"/pacientes/{self.pid}/historial")
        self.assertEqual(r.status_code,404)

    async def test_lab_duplicate_booking_and_stale_version(self):
        m=await self.movement()
        await self.post("/movimientos",self.movement_body(m["orden_id"]),409)
        body=self.movement_body(m["orden_id"])|{"version":1}
        r=await self.client.patch(self.prefix+f"/movimientos/{m['id']}",json=body)
        self.assertEqual(r.status_code,200,r.text)
        r=await self.client.patch(self.prefix+f"/movimientos/{m['id']}",json=body)
        self.assertEqual(r.status_code,409)
        await self.post(f"/movimientos/{m['id']}/anular",{"version":2},422)

    async def test_lab_results_required_and_closed_immutable(self):
        m=await self.movement()
        await self.post(f"/movimientos/{m['id']}/validar",{"version":1},409)
        m=await self.post(f"/movimientos/{m['id']}/tomar-muestra",{"version":1},200)
        await self.post(f"/movimientos/{m['id']}/validar",{"version":m["version"]},422)
        r=await self.client.put(self.prefix+f"/movimientos/{m['id']}/resultados",json={
            "version":m["version"],"items":[{"item_id":str(uuid.uuid4()),"valores":[{"parametro":"Prueba","valor":"x"}]}]})
        self.assertEqual(r.status_code,404)
        m=await self.post(f"/movimientos/{m['id']}/anular",{"version":m["version"],"motivo":"Prueba"},200)
        r=await self.client.put(self.prefix+f"/movimientos/{m['id']}/resultados",json={
            "version":m["version"],"items":[{"item_id":m["items"][0]["id"],"valores":[{"parametro":"Prueba","valor":"x"}]}]})
        self.assertEqual(r.status_code,409)

    async def test_lab_covid_filters_validation_and_report(self):
        body={"patient_id":str(self.pid),"fecha":"2030-01-01","tipo_prueba":"Prueba sintética",
              "muestra":"Muestra sintética","resultado":"pendiente","observaciones":""}
        c=await self.post("/ficha-covid",body)
        body["resultado"]="negativo"
        r=await self.client.patch(self.prefix+f"/ficha-covid/{c['id']}",json=body|{"version":1})
        self.assertEqual(r.status_code,200,r.text)
        r=await self.client.patch(self.prefix+f"/ficha-covid/{c['id']}",json=body|{"version":1})
        self.assertEqual(r.status_code,409)
        r=await self.client.get(self.prefix+"/ficha-covid",params={"fecha":"2030-01-01","estado":"negativo"})
        self.assertEqual(r.json()["total"],1)
        r=await self.client.get(self.prefix+f"/ficha-covid/{c['id']}/reporte.pdf")
        self.assertEqual(r.status_code,200)
        Path("/tmp/laboratorio-pdf-qa").mkdir(parents=True,exist_ok=True)
        Path("/tmp/laboratorio-pdf-qa/laboratorio-covid-qa.pdf").write_bytes(r.content)

    async def test_lab_input_validation_and_no_partial_writes(self):
        body=self.order_body();body["examen_ids"]*=2
        await self.post("/ordenes",body,422)
        o=await self.order()
        await self.post("/movimientos",self.movement_body(o["id"]),409)
        await self.post("/cupos",{"fecha":"2030-01-01","cupos":-1},422)
        await self.post("/cupos",{"fecha":"2030-01-01","cupos":1})
        body=self.movement_body(o["id"]);body["items"][0]["precio"]="-1"
        await self.post("/movimientos",body,422)
        r=await self.client.get(self.prefix+"/movimientos")
        self.assertEqual(r.json()["total"],0)
        r=await self.client.get(self.prefix+"/ordenes",params={"page_size":101})
        self.assertEqual(r.status_code,422)

    async def test_lab_consulta_externa_legacy_order_appears(self):
        from app.hospital.consulta_externa.models import ProgramacionMedica,Cita,AtencionMedica,OrdenLaboratorio,OrdenLaboratorioItem
        async with self.session() as db:
            p=ProgramacionMedica(tenant_id=self.tenant_id,medico_id=self.staff,servicio_id=self.service,
                fecha=date(2030,1,1),turno="M",hora_inicio="08:00",hora_fin="09:00")
            db.add(p);await db.flush()
            c=Cita(tenant_id=self.tenant_id,programacion_medica_id=p.id,patient_id=self.pid,
                hora_inicio="08:00",hora_fin="08:15",numero_cuenta="LEGACY")
            db.add(c);await db.flush()
            a=AtencionMedica(tenant_id=self.tenant_id,cita_id=c.id,motivo_consulta="Prueba")
            db.add(a);await db.flush()
            o=OrdenLaboratorio(tenant_id=self.tenant_id,atencion_medica_id=a.id,numero_orden="TEST-"+uuid.uuid4().hex[:20])
            db.add(o);await db.flush();db.add(OrdenLaboratorioItem(orden_id=o.id,examen_id=self.exam));await db.commit()
            oid=o.id
        r=await self.client.get(self.prefix+f"/ordenes/{oid}")
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()["numero_cuenta"],"LEGACY")
        self.assertEqual(r.json()["patient_id"],str(self.pid))
        await self.movement({"id":str(oid)})


    async def test_lab_estado_pago_reflejado_desde_caja(self):
        # El estado de pago del movimiento se calcula a partir de los cobros
        # reales de Caja (CobroItem origen='LABORATORIO'), no de un campo de
        # texto libre -- verificamos que pendiente/parcial/pagado reflejen
        # exactamente lo que Caja registró.
        mov = await self.movement()
        r = await self.client.get(self.prefix + f"/movimientos/{mov['id']}")
        self.assertEqual(r.json()["estado_pago"], "pendiente")
        self.assertEqual(float(r.json()["monto_cobrado"]), 0)
        total = float(r.json()["total"])  # 18.1234 * 2 = 36.2468

        async with self.session() as db:
            caja_id = uuid.uuid4()
            sesion_id = uuid.uuid4()
            db.add(CajaFisica(id=caja_id, tenant_id=self.tenant_id, nombre="Caja de prueba"))
            db.add(CajaSesion(id=sesion_id, tenant_id=self.tenant_id, caja_id=caja_id, cajero_id=self.staff,
                numero="CS-TEST-1", estado="abierta"))
            cobro_id = uuid.uuid4()
            db.add(Cobro(id=cobro_id, tenant_id=self.tenant_id, caja_sesion_id=sesion_id, numero="CB-TEST-1",
                numero_cuenta="CUENTA-TEST", forma_pago="EFECTIVO", monto=20, registrado_por="Prueba"))
            db.add(CobroItem(tenant_id=self.tenant_id, cobro_id=cobro_id, origen="LABORATORIO",
                origen_id=mov["id"], descripcion="Pago parcial de prueba", monto=20))
            await db.commit()

        r = await self.client.get(self.prefix + f"/movimientos/{mov['id']}")
        self.assertEqual(r.json()["estado_pago"], "parcial")
        self.assertAlmostEqual(float(r.json()["monto_pendiente"]), total - 20, places=2)

        async with self.session() as db:
            db.add(CobroItem(tenant_id=self.tenant_id, cobro_id=cobro_id, origen="LABORATORIO",
                origen_id=mov["id"], descripcion="Resto de la cuenta", monto=total - 20))
            await db.commit()

        r = await self.client.get(self.prefix + f"/movimientos/{mov['id']}")
        self.assertEqual(r.json()["estado_pago"], "pagado")
        self.assertAlmostEqual(float(r.json()["monto_pendiente"]), 0, places=2)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(LaboratorioTests(name) for name in LaboratorioTests.__dict__ if name.startswith("test_lab_"))
