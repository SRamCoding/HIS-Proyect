"""Informes (reportes de solo lectura sobre datos reales de otros modulos):
pruebas HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_informes -v
"""
import unittest
import uuid
from datetime import date, datetime, timedelta
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import Patient, ClinicalRecord, ListaEspera
from app.hospital.consulta_externa.models import (
    ProgramacionMedica, Cita, AtencionMedica, Interconsulta, Hospitalizacion,
    OrdenLaboratorio, OrdenImagen, Receta, Referencia,
)
from app.hospital.emergencia.models import AtencionEmergencia, AdmisionEmergencia
from app.sigarh.rrhh.models import Empleado, Especialidad
from app.sigarh.infraestructura_hosp.models import Cama
from app.core.security import create_access_token


class InformesTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="informes"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))
            self.medico_id = uuid.uuid4()
            self.esp_id = uuid.uuid4()
            db.add(Empleado(id=self.medico_id, tenant_id=self.tenant_id, dni="55554444", nombres="Medico",
                apellido_paterno="De Prueba", apellido_materno="Informes"))
            db.add(Especialidad(id=self.esp_id, tenant_id=self.tenant_id, nombre="Medicina Interna",
                codigo="MED-INT", is_active=True))

            self.prog_id = uuid.uuid4()
            db.add(ProgramacionMedica(id=self.prog_id, tenant_id=self.tenant_id, medico_id=self.medico_id,
                fecha=date.today(), turno="M", hora_inicio="09:00", hora_fin="10:00",
                tiempo_promedio_atencion=15))  # 4 cupos de 15 min
            self.cita_id = uuid.uuid4()
            db.add(Cita(id=self.cita_id, tenant_id=self.tenant_id, programacion_medica_id=self.prog_id,
                patient_id=self.pid, hora_inicio="09:00", hora_fin="09:15", estado="atendida"))
            self.cita2_id = uuid.uuid4()
            db.add(Cita(id=self.cita2_id, tenant_id=self.tenant_id, programacion_medica_id=self.prog_id,
                patient_id=self.pid, hora_inicio="09:15", hora_fin="09:30", estado="cancelada"))
            self.atencion_id = uuid.uuid4()
            db.add(AtencionMedica(id=self.atencion_id, tenant_id=self.tenant_id, cita_id=self.cita_id,
                motivo_consulta="Control", destino_atencion="ALTA", estado="firmado",
                firmado_por_id=self.medico_id, firmado_at=datetime.utcnow()))
            db.add(Interconsulta(id=uuid.uuid4(), tenant_id=self.tenant_id, atencion_medica_id=self.atencion_id,
                patient_id=self.pid, especialidad_destino_id=self.esp_id, motivo="Evaluacion"))

            self.cama_id = uuid.uuid4()
            db.add(Cama(id=self.cama_id, tenant_id=self.tenant_id, codigo="C-01", nombre="Cama 1"))
            self.hosp_id = uuid.uuid4()
            db.add(Hospitalizacion(id=self.hosp_id, tenant_id=self.tenant_id, patient_id=self.pid,
                cama_id=self.cama_id, especialidad_ingreso_id=self.esp_id, numero_hospitalizacion="HOSP-0001",
                fecha_ingreso=datetime.utcnow() - timedelta(days=3),
                fecha_alta=datetime.utcnow() - timedelta(days=1), estado="alta"))

            db.add(OrdenLaboratorio(id=uuid.uuid4(), tenant_id=self.tenant_id, atencion_medica_id=self.atencion_id,
                patient_id=self.pid, numero_orden="LAB-0001", estado="pendiente"))
            db.add(Receta(id=uuid.uuid4(), tenant_id=self.tenant_id, atencion_medica_id=self.atencion_id,
                numero_receta="REC-0001", estado="pendiente"))

            self.admision_em_id = uuid.uuid4()
            db.add(AdmisionEmergencia(id=self.admision_em_id, tenant_id=self.tenant_id, patient_id=self.pid,
                numero_cuenta="EMG-0001", estado="admitido"))

            db.add(ListaEspera(id=uuid.uuid4(), tenant_id=self.tenant_id, patient_id=self.pid, estado="pendiente"))

            db.add(Referencia(id=uuid.uuid4(), tenant_id=self.tenant_id, atencion_medica_id=None,
                patient_id=self.pid, nombre_ipress_destino="Hospital Regional", motivo="Evaluacion especializada",
                numero_referencia="REF-0001", estado="contrarreferida",
                fecha_contrarreferencia=date.today() - timedelta(days=1),
                created_at=datetime.utcnow() - timedelta(days=5)))
            await db.commit()
        self.prefix = "/app/informes"
        self.hoy = date.today().isoformat()
        self.desde = (date.today() - timedelta(days=10)).isoformat()
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def test_informes_reporte_medico_cuenta_citas_atenciones_e_interconsultas(self):
        r = await self.client.get(self.prefix + "/reporte-medico", params={"fecha_desde": self.desde, "fecha_hasta": self.hoy})
        self.assertEqual(r.status_code, 200, r.text)
        filas = r.json()
        self.assertEqual(len(filas), 1)
        fila = filas[0]
        self.assertEqual(fila["citas_programadas"], 2)
        self.assertEqual(fila["citas_atendidas"], 1)
        self.assertEqual(fila["citas_canceladas"], 1)
        self.assertEqual(fila["atenciones_firmadas_consulta_externa"], 1)
        self.assertEqual(fila["interconsultas_generadas"], 1)

    async def test_informes_reportes_hospitalizacion_calcula_promedio_estancia_y_especialidad(self):
        r = await self.client.get(self.prefix + "/reportes-hospitalizacion", params={"fecha_desde": self.desde, "fecha_hasta": self.hoy})
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["ingresos"], 1)
        self.assertEqual(data["altas"], 1)
        self.assertEqual(data["promedio_estancia_dias"], 3.0)
        self.assertEqual(data["por_especialidad"], [{"especialidad": "Medicina Interna", "ingresos": 1}])

    async def test_informes_gestion_cupos_calcula_totales_usados_disponibles(self):
        r = await self.client.get(self.prefix + "/gestion-cupos", params={"fecha_desde": self.hoy, "fecha_hasta": self.hoy})
        self.assertEqual(r.status_code, 200, r.text)
        filas = r.json()
        self.assertEqual(len(filas), 1)
        fila = filas[0]
        self.assertEqual(fila["cupos_totales"], 4)  # 60 min / 15 min
        self.assertEqual(fila["cupos_usados"], 1)  # la cancelada no cuenta
        self.assertEqual(fila["cupos_disponibles"], 3)

    async def test_informes_gestion_tickets_agrupa_por_estado(self):
        r = await self.client.get(self.prefix + "/gestion-tickets", params={"fecha_desde": self.desde, "fecha_hasta": self.hoy})
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["laboratorio"]["total"], 1)
        self.assertEqual(data["laboratorio"]["por_estado"], {"pendiente": 1})
        self.assertEqual(data["farmacia_recetas"]["total"], 1)

    async def test_informes_visor_colas_cuenta_pendientes_reales(self):
        r = await self.client.get(self.prefix + "/visor-colas")
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["admision_lista_espera_pendientes"], 1)
        self.assertEqual(data["emergencia_admitidos_sin_triaje"], 1)
        self.assertEqual(data["laboratorio_ordenes_pendientes"], 1)
        self.assertEqual(data["farmacia_recetas_pendientes"], 1)

    async def test_informes_externos_agrupa_por_estado_y_calcula_dias_contrarreferencia(self):
        r = await self.client.get(self.prefix + "/externos", params={"fecha_desde": self.desde, "fecha_hasta": self.hoy})
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["por_estado"], {"contrarreferida": 1})
        self.assertEqual(data["items"][0]["destino"], "Hospital Regional")
        self.assertIsNotNone(data["promedio_dias_contrarreferencia"])

    async def test_informes_rango_de_fechas_invalido_es_rechazado(self):
        r = await self.client.get(self.prefix + "/externos", params={"fecha_desde": self.hoy, "fecha_hasta": self.desde})
        self.assertEqual(r.status_code, 400, r.text)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(InformesTests(name) for name in InformesTests.__dict__ if name.startswith("test_informes_"))
