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
import asyncio
import json
import logging
import uuid
from contextvars import ContextVar
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from pathlib import Path

from sqlalchemy import event, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, attributes

# Si escribir en AuditLog falla, el lote se guarda en la tabla
# audit_log_fallback (misma BD central) en vez de perderse. Se eligio una
# tabla de Postgres y no un archivo justamente para poder reclamar filas de
# forma atomica con SELECT ... FOR UPDATE SKIP LOCKED: un asyncio.Lock() de
# Python solo coordina dentro de UN proceso, y backend/worker corren en
# procesos (contenedores) distintos -- con un archivo, uno podia leer el
# archivo, el otro escribir una linea nueva mientras tanto, y el primero
# terminaba reescribiendo el archivo sin esa linea: evento perdido.
#
# Contrapartida honesta: si la BD central entera esta inalcanzable (no solo
# un fallo puntual de la escritura), este fallback TAMPOCO puede escribir
# -- en ese escenario extremo (todo el ERP deja de funcionar, no solo la
# auditoria) se usa como ultimo recurso un archivo plano local, con el mismo
# riesgo de carrera entre procesos que antes, documentado como tal.
_FALLBACK_ARCHIVO_ULTIMO_RECURSO = Path(__file__).resolve().parents[2] / "var" / "audit_fallback_emergencia.jsonl"

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


async def _nombre_de_tenant(db, cache: dict, tenant_id_str: str | None) -> str | None:
    if not tenant_id_str:
        return None
    from app.tenants.hospitales.models import Tenant
    if tenant_id_str not in cache:
        try:
            tenant = await db.get(Tenant, uuid.UUID(tenant_id_str))
            cache[tenant_id_str] = tenant.name if tenant else None
        except (ValueError, TypeError):
            cache[tenant_id_str] = None
    return cache[tenant_id_str]


async def _tenant_id_por_db_name(db, cache: dict, db_name: str | None) -> str | None:
    """Para cuando el objeto auditado no trae tenant_id propio (las cuentas
    de un hospital con base fisica no lo necesitan, la base entera ya es de
    ESE hospital) -- se busca que Tenant tiene esa base fisica registrada
    como la suya."""
    from app.tenants.hospitales.models import Tenant
    if not db_name:
        return None
    if db_name not in cache:
        tenant = await db.scalar(select(Tenant).where(Tenant.database_name == db_name))
        cache[db_name] = str(tenant.id) if tenant else None
    return cache[db_name]


async def _escribir_en_audit_log(pila: list[dict], actor: dict, ip_address: str | None) -> None:
    """Intenta escribir el lote en AuditLog (BD central). Propaga cualquier
    excepcion -- el llamador decide que hacer con un fallo (flush_pending_audits
    lo manda al fallback en disco; el reintento del fallback simplemente lo
    deja para la proxima corrida)."""
    from app.core.database import AsyncSessionLocal
    from app.admin.auditoria.models import AuditLog

    user_id = actor.get("user_id")
    user_name = actor.get("user_name")
    actor_tenant_id = actor.get("tenant_id")
    nombres_cache: dict[str, str | None] = {}
    db_name_cache: dict[str, str | None] = {}

    async with AsyncSessionLocal() as db:
        for entrada in pila:
            # El tenant real de la fila afectada manda sobre el del actor: un
            # admin (sin tenant propio) puede tocar datos de un hospital
            # puntual y ese evento debe poder filtrarse por ese hospital. Si
            # ni la fila ni el actor traen tenant_id (cuenta hospitalaria sin
            # FK propia, editada por un admin central), se infiere del nombre
            # de la base fisica a la que estaba conectada la sesion.
            tenant_id = (
                entrada.get("tenant_hint")
                or actor_tenant_id
                or await _tenant_id_por_db_name(db, db_name_cache, entrada.get("db_name_hint"))
            )
            db.add(AuditLog(
                user_id=uuid.UUID(user_id) if user_id else None,
                user_name=user_name,
                tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
                tenant_name=await _nombre_de_tenant(db, nombres_cache, tenant_id),
                action=entrada["action"],
                model=entrada["model"],
                model_id=entrada["model_id"],
                description=entrada.get("description") or f'{entrada["model"]} {entrada["action"]}',
                old_values=entrada["old_values"],
                new_values=entrada["new_values"],
                ip_address=ip_address,
            ))
        await db.commit()


