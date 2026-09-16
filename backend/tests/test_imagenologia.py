"""Imagenología: pruebas HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_imagenologia -v
"""
import unittest
import uuid
from datetime import date
from pathlib import Path
from sqlalchemy import select, update
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import Patient, ClinicalRecord
from app.sigarh.imagenologia.models import ExamenImagenologia
from app.sigarh.mantenimiento.models import Servicio
from app.sigarh.rrhh.models import Empleado
from app.hospital.imagenes.models import ImagenMovimiento, ImagenMovimientoItem


class ImagenologiaTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="imagenes"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))
            self.other_pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.other_record))
            self.staff, self.exam, self.service = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
            self.other_exam = uuid.uuid4()
            db.add(Empleado(id=self.staff, tenant_id=self.tenant_id, dni="99999999", nombres="Profesional",
                apellido_paterno="Prueba", apellido_materno="Imagenología"))
            db.add(Servicio(id=self.service, tenant_id=self.tenant_id, nombre="Imagenología de prueba"))
            db.add(ExamenImagenologia(id=self.exam, tenant_id=self.tenant_id, codigo="TEST-IMG",
                nombre="Estudio sintético", precio=45.1234, modalidad="Rayos X", parte_cuerpo="Tórax"))
            db.add(ExamenImagenologia(id=self.other_exam, tenant_id=self.other_tenant, nombre="Otro hospital", modalidad="Rayos X"))
            await db.commit()
        self.prefix = "/app/imagenes"

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

    async def movement(self, order=None):
        o = order or await self.order()
        return await self.post("/movimientos", self.movement_body(o["id"]))

    def movement_body(self, oid):
        return {"orden_id":oid,"fecha":"2030-01-01","tecnico_id":str(self.staff),
            "items":[{"examen_id":str(self.exam),"cantidad":2,"precio":"45.1234"}]}

    def informe_body(self, version, item_id):
        return {"version":version,"items":[{"item_id":item_id,"tecnica":"Técnica sintética",
            "hallazgos":"Hallazgo de prueba","impresion_diagnostica":"Impresión de prueba"}]}

    async def test_img_full_flow_informe_pdf_csv_audit(self):
        o = await self.order()
        m = await self.movement(o)
        self.assertEqual(str(m["total"]), "90.2468")
        r = await self.client.get(self.prefix+f"/movimientos/{m['id']}/informe.pdf")
        self.assertEqual(r.status_code,409)
        m = await self.post(f"/movimientos/{m['id']}/tomar-estudio",{"version":m["version"]},200)
        r = await self.client.put(self.prefix+f"/movimientos/{m['id']}/informe",
            json=self.informe_body(m["version"], m["items"][0]["id"]))
        self.assertEqual(r.status_code,200,r.text)
        m = await self.post(f"/movimientos/{m['id']}/validar",{"version":r.json()["version"]},200)
        self.assertEqual(m["estado"],"atendido")
        for kind in ("ticket","informe"):
            r = await self.client.get(self.prefix+f"/movimientos/{m['id']}/{kind}.pdf")
            self.assertEqual(r.status_code,200,r.text[:100])
            self.assertTrue(r.content.startswith(b"%PDF"))
            path=Path("/tmp/imagenologia-pdf-qa");path.mkdir(parents=True,exist_ok=True)
            (path/f"imagenologia-{kind}-qa.pdf").write_bytes(r.content)
        r=await self.client.get(self.prefix+f"/movimientos/{m['id']}/auditoria")
        self.assertEqual(len(r.json()),4)
        r=await self.client.get(self.prefix+"/reportes/movimientos.csv",params={"cuenta":"CUENTA-TEST"})
        self.assertEqual(r.status_code,200,r.text)
        self.assertIn("CUENTA-TEST",r.text)
        r=await self.client.get(self.prefix+f"/ordenes/{o['id']}")
        self.assertEqual(r.json()["estado"],"completada")
        r=await self.client.get(self.prefix+f"/pacientes/{self.pid}/historial")
        self.assertEqual(len(r.json()),1)

    async def test_img_tenant_foreign_keys_and_visibility(self):
        for field,value in (("patient_id",str(self.other_pid)),("medico_id",str(uuid.uuid4())),
                            ("examen_ids",[str(self.other_exam)])):
            body=self.order_body();body[field]=value
            await self.post("/ordenes",body,404)
        o=await self.order()
        from app.core.security import create_access_token
        self.client.headers["Authorization"]="Bearer "+create_access_token(self.claims|{"tenant_id":str(self.other_tenant)})
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.other_tenant,module_code="imagenes"));await db.commit()
        r=await self.client.get(self.prefix+f"/ordenes/{o['id']}")
        self.assertEqual(r.status_code,404)
        r=await self.client.get(self.prefix+"/ordenes")
        self.assertEqual(r.json()["total"],0)
        r=await self.client.get(self.prefix+f"/pacientes/{self.pid}/historial")
        self.assertEqual(r.status_code,404)

    async def test_img_duplicate_booking_and_stale_version(self):
        m=await self.movement()
        await self.post("/movimientos",self.movement_body(m["orden_id"]),409)
        body=self.movement_body(m["orden_id"])|{"version":1}
        r=await self.client.patch(self.prefix+f"/movimientos/{m['id']}",json=body)
        self.assertEqual(r.status_code,200,r.text)
        r=await self.client.patch(self.prefix+f"/movimientos/{m['id']}",json=body)
        self.assertEqual(r.status_code,409)
        await self.post(f"/movimientos/{m['id']}/anular",{"version":2},422)

    async def test_img_informe_required_and_closed_immutable(self):
        m=await self.movement()
        await self.post(f"/movimientos/{m['id']}/validar",{"version":1},409)
        m=await self.post(f"/movimientos/{m['id']}/tomar-estudio",{"version":1},200)
        await self.post(f"/movimientos/{m['id']}/validar",{"version":m["version"]},422)
        r=await self.client.put(self.prefix+f"/movimientos/{m['id']}/informe",
            json=self.informe_body(m["version"], str(uuid.uuid4())))
        self.assertEqual(r.status_code,404)
        m=await self.post(f"/movimientos/{m['id']}/anular",{"version":m["version"],"motivo":"Prueba"},200)
        r=await self.client.put(self.prefix+f"/movimientos/{m['id']}/informe",
            json=self.informe_body(m["version"], m["items"][0]["id"]))
        self.assertEqual(r.status_code,409)

    async def test_img_input_validation_and_no_partial_writes(self):
        body=self.order_body();body["examen_ids"]*=2
        await self.post("/ordenes",body,422)
        o=await self.order()
        await self.movement(o)
        await self.post("/movimientos",self.movement_body(o["id"]),409)
        body=self.movement_body((await self.order())["id"]);body["items"][0]["precio"]="-1"
        await self.post("/movimientos",body,422)
        r=await self.client.get(self.prefix+"/ordenes",params={"page_size":101})
        self.assertEqual(r.status_code,422)

    async def test_img_consulta_externa_legacy_order_appears(self):
        from app.hospital.consulta_externa.models import ProgramacionMedica,Cita,AtencionMedica,OrdenImagen,OrdenImagenItem
        async with self.session() as db:
            p=ProgramacionMedica(tenant_id=self.tenant_id,medico_id=self.staff,servicio_id=self.service,
                fecha=date(2030,1,1),turno="M",hora_inicio="08:00",hora_fin="09:00")
            db.add(p);await db.flush()
            c=Cita(tenant_id=self.tenant_id,programacion_medica_id=p.id,patient_id=self.pid,
                hora_inicio="08:00",hora_fin="08:15",numero_cuenta="LEGACY")
            db.add(c);await db.flush()
            a=AtencionMedica(tenant_id=self.tenant_id,cita_id=c.id,motivo_consulta="Prueba")
            db.add(a);await db.flush()
            o=OrdenImagen(tenant_id=self.tenant_id,atencion_medica_id=a.id,numero_orden="TEST-"+uuid.uuid4().hex[:20])
            db.add(o);await db.flush();db.add(OrdenImagenItem(orden_id=o.id,examen_id=self.exam));await db.commit()
            oid=o.id
        r=await self.client.get(self.prefix+f"/ordenes/{oid}")
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()["numero_cuenta"],"LEGACY")
        self.assertEqual(r.json()["patient_id"],str(self.pid))
        await self.movement({"id":str(oid)})


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(ImagenologiaTests(name) for name in ImagenologiaTests.__dict__ if name.startswith("test_img_"))
