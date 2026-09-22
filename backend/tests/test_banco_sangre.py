"""Banco de Sangre (Ley N.° 26454 / D.S. N.° 03-95-SA -- PRONAHEBAS): pruebas
HTTP con PostgreSQL y rollback por caso.

Ejecutar en Docker:
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest tests.test_banco_sangre -v
"""
import unittest
import uuid
from datetime import datetime
from sqlalchemy import select
import test_archivo_clinico as archive
from app.tenants.hospitales.models import TenantModule
from app.hospital.admision.models import Patient, ClinicalRecord
from app.hospital.consulta_externa.models import ProgramacionMedica, Cita, AtencionMedica
from app.sigarh.rrhh.models import Empleado
from app.core.security import create_access_token


class BancoSangreTests(archive.ArchivoClinicoTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        async with self.session() as db:
            db.add(TenantModule(tenant_id=self.tenant_id, module_code="banco_sangre"))
            self.pid = await db.scalar(select(ClinicalRecord.patient_id).where(ClinicalRecord.id == self.record_id))
            self.medico_id = uuid.uuid4()
            db.add(Empleado(id=self.medico_id, tenant_id=self.tenant_id, dni="66665555", nombres="Medico",
                apellido_paterno="De Prueba", apellido_materno="Banco"))
            await db.flush()
            self.prog_id = uuid.uuid4()
            db.add(ProgramacionMedica(id=self.prog_id, tenant_id=self.tenant_id, medico_id=self.medico_id,
                fecha=datetime.utcnow().date(), turno="M", hora_inicio="09:00", hora_fin="09:15"))
            await db.flush()
            self.cita_id = uuid.uuid4()
            db.add(Cita(id=self.cita_id, tenant_id=self.tenant_id, programacion_medica_id=self.prog_id,
                patient_id=self.pid, hora_inicio="09:00", hora_fin="09:15", estado="atendida"))
            await db.flush()
            self.atencion_id = uuid.uuid4()
            db.add(AtencionMedica(id=self.atencion_id, tenant_id=self.tenant_id, cita_id=self.cita_id,
                motivo_consulta="Anemia", destino_atencion="ALTA", estado="firmado",
                firmado_por_id=self.medico_id, firmado_at=datetime.utcnow()))
            await db.commit()
        self.prefix = "/app/banco-sangre"
        self.client.headers["Authorization"] = "Bearer " + create_access_token(self.claims)

    async def _crear_donante(self, dni="12345678"):
        r = await self.client.post(self.prefix + "/donantes", json={
            "dni": dni, "nombres": "Donante", "apellido_paterno": "De", "apellido_materno": "Prueba",
            "fecha_nacimiento": "1990-01-01", "sexo": "M",
        })
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()["id"]

    async def _unidad_apta(self, donante_id, grupo="O", rh="-"):
        r = await self.client.post(self.prefix + "/unidades", json={
            "donante_id": donante_id, "grupo_sanguineo": grupo, "factor_rh": rh,
        })
        unidad_id = r.json()["id"]
        await self.client.post(f"{self.prefix}/unidades/{unidad_id}/tamizaje", json={
            "vih_reactivo": False, "hbsag_reactivo": False, "hcv_reactivo": False,
            "sifilis_reactivo": False, "chagas_reactivo": False,
        })
        return unidad_id

    async def test_banco_sangre_donante_duplicado_por_dni_es_rechazado(self):
        await self._crear_donante("11112222")
        r = await self.client.post(self.prefix + "/donantes", json={
            "dni": "11112222", "nombres": "Otro", "apellido_paterno": "X", "apellido_materno": "Y",
            "fecha_nacimiento": "1990-01-01", "sexo": "F",
        })
        self.assertEqual(r.status_code, 409, r.text)

    async def test_banco_sangre_tamizaje_reactivo_descarta_la_unidad(self):
        donante_id = await self._crear_donante()
        r = await self.client.post(self.prefix + "/unidades", json={
            "donante_id": donante_id, "grupo_sanguineo": "O", "factor_rh": "+",
        })
        unidad_id = r.json()["id"]
        r = await self.client.post(f"{self.prefix}/unidades/{unidad_id}/tamizaje", json={
            "vih_reactivo": True, "hbsag_reactivo": False, "hcv_reactivo": False,
            "sifilis_reactivo": False, "chagas_reactivo": False,
        })
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertFalse(data["apto"])
        self.assertEqual(data["estado"], "descartada")

        r = await self.client.post(f"{self.prefix}/unidades/{unidad_id}/fraccionar", json={"tipos": ["PAQUETE_GLOBULAR"]})
        self.assertEqual(r.status_code, 400, r.text)

    async def test_banco_sangre_fraccionar_produce_componentes_con_vencimiento_correcto(self):
        donante_id = await self._crear_donante()
        unidad_id = await self._unidad_apta(donante_id)
        r = await self.client.post(f"{self.prefix}/unidades/{unidad_id}/fraccionar",
            json={"tipos": ["PAQUETE_GLOBULAR", "PLAQUETAS"]})
        self.assertEqual(r.status_code, 200, r.text)
        componentes = r.json()
        self.assertEqual(len(componentes), 2)
        pg = next(c for c in componentes if c["tipo"] == "PAQUETE_GLOBULAR")
        plaq = next(c for c in componentes if c["tipo"] == "PLAQUETAS")
        self.assertEqual(pg["dias_para_vencer"], 35)
        self.assertEqual(plaq["dias_para_vencer"], 5)

        r = await self.client.get(self.prefix + "/inventario")
        tipos = {i["tipo"] for i in r.json()}
        self.assertEqual(tipos, {"PAQUETE_GLOBULAR", "PLAQUETAS"})

    async def test_banco_sangre_solicitud_resuelve_paciente_desde_atencion_medica(self):
        r = await self.client.post(self.prefix + "/solicitud-transfusional", json={
            "atencion_medica_id": str(self.atencion_id), "tipo_componente": "PAQUETE_GLOBULAR",
            "cantidad_unidades": 1, "grupo_sanguineo_paciente": "O", "factor_rh_paciente": "-",
            "urgencia": "URGENTE", "motivo_clinico": "Anemia severa",
        })
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual(r.json()["patient_id"], str(self.pid))
        self.assertEqual(r.json()["origen"], "CONSULTA_EXTERNA")

    async def test_banco_sangre_rechaza_componente_abo_incompatible(self):
        donante_id = await self._crear_donante()
        unidad_id = await self._unidad_apta(donante_id, grupo="AB", rh="+")
        comp = (await self.client.post(f"{self.prefix}/unidades/{unidad_id}/fraccionar",
            json={"tipos": ["PAQUETE_GLOBULAR"]})).json()[0]

        sol = (await self.client.post(self.prefix + "/solicitud-transfusional", json={
            "atencion_medica_id": str(self.atencion_id), "tipo_componente": "PAQUETE_GLOBULAR",
            "cantidad_unidades": 1, "grupo_sanguineo_paciente": "O", "factor_rh_paciente": "-",
            "urgencia": "RUTINA", "motivo_clinico": "Verificacion",
        })).json()

        r = await self.client.post(f"{self.prefix}/solicitud-transfusional/{sol['id']}/asignar-componente",
            json={"componente_id": comp["id"]})
        self.assertEqual(r.status_code, 400, r.text)

    async def test_banco_sangre_flujo_completo_asignar_prueba_cruzada_dispensar(self):
        donante_id = await self._crear_donante()
        unidad_id = await self._unidad_apta(donante_id, grupo="O", rh="-")
        comp = (await self.client.post(f"{self.prefix}/unidades/{unidad_id}/fraccionar",
            json={"tipos": ["PAQUETE_GLOBULAR"]})).json()[0]

        sol = (await self.client.post(self.prefix + "/solicitud-transfusional", json={
            "atencion_medica_id": str(self.atencion_id), "tipo_componente": "PAQUETE_GLOBULAR",
            "cantidad_unidades": 1, "grupo_sanguineo_paciente": "O", "factor_rh_paciente": "-",
            "urgencia": "URGENTE", "motivo_clinico": "Anemia",
        })).json()

        r = await self.client.post(f"{self.prefix}/solicitud-transfusional/{sol['id']}/asignar-componente",
            json={"componente_id": comp["id"]})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "en_pruebas_cruzadas")
        asignacion_id = r.json()["asignaciones"][0]["id"]

        r = await self.client.post(f"{self.prefix}/solicitud-transfusional/asignaciones/{asignacion_id}/prueba-cruzada",
            json={"resultado": "compatible"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "lista_para_dispensar")

        r = await self.client.post(f"{self.prefix}/solicitud-transfusional/asignaciones/{asignacion_id}/dispensar")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["estado"], "dispensada")

        r = await self.client.get(self.prefix + "/inventario")
        self.assertEqual(r.json(), [])  # el unico componente ya fue transfundido

    async def test_banco_sangre_no_permite_anular_solicitud_dispensada(self):
        donante_id = await self._crear_donante()
        unidad_id = await self._unidad_apta(donante_id, grupo="O", rh="-")
        comp = (await self.client.post(f"{self.prefix}/unidades/{unidad_id}/fraccionar",
            json={"tipos": ["PAQUETE_GLOBULAR"]})).json()[0]
        sol = (await self.client.post(self.prefix + "/solicitud-transfusional", json={
            "atencion_medica_id": str(self.atencion_id), "tipo_componente": "PAQUETE_GLOBULAR",
            "cantidad_unidades": 1, "grupo_sanguineo_paciente": "O", "factor_rh_paciente": "-",
            "urgencia": "RUTINA", "motivo_clinico": "Verificacion",
        })).json()
        asignacion = (await self.client.post(f"{self.prefix}/solicitud-transfusional/{sol['id']}/asignar-componente",
            json={"componente_id": comp["id"]})).json()["asignaciones"][0]
        await self.client.post(f"{self.prefix}/solicitud-transfusional/asignaciones/{asignacion['id']}/prueba-cruzada",
            json={"resultado": "compatible"})
        await self.client.post(f"{self.prefix}/solicitud-transfusional/asignaciones/{asignacion['id']}/dispensar")

        r = await self.client.post(f"{self.prefix}/solicitud-transfusional/{sol['id']}/anular", json={"motivo": "no debería"})
        self.assertEqual(r.status_code, 409, r.text)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(BancoSangreTests(name) for name in BancoSangreTests.__dict__ if name.startswith("test_banco_sangre_"))
