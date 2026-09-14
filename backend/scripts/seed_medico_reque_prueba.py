"""Caso persistente de prueba autorizado: Reque, octubre 2026. No es acreditacion real."""
import asyncio, json, uuid, secrets
from datetime import date
import bcrypt
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine
from app.core.tenant_db import get_tenant_sessionmaker, _tenant_engines
from app.sigarh.mantenimiento.models import (Servicio, Profesion, TipoTrabajador, NivelRemunerativo, Actividad, HorarioGuardia, RolSistema, PerfilUsuario, UsuarioSigarh, ServicioEspecialidad)
from app.sigarh.mantenimiento.security import contexto_sigarh
from app.sigarh.mantenimiento.guardias_catalogo import stable_id
from app.sigarh.rrhh.models import Empleado, Especialidad
from app.sigarh.rrhh.schemas import EmpleadoCreate, EmpleadoEspecialidadCreate
from app.sigarh.rrhh.service import crear_empleado
from app.sigarh.infraestructura.models import Consultorio
from app.sigarh.creacion_roles.schemas import RolCreate, TurnoRequest
from app.sigarh.creacion_roles import service as roles
from app.sigarh.roles_pendientes.service import aprobar_rol
from app.hospital.consulta_externa.models import ProgramacionMedica
from app.hospital.consulta_externa.service import get_cupos, sincronizar_programacion_sigarh

TID = uuid.UUID("55540838-24a6-4e78-843b-f9b93e57733a")
DNI = "00009991"
DIAS = [1, 2, 4, 5, 6]

