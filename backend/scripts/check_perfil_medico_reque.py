"""Comprueba el panel y sus bloqueos con cuenta simulada; revierte sus datos."""
import asyncio
import uuid
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models import User, PerfilHospital
from app.auth.hospital_access import contexto_hospital, MEDICO_MODULOS
from app.core.database import get_db, engine
from app.core.dependencies import get_current_user
from app.core.tenant_db import get_tenant_engine, _tenant_engines
from app.tenants.hospitales.models import Tenant
from app.hospital.consulta_externa.models import ProgramacionMedica, Cita
from app.core.database import AsyncSessionLocal
from main import app


async def main():
    tid = uuid.UUID('55540838-24a6-4e78-843b-f9b93e57733a')
    mid = uuid.UUID('e240638f-995e-43bd-bf80-7bca417d8526')
    async with AsyncSessionLocal() as central:
        hospital = await central.get(Tenant, tid)
    tenant_engine = get_tenant_engine(hospital.database_name)
    try:
        async with tenant_engine.connect() as connection:
            transaccion = await connection.begin()
            async with AsyncSession(bind=connection, expire_on_commit=False, join_transaction_mode='create_savepoint') as db:
                perfil = PerfilHospital(id=uuid.uuid4(), tenant_id=tid, nombre='SIMULADO prueba perfil', role='medico', modulos=sorted(MEDICO_MODULOS), is_active=True)
                usuario = User(id=uuid.uuid4(), name='SIMULADO prueba panel', email=f'qa-{uuid.uuid4()}@example.test', password='SIN_LOGIN', role='medico', panel='app', empleado_id=mid, perfil_hospital_id=perfil.id, is_active=True)
                db.add(perfil); await db.flush(); db.add(usuario); await db.flush()
                contexto = await contexto_hospital(db, usuario, hospital, {'consulta_externa', 'admision'})
                async def actual(): return contexto
                async def session(): yield db
                app.dependency_overrides[get_current_user] = actual
                app.dependency_overrides[get_db] = session
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://127.0.0.1') as client:
                    for recurso in ['programacion-medica', 'citas']:
                        r = await client.get('/app/consulta-externa/' + recurso, params={'medico_id': str(uuid.uuid4())})
                        assert r.status_code == 200, (recurso, r.text)
                        assert all(i.get('medico_id') == str(mid) for i in r.json()), 'No respeta filtro del medico'
                        if recurso == 'programacion-medica': assert r.json(), 'No encuentra jornadas del medico'
                    cita = await db.scalar(select(Cita).join(ProgramacionMedica, ProgramacionMedica.id == Cita.programacion_medica_id).where(Cita.tenant_id == tid, ProgramacionMedica.medico_id == mid))
                    assert cita
                    for recurso in [f'citas/{cita.id}', f'paciente-consulta/{cita.id}', f'atenciones-medicas/{cita.id}/acceso', 'atenciones-medicas/cie10/buscar?q=colera', 'triaje/pendientes', 'estado-citas-medico']:
                        r = await client.get('/app/consulta-externa/' + recurso)
                        assert r.status_code == 200, (recurso, r.text)
                    for recurso, verbo in [(f'citas/{cita.id}/confirmar', 'POST'), (f'triaje/{cita.id}', 'POST'), ('programacion-medica/sincronizar-sigarh', 'POST'), ('/app/admision/buscar', 'GET')]:
                        path = recurso if recurso.startswith('/') else '/app/consulta-externa/' + recurso
                        r = await client.request(verbo, path, json={} if verbo == 'POST' else None)
                        assert r.status_code == 403, (recurso, r.text)
                    r = await client.get(f'/app/consulta-externa/citas/{uuid.uuid4()}')
                    assert r.status_code == 404
                    perfil.is_active = False; await db.flush()
                    from fastapi import HTTPException
                    try: await contexto_hospital(db, usuario, hospital, {'consulta_externa'})
                    except HTTPException as e: assert e.status_code == 403
                    else: raise AssertionError('Perfil inactivo permite acceso')
                await transaccion.rollback()
        print('OK: panel, filtro propio, antecedentes, CIE10, acceso clinico y bloqueos. Datos de prueba revertidos.')
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()
        for e in _tenant_engines.values(): await e.dispose()

if __name__ == '__main__': asyncio.run(main())
