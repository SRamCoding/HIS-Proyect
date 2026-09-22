"""Admision: Altas, Lista de Espera, Anuncios, Mensajito -- pruebas HTTP con
PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_admision_extra -v
"""
import unittest
import uuid
from datetime import date, datetime, timedelta
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import Hospitalizacion, ProgramacionMedica, Cita
from app.hospital.emergencia.models import AdmisionEmergencia, AtencionEmergencia
from app.sigarh.infraestructura_hosp.models import Cama
from app.sigarh.rrhh.models import Empleado, Especialidad
from app.sigarh.mantenimiento.models import Servicio
from app.auth.models import User
from app.core.security import create_access_token


class AdmisionExtraTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="admision"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))

            # --- Fixtures para Altas ---
            self.cama_id = uuid.uuid4()
            db.add(Cama(id=self.cama_id, tenant_id=self.tenant_id, codigo="CAMA-ALTA-1", nombre="Cama de prueba"))
            self.pid2 = await self.crear_paciente_extra(db, "Emergencia Alta")
            self.admision_emerg_id = uuid.uuid4()
            db.add(AdmisionEmergencia(id=self.admision_emerg_id, tenant_id=self.tenant_id, patient_id=self.pid2,
                numero_cuenta="EMG-ALTA-1", servicio_emergencia="Emergencia General", estado="atendido"))

            # --- Fixtures para Lista de Espera (servicio + programacion + cita) ---
            self.servicio_id = uuid.uuid4()
            db.add(Servicio(id=self.servicio_id, tenant_id=self.tenant_id, nombre="Medicina General"))
            self.medico_id = uuid.uuid4()
            db.add(Empleado(id=self.medico_id, tenant_id=self.tenant_id, dni="88888888",
                nombres="Medico", apellido_paterno="Lista", apellido_materno="Espera"))
            await db.flush()

            db.add(Hospitalizacion(tenant_id=self.tenant_id, patient_id=self.pid, cama_id=self.cama_id,
                numero_hospitalizacion="HOSP-TEST-ALTA-1", estado="alta",
                fecha_alta=datetime.utcnow(), resumen_alta="Evolución favorable, egresa por mejoría"))
            db.add(AtencionEmergencia(tenant_id=self.tenant_id, admision_id=self.admision_emerg_id,
                motivo_consulta="Cefalea", plan_tratamiento="Analgesia y control ambulatorio",
                destino_atencion="ALTA", estado="firmado", firmado_at=datetime.utcnow()))
            self.prog_id = uuid.uuid4()
            db.add(ProgramacionMedica(id=self.prog_id, tenant_id=self.tenant_id, medico_id=self.medico_id,
                servicio_id=self.servicio_id, fecha=date.today() + timedelta(days=1), turno="mañana",
                hora_inicio="08:00", hora_fin="08:15"))
            await db.flush()

            self.cita_id = uuid.uuid4()
            db.add(Cita(id=self.cita_id, tenant_id=self.tenant_id, programacion_medica_id=self.prog_id,
                patient_id=self.pid, hora_inicio="08:00", hora_fin="08:15"))

            # --- Fixtures para Mensajito ---
            self.remitente_id = uuid.uuid4()
            self.destinatario_id = uuid.uuid4()
            # role="administrador": unico rol seeded en SystemRole (panel='app') que no
            # exige PerfilHospital/RolSistema ni Empleado vinculado (ver
            # contexto_hospital() en app/auth/hospital_access.py) -- evita fixture
            # adicional de perfil/empleado que esta prueba de mensajeria no necesita.
            db.add(User(id=self.remitente_id, name="Remitente Prueba", email="remitente.adm@test.com",
                password="x", role="administrador", panel="app", is_active=True))
            db.add(User(id=self.destinatario_id, name="Destinatario Prueba", email="destinatario.adm@test.com",
                password="x", role="administrador", panel="app", is_active=True))

            await db.commit()
        self.prefix = "/app/admision"
        self.claims = {**self.claims, "sub": str(self.remitente_id)}
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def crear_paciente_extra(self, db, nombre):
        patient = Patient(tenant_id=self.tenant_id, dni=str(uuid.uuid4().int)[:8], first_name=nombre,
            last_name_paterno="Prueba", last_name_materno="Extra", birth_date=date(1990, 1, 1), gender="F")
        db.add(patient)
        await db.flush()
        return patient.id

    # --- Altas ---
    async def test_altas_lista_hospitalizacion_y_emergencia(self):
        r = await self.client.get(self.prefix + "/altas")
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        origenes = {i["origen"] for i in data}
        self.assertEqual(origenes, {"hospitalizacion", "emergencia"})
        hosp = next(i for i in data if i["origen"] == "hospitalizacion")
        self.assertEqual(hosp["numero"], "HOSP-TEST-ALTA-1")
        self.assertIn("mejoría", hosp["resumen"])

    async def test_altas_filtro_por_busqueda(self):
        r = await self.client.get(self.prefix + "/altas", params={"q": "Emergencia Alta"})
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["origen"], "emergencia")

    # --- Lista de Espera ---
    async def test_lista_espera_ciclo_completo(self):
        r = await self.client.post(self.prefix + "/lista-espera", json={
            "patient_id": str(self.pid), "servicio_id": str(self.servicio_id),
            "motivo": "Sin cupos esta semana", "prioridad": "urgente",
        })
        self.assertEqual(r.status_code, 201, r.text)
        item = r.json()
        self.assertEqual(item["estado"], "pendiente")
        self.assertEqual(item["servicio_nombre"], "Medicina General")

        r = await self.client.get(self.prefix + "/lista-espera")
        self.assertEqual(len(r.json()), 1)

        r = await self.client.post(f"{self.prefix}/lista-espera/{item['id']}/atender", json={"cita_id": str(self.cita_id)})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "atendido")
        self.assertEqual(r.json()["cita_id"], str(self.cita_id))

        r = await self.client.get(self.prefix + "/lista-espera")
        self.assertEqual(len(r.json()), 0)  # ya no esta pendiente

    async def test_lista_espera_requiere_servicio_o_especialidad(self):
        r = await self.client.post(self.prefix + "/lista-espera", json={"patient_id": str(self.pid)})
        self.assertEqual(r.status_code, 422)

    async def test_lista_espera_cancelar(self):
        r = await self.client.post(self.prefix + "/lista-espera", json={
            "patient_id": str(self.pid), "servicio_id": str(self.servicio_id),
        })
        item_id = r.json()["id"]
        r = await self.client.post(f"{self.prefix}/lista-espera/{item_id}/cancelar")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "cancelado")

    # --- Anuncios ---
    async def test_anuncios_crear_listar_desactivar(self):
        r = await self.client.post(self.prefix + "/anuncios", json={
            "titulo": "Consultorio 3 cerrado", "contenido": "Por mantenimiento hasta el viernes"})
        self.assertEqual(r.status_code, 201, r.text)
        anuncio_id = r.json()["id"]

        r = await self.client.get(self.prefix + "/anuncios")
        self.assertEqual(len(r.json()), 1)

        r = await self.client.patch(f"{self.prefix}/anuncios/{anuncio_id}", json={"is_active": False})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertFalse(r.json()["is_active"])

        r = await self.client.get(self.prefix + "/anuncios")
        self.assertEqual(len(r.json()), 0)
        r = await self.client.get(self.prefix + "/anuncios", params={"incluir_inactivos": True})
        self.assertEqual(len(r.json()), 1)

    # --- Mensajito ---
    async def test_mensajito_envio_y_bandeja(self):
        r = await self.client.get(self.prefix + "/mensajito/destinatarios")
        self.assertEqual(r.status_code, 200, r.text)
        nombres = {d["name"] for d in r.json()}
        self.assertIn("Destinatario Prueba", nombres)

        r = await self.client.post(self.prefix + "/mensajito", json={
            "contenido": "Paciente en sala de espera hace 2h",
            "destinatario_user_id": str(self.destinatario_id), "patient_id": str(self.pid)})
        self.assertEqual(r.status_code, 201, r.text)
        msg_id = r.json()["id"]
        self.assertFalse(r.json()["leido"])

        r = await self.client.get(self.prefix + "/mensajito/enviados")
        self.assertEqual(len(r.json()), 1)

        # El destinatario revisa su bandeja
        self.client.headers["Authorization"] = "Bearer " + create_access_token({**self.claims, "sub": str(self.destinatario_id)})
        r = await self.client.get(self.prefix + "/mensajito/inbox")
        self.assertEqual(len(r.json()), 1)
        self.assertEqual(r.json()[0]["paciente_nombre"], (await self._nombre_paciente()))

        r = await self.client.post(f"{self.prefix}/mensajito/{msg_id}/leido")
        self.assertEqual(r.status_code, 200, r.text)
        r = await self.client.get(self.prefix + "/mensajito/inbox")
        self.assertTrue(r.json()[0]["leido"])

    async def _nombre_paciente(self):
        async with self.session() as db:
            p = (await db.execute(select(Patient).where(Patient.id == self.pid))).scalar_one()
            return p.full_name

    async def test_mensajito_broadcast_por_rol(self):
        r = await self.client.post(self.prefix + "/mensajito", json={
            "contenido": "Reunión de coordinación a las 3pm", "destinatario_role": "administrador"})
        self.assertEqual(r.status_code, 201, r.text)

        self.client.headers["Authorization"] = "Bearer " + create_access_token(
            {**self.claims, "sub": str(self.destinatario_id)})
        r = await self.client.get(self.prefix + "/mensajito/inbox")
        self.assertEqual(len(r.json()), 1)
        self.assertEqual(r.json()[0]["destinatario_role"], "administrador")


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(AdmisionExtraTests(name) for name in AdmisionExtraTests.__dict__ if name.startswith("test_"))
