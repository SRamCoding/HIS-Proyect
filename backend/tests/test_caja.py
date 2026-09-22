"""Caja: pruebas HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_caja -v
"""
import unittest
import uuid
from datetime import date
from sqlalchemy import select, update
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import ProgramacionMedica, Cita
from app.hospital.emergencia.models import AdmisionEmergencia
from app.sigarh.rrhh.models import Empleado, Especialidad
from app.sigarh.mantenimiento.models import Servicio
from app.sigarh.config_financiera.models import Caja as CajaFisica, Tarifario
from app.auth.models import User
from app.core.security import create_access_token


class CajaTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="caja"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))
            self.staff = uuid.uuid4()
            self.service = uuid.uuid4()
            self.espec = uuid.uuid4()
            self.caja_id = uuid.uuid4()
            db.add(Empleado(id=self.staff, tenant_id=self.tenant_id, dni="99999999", nombres="Cajero",
                apellido_paterno="Prueba", apellido_materno="Caja"))
            db.add(Servicio(id=self.service, tenant_id=self.tenant_id, nombre="Consulta de prueba"))
            db.add(Especialidad(id=self.espec, tenant_id=self.tenant_id, nombre="Especialidad de prueba"))
            db.add(CajaFisica(id=self.caja_id, tenant_id=self.tenant_id, nombre="Caja 1 de prueba"))
            await db.flush()
            await db.execute(update(User).where(User.id == self.user_id).values(empleado_id=self.staff))
            db.add(Tarifario(tenant_id=self.tenant_id, descripcion_servicio="Consulta general",
                tipo_servicio="CONSULTA_EXTERNA", especialidad_id=self.espec, precio=35.5))
            db.add(Tarifario(tenant_id=self.tenant_id, descripcion_servicio="Atención de emergencia",
                tipo_servicio="EMERGENCIA", precio=60))
            prog = ProgramacionMedica(tenant_id=self.tenant_id, medico_id=self.staff, servicio_id=self.service,
                especialidad_id=self.espec, fecha=date(2030, 1, 1), turno="M", hora_inicio="08:00", hora_fin="09:00")
            db.add(prog)
            await db.flush()
            self.cita_id = uuid.uuid4()
            db.add(Cita(id=self.cita_id, tenant_id=self.tenant_id, programacion_medica_id=prog.id,
                patient_id=self.pid, hora_inicio="08:00", hora_fin="08:15", numero_cuenta="CTA-TEST-1"))
            self.emergencia_id = uuid.uuid4()
            db.add(AdmisionEmergencia(id=self.emergencia_id, tenant_id=self.tenant_id, patient_id=self.pid,
                numero_cuenta="CTA-TEST-2", servicio_emergencia="Emergencia General"))
            await db.commit()
        self.prefix = "/app/caja"
        self.claims = {**self.claims, "empleado_id": str(self.staff)}
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def post(self, path, data, status=201):
        r = await self.client.post(self.prefix+path, json=data)
        self.assertEqual(r.status_code, status, r.text)
        return r.json()

    async def abrir_turno(self, monto=100):
        return await self.post("/sesiones", {"caja_id": str(self.caja_id), "monto_apertura": monto,
            "observaciones_apertura": "Apertura de prueba"})

    async def test_caja_abrir_cerrar_turno_y_diferencia(self):
        s = await self.abrir_turno(100)
        self.assertEqual(s["estado"], "abierta")
        r = await self.client.get(self.prefix+"/sesiones/mi-turno")
        self.assertEqual(r.json()["id"], s["id"])
        await self.post("/sesiones", {"caja_id": str(self.caja_id), "monto_apertura": 50}, 409)
        c = await self.client.get(self.prefix+"/cuentas/CTA-TEST-1")
        cuenta = c.json()
        self.assertEqual(str(cuenta["total_pendiente"]), "35.5")
        item = next(i for i in cuenta["items"] if i["origen"] == "CONSULTA_EXTERNA")
        cobro = await self.post(f"/sesiones/{s['id']}/cobros", {
            "numero_cuenta": "CTA-TEST-1", "patient_id": str(self.pid), "forma_pago": "EFECTIVO",
            "items": [{"origen": "CONSULTA_EXTERNA", "origen_id": item["origen_id"], "descripcion": item["descripcion"], "monto": "35.5"}]})
        self.assertEqual(str(cobro["monto"]), "35.5")
        r = await self.client.get(self.prefix+"/cobros/"+cobro["id"]+"/comprobante.pdf")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.content.startswith(b"%PDF"))
        r = await self.client.post(self.prefix+f"/sesiones/{s['id']}/cerrar",
            json={"monto_cierre_declarado": "130", "observaciones_cierre": "Cuadre exacto"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(str(r.json()["monto_cierre_sistema"]), "135.5")
        self.assertEqual(str(r.json()["diferencia"]), "-5.5")

    async def test_caja_no_doble_cobro_ni_exceso(self):
        s = await self.abrir_turno()
        cuenta = (await self.client.get(self.prefix+"/cuentas/CTA-TEST-2")).json()
        item = cuenta["items"][0]
        await self.post(f"/sesiones/{s['id']}/cobros", {
            "numero_cuenta": "CTA-TEST-2", "forma_pago": "EFECTIVO",
            "items": [{"origen": "EMERGENCIA", "origen_id": item["origen_id"], "descripcion": item["descripcion"], "monto": "70"}]}, 409)
        cobro = await self.post(f"/sesiones/{s['id']}/cobros", {
            "numero_cuenta": "CTA-TEST-2", "forma_pago": "EFECTIVO",
            "items": [{"origen": "EMERGENCIA", "origen_id": item["origen_id"], "descripcion": item["descripcion"], "monto": "60"}]})
        await self.post(f"/sesiones/{s['id']}/cobros", {
            "numero_cuenta": "CTA-TEST-2", "forma_pago": "EFECTIVO",
            "items": [{"origen": "EMERGENCIA", "origen_id": item["origen_id"], "descripcion": item["descripcion"], "monto": "1"}]}, 409)
        r = await self.client.post(self.prefix+f"/cobros/{cobro['id']}/anular", json={"motivo": "Prueba de anulación"})
        self.assertEqual(r.status_code, 200, r.text)
        r = await self.client.get(self.prefix+"/cuentas/CTA-TEST-2")
        self.assertEqual(str(r.json()["total_pendiente"]), "60.0")

    async def test_caja_sesion_cerrada_bloquea_cobros_y_anulaciones(self):
        s = await self.abrir_turno()
        r = await self.client.post(self.prefix+f"/sesiones/{s['id']}/cerrar",
            json={"monto_cierre_declarado": "100"})
        self.assertEqual(r.status_code, 200, r.text)
        cuenta = (await self.client.get(self.prefix+"/cuentas/CTA-TEST-1")).json()
        item = cuenta["items"][0]
        await self.post(f"/sesiones/{s['id']}/cobros", {
            "numero_cuenta": "CTA-TEST-1", "forma_pago": "EFECTIVO",
            "items": [{"origen": "CONSULTA_EXTERNA", "origen_id": item["origen_id"], "descripcion": item["descripcion"], "monto": "10"}]}, 409)

    async def test_caja_tenant_isolation(self):
        s = await self.abrir_turno()
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims | {"tenant_id": str(self.other_tenant), "empleado_id": str(uuid.uuid4())})
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.other_tenant, module_code="caja"))
            # El usuario real sigue vinculado (User.empleado_id) al Empleado del OTRO
            # tenant (self.tenant_id) -- contexto_hospital() lo resolveria como
            # "empleado de otro hospital" (403) antes de llegar al chequeo de
            # aislamiento de sesion que esta prueba quiere ejercitar. Se limpia el
            # vinculo para simular una cuenta admin sin empleado asignado en este
            # segundo hospital, igual que al principio de asyncSetUp.
            await db.execute(update(User).where(User.id == self.user_id).values(empleado_id=None))
            await db.commit()
        r = await self.client.get(self.prefix+f"/sesiones/{s['id']}")
        self.assertEqual(r.status_code, 404)
        r = await self.client.get(self.prefix+"/sesiones/mi-turno")
        self.assertIsNone(r.json())


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(CajaTests(name) for name in CajaTests.__dict__ if name.startswith("test_caja_"))