async def _guardar_en_fallback(pila: list[dict], actor: dict, ip_address: str | None) -> None:
    """Cuando escribir en AuditLog falla, cada entrada del lote se guarda
    como una fila propia en audit_log_fallback (misma BD central), con su
    fecha de ocurrencia real (`ocurrido_en`, no la que tendria si se
    insertara recien en el reintento). Si ni siquiera esto se puede
    escribir (la BD central esta totalmente inalcanzable), cae al archivo
    de emergencia como ultimo recurso."""
    from app.core.database import AsyncSessionLocal
    from app.admin.auditoria.models import AuditLogFallback

    ahora = datetime.utcnow()
    try:
        async with AsyncSessionLocal() as db:
            for entrada in pila:
                db.add(AuditLogFallback(ocurrido_en=ahora, actor=actor, ip_address=ip_address, entrada=entrada))
            await db.commit()
    except Exception:
        logging.getLogger(__name__).exception(
            "No se pudo guardar en audit_log_fallback (la BD central parece inalcanzable), usando archivo de emergencia"
        )
        try:
            # `_id` estable desde que nace el evento (no uno nuevo cada vez
            # que se migra): si el archivo se procesa dos veces -- por una
            # carrera que el lock no alcanzo a evitar, o porque el proceso
            # murio entre migrar e reescribir el archivo -- ese mismo id
            # vuelve a usarse como AuditLogFallback.id, y un choque de clave
            # primaria confirma "ya migrado" en vez de duplicar la fila.
            registros = [
                {**entrada, "_id": str(uuid.uuid4()), "_actor": actor, "_ip_address": ip_address, "_ocurrido_en": ahora.isoformat()}
                for entrada in pila
            ]
            lock_fd = await asyncio.to_thread(_adquirir_lock_emergencia)
            try:
                await asyncio.to_thread(_anexar_registros_emergencia, registros)
            finally:
                await asyncio.to_thread(_liberar_lock_emergencia, lock_fd)
        except Exception:
            logging.getLogger(__name__).critical(
                "PERDIDA DE AUDITORIA: %d eventos no se pudieron escribir en AuditLog, ni en audit_log_fallback, ni en el archivo de emergencia",
                len(pila),
            )
        return

    # Best-effort, cada uno con su propio try: ni la notificacion ni el
    # encolado del reintento deben poder generar un segundo fallo.
    try:
        from app.admin.notificaciones.service import crear_notificacion
        await crear_notificacion(
            "Fallo la auditoría automática",
            f"{len(pila)} evento(s) no se pudieron registrar y quedaron en espera de reintento.",
            nivel="alerta",
        )
    except Exception:
        logging.getLogger(__name__).exception("No se pudo notificar el fallo de auditoria")
    try:
        from workers.tasks import reintentar_auditoria_fallback
        reintentar_auditoria_fallback.delay()
    except Exception:
        # No es grave: el schedule periodico de Celery beat tambien procesa
        # esta cola. Esto solo intenta acelerarlo.
        logging.getLogger(__name__).exception("No se pudo encolar el reintento inmediato de auditoria")


async def guardar_evento_en_fallback(entrada: dict, actor: dict, ip_address: str | None) -> None:
    """Punto de entrada publico para auditoria puntual fuera del listener
    automatico (por ahora, el logout de auth/router.py): cuando ese INSERT
    directo a AuditLog falla, cae a la misma cola de recuperacion que usa
    la auditoria automatica en vez de solo quedar en el log tecnico."""
    await _guardar_en_fallback([entrada], actor, ip_address)


