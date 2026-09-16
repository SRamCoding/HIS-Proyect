# backend/app/core/audit.py
"""Auditoria automatica a nivel de base de datos.

En vez de depender de que cada endpoint recuerde llamar a una funcion de
auditoria (lo que dejo la mayoria de modulos SIGARH/Hospital sin cubrir),
un listener de SQLAlchemy engancha CADA insert/update/delete de CUALQUIER
modelo mapeado sobre `Base` -- sin importar por que sesion (central o BD
fisica de un hospital) ni por que servicio pase. El registro final siempre
se escribe en la BD central (AuditLog vive solo ahi).

Flujo:
  1. `get_current_user` (dependencies.py) fija el actor (usuario/tenant) en
     un contextvar apenas resuelve el JWT.
  2. `before_flush` (este modulo) captura, en memoria, el before/after de
     cada objeto nuevo/modificado/eliminado del flush -- de la sesion que
     sea -- y lo apila en otro contextvar (no escribe nada todavia: no se
     puede abrir una sesion nueva en medio de un flush ajeno).
  3. `get_db`/`get_db_central` (database.py), justo despues de que su propio
     `session.commit()` tuvo exito, vacian esa pila hacia AuditLog usando
     una sesion central dedicada.
"""
import uuid
from contextvars import ContextVar
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

from sqlalchemy import event, inspect, select
from sqlalchemy.orm import Session, attributes

_actor: ContextVar[dict | None] = ContextVar("_audit_actor", default=None)
_pending: ContextVar[list | None] = ContextVar("_audit_pending", default=None)

# Nombres de columna que jamas se guardan en texto plano en el log.
_CAMPOS_SENSIBLES = ("password", "contrasena", "secret", "token", "hash")

# Modelos que no se auditan (la propia tabla de auditoria: evita recursion).
_MODELOS_EXCLUIDOS: set[str] = {"AuditLog"}


def set_audit_actor(*, user_id: str | None, user_name: str | None, tenant_id: str | None) -> None:
    """Llamado por get_current_user apenas resuelve el JWT de la request."""
    _actor.set({"user_id": user_id, "user_name": user_name, "tenant_id": tenant_id})


def init_audit_batch() -> None:
    """Llamado al abrir cada sesion (get_db/get_db_central): arranca la
    pila de cambios pendientes de ESTA request en limpio."""
    _pending.set([])


def _json_safe(value):
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    return value


def _es_sensible(nombre_columna: str) -> bool:
    bajo = nombre_columna.lower()
    return any(campo in bajo for campo in _CAMPOS_SENSIBLES)


def _fila_completa(obj) -> dict:
    fila = {}
    for attr in inspect(obj).mapper.column_attrs:
        key = attr.key
        valor = getattr(obj, key)
        fila[key] = "***" if _es_sensible(key) else _json_safe(valor)
    return fila


def _id_de(obj) -> str | None:
    pk_cols = inspect(obj).mapper.primary_key
    valores = []
    for col in pk_cols:
        prop = inspect(obj).mapper.get_property_by_column(col)
        v = getattr(obj, prop.key, None)
        if v is None:
            return None
        valores.append(str(v))
    return "-".join(valores) if valores else None


def _tenant_hint(obj) -> str | None:
    """De que hospital es este cambio, segun el propio objeto (no el actor).
    Necesario porque un admin (sin tenant_id en su JWT) puede modificar datos
    de un hospital puntual -- ej. activar modulos, crear el hospital -- y esas
    filas deben poder filtrarse por ese hospital en Auditoria por Hospital,
    no solo aparecer como evento "global"."""
    mapper = inspect(obj).mapper
    if "tenant_id" in mapper.columns:
        v = getattr(obj, "tenant_id", None)
        return str(v) if v else None
    if type(obj).__name__ == "Tenant":
        return str(obj.id) if obj.id else None
    return None


def _db_name_de(session) -> str | None:
    """Nombre de la BD fisica a la que esta conectada esta sesion (lectura de
    la URL ya resuelta, sin I/O). Sirve para inferir el hospital cuando el
    objeto auditado no trae su propio tenant_id -- las cuentas User de un
    hospital con base fisica propia lo dejan en NULL porque la base entera
    ya esta scopeada a ese tenant, no hace falta repetirlo por fila."""
    try:
        return session.get_bind().url.database
    except Exception:
        return None


def _acumular(action: str, model: str, model_id: str | None, old_values: dict | None, new_values: dict | None, tenant_hint: str | None, db_name_hint: str | None, obj=None) -> None:
    pila = _pending.get()
    if pila is None:
        # Sesion abierta fuera del ciclo get_db/get_db_central (ej. scripts).
        return
    entrada = {
        "action": action, "model": model, "model_id": model_id,
        "old_values": old_values, "new_values": new_values,
        "tenant_hint": tenant_hint, "db_name_hint": db_name_hint,
    }
    if model_id is None and obj is not None:
        # El id todavia no existe (default resuelto durante el flush, no antes):
        # se completa en after_flush, cuando el INSERT ya corrio.
        entrada["_pendiente_id"] = obj
    pila.append(entrada)


