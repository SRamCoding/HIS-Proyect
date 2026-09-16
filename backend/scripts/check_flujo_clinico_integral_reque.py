"""Prueba E2E transaccional del flujo clinico de Reque.

Crea datos QA, cruza las bandejas asistenciales y revierte todo al terminar.
No acredita profesionales ni deja informacion clinica persistente.
"""
import asyncio
import hashlib
import json
import uuid
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.database import engine
from app.core.tenant_db import _tenant_engines, get_tenant_sessionmaker
from app.hospital.admision.models import Patient
from app.hospital.consulta_externa import service as ce
from app.hospital.consulta_externa.models import Cita, ProgramacionMedica
from app.hospital.consulta_externa.schemas import (
    AtencionMedicaCreate, AtencionMedicaUpdate, CitaCreate, HospitalizacionCreate,
    InterconsultaCreate, OrdenImagenCreate, OrdenLaboratorioCreate, RecetaCreate,
    ReferenciaCreate, TriajeCreate,
)
from app.hospital.farmacia import schemas as far_schemas, service as far
from app.hospital.imagenes import schemas as img_schemas, service as img
from app.hospital.laboratorio import schemas as lab_schemas, service as lab
from app.hospital.hospitalizacion import schemas as hosp_schemas, service as hosp_service
from app.hospital.referencias import service as refs
from app.sigarh.config_farmacia.models import Almacen, Medicamento
from app.sigarh.general.models import DiagnosticoCIE10
from app.sigarh.imagenologia.models import ExamenImagenologia
from app.sigarh.infraestructura_hosp.models import Cama
from app.sigarh.laboratorio.models import ExamenLaboratorio
from app.sigarh.rrhh.models import Empleado, Especialidad

TID = uuid.UUID("55540838-24a6-4e78-843b-f9b93e57733a")
DB = "his_hospital_reque"


def ok(nombre):
    print(f"[OK] {nombre}")