async def flush_pending_audits(ip_address: str | None) -> None:
    """Vacia lo acumulado por before_flush hacia AuditLog (BD central).
    Se llama justo despues de un session.commit() exitoso. Nunca propaga
    excepciones: un fallo al auditar no debe tumbar una operacion de
    negocio que ya se guardo correctamente -- pero tampoco debe perder el
    evento en silencio, por eso el fallback."""
    pila = _pending.get()
    if not pila:
        return
    _pending.set([])
    actor = _actor.get() or {}

    try:
        await _escribir_en_audit_log(pila, actor, ip_address)
    except Exception:
        logging.getLogger(__name__).exception("No se pudo escribir la auditoria automatica, se guarda en fallback")
        await _guardar_en_fallback(pila, actor, ip_address)


async def _recuperar_fila_fallback_bloqueada(db, fila) -> str:
    """Recibe una fila de audit_log_fallback YA bloqueada (FOR UPDATE) por
    el llamador, dentro de la misma sesion/transaccion. Inserta en AuditLog
    reusando el `id` de la fila del fallback: si esta funcion se ejecuta de
    nuevo sobre un evento que ya se inserto (el proceso murio entre el
    INSERT y el DELETE de una corrida anterior), el choque de clave
    primaria confirma que ya existe -- se trata como exito, no como error,
    y solo falta terminar de borrar la fila del fallback."""
    from app.admin.auditoria.models import AuditLog

    # Capturado ANTES de cualquier posible rollback: Session.rollback()
    # expira los atributos de los objetos de la sesion, y en una sesion
    # ASYNC acceder a un atributo expirado dispara una recarga implicita
    # que revienta con MissingGreenlet fuera de un contexto que lo permita
    # (el mismo problema documentado para asignar relaciones ORM tras un
    # flush). Usar esta variable en vez de `fila.id` en cualquier codigo
    # que corra despues de un rollback evita depender de esa garantia.
    fila_id = fila.id
    entrada = fila.entrada
    actor = fila.actor or {}
    actor_tenant_id = actor.get("tenant_id")
    nombres_cache: dict[str, str | None] = {}
    db_name_cache: dict[str, str | None] = {}
    tenant_id = (
        entrada.get("tenant_hint")
        or actor_tenant_id
        or await _tenant_id_por_db_name(db, db_name_cache, entrada.get("db_name_hint"))
    )
    try:
        user_id = actor.get("user_id")
        db.add(AuditLog(
            id=fila.id,
            user_id=uuid.UUID(user_id) if user_id else None,
            user_name=actor.get("user_name"),
            tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
            tenant_name=await _nombre_de_tenant(db, nombres_cache, tenant_id),
            action=entrada["action"],
            model=entrada["model"],
            model_id=entrada["model_id"],
            description=entrada.get("description") or f'{entrada["model"]} {entrada["action"]}',
            old_values=entrada["old_values"],
            new_values=entrada["new_values"],
            ip_address=fila.ip_address,
            created_at=fila.ocurrido_en,
        ))
        await db.flush()
    except IntegrityError:
        # OJO: un IntegrityError NO siempre significa "ya existe" -- tambien
        # lo lanza una violacion NOT NULL, una FK invalida o un CHECK
        # incumplido, y esos son errores REALES sobre el evento, no una
        # repeticion. Tratar cualquier IntegrityError como "ya_estaba" y
        # borrar el respaldo de una vez perdia el evento para siempre en
        # esos casos. Se confirma explicitamente que el AuditLog con este
        # id existe antes de borrar nada.
        await db.rollback()
        from app.core.database import AsyncSessionLocal
        from app.admin.auditoria.models import AuditLogFallback
        async with AsyncSessionLocal() as db2:
            ya_existe = await db2.get(AuditLog, fila_id)
            if not ya_existe:
                logging.getLogger(__name__).exception(
                    "Fallback de auditoria %s: IntegrityError que NO es una repeticion, se conserva", fila_id
                )
                return "sigue_fallando"
            f2 = await db2.get(AuditLogFallback, fila_id)
            if f2:
                await db2.delete(f2)
                await db2.commit()
        return "ya_estaba"
    except Exception:
        await db.rollback()
        logging.getLogger(__name__).exception("Fallback de auditoria %s sigue sin poder recuperarse", fila_id)
        return "sigue_fallando"

    await db.delete(fila)
    await db.commit()
    return "recuperado"