@event.listens_for(Session, "before_flush")
def _before_flush(session, flush_context, instances):
    db_name_hint = _db_name_de(session)

    for obj in session.new:
        model = type(obj).__name__
        if model in _MODELOS_EXCLUIDOS:
            continue
        _acumular("created", model, _id_de(obj), None, _fila_completa(obj), _tenant_hint(obj), db_name_hint, obj)

    for obj in session.dirty:
        model = type(obj).__name__
        if model in _MODELOS_EXCLUIDOS or not session.is_modified(obj, include_collections=False):
            continue
        old_values, new_values = {}, {}
        for attr in inspect(obj).mapper.column_attrs:
            hist = attributes.get_history(obj, attr.key)
            if not hist.has_changes():
                continue
            campo = attr.key
            old_values[campo] = "***" if _es_sensible(campo) else _json_safe(hist.deleted[0] if hist.deleted else None)
            new_values[campo] = "***" if _es_sensible(campo) else _json_safe(hist.added[0] if hist.added else None)
        if old_values or new_values:
            _acumular("updated", model, _id_de(obj), old_values, new_values, _tenant_hint(obj), db_name_hint)

    for obj in session.deleted:
        model = type(obj).__name__
        if model in _MODELOS_EXCLUIDOS:
            continue
        _acumular("deleted", model, _id_de(obj), _fila_completa(obj), None, _tenant_hint(obj), db_name_hint)


@event.listens_for(Session, "after_flush")
def _after_flush(session, flush_context):
    """El INSERT ya corrio: los ids con default resuelto durante el flush
    (no asignados a mano antes del add()) ya existen. Se completan aqui.
    Una request puede tocar mas de una sesion (BD fisica + central); solo se
    resuelve el objeto que en verdad pertenece a ESTA sesion que acaba de
    flushear -- el de otra sesion se deja intacto para su propio after_flush."""
    pila = _pending.get()
    if not pila:
        return
    for entrada in pila:
        obj = entrada.get("_pendiente_id")
        if obj is None or entrada["model_id"] is not None:
            continue
        if obj in session:
            entrada["model_id"] = _id_de(obj)
            del entrada["_pendiente_id"]


async def flush_pending_audits(ip_address: str | None) -> None:
    """Vacia lo acumulado por before_flush hacia AuditLog (BD central).
    Se llama justo despues de un session.commit() exitoso. Nunca propaga
    excepciones: un fallo al auditar no debe tumbar una operacion de
    negocio que ya se guardo correctamente."""
    pila = _pending.get()
    if not pila:
        return
    _pending.set([])

    try:
        actor = _actor.get() or {}
        user_id = actor.get("user_id")
        user_name = actor.get("user_name")
        actor_tenant_id = actor.get("tenant_id")

        from app.core.database import AsyncSessionLocal
        from app.admin.auditoria.models import AuditLog
        from app.tenants.hospitales.models import Tenant

        nombres_cache: dict[str, str | None] = {}
        db_name_cache: dict[str, str | None] = {}

        async def nombre_de(db, tenant_id_str: str | None) -> str | None:
            if not tenant_id_str:
                return None
            if tenant_id_str not in nombres_cache:
                try:
                    tenant = await db.get(Tenant, uuid.UUID(tenant_id_str))
                    nombres_cache[tenant_id_str] = tenant.name if tenant else None
                except (ValueError, TypeError):
                    nombres_cache[tenant_id_str] = None
            return nombres_cache[tenant_id_str]

        async def tenant_id_por_db_name(db, db_name: str | None) -> str | None:
            """Para cuando el objeto auditado no trae tenant_id propio (las
            cuentas de un hospital con base fisica no lo necesitan, la base
            entera ya es de ESE hospital) -- se busca que Tenant tiene esa
            base fisica registrada como la suya."""
            if not db_name:
                return None
            if db_name not in db_name_cache:
                tenant = await db.scalar(select(Tenant).where(Tenant.database_name == db_name))
                db_name_cache[db_name] = str(tenant.id) if tenant else None
            return db_name_cache[db_name]

        async with AsyncSessionLocal() as db:
            for entrada in pila:
                # El tenant real de la fila afectada manda sobre el del actor:
                # un admin (sin tenant propio) puede tocar datos de un hospital
                # puntual y ese evento debe poder filtrarse por ese hospital.
                # Si ni la fila ni el actor traen tenant_id (cuenta hospitalaria
                # sin FK propia, editada por un admin central), se infiere del
                # nombre de la base fisica a la que estaba conectada la sesion.
                tenant_id = (
                    entrada["tenant_hint"]
                    or actor_tenant_id
                    or await tenant_id_por_db_name(db, entrada.get("db_name_hint"))
                )
                db.add(AuditLog(
                    user_id=uuid.UUID(user_id) if user_id else None,
                    user_name=user_name,
                    tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
                    tenant_name=await nombre_de(db, tenant_id),
                    action=entrada["action"],
                    model=entrada["model"],
                    model_id=entrada["model_id"],
                    description=f'{entrada["model"]} {entrada["action"]}',
                    old_values=entrada["old_values"],
                    new_values=entrada["new_values"],
                    ip_address=ip_address,
                ))
            await db.commit()
    except Exception:
        import logging
        logging.getLogger(__name__).exception("No se pudo escribir la auditoria automatica")
