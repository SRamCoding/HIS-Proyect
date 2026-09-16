"""Firma Electrónica (Ley N.° 30024 -- RENHICE / Ley N.° 27269 -- Firmas y
Certificados Digitales): pruebas HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_firma_electronica -v
"""
import json
import unittest
import uuid
from datetime import date, datetime
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.tenants.modulos.models import Module
from app.hospital.admision.models import ClinicalRecord
from app.hospital.consulta_externa.models import ProgramacionMedica, Cita, AtencionMedica, AtencionDiagnostico, Triaje
from app.hospital.emergencia.models import AdmisionEmergencia, AtencionEmergencia
from app.sigarh.rrhh.models import Empleado
from app.sigarh.mantenimiento.models import Profesion, RolSistema, PerfilUsuario
from app.sigarh.general.models import DiagnosticoCIE10
from app.auth.models import User
from app.core.security import create_access_token

_ANTECEDENTES = {"antecedente_quirurgico": "No refiere", "antecedente_patologico": "No refiere",
    "antecedente_alergias": "No refiere", "antecedentes_obstetricos": "No refiere",
    "antecedente_familiares": "No refiere", "antecedente_otros": "No refiere"}


class FirmaElectronicaTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            for code in ("firma_electronica", "consulta_externa", "emergencia"):
                db.add(TenantModule(tenant_id=self.tenant_id, module_code=code, is_active=True))
                if not await db.scalar(select(Module.code).where(Module.code == code)):
                    db.add(Module(code=code, name=code, category="clinico", is_active=True))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))

            self.medico_empleado_id = uuid.uuid4()
            profesion_id = uuid.uuid4()
            db.add(Profesion(id=profesion_id, tenant_id=self.tenant_id, grupo_ocupacional_id=uuid.uuid4(),
                nombre="Médico Cirujano", codigo="MED"))
            db.add(Empleado(id=self.medico_empleado_id, tenant_id=self.tenant_id, dni="77778888",
                nombres="Medico", apellido_paterno="De", apellido_materno="Firma",
                profesion_id=profesion_id, habilitado_colegio=True, numero_cmp="CMP-9999"))

            rol_id = uuid.uuid4()
            db.add(RolSistema(id=rol_id, tenant_id=self.tenant_id, nombre="Médico", panel="app",
                tipo_usuario="medico", modulos_permitidos=json.dumps(["firma_electronica"])))
            perfil_id = uuid.uuid4()
            db.add(PerfilUsuario(id=perfil_id, tenant_id=self.tenant_id, nombre="Médico",
                rol_sistema_id=rol_id, modulos_acceso=json.dumps(["firma_electronica"])))

            self.medico_user_id = uuid.uuid4()
            db.add(User(id=self.medico_user_id, name="Medico De Firma", email="medico.firma@test.pe",
                password="x", role="medico", panel="app", is_active=True,
                empleado_id=self.medico_empleado_id, perfil_usuario_id=perfil_id))

            self.prog_id = uuid.uuid4()
            db.add(ProgramacionMedica(id=self.prog_id, tenant_id=self.tenant_id, medico_id=self.medico_empleado_id,
                fecha=date.today(), turno="T", hora_inicio="16:00", hora_fin="16:30"))
            self.cita_id = uuid.uuid4()
            db.add(Cita(id=self.cita_id, tenant_id=self.tenant_id, programacion_medica_id=self.prog_id,
                patient_id=self.pid, hora_inicio="16:00", hora_fin="16:15", estado="confirmada"))
            db.add(Triaje(id=uuid.uuid4(), tenant_id=self.tenant_id, cita_id=self.cita_id, pulso=72,
                temperatura=36.5, presion_sistolica=120, presion_diastolica=80, peso=70, talla=170))

            self.dx_id = uuid.uuid4()
            db.add(DiagnosticoCIE10(id=self.dx_id, tenant_id=self.tenant_id, codigo_cie10="J00",
                descripcion="Rinofaringitis aguda"))
            self.atencion_id = uuid.uuid4()
            db.add(AtencionMedica(id=self.atencion_id, tenant_id=self.tenant_id, cita_id=self.cita_id,
                motivo_consulta="Control", enfermedad_actual="Ninguna", examen_clinico="Sin hallazgos",
                plan_tratamiento="Observación", indicaciones_alta="Reposo relativo",
                destino_atencion="ALTA", estado="borrador", antecedentes_snapshot=dict(_ANTECEDENTES)))
            db.add(AtencionDiagnostico(atencion_medica_id=self.atencion_id, diagnostico_cie10_id=self.dx_id, tipo="definitivo"))

            self.admision_id = uuid.uuid4()
            db.add(AdmisionEmergencia(id=self.admision_id, tenant_id=self.tenant_id, patient_id=self.pid,
                numero_cuenta="EMG-FIRMA-0001", estado="en_atencion"))
            self.atencion_emg_id = uuid.uuid4()
            db.add(AtencionEmergencia(id=self.atencion_emg_id, tenant_id=self.tenant_id, admision_id=self.admision_id,
                motivo_consulta="Dolor abdominal", destino_atencion="ALTA", estado="borrador"))
            await db.commit()

        self.prefix = "/app/firma-electronica"
        medico_claims = {"sub": str(self.medico_user_id), "name": "Medico De Firma", "panel": "app",
            "tenant_id": str(self.tenant_id), "role": "medico"}
        self.client.headers["Authorization"] = "Bearer " + create_access_token(medico_claims)

    async def test_firma_electronica_bandeja_lista_documentos_pendientes_del_medico(self):
        r = await self.client.get(self.prefix + "/bandeja")
        self.assertEqual(r.status_code, 200, r.text)
        tipos = {d["documento_tipo"] for d in r.json()}
        self.assertEqual(tipos, {"ATENCION_MEDICA", "ATENCION_EMERGENCIA"})

    async def test_firma_electronica_firmar_atencion_medica_genera_evidencia_y_registro(self):
        r = await self.client.post(self.prefix + "/bandeja/firmar",
            json={"documento_tipo": "ATENCION_MEDICA", "documento_id": str(self.atencion_id)})
        self.assertEqual(r.status_code, 200, r.text)
        evidencia = r.json()["cierre_evidencia"]
        self.assertEqual(evidencia["colegiatura"], "CMP-9999")
        self.assertTrue(evidencia["sha256"])

        r = await self.client.get(self.prefix + "/registros")
        self.assertEqual(len(r.json()), 1)
        self.assertEqual(r.json()[0]["documento_tipo"], "ATENCION_MEDICA")

        r = await self.client.get(self.prefix + "/bandeja")
        self.assertEqual({d["documento_id"] for d in r.json()}, {str(self.atencion_emg_id)})

    async def test_firma_electronica_firmar_atencion_emergencia_exige_autor_valido(self):
        r = await self.client.post(self.prefix + "/bandeja/firmar",
            json={"documento_tipo": "ATENCION_EMERGENCIA", "documento_id": str(self.atencion_emg_id)})
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["firmado_por_id"], str(self.medico_empleado_id))
        self.assertEqual(data["cierre_evidencia"]["colegiatura"], "CMP-9999")

    async def test_firma_electronica_no_permite_firmar_dos_veces(self):
        await self.client.post(self.prefix + "/bandeja/firmar",
            json={"documento_tipo": "ATENCION_EMERGENCIA", "documento_id": str(self.atencion_emg_id)})
        r = await self.client.post(self.prefix + "/bandeja/firmar",
            json={"documento_tipo": "ATENCION_EMERGENCIA", "documento_id": str(self.atencion_emg_id)})
        self.assertEqual(r.status_code, 400, r.text)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(FirmaElectronicaTests(name) for name in FirmaElectronicaTests.__dict__ if name.startswith("test_firma_electronica_"))