def _ruta_lock_emergencia() -> Path:
    return _FALLBACK_ARCHIVO_ULTIMO_RECURSO.parent / ".audit_fallback_emergencia.lock"


def _adquirir_lock_emergencia():
    """Toma un lock EXCLUSIVO de archivo (fcntl, bloqueante) y devuelve el
    descriptor abierto -- el llamador lo mantiene vivo mientras dure toda
    la seccion critica (que puede incluir trabajo async, como inserts a
    Postgres) y lo libera el mismo con _liberar_lock_emergencia(). Serializa
    TODO acceso al archivo de emergencia (anexar Y migrar) entre procesos
    distintos: sin esto, un lector a mitad de camino de migrar (leer ->
    insertar en Postgres -> reescribir) podia perder una linea que otro
    proceso anexo justo en el medio, porque la reescritura final solo
    conserva lo que se leyo al principio. En una plataforma sin fcntl
    (Windows: donde este archivo de ultimo recurso jamas se ejecuta de
    verdad, el despliegue real corre en contenedores Linux) devuelve None
    y se sigue sin lock -- best-effort, sin perdida de funcionalidad en el
    entorno real."""
    try:
        import fcntl
    except ImportError:
        return None
    _FALLBACK_ARCHIVO_ULTIMO_RECURSO.parent.mkdir(parents=True, exist_ok=True)
    fd = open(_ruta_lock_emergencia(), "a+")
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def _liberar_lock_emergencia(fd) -> None:
    if fd is None:
        return
    import fcntl
    fcntl.flock(fd, fcntl.LOCK_UN)
    fd.close()


def _anexar_registros_emergencia(registros: list[dict]) -> None:
    _FALLBACK_ARCHIVO_ULTIMO_RECURSO.parent.mkdir(parents=True, exist_ok=True)
    with open(_FALLBACK_ARCHIVO_ULTIMO_RECURSO, "a", encoding="utf-8") as f:
        for r in registros:
            f.write(json.dumps(r, default=str, ensure_ascii=False) + "\n")


def _leer_registros_emergencia() -> list[dict]:
    if not _FALLBACK_ARCHIVO_ULTIMO_RECURSO.exists():
        return []
    with open(_FALLBACK_ARCHIVO_ULTIMO_RECURSO, "r", encoding="utf-8") as f:
        return [json.loads(linea) for linea in f if linea.strip()]


def _reescribir_registros_emergencia(pendientes: list[dict]) -> None:
    if pendientes:
        with open(_FALLBACK_ARCHIVO_ULTIMO_RECURSO, "w", encoding="utf-8") as f:
            for r in pendientes:
                f.write(json.dumps(r, default=str, ensure_ascii=False) + "\n")
    elif _FALLBACK_ARCHIVO_ULTIMO_RECURSO.exists():
        _FALLBACK_ARCHIVO_ULTIMO_RECURSO.unlink()


