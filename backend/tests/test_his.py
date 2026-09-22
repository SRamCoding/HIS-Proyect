"""HIS (Formato HIS + Registro de la MicroRed): pruebas HTTP con PostgreSQL y
rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_his -v
"""
import unittest
import uuid
from datetime import date, datetime, timedelta
from sqlalchemy import select, update
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import ProgramacionMedica, Cita, AtencionMedica, AtencionDiagnostico
from app.sigarh.rrhh.models import Empleado
from app.sigarh.general.models import DiagnosticoCIE10
from app.sigarh.config_financiera.models import Seguro
from app.core.security import create_access_token


class HisTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="his"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))
            self.medico_id = uuid.uuid4()
            self.dx1_id = uuid.uuid4()
            self.dx2_id = uuid.uuid4()
            db.add(Empleado(id=self.medico_id, tenant_id=self.tenant_id, dni="77776666", nombres="Medico",
                apellido_paterno="De Prueba", apellido_materno="His"))
            db.add(DiagnosticoCIE10(id=self.dx1_id, tenant_id=self.tenant_id, codigo_cie10="J00",
                descripcion="Rinofaringitis aguda"))
            db.add(DiagnosticoCIE10(id=self.dx2_id, tenant_id=self.tenant_id, codigo_cie10="R50.9",
                descripcion="Fiebre, no especificada"))
            db.add(Seguro(id=uuid.uuid4(), tenant_id=self.tenant_id, codigo="PARTICULAR", nombre="Particular",
                tipo_entidad="Privado", requiere_fua=False, is_active=True))
            await db.flush()

            self.prog_id = uuid.uuid4()
            db.add(ProgramacionMedica(id=self.prog_id, tenant_id=self.tenant_id, medico_id=self.medico_id,
                fecha=date.today(), turno="M", hora_inicio="09:00", hora_fin="09:15"))
            await db.flush()

            self.cita_id = uuid.uuid4()
            db.add(Cita(id=self.cita_id, tenant_id=self.tenant_id, programacion_medica_id=self.prog_id,
                patient_id=self.pid, hora_inicio="09:00", hora_fin="09:15", fuente_financiamiento="Particular"))
            # Atencion sin diagnostico -- igual debe reportarse (una fila con dx en blanco).
            self.cita_sin_dx_id = uuid.uuid4()
            db.add(Cita(id=self.cita_sin_dx_id, tenant_id=self.tenant_id, programacion_medica_id=self.prog_id,
                patient_id=self.pid, hora_inicio="09:15", hora_fin="09:30"))
            await db.flush()

            # Timestamps de firma explicitamente distintos (no dos datetime.utcnow()
            # sucesivos): en Windows la resolucion del reloj puede hacer que ambas
            # llamadas devuelvan el mismo microsegundo, y el reporte HIS -- ordenado
            # por fecha_atencion desc -- queda con un desempate no determinista entre
            # las dos atenciones (filas[0] deja de ser predecible de una corrida a otra).
            self.atencion_id = uuid.uuid4()
            db.add(AtencionMedica(id=self.atencion_id, tenant_id=self.tenant_id, cita_id=self.cita_id,
                motivo_consulta="Control", destino_atencion="ALTA", estado="firmado",
                firmado_por_id=self.medico_id, firmado_at=datetime.utcnow()))
            self.atencion_sin_dx_id = uuid.uuid4()
            db.add(AtencionMedica(id=self.atencion_sin_dx_id, tenant_id=self.tenant_id, cita_id=self.cita_sin_dx_id,
                motivo_consulta="Sin diagnostico", destino_atencion="ALTA", estado="firmado",
                firmado_por_id=self.medico_id, firmado_at=datetime.utcnow() - timedelta(seconds=1)))
            await db.flush()

            db.add(AtencionDiagnostico(atencion_medica_id=self.atencion_id, diagnostico_cie10_id=self.dx1_id, tipo="definitivo"))
            db.add(AtencionDiagnostico(atencion_medica_id=self.atencion_id, diagnostico_cie10_id=self.dx2_id, tipo="repetitivo"))
            await db.commit()
        self.prefix = "/app/his"
        self.hoy = date.today().isoformat()
        self.ayer = (date.today() - timedelta(days=1)).isoformat()
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def test_his_formato_una_fila_por_diagnostico_y_atencion_sin_dx_igual_se_reporta(self):
        r = await self.client.get(self.prefix + "/formato-his", params={"fecha_desde": self.hoy, "fecha_hasta": self.hoy})
        self.assertEqual(r.status_code, 200, r.text)
        filas = r.json()
        self.assertEqual(len(filas), 3)  # 2 diagnosticos de la primera atencion + 1 fila sin dx de la segunda
        con_dx = [f for f in filas if f["diagnostico_codigo"]]
        sin_dx = [f for f in filas if not f["diagnostico_codigo"]]
        self.assertEqual({f["diagnostico_codigo"] for f in con_dx}, {"J00", "R50.9"})
        self.assertEqual(len(sin_dx), 1)
        self.assertEqual(filas[0]["financiador"], "Particular")

    async def test_his_formato_respeta_rango_de_fechas(self):
        r = await self.client.get(self.prefix + "/formato-his", params={"fecha_desde": self.ayer, "fecha_hasta": self.ayer})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json(), [])

    async def test_his_formato_csv_incluye_encabezado_real(self):
        r = await self.client.get(self.prefix + "/formato-his.csv", params={"fecha_desde": self.hoy, "fecha_hasta": self.hoy})
        self.assertEqual(r.status_code, 200, r.text)
        texto = r.content.decode("utf-8-sig")
        self.assertIn("diagnostico_codigo", texto.splitlines()[0])
        self.assertIn("J00", texto)

    async def test_his_envio_ciclo_completo_y_duplicado_rechazado(self):
        body = {"periodo": "2026-09", "fecha_desde": self.hoy, "fecha_hasta": self.hoy}
        r = await self.client.post(self.prefix + "/registro-microred", json=body)
        self.assertEqual(r.status_code, 201, r.text)
        envio = r.json()
        self.assertEqual(envio["estado"], "borrador")
        self.assertEqual(envio["total_registros"], 3)

        r = await self.client.post(self.prefix + "/registro-microred", json=body)
        self.assertEqual(r.status_code, 409, r.text)

        r = await self.client.post(f"{self.prefix}/registro-microred/{envio['id']}/cerrar", json={})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "enviado")
        self.assertIsNotNone(r.json()["fecha_envio"])

        r = await self.client.post(f"{self.prefix}/registro-microred/{envio['id']}/cerrar", json={})
        self.assertEqual(r.status_code, 409, r.text)

    async def test_his_periodo_con_formato_invalido_es_rechazado(self):
        r = await self.client.post(self.prefix + "/registro-microred",
            json={"periodo": "2026-9", "fecha_desde": self.hoy, "fecha_hasta": self.hoy})
        self.assertEqual(r.status_code, 422, r.text)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(HisTests(name) for name in HisTests.__dict__ if name.startswith("test_his_"))
