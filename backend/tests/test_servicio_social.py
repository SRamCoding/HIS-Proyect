"""Servicio Social (Trabajo Social hospitalario -- Ley N.° 23808): pruebas
HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_servicio_social -v
"""
import unittest
import uuid
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import ClinicalRecord
from app.sigarh.rrhh.models import Empleado
from app.sigarh.mantenimiento.models import Profesion
from app.core.security import create_access_token


class ServicioSocialTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="servicio_social"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))

            profesion_tso = uuid.uuid4()
            db.add(Profesion(id=profesion_tso, tenant_id=self.tenant_id, grupo_ocupacional_id=uuid.uuid4(),
                nombre="Trabajador Social", codigo="TSO"))
            self.trabajador_id = uuid.uuid4()
            db.add(Empleado(id=self.trabajador_id, tenant_id=self.tenant_id, dni="22223333", nombres="Trabajadora",
                apellido_paterno="Social", apellido_materno="Prueba", profesion_id=profesion_tso))

            profesion_otra = uuid.uuid4()
            db.add(Profesion(id=profesion_otra, tenant_id=self.tenant_id, grupo_ocupacional_id=uuid.uuid4(),
                nombre="Enfermería", codigo="ENF"))
            self.no_trabajador_id = uuid.uuid4()
            db.add(Empleado(id=self.no_trabajador_id, tenant_id=self.tenant_id, dni="11112222", nombres="Otro",
                apellido_paterno="Profesional", apellido_materno="Prueba", profesion_id=profesion_otra))
            await db.commit()
        self.prefix = "/app/servicio-social"
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def _crear_evaluacion(self, **extra):
        body = {"patient_id": str(self.pid), "trabajador_social_id": str(self.trabajador_id), **extra}
        r = await self.client.post(self.prefix + "/servicio-social", json=body)
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()

    async def test_servicio_social_exige_profesion_trabajador_social(self):
        r = await self.client.post(self.prefix + "/servicio-social", json={
            "patient_id": str(self.pid), "trabajador_social_id": str(self.no_trabajador_id),
        })
        self.assertEqual(r.status_code, 400, r.text)

    async def test_servicio_social_derivacion_externa_exige_entidad(self):
        r = await self.client.post(self.prefix + "/servicio-social", json={
            "patient_id": str(self.pid), "trabajador_social_id": str(self.trabajador_id),
            "requiere_derivacion_externa": True,
        })
        self.assertEqual(r.status_code, 422, r.text)

    async def test_servicio_social_crea_evaluacion_con_derivacion_valida(self):
        data = await self._crear_evaluacion(tipo_vivienda="ALQUILADA", clasificacion_socioeconomica="POBRE",
            factores_riesgo=["adulto_mayor_solo"], requiere_derivacion_externa=True, entidad_derivacion="MIMP")
        self.assertEqual(data["estado"], "abierto")
        self.assertEqual(data["entidad_derivacion"], "MIMP")
        self.assertIn("paciente_datos_admision", data)

    async def test_servicio_social_rechaza_factor_riesgo_invalido(self):
        r = await self.client.post(self.prefix + "/servicio-social", json={
            "patient_id": str(self.pid), "trabajador_social_id": str(self.trabajador_id),
            "factores_riesgo": ["riesgo_inventado"],
        })
        self.assertEqual(r.status_code, 422, r.text)

    async def test_servicio_social_gestiones_y_cierre_de_caso(self):
        data = await self._crear_evaluacion()
        r = await self.client.post(f"{self.prefix}/servicio-social/{data['id']}/gestiones", json={
            "tipo_gestion": "VISITA_DOMICILIARIA", "descripcion": "Visita realizada, familia colabora",
        })
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual(len(r.json()["gestiones"]), 1)

        r = await self.client.post(f"{self.prefix}/servicio-social/{data['id']}/cerrar", json={"recomendaciones": "Caso resuelto"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "cerrado")

        r = await self.client.post(f"{self.prefix}/servicio-social/{data['id']}/gestiones", json={
            "tipo_gestion": "LLAMADA_TELEFONICA", "descripcion": "no debería funcionar",
        })
        self.assertEqual(r.status_code, 409, r.text)

        r = await self.client.post(f"{self.prefix}/servicio-social/{data['id']}/cerrar", json={})
        self.assertEqual(r.status_code, 409, r.text)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(ServicioSocialTests(name) for name in ServicioSocialTests.__dict__ if name.startswith("test_servicio_social_"))
