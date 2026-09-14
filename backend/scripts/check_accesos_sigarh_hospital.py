"""Prueba Rol → Perfil → Usuario → login App con datos revertidos."""
import asyncio, uuid
from contextlib import asynccontextmanager
from unittest.mock import patch, AsyncMock
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, AsyncSessionLocal, engine
from app.core.dependencies import get_current_user
from app.core.tenant_db import get_tenant_engine, _tenant_engines
from app.tenants.hospitales.models import Tenant
from app.sigarh.mantenimiento.models import UsuarioSigarh
from app.sigarh.mantenimiento.security import contexto_sigarh
from app.auth.models import User
from app.auth.hospital_access import contexto_hospital
from main import app

async def main():
    tid = uuid.UUID('55540838-24a6-4e78-843b-f9b93e57733a')
    mid = uuid.UUID('e240638f-995e-43bd-bf80-7bca417d8526')
    async with AsyncSessionLocal() as central: hospital = await central.get(Tenant, tid)
    try:
        async with get_tenant_engine(hospital.database_name).connect() as conn:
            outer = await conn.begin()
            async with AsyncSession(bind=conn, expire_on_commit=False, join_transaction_mode='create_savepoint') as db:
                marco = await db.scalar(select(UsuarioSigarh).where(UsuarioSigarh.is_active.is_(True)))
                contexto = await contexto_sigarh(db, marco, hospital)
                async def user(): return contexto
                async def session(request: __import__('fastapi').Request):
                    if request.url.path == '/auth/login':
                        async with AsyncSessionLocal() as central: yield central
                    else: yield db
                @asynccontextmanager
                async def tenant_session(_): yield db
                app.dependency_overrides[get_current_user] = user
                app.dependency_overrides[get_db] = session
                with patch('app.sigarh.mantenimiento.service.auditar', AsyncMock()), patch('app.auth.router._log_audit', AsyncMock()), patch('app.core.tenant_db.tenant_session', tenant_session):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://localhost', headers={'X-Tenant-ID': str(tid)}) as client:
                        prefix = '/sigarh/mantenimiento/'
                        r = await client.get(prefix + 'modulos-catalogo?panel=app'); assert r.status_code == 200, r.text
                        assert all(not m['code'].startswith('sigarh_') for m in r.json())
                        mods = ['consulta_externa.programacion','consulta_externa.atenciones']
                        r = await client.post(prefix + 'roles-sistema', json={'codigo':'QA_' + uuid.uuid4().hex, 'nombre':'SIMULADO rol médico', 'panel':'app','tipo_usuario':'medico','modulos_permitidos':mods})
                        assert r.status_code == 201, r.text
                        rol = r.json()
                        r = await client.post(prefix + 'perfiles-usuario', json={'nombre':'SIMULADO perfil ' + uuid.uuid4().hex,'rol_sistema_id':rol['id'],'modulos_acceso':mods})
                        assert r.status_code == 201, r.text
                        perfil = r.json()
                        login = 'qa_' + uuid.uuid4().hex
                        password = 'Simulado-Acceso1!'
                        r = await client.post(prefix + 'usuarios', json={'panel':'app','username':login,'email':login+'@example.test','password':password,'perfil_id':perfil['id'],'empleado_id':str(mid)})
                        assert r.status_code == 201, r.text
                        cuenta = r.json(); assert cuenta['panel'] == 'app'
                        r = await client.patch(prefix + 'usuarios/' + cuenta['id'], json={'email': login + '-edit@example.test'})
                        assert r.status_code == 200 and r.json()['username'] == login, r.text
                        r = await client.get(prefix + 'usuarios'); assert r.status_code == 200, r.text
                        assert any(u['id']==cuenta['id'] and u['panel']=='app' for u in r.json())
                        r = await client.post('/auth/login', json={'email':login,'password':password,'panel':'app'})
                        assert r.status_code == 200, r.text
                        assert set(r.json()['user']['active_modules']) == set(mods)
                        assert r.json()['user']['empleado_id'] == str(mid)
                        medico = await db.get(User, uuid.UUID(cuenta['id']))
                        contexto = await contexto_hospital(db, medico, hospital, {'consulta_externa'})
                        r = await client.get('/app/consulta-externa/programacion-medica'); assert r.status_code == 200, r.text
                        assert r.json() and all(p['medico_id']==str(mid) for p in r.json())
                        r = await client.post('/app/consulta-externa/programacion-medica/sincronizar-sigarh'); assert r.status_code == 403, r.text
                        from app.sigarh.mantenimiento.models import PerfilUsuario
                        from fastapi import HTTPException
                        perfil_db = await db.get(PerfilUsuario, uuid.UUID(perfil['id']))
                        perfil_db.is_active = False; await db.flush()
                        try: await contexto_hospital(db, medico, hospital, {'consulta_externa'})
                        except HTTPException as exc: assert exc.status_code == 403
                        else: raise AssertionError('Perfil inactivo conserva acceso')
                await outer.rollback()
        print('OK: SIGARH crea rol hospitalario, perfil, usuario y login App; programación propia y bloqueos. Todo revertido.')
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()
        for e in _tenant_engines.values(): await e.dispose()

if __name__ == '__main__': asyncio.run(main())