async def main():
    get_tenant_sessionmaker(DB)
    try:
        async with _tenant_engines[DB].connect() as conn:
            outer = await conn.begin()
            try:
                async with AsyncSession(bind=conn, expire_on_commit=False,
                                        join_transaction_mode="create_savepoint") as db:
                    original = await db.scalar(select(Cita).where(Cita.tenant_id == TID).limit(1))
                    assert original, "Reque necesita al menos una cita de referencia"
                    prog = await db.scalar(select(ProgramacionMedica).where(
                        ProgramacionMedica.id == original.programacion_medica_id))
                    cupo = next((x for x in await ce.get_cupos(db, TID, prog.id) if x["disponible"]), None)
                    assert cupo, "La programacion de prueba no tiene cupos disponibles"

                    empleado_enf = Empleado(tenant_id=TID, dni=str(uuid.uuid4().int)[:8],
                        nombres="QA", apellido_paterno="ENFERMERIA", apellido_materno="REQUE")
                    db.add(empleado_enf); await db.flush()
                    medico = User(name="QA MEDICO REQUE", email=f"qa.medico.{uuid.uuid4()}@invalid.local",
                        password="sin-login", role="medico", panel="app", empleado_id=prog.medico_id, is_active=True)
                    enfermera = User(name="QA ENFERMERIA REQUE", email=f"qa.enfermeria.{uuid.uuid4()}@invalid.local",
                        password="sin-login", role="enfermera", panel="app",
                        empleado_id=empleado_enf.id, is_active=True)
                    farmacia = User(name="QA FARMACIA REQUE", email=f"qa.farmacia.{uuid.uuid4()}@invalid.local",
                        password="sin-login", role="farmacia", panel="app", is_active=True)
                    laboratorio = User(name="QA LABORATORIO REQUE", email=f"qa.lab.{uuid.uuid4()}@invalid.local",
                        password="sin-login", role="laboratorio", panel="app", is_active=True)
                    imagenes = User(name="QA IMAGENES REQUE", email=f"qa.img.{uuid.uuid4()}@invalid.local",
                        password="sin-login", role="imagenes", panel="app", is_active=True)
                    db.add_all([medico, enfermera, farmacia, laboratorio, imagenes]); await db.flush()
                    u_med = {"sub": str(medico.id), "name": medico.name}
                    u_enf = {"sub": str(enfermera.id), "name": enfermera.name,
                             "empleado_id": str(empleado_enf.id)}
                    u_far = {"sub": str(farmacia.id), "name": farmacia.name}
                    u_lab = {"sub": str(laboratorio.id), "name": laboratorio.name}
                    u_img = {"sub": str(imagenes.id), "name": imagenes.name}
                    ok("usuarios QA separados por perfil")

                    cita_out = await ce.create_cita(db, TID, CitaCreate(
                        programacion_medica_id=prog.id, patient_id=original.patient_id,
                        hora_inicio=cupo["hora_inicio"], hora_fin=cupo["hora_fin"]))
                    cita_id = cita_out["id"]
                    await ce.confirmar_cita(db, TID, cita_id)
                    await ce.create_triaje(db, TID, cita_id, TriajeCreate(
                        pulso=76, temperatura=36.7, frecuencia_respiratoria=18,
                        frecuencia_cardiaca=76, presion_sistolica=118,
                        presion_diastolica=76, peso=70, talla=170,
                        saturacion_o2=98), u_enf)
                    triaje = await ce.get_triaje_by_cita(db, TID, cita_id)
                    assert triaje.realizado_por_id == empleado_enf.id
                    assert (await ce.get_cita_by_id(db, TID, cita_id))["estado"] == "confirmada"
                    ok("programacion -> cita -> confirmacion -> triaje (enfermeria)")

                    dx = await db.scalar(select(DiagnosticoCIE10).where(
                        DiagnosticoCIE10.tenant_id == TID, DiagnosticoCIE10.is_active.is_(True)))
                    especialidades = (await db.scalars(select(Especialidad).where(
                        Especialidad.tenant_id == TID, Especialidad.is_active.is_(True)).limit(2))).all()
                    assert dx and especialidades, "Faltan catalogos CIE-10/especialidad en Reque"
                    antecedentes = {k: "QA: paciente no refiere" for k in ce.ANTECEDENTES}
                    at = await ce.create_atencion_medica(db, TID, cita_id, AtencionMedicaCreate(
                        motivo_consulta="QA integral: dolor controlado", enfermedad_actual="QA documentada",
                        examen_clinico="QA: paciente estable", plan_tratamiento="QA: control y examenes",
                        indicaciones_alta="QA: acudir a control", antecedentes=antecedentes,
                        diagnosticos=[{"diagnostico_cie10_id": dx.id}],
                        destino_atencion="HOSPITALIZACION",
                        prestaciones=["FARMACIA", "LABORATORIO", "IMAGEN", "INTERCONSULTA"]), u_med)

                    med = Medicamento(tenant_id=TID, codigo_interno="QA-" + uuid.uuid4().hex[:8],
                        nombre_comercial="Medicamento QA no administrar", nombre_generico="QA", is_active=True)
                    ex_lab = ExamenLaboratorio(tenant_id=TID, codigo="QA-LAB-" + uuid.uuid4().hex[:6],
                        nombre="Examen laboratorio QA", precio=Decimal("1.00"), is_active=True)
                    ex_img = ExamenImagenologia(tenant_id=TID, codigo="QA-IMG-" + uuid.uuid4().hex[:6],
                        nombre="Imagen QA", modalidad="Rayos X", precio=Decimal("1.00"), is_active=True)
                    almacen = Almacen(tenant_id=TID, codigo="QA-" + uuid.uuid4().hex[:6],
                        nombre="Farmacia QA temporal", tipo="farmacia", is_active=True)
                    db.add_all([med, ex_lab, ex_img, almacen]); await db.flush()
                    receta = await ce.create_receta(db, TID, cita_id, RecetaCreate(items=[{
                        "medicamento_id": med.id, "cantidad": 1, "dosis": "1 unidad",
                        "frecuencia": "dosis unica", "duracion_dias": 1,
                        "indicaciones": "Solo prueba QA; no administrar"}]), user=u_med)
                    orden_lab = await ce.create_orden_laboratorio(db, TID, cita_id,
                        OrdenLaboratorioCreate(examen_ids=[ex_lab.id], indicacion_clinica="QA"), user=u_med)
                    orden_img = await ce.create_orden_imagen(db, TID, cita_id,
                        OrdenImagenCreate(examen_ids=[ex_img.id], indicacion_clinica="QA"), user=u_med)
                    interc = await ce.create_interconsulta(db, TID, cita_id, InterconsultaCreate(
                        especialidad_destino_id=especialidades[-1].id, diagnostico_id=dx.id,
                        motivo="Evaluacion QA", urgente=False), user=u_med)
                    assert any(x["id"] == receta["id"] for x in await far.list_recipes(db, TID, "pendiente"))
                    assert (await lab.list_orders(db, TID, {"estado": "pendiente"}))["total"] >= 1
                    assert (await img.list_orders(db, TID, {"estado": "pendiente"}))["total"] >= 1
                    assert any(x["id"] == interc["id"] for x in await ce.list_interconsultas_pendientes(db, TID))
                    ok("atencion -> receta, laboratorio, imagenes e interconsulta visibles en bandejas")

                    ingreso = far_schemas.MovimientoIn(tipo="INGRESO", ambito="FARMACIA", concepto="QA",
                        almacen_destino_id=almacen.id, confirmar=True, items=[{
                            "medicamento_id": med.id, "numero_lote": "QA-LOTE",
                            "fecha_vencimiento": date.today() + timedelta(days=365),
                            "cantidad": Decimal("2"), "precio_unitario": Decimal("1") }])
                    await far.create_movement(db, TID, u_far, ingreso)
                    detalle_receta = await far.recipe_detail(db, TID, receta["id"])
                    desp = await far.dispense(db, TID, u_far, receta["id"], far_schemas.DispensarIn(
                        almacen_id=almacen.id, items=[{"receta_item_id": detalle_receta["items"][0]["id"], "cantidad": 1}],
                        observaciones="QA"))
                    assert (await far.recipe_detail(db, TID, receta["id"]))["estado"] == "despachada"
                    ok("farmacia recibio y despacho receta")

                    await lab.save_cupo(db, TID, u_lab, lab_schemas.CupoEntrada(fecha=date.today(), cupos=10), True)
                    mov_lab = await lab.save_movement(db, TID, u_lab, lab_schemas.MovimientoCreate(
                        orden_id=orden_lab["id"], fecha=date.today(), toma_examen_id=prog.medico_id,
                        items=[{"examen_id": ex_lab.id, "cantidad": 1, "precio": 1}]), None)
                    mov_lab = await lab.transition(db, TID, u_lab, mov_lab["id"], "tomar-muestra",
                        lab_schemas.Accion(version=mov_lab["version"]))
                    mov_lab = await lab.save_results(db, TID, u_lab, mov_lab["id"], lab_schemas.ResultadosEntrada(
                        version=mov_lab["version"], items=[{"item_id": mov_lab["items"][0]["id"],
                        "valores": [{"parametro": "QA", "valor": "Normal"}]}]))
                    mov_lab = await lab.transition(db, TID, u_lab, mov_lab["id"], "validar",
                        lab_schemas.Accion(version=mov_lab["version"]))
                    assert mov_lab["estado"] == "atendido"
                    ok("laboratorio recibio, tomo muestra, informo y valido")

                    mov_img = await img.save_movement(db, TID, u_img, img_schemas.MovimientoCreate(
                        orden_id=orden_img["id"], fecha=date.today(), tecnico_id=prog.medico_id,
                        items=[{"examen_id": ex_img.id, "cantidad": 1, "precio": 1}]), None)
                    mov_img = await img.transition(db, TID, u_img, mov_img["id"], "tomar-estudio",
                        img_schemas.Accion(version=mov_img["version"]))
                    mov_img = await img.save_informe(db, TID, u_img, mov_img["id"], img_schemas.InformeEntrada(
                        version=mov_img["version"], items=[{"item_id": mov_img["items"][0]["id"],
                        "tecnica": "QA", "hallazgos": "Sin hallazgos QA",
                        "impresion_diagnostica": "Estudio QA normal"}]))
                    mov_img = await img.transition(db, TID, u_img, mov_img["id"], "validar",
                        img_schemas.Accion(version=mov_img["version"]))
                    assert mov_img["estado"] == "atendido"
                    ok("imagenes recibio, realizo, informo y valido")

                    cama = await db.scalar(select(Cama).where(Cama.tenant_id == TID,
                        Cama.is_active.is_(True), Cama.estado == "DISPONIBLE"))
                    if not cama:
                        cama = Cama(tenant_id=TID, codigo="QA-" + uuid.uuid4().hex[:8],
                            nombre="Cama QA temporal", sala_texto="QA", piso_texto="QA",
                            estado="DISPONIBLE", is_active=True)
                        db.add(cama); await db.flush()
                    hosp = await ce.create_hospitalizacion(db, TID, cita_id, HospitalizacionCreate(
                        cama_id=cama.id, especialidad_ingreso_id=especialidades[0].id,
                        diagnostico_ingreso_id=dx.id), user=u_med)
                    assert hosp["estado"] == "internado" and cama.estado == "OCUPADA"
                    ok("hospitalizacion recibio destino y ocupo cama")
                    nota = await hosp_service.crear_nota(db, TID, u_enf, hosp["id"],
                        hosp_schemas.NotaEvolucionCreate(tipo="ENFERMERIA", pulso=74,
                            temperatura=36.5, presion_sistolica=116, presion_diastolica=74,
                            frecuencia_cardiaca=74, frecuencia_respiratoria=17,
                            saturacion_o2=99, contenido="Seguimiento QA de enfermeria",
                            plan_indicaciones="Continuar vigilancia QA"))
                    assert any(x["id"] == nota["id"] for x in
                               await hosp_service.listar_notas(db, TID, hosp["id"]))
                    ok("enfermeria registro seguimiento de hospitalizacion")

                    firmado = await ce.firmar_atencion_medica(db, TID, cita_id, user=u_med)
                    evidencia = firmado["cierre_evidencia"]
                    esperado = hashlib.sha256(json.dumps(evidencia["contenido"], sort_keys=True,
                        ensure_ascii=False).encode()).hexdigest()
                    assert firmado["estado"] == "firmado" and evidencia["sha256"] == esperado
                    assert (await ce.get_cita_by_id(db, TID, cita_id))["estado"] == "atendida"
                    ok("firma, hash, cierre inmutable y cita atendida")

                    cupo_ref = next((x for x in await ce.get_cupos(db, TID, prog.id) if x["disponible"]), None)
                    assert cupo_ref, "La programacion necesita un segundo cupo para probar referencia"
                    cita_ref = await ce.create_cita(db, TID, CitaCreate(
                        programacion_medica_id=prog.id, patient_id=original.patient_id,
                        hora_inicio=cupo_ref["hora_inicio"], hora_fin=cupo_ref["hora_fin"]))
                    await ce.confirmar_cita(db, TID, cita_ref["id"])
                    await ce.create_triaje(db, TID, cita_ref["id"], TriajeCreate(
                        pulso=75, temperatura=36.6, frecuencia_respiratoria=17,
                        frecuencia_cardiaca=75, presion_sistolica=117,
                        presion_diastolica=75, saturacion_o2=99), u_enf)
                    await ce.create_atencion_medica(db, TID, cita_ref["id"], AtencionMedicaCreate(
                        motivo_consulta="QA integral de referencia", enfermedad_actual="QA documentada",
                        examen_clinico="QA estable", plan_tratamiento="Referencia coordinada",
                        antecedentes=antecedentes, diagnosticos=[{"diagnostico_cie10_id": dx.id}],
                        destino_atencion="REFERENCIA"), u_med)
                    ref = await ce.create_referencia(db, TID, cita_ref["id"], ReferenciaCreate(
                        codigo_renipress_destino="QA-0001", nombre_ipress_destino="IPRESS QA TEMPORAL",
                        especialidad_destino=especialidades[0].nombre, diagnostico_id=dx.id,
                        motivo="Prueba integral de referencia"), user=u_med)
                    bandeja_ref = await refs.list_referencias(db, TID, {"estado": "enviada"})
                    assert any(x["id"] == ref["id"] for x in bandeja_ref["items"])
                    ok("referencias recibio destino de consulta externa")
                    assert (await ce.firmar_atencion_medica(db, TID, cita_ref["id"], user=u_med))["estado"] == "firmado"
                    ok("referencia firmada y cerrada")
                    print("RESULTADO: flujo clinico integral aprobado")
            finally:
                await outer.rollback()
        print("ROLLBACK: todos los usuarios y datos QA temporales fueron eliminados")
    finally:
        await engine.dispose()
        for tenant_engine in _tenant_engines.values():
            await tenant_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