async def _migrar_emergencia_a_tabla() -> int:
    """El archivo de emergencia (_FALLBACK_ARCHIVO_ULTIMO_RECURSO) solo se
    usa cuando ni siquiera se pudo insertar en audit_log_fallback -- es
    decir, la BD central estaba totalmente inalcanzable. Si ahora SI
    responde, cada linea se migra a la tabla (de donde reintentar_fallback_pendiente
    ya sabe recuperar) y se borra del archivo. Antes esto no existia: los
    eventos quedaban atrapados ahi para siempre, invisibles para el
    reintento normal, que solo miraba la tabla.

    El lock se toma UNA sola vez y se mantiene durante TODO el ciclo
    (leer, insertar en Postgres, reescribir): partirlo en varias
    adquisiciones separadas reabre exactamente la ventana que esto intenta
    cerrar, porque un anexo que llegue justo entre "leer" y "reescribir"
    se perderia en la reescritura final de todos modos."""
    from app.core.database import AsyncSessionLocal
    from app.admin.auditoria.models import AuditLogFallback

    lock_fd = await asyncio.to_thread(_adquirir_lock_emergencia)
    try:
        registros = await asyncio.to_thread(_leer_registros_emergencia)
        if not registros:
            return 0

        migrados = []
        pendientes = []
        for registro in registros:
            actor = registro.pop("_actor", {})
            ip_address = registro.pop("_ip_address", None)
            ocurrido_en_str = registro.pop("_ocurrido_en", None)
            id_str = registro.pop("_id", None)
            try:
                ocurrido_en = datetime.fromisoformat(ocurrido_en_str) if ocurrido_en_str else datetime.utcnow()
                async with AsyncSessionLocal() as db:
                    fila = AuditLogFallback(ocurrido_en=ocurrido_en, actor=actor, ip_address=ip_address, entrada=registro)
                    if id_str:
                        fila.id = uuid.UUID(id_str)
                    db.add(fila)
                    try:
                        await db.commit()
                    except IntegrityError:
                        # id_str repetido: esta linea ya se migro en una
                        # corrida anterior que no alcanzo a reescribir el
                        # archivo antes de morir. Ya esta en la tabla --
                        # se descarta del archivo igual, no es un fallo.
                        await db.rollback()
                migrados.append(registro)
            except Exception:
                registro["_id"] = id_str
                registro["_actor"] = actor
                registro["_ip_address"] = ip_address
                registro["_ocurrido_en"] = ocurrido_en_str
                pendientes.append(registro)

        await asyncio.to_thread(_reescribir_registros_emergencia, pendientes)
        return len(migrados)
    finally:
        await asyncio.to_thread(_liberar_lock_emergencia, lock_fd)


async def reintentar_fallback_pendiente(limite: int = 200) -> dict:
    """Reprocesa audit_log_fallback una fila a la vez, cada una con su
    propio SELECT ... FOR UPDATE SKIP LOCKED: si otro proceso (otro worker
    de Celery, o este mismo corriendo dos veces) esta procesando una fila
    en paralelo, este simplemente la salta y toma otra -- sin bloquearse y
    sin poder tocar la misma fila dos veces a la vez. Es lo que garantiza
    que esto sea seguro con mas de un worker, algo que un lock en memoria
    de un solo proceso nunca puede ofrecer entre procesos distintos.

    Antes de procesar la tabla, intenta migrar el archivo de emergencia
    (ver _migrar_emergencia_a_tabla): si la BD central ya volvio, esos
    eventos dejan de estar atrapados fuera del circuito normal."""
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import func
    from app.admin.auditoria.models import AuditLogFallback

    migrados_de_emergencia = await _migrar_emergencia_a_tabla()

    reintentados = 0
    recuperados = 0
    errores = 0
    for _ in range(limite):
        async with AsyncSessionLocal() as db:
            fila = (await db.execute(
                select(AuditLogFallback).with_for_update(skip_locked=True).limit(1)
            )).scalar_one_or_none()
            if fila is None:
                break
            reintentados += 1
            resultado = await _recuperar_fila_fallback_bloqueada(db, fila)
        if resultado in ("recuperado", "ya_estaba"):
            recuperados += 1
        else:
            # "sigue_fallando": la fila queda en audit_log_fallback para el
            # proximo reintento, pero hay que contarla aca -- si no, un
            # evento con un error real (no una repeticion) queda invisible
            # entre "reintentados" y "recuperados" sin ninguna cuenta propia.
            errores += 1

    async with AsyncSessionLocal() as db:
        pendientes = await db.scalar(select(func.count()).select_from(AuditLogFallback))

    return {
        "reintentados": reintentados, "recuperados": recuperados, "errores": errores,
        "pendientes": pendientes, "migrados_de_emergencia": migrados_de_emergencia,
    }
