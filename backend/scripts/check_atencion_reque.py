"""Prueba clinica de Reque con rollback; no acredita profesionales reales."""
import asyncio, uuid, hashlib, json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine
from app.core.tenant_db import get_tenant_sessionmaker, _tenant_engines
import app.shared.ubigeo.models
from app.auth.models import User
from app.hospital.consulta_externa import service as s
from app.hospital.consulta_externa.schemas import AtencionMedicaCreate, AtencionMedicaUpdate, TriajeCreate, CitaCreate, RecetaCreate, OrdenLaboratorioCreate
from app.sigarh.config_farmacia.models import Medicamento
from app.sigarh.laboratorio.models import ExamenLaboratorio
from app.hospital.consulta_externa.models import Cita, ProgramacionMedica
from app.hospital.admision.models import Patient
from app.sigarh.general.models import DiagnosticoCIE10

TID = uuid.UUID("55540838-24a6-4e78-843b-f9b93e57733a")

async def main():
    get_tenant_sessionmaker("his_hospital_reque")
    try:
        async with _tenant_engines["his_hospital_reque"].connect() as conn:
            tx = await conn.begin()
            try:
                async with AsyncSession(bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint") as db:
                    original = await db.scalar(select(Cita).where(Cita.tenant_id == TID).limit(1))
                    assert original, "Se requiere una cita como referencia de paciente"
                    prog = await db.scalar(select(ProgramacionMedica).where(ProgramacionMedica.id == original.programacion_medica_id))
                    cupo = next(c for c in await s.get_cupos(db, TID, prog.id) if c["disponible"])
                    nueva = await s.create_cita(db, TID, CitaCreate(programacion_medica_id=prog.id, patient_id=original.patient_id, hora_inicio=cupo["hora_inicio"], hora_fin=cupo["hora_fin"]))
                    cita = await db.scalar(select(Cita).where(Cita.id == nueva["id"]))
                    actor = User(name="SIMULADO - medico QA", email=f"{uuid.uuid4()}@example.invalid", password="sin-acceso-login",
                        role="medico", panel="app", empleado_id=prog.medico_id, is_active=True)
                    db.add(actor); await db.flush()
                    user = {"sub": str(actor.id)}
                    await s.confirmar_cita(db, TID, cita.id)
                    try:
                        await s.create_atencion_medica(db, TID, cita.id, AtencionMedicaCreate(motivo_consulta="Prueba"), user)
                    except ValueError as e:
                        assert "triaje" in str(e)
                    else: raise AssertionError("Permitio omitir triaje")
                    await s.create_triaje(db, TID, cita.id, TriajeCreate(pulso=80, temperatura=37,
                        frecuencia_respiratoria=18, frecuencia_cardiaca=80, presion_sistolica=120, presion_diastolica=80))
                    dx = (await db.scalars(select(DiagnosticoCIE10).where(DiagnosticoCIE10.tenant_id == TID, DiagnosticoCIE10.is_active == True).limit(2))).all()
                    antecedentes = {k: "SIMULADO: antecedente documentado para prueba" for k in s.ANTECEDENTES}
                    data = AtencionMedicaCreate(motivo_consulta="Prueba autorizada", enfermedad_actual="SIMULADO: enfermedad actual",
                        examen_clinico="SIMULADO: examen documentado", plan_tratamiento="SIMULADO: plan",
                        indicaciones_alta="SIMULADO: seguimiento", antecedentes=antecedentes,
                        diagnosticos=[{"diagnostico_cie10_id": dx[0].id}])
                    result = await s.create_atencion_medica(db, TID, cita.id, data, user)
                    assert result["estado"] == "borrador"
                    assert (await s.get_cita_by_id(db, TID, cita.id))["estado"] == "confirmada"
                    paciente = await db.scalar(select(Patient).where(Patient.id == cita.patient_id))
                    paciente.antecedente_alergias = "SIMULADO: dato posterior diferente"
                    await db.flush()
                    assert (await s.get_atencion_medica(db, TID, cita.id))["antecedente_alergias"] == antecedentes["antecedente_alergias"]
                    try:
                        await s.update_atencion_medica(db, TID, cita.id, AtencionMedicaUpdate(diagnosticos=[{"diagnostico_cie10_id": uuid.uuid4()}]), user)
                    except ValueError: pass
                    else: raise AssertionError("Acepto diagnostico ajeno")
                    result = await s.update_atencion_medica(db, TID, cita.id, AtencionMedicaUpdate(
                        diagnosticos=[{"diagnostico_cie10_id": dx[1].id, "tipo": "presuntivo"}], prestaciones=["LABORATORIO", "FARMACIA"]), user)
                    assert len(result["diagnosticos"]) == 1 and result["diagnosticos"][0]["diagnostico_cie10_id"] == dx[1].id
                    try:
                        await s.firmar_atencion_medica(db, TID, cita.id, user=user)
                    except ValueError as e: assert "documento" in str(e)
                    else: raise AssertionError("Permitio cerrar sin orden seleccionada")
                    medicamento = Medicamento(tenant_id=TID, codigo_interno="QA-" + uuid.uuid4().hex[:8], nombre_comercial="SIMULADO QA", nombre_generico="SIMULADO QA", is_active=True)
                    examen = ExamenLaboratorio(tenant_id=TID, nombre="SIMULADO QA", is_active=True)
                    db.add_all([medicamento, examen]); await db.flush()
                    receta = await s.create_receta(db, TID, cita.id, RecetaCreate(items=[{"medicamento_id": medicamento.id, "cantidad": 1, "indicaciones": "SIMULADO: no administrar"}]), user=user)
                    orden = await s.create_orden_laboratorio(db, TID, cita.id, OrdenLaboratorioCreate(examen_ids=[examen.id]), user=user)
                    assert len(receta["items"]) == len(orden["items"]) == 1
                    try:
                        await s.update_atencion_medica(db, TID, cita.id, AtencionMedicaUpdate(prestaciones=[]), user)
                    except ValueError: pass
                    else: raise AssertionError("Permitio quitar prestaciones emitidas")
                    print("Alta con receta y orden simultaneas: OK")
                    try:
                        await s.firmar_atencion_medica(db, TID, cita.id)
                    except ValueError: pass
                    else: raise AssertionError("Permitio cerrar sin autor")
                    result = await s.firmar_atencion_medica(db, TID, cita.id, user=user)
                    assert result["estado"] == "firmado" and result["cierre_evidencia"]["usuario_id"] == str(actor.id)
                    evidencia = result["cierre_evidencia"]
                    assert evidencia["sha256"] == hashlib.sha256(json.dumps(evidencia["contenido"],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
                    assert (await s.get_cita_by_id(db, TID, cita.id))["estado"] == "atendida"
                    try:
                        await s.update_atencion_medica(db, TID, cita.id, AtencionMedicaUpdate(examen_clinico="Cambio"), user)
                    except ValueError: pass
                    else: raise AssertionError("Permitio editar cierre")
                    assert await s.get_atencion_medica(db, uuid.uuid4(), cita.id) is None
                    print("OK: triaje, borrador, antecedentes historicos, CIE10 editable, prestaciones, bloqueo de cierre, identidad, hash e inmutabilidad")
            finally: await tx.rollback()
        print("Rollback completo: cita y paciente originales conservados")
    finally:
        await engine.dispose()
        for e in _tenant_engines.values(): await e.dispose()

if __name__ == "__main__": asyncio.run(main())
