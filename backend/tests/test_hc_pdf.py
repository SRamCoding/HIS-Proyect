"""Ejecutar con RUN_ARCHIVO_DB_TESTS=1 contra una base aislada migrada."""
import hashlib
import json
import uuid
from datetime import datetime, date
from io import BytesIO

from pypdf import PdfReader
from sqlalchemy import select
import test_archivo_clinico as archive
from app.hospital.admision.models import ClinicalRecord
from app.hospital.admision.schemas import PatientCreate, PatientUpdate
from app.hospital.admision.service import create_patient, update_patient, search_patients
from app.hospital.archivo_clinico.service import list_historias
from app.hospital.emergencia.models import AdmisionEmergencia, AtencionEmergencia
from app.hospital.consulta_externa.models import OrdenLaboratorio
from app.admin.auditoria.models import AuditLog
from app.tenants.hospitales.models import TenantModule
from app.core.security import create_refresh_token


class HcPdfTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        from app.admin.roles.models import SystemRole
        from app.tenants.modulos.models import Module
        async with self.session() as db:
            for code in ("archivo_clinico", "admision"):
                if not await db.scalar(select(Module).where(Module.code == code)):
                    db.add(Module(code=code, name=code, category="clinico"))
            if not await db.scalar(select(SystemRole).where(SystemRole.name == "administrador")):
                db.add(SystemRole(name="administrador", label="Administrador de pruebas", panel="app", allowed_modules=None))
            await db.commit()

    async def test_hc_pdf_firma_aislamiento_auditoria(self):
        async with self.session() as db:
            record = await db.get(ClinicalRecord, self.record_id)
            admission = AdmisionEmergencia(id=uuid.uuid4(), tenant_id=self.tenant_id,
                patient_id=record.patient_id, numero_cuenta="EMG-HC-TEST", servicio_emergencia="Emergencia", estado="atendido")
            db.add(admission)
            await db.flush()
            content = {"motivo_consulta": "DOLOR DE PRUEBA", "plan_tratamiento": "PLAN CERRADO"}
            evidence = {"contenido": content, "medico_nombre": "Médico PDF", "colegiatura": "54321",
                "sha256": hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False).encode()).hexdigest()}
            attention = AtencionEmergencia(tenant_id=self.tenant_id, admision_id=admission.id,
                motivo_consulta="TEXTO ACTUAL DIFERENTE", estado="firmado", firmado_at=datetime.utcnow(), cierre_evidencia=evidence)
            db.add(attention)
            # Orden heredada sin patient_id: debe entrar a través del ingreso.
            db.add(OrdenLaboratorio(tenant_id=self.tenant_id, emergencia_id=admission.id,
                patient_id=None, numero_orden="LAB-HC-HEREDADA", indicacion_clinica="EXAMEN HEREDADO"))
            await db.commit()
        url = f"/app/archivo-clinico/historias/{self.record_id}/pdf"
        response = await self.client.get(url)
        self.assertEqual(response.status_code, 200, response.text[:300] if response.status_code != 200 else "")
        self.assertIn("no-store", response.headers["cache-control"])
        self.assertTrue(response.content.startswith(b"%PDF"))
        text = "\n".join(p.extract_text() for p in PdfReader(BytesIO(response.content)).pages)
        self.assertIn("PLAN CERRADO", text)
        self.assertIn("54321", text)
        self.assertIn("EXAMEN HEREDADO", text)
        self.assertNotIn("TEXTO ACTUAL DIFERENTE", text)
        async with self.session() as db:
            event = await db.scalar(select(AuditLog).where(AuditLog.action == "hc_pdf_exportada", AuditLog.model_id == str(self.record_id)))
            self.assertIsNotNone(event)
            self.assertEqual(event.tenant_id, self.tenant_id)
        response = await self.client.get(url, params={"alcance": "ficha"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("PLAN CERRADO", "\n".join(p.extract_text() for p in PdfReader(BytesIO(response.content)).pages))
        self.assertEqual((await self.client.get(f"/app/archivo-clinico/historias/{self.other_record}/pdf")).status_code, 404)
        self.assertEqual((await self.client.get(url, params={"alcance": "invalido"})).status_code, 422)
        self.client.headers["Authorization"] = "Bearer " + create_refresh_token(self.claims)
        self.assertEqual((await self.client.get(url)).status_code, 401)
        self.client.headers.pop("Authorization")
        self.assertIn((await self.client.get(url)).status_code, (401, 403))

    async def test_hc_numeracion_actualizacion_alias_y_nn(self):
        async with self.session() as db:
            data = PatientCreate(dni="00123456", first_name="Prueba", last_name_paterno="HC", last_name_materno="DNI", birth_date=date(1990, 1, 1), gender="F")
            patient = await create_patient(db, self.tenant_id, data)
            self.assertEqual(patient.clinical_record.record_number, "00123456")
            record_id = patient.clinical_record.id
            patient = await update_patient(db, self.tenant_id, patient.id, PatientUpdate(dni="00123457"))
            self.assertEqual(patient.clinical_record.id, record_id)
            self.assertEqual(patient.clinical_record.record_number, "00123457")
            self.assertIn("00123456", patient.clinical_record.previous_record_numbers)
            result = await list_historias(db, self.tenant_id, "00123456", None, None, 1, 20)
            self.assertEqual(result["total"], 1)
            _, total = await search_patients(db, self.tenant_id, "00123456")
            self.assertEqual(total, 1)
            data = data.model_copy(update={"dni": None, "is_nn": True})
            nn = await create_patient(db, self.tenant_id, data)
            self.assertTrue(nn.clinical_record.record_number.startswith("HC-"))
            original = nn.clinical_record.record_number
            nn = await update_patient(db, self.tenant_id, nn.id, PatientUpdate(is_nn=False, dni="00999999"))
            self.assertEqual(nn.clinical_record.record_number, "00999999")
            self.assertIn(original, nn.clinical_record.previous_record_numbers)

    async def test_hc_pdf_modulo_inactivo(self):
        async with self.session() as db:
            module = await db.scalar(select(TenantModule).where(TenantModule.tenant_id == self.tenant_id, TenantModule.module_code == "archivo_clinico"))
            module.is_active = False
            await db.commit()
        response = await self.client.get(f"/app/archivo-clinico/historias/{self.record_id}/pdf")
        self.assertEqual(response.status_code, 403)


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromTestCase(HcPdfTests)