async def main():
    get_tenant_sessionmaker("his_hospital_reque")
    async with _tenant_engines["his_hospital_reque"].connect() as conn:
        tx = await conn.begin()
        try:
            async with AsyncSession(bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint") as db:
                existente = await db.scalar(select(Empleado).where(Empleado.tenant_id == TID, Empleado.dni == DNI))
                if existente:
                    raise RuntimeError("El caso de prueba ya existe; no se duplicara.")
                servicio = await db.scalar(select(Servicio).where(Servicio.tenant_id == TID, Servicio.codigo == "SRV-MED"))
                profesion = await db.scalar(select(Profesion).where(Profesion.tenant_id == TID, Profesion.codigo == "MED"))
                tipo = await db.scalar(select(TipoTrabajador).where(TipoTrabajador.tenant_id == TID, TipoTrabajador.codigo == "TT-CAS"))
                nivel = await db.scalar(select(NivelRemunerativo).where(NivelRemunerativo.tenant_id == TID, NivelRemunerativo.profesion_codigo == "MED").order_by(NivelRemunerativo.codigo))
                esp = await db.scalar(select(Especialidad).where(Especialidad.tenant_id == TID, Especialidad.codigo == "CON-ESP-026", Especialidad.is_active == True))
                assert await db.scalar(select(ServicioEspecialidad.servicio_id).where(ServicioEspecialidad.servicio_id == servicio.id, ServicioEspecialidad.especialidad_id == esp.id))
                revisor = await db.scalar(select(UsuarioSigarh).where(UsuarioSigarh.tenant_id == TID, UsuarioSigarh.username == "marco"))
                contexto_revisor = await contexto_sigarh(db, revisor)
                empleado = await crear_empleado(db, TID, EmpleadoCreate(
                    dni=DNI, nombres="MEDICO DE PRUEBA", apellido_paterno="REQUE", apellido_materno="SIMULADO",
                    fecha_nacimiento=date(1990, 1, 1), sexo="M", correo="qa-medico-reque@example.invalid",
                    profesion_id=profesion.id, grupo_ocupacional_id=profesion.grupo_ocupacional_id,
                    tipo_trabajador_id=tipo.id, nivel_remunerativo_id=nivel.id,
                    departamento_id=servicio.departamento_id, servicio_id=servicio.id,
                    cargo_laboral="Medico de prueba - Medicina Interna", modalidad="CAS",
                    fecha_ingreso=date(2026, 9, 1), vinculo_laboral_codigo="1057_CONTRATADO",
                    numero_legajo="QA-REQUE-2026-10", numero_colegiatura="QA-CMP-REQUE", numero_cmp="QA-CMP-REQUE",
                    habilitado_colegio=True, jornada_mensual_horas=150,
                    jornada_sustento="SIMULADO: caso de prueba autorizado; no representa un contrato real",
                    documento_vinculo_laboral="SIMULADO - pruebas de flujo hospitalario",
                    especialidades=[EmpleadoEspecialidadCreate(especialidad_id=esp.id, numero_rne="QA-RNE-REQUE", validado=True)]))
                # Autor tecnico separado del revisor, sin acceso administrativo.
                acceso = ["sigarh_creacion_roles.medicos"]
                rol_acceso = RolSistema(tenant_id=TID, codigo="QA_AUTOR_REQUE", nombre="Autor tecnico de prueba Reque",
                    panel="sigarh", modulos_permitidos=json.dumps(acceso), permisos_accion="[]", alcance_global=False,
                    descripcion="SIMULADO - soporte del caso de prueba", is_active=True)
                db.add(rol_acceso); await db.flush()
                perfil = PerfilUsuario(tenant_id=TID, nombre="Autor tecnico de prueba Reque", rol_sistema_id=rol_acceso.id,
                    modulos_acceso=json.dumps(acceso), descripcion="SIMULADO - no se entrega acceso de login", is_active=True)
                db.add(perfil); await db.flush()
                autor = UsuarioSigarh(tenant_id=TID, name="Carga tecnica de prueba Reque", username="qa_autor_reque",
                    email="qa-autor-reque@example.invalid", empleado_id=empleado.id, perfil_id=perfil.id,
                    password=bcrypt.hashpw(secrets.token_urlsafe(32).encode(), bcrypt.gensalt()).decode(), is_active=True)
                db.add(autor); await db.flush()
                await contexto_sigarh(db, autor)
                rol = await roles.crear_rol(db, TID, RolCreate(categoria_personal="medicos", tipo_rol="ordinario",
                    departamento_id=servicio.departamento_id, servicio_id=servicio.id, mes=10, anio=2026), autor.name, autor.id)
                detalle = await roles.agregar_personal(db, TID, rol["id"], [empleado.id])
                re_id = detalle["empleados"][0]["id"]
                for code, horario in [("ACT-CE", "CE-M4"), ("ACT-GE", "GC-M2")]:
                    actividad = await db.scalar(select(Actividad).where(Actividad.tenant_id == TID, Actividad.codigo == code))
                    detalle = await roles.agregar_actividades(db, TID, re_id, [actividad.id])
                    ra = next(a for a in detalle["empleados"][0]["actividades"] if a["actividad_id"] == actividad.id)
                    await roles.agregar_turno(db, TID, ra["id"], TurnoRequest(horario_guardia_id=stable_id(TID, horario), dias_semana=DIAS))
                # Los cinco dias elegidos suman 23 jornadas de seis horas (138 h).
                # Cuatro domingos de tres horas completan las 150 h mensuales.
                domingo = HorarioGuardia(tenant_id=TID, nombre="Consulta de prueba domingo 08:00-11:00",
                    hora_inicio="08:00", hora_fin="11:00", horas_totales=3, duracion_minutos=180, is_active=True)
                db.add(domingo); await db.flush()
                ce_actividad = await db.scalar(select(Actividad).where(Actividad.tenant_id == TID, Actividad.codigo == "ACT-CE"))
                detalle = await roles.serializar_uno(db, TID, await roles.obtener_rol_orm(db, rol["id"], TID))
                ce = next(a for a in detalle["empleados"][0]["actividades"] if a["actividad_id"] == ce_actividad.id)
                await roles.agregar_turno(db, TID, ce["id"], TurnoRequest(horario_guardia_id=domingo.id, dias_semana=[0]))
                await roles.enviar_rol(db, TID, rol["id"])
                aprobado = await aprobar_rol(db, TID, rol["id"], contexto_revisor)
                assert aprobado["status"] == "approved"
                consultorio = Consultorio(tenant_id=TID, nombre="Consultorio de prueba Reque - Medicina Interna", especialidad_id=esp.id,
                    capacidad=1, equipamiento="SIMULADO - pruebas de agenda", is_active=True)
                db.add(consultorio); await db.flush()
                agendas = (await db.scalars(select(ProgramacionMedica).where(ProgramacionMedica.tenant_id == TID,
                    ProgramacionMedica.medico_id == empleado.id).order_by(ProgramacionMedica.fecha))).all()
                assert len(agendas) == 27, len(agendas)
                for agenda in agendas:
                    agenda.consultorio_id = consultorio.id
                await db.flush()
                assert len(await get_cupos(db, TID, agendas[0].id)) == 16
                assert (await sincronizar_programacion_sigarh(db, TID, 10, 2026))["creadas"] == 0
                diagnostico = await roles.diagnosticar_rol(db, TID, await roles.obtener_rol_orm(db, rol["id"], TID))
                assert not roles.errores_bloqueantes(diagnostico), diagnostico
                # La identidad tecnica queda deshabilitada y sin password conocido.
                autor.is_active = False; rol_acceso.is_active = False; perfil.is_active = False
                await db.commit()
                resultado = {"hospital": "Reque", "empleado": empleado.nombre_completo, "dni_ficticio": DNI,
                    "empleado_id": str(empleado.id), "rol_id": str(rol["id"]), "estado": "approved",
                    "periodo": "octubre 2026", "dias_semana": DIAS, "horas": 150,
                    "programaciones": len(agendas), "cupos_por_fecha": 16, "cupos_domingo": 12, "cupos_totales": 416,
                    "primera_fecha": str(agendas[0].fecha), "primera_programacion_id": str(agendas[0].id),
                    "consultorio_id": str(consultorio.id), "autor_tecnico_deshabilitado": True, "datos_simulados": True}
            await tx.commit()
            print(json.dumps(resultado, ensure_ascii=True, indent=2))
        except Exception:
            await tx.rollback()
            raise
    for motor in _tenant_engines.values(): await motor.dispose()
    await engine.dispose()

if __name__ == "__main__": asyncio.run(main())
