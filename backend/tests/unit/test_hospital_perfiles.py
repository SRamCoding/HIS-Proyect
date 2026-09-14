import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.auth.hospital_access import contexto_hospital, permiso_recurso, validar_perfil


@pytest.mark.parametrize("ruta,metodo,esperado", [
    ("programacion-medica", "GET", "programacion"),
    ("programacion-medica", "POST", "agendamiento"),
    ("citas/abc/confirmar", "POST", "confirmacion"),
    ("triaje/abc", "PATCH", "triaje"),
    ("triaje/abc", "GET", "atenciones"),
    ("atenciones-medicas/abc/firmar", "POST", "atenciones"),
    ("farmacia/recetas/abc", "POST", "atenciones"),
    ("paciente-consulta/abc", "GET", "atenciones"),
])
def test_recursos_separan_operaciones(ruta, metodo, esperado):
    assert permiso_recurso('/app/consulta-externa/' + ruta, metodo, 'consulta_externa') == 'consulta_externa.' + esperado


def cuenta(**kwargs):
    return SimpleNamespace(id=uuid.uuid4(), name="Prueba", email="prueba@example.test", panel="app",
        role=kwargs.get("role", "medico"), perfil_hospital_id=kwargs.get("perfil_hospital_id"),
        empleado_id=kwargs.get("empleado_id"))


def test_medico_sin_perfil_no_hereda_modulos():
    with pytest.raises(HTTPException):
        asyncio.run(contexto_hospital(SimpleNamespace(), cuenta(), SimpleNamespace(id=uuid.uuid4()), {"consulta_externa"}))


def test_administrador_general_preserva_acceso():
    r = asyncio.run(contexto_hospital(SimpleNamespace(), cuenta(role="administrador"), SimpleNamespace(id=uuid.uuid4()), {"admision"}))
    assert r['active_modules'] == ['admision']


def test_perfil_inactivo_revoca_acceso():
    db = SimpleNamespace(scalar=AsyncMock(return_value=None))
    with pytest.raises(HTTPException):
        asyncio.run(contexto_hospital(db, cuenta(perfil_hospital_id=uuid.uuid4()), SimpleNamespace(id=uuid.uuid4()), {"consulta_externa"}))


def test_medico_no_recibe_modulos_extra_ni_no_habilitados():
    perfil = SimpleNamespace(id=uuid.uuid4(), role="medico", modulos=["admision", "consulta_externa.atenciones", "consulta_externa.programacion"])
    empleado = SimpleNamespace(id=uuid.uuid4())
    db = SimpleNamespace(scalar=AsyncMock(side_effect=[perfil, empleado]))
    user = cuenta(perfil_hospital_id=perfil.id, empleado_id=empleado.id)
    r = asyncio.run(contexto_hospital(db, user, SimpleNamespace(id=uuid.uuid4()), {"consulta_externa"}))
    assert r['active_modules'] == ['consulta_externa.atenciones', 'consulta_externa.programacion']
    assert r['empleado_id'] == str(empleado.id)


def test_perfil_de_otro_hospital_no_se_asigna():
    perfil = SimpleNamespace(tenant_id=uuid.uuid4(), role="medico")
    db = SimpleNamespace(scalar=AsyncMock(return_value=perfil))
    with pytest.raises(HTTPException):
        asyncio.run(validar_perfil(db, uuid.uuid4(), uuid.uuid4(), 'medico', uuid.uuid4(), 'app'))


def test_sesion_app_recalcula_permisos_sin_confiar_en_jwt():
    from app.sigarh.mantenimiento.security import usuario_actual
    uid, tid = uuid.uuid4(), uuid.uuid4()
    hospital = SimpleNamespace(id=tid, database_name='prueba')
    usuario = cuenta(role='administrador'); usuario.id = uid
    central = SimpleNamespace(scalar=AsyncMock(side_effect=[hospital, SimpleNamespace(allowed_modules=None)]),
        scalars=AsyncMock(return_value=SimpleNamespace(all=lambda: ['consulta_externa'])))
    tdb = SimpleNamespace(scalar=AsyncMock(return_value=usuario))
    sesion = AsyncMock(); sesion.__aenter__.return_value = tdb
    with patch('app.core.tenant_db.get_tenant_sessionmaker', return_value=lambda: sesion):
        r = asyncio.run(usuario_actual(central, {'sub': str(uid), 'tenant_id': str(tid), 'panel': 'app', 'active_modules': ['farmacia']}))
    assert r['active_modules'] == ['consulta_externa']
