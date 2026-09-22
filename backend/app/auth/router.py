from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from app.core.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import bcrypt
import secrets
import uuid as uuid_lib

from app.core.database import get_db, get_db_central
from app.core.security import create_access_token, create_refresh_token, verify_token, create_mfa_pending_token
from app.core.config import settings
from app.auth.models import User
from app.sigarh.mantenimiento.models import UsuarioSigarh, PerfilUsuario
from app.auth.schemas import (
    LoginRequest, SessionResponse, RefreshRequest, MfaRequiredResponse, MfaVerifyRequest,
)
from app.core.rate_limit import verificar_limite_login, registrar_intento_fallido, limpiar_intentos
from app.core.refresh_tracking import emitir_jti, reservar_rotacion, olvidar
from app.core.totp import generar_secreto, uri_otpauth, qr_png_base64, verificar_codigo
from app.core.crypto import cifrar, descifrar
import time

router = APIRouter()

# Los tokens viajan SOLO por cookie httpOnly, nunca en el body de la
# respuesta (ver SessionResponse en schemas.py) -- devolverlos tambien en
# JSON anulaba el punto de usar httpOnly: cualquier script en el mismo
# origen podia leerlos ahi sin tocar la cookie para nada. El header
# Authorization: Bearer SI se sigue aceptando en get_current_user y
# _bd_fisica_sigarh (database.py, que NO pasa por get_current_user) como
# via alternativa para quien lo arme por su cuenta (scripts, otro
# cliente), pero el backend ya no es quien se lo entrega.
#
# Nombradas por panel (access_token_admin, access_token_app, ...) en vez de
# un unico "access_token": las cookies son por ORIGEN de navegador, no por
# pestaña. Antes, con el token guardado en sessionStorage, cada pestaña
# tenia su propia sesion independiente (asi se podia estar logueado en
# admin y en el panel de un hospital al mismo tiempo, en pestañas
# distintas). Una sola cookie de sesion, sin distinguir panel, haria que
# loguearse en otro panel en otra pestaña PISE la sesion de la primera
# (misma cookie, mismo nombre, mismo origen). Nombrando la cookie por panel,
# cada una convive con las demas sin pisarse -- ver PANELES_CON_COOKIE.
#
# SameSite="none" + secure=True funciona tanto cruzando puertos en local
# (localhost:3000 -> localhost:8000, ambos considerados "contexto seguro"
# por navegadores modernos aunque sea http://) como en produccion, donde
# Apache expone frontend y backend en el mismo origen (ver HANDOFF.md) --
# "none" es un superconjunto de "lax"/"strict", asi que tambien funciona
# ahi sin condicionar la config por entorno.
PANELES_CON_COOKIE = ("admin", "app", "sigarh", "portal")


def _set_csrf_cookie(response: Response) -> None:
    # NO httponly, y NO por panel: el frontend lo lee por JS y lo reenvia
    # como header X-CSRF-Token en peticiones que mutan estado (patron
    # "doble presentacion" -- ver el middleware de CSRF en main.py). No
    # esta atado a una identidad, solo prueba que el JS que llama corre en
    # este origen, asi que compartirlo entre paneles/pestañas no debilita
    # nada: un atacante cross-site no puede leerlo para reproducir el
    # header sea cual sea el panel activo. Se setea tanto al terminar el
    # login como en la respuesta "MFA requerido" -- el paso de /auth/mfa/
    # verify tambien muta estado y necesita el mismo CSRF ya presente.
    response.set_cookie("csrf_token", secrets.token_urlsafe(32), httponly=False, secure=True, samesite="none",
                         max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400, path="/")


def _set_auth_cookies(response: Response, panel: str, access_token: str, refresh_token: str) -> None:
    response.set_cookie(f"access_token_{panel}", access_token, httponly=True, secure=True, samesite="none",
                         max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, path="/")
    # path="/" -- NO path="/auth". En este servidor el frontend llama a la
    # API bajo el prefijo "/api" (NUXT_PUBLIC_API_URL=/api), que Apache
    # reescribe/quita antes de reenviar al backend (que internamente monta
    # este router en "/auth", ver main.py). Pero el navegador decide a que
    # peticiones adjuntar una cookie mirando la URL que EL VE (".../api/
    # auth/refresh"), no la ruta interna del backend -- una cookie con
    # path="/auth" nunca calza como prefijo de "/api/auth/...", asi que el
    # navegador simplemente la descartaba y jamas la reenviaba. Esto rompia
    # tanto /auth/refresh (sesion "expiraba" sola tras 60 min) como, con el
    # mismo bug en mfa_pending mas abajo, CADA intento de verificar el
    # codigo MFA (por eso "login expirado" en absolutamente todos los
    # intentos, sin importar la duracion del token).
    response.set_cookie(f"refresh_token_{panel}", refresh_token, httponly=True, secure=True, samesite="none",
                         max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400, path="/")
    _set_csrf_cookie(response)


def _clear_auth_cookies(response: Response, panel: str) -> None:
    response.delete_cookie(f"access_token_{panel}", path="/")
    response.delete_cookie(f"refresh_token_{panel}", path="/")


def _json_con_cookies(modelo, response: Response) -> JSONResponse:
    """FastAPI a veces solo conserva UN Set-Cookie del `response` inyectado
    cuando la ruta devuelve un modelo Pydantic plano sin response_model
    declarado (se confirmo empiricamente: `response.raw_headers` trae
    todos los Set-Cookie antes de retornar, pero la respuesta HTTP final
    solo trae el primero). Construir el JSONResponse a mano y copiarle los
    headers directamente evita depender de ese merge interno."""
    final = JSONResponse(content=modelo.model_dump())
    final.raw_headers.extend(h for h in response.raw_headers if h[0] == b"set-cookie")
    return final


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# Subconjunto de modulos con category="app" que tiene sentido mostrar como
# "servicio" en la landing publica de un hospital -- el catalogo completo
# mezcla atencion clinica real (farmacia, emergencia...) con modulos de
# configuracion/back-office (fact_config, firma_electronica, auditoria,
# general, seguridad, informes...) que un visitante nunca deberia ver
# listados como si fueran una prestacion de salud.
MODULOS_SERVICIO_PUBLICO = {
    "admision", "consulta_externa", "emergencia", "hospitalizacion",
    "farmacia", "laboratorio", "imagenes", "telesalud", "medicina_fisica",
    "banco_sangre", "hemodialisis", "procedimientos", "archivo_clinico",
}


@router.get("/tenant-publico/{tenant_id}", summary="Datos públicos de un hospital para su landing")
async def tenant_publico(tenant_id: uuid_lib.UUID, db: AsyncSession = Depends(get_db)):
    """Sin autenticacion, a proposito: la landing de un hospital
    (frontend/pages/index.vue con ?tenant=) se ve ANTES de iniciar sesion,
    asi que necesita poder mostrar el contenido institucional del hospital
    sin exigir un token todavia. Expone solo los campos que el propio
    admin ya carga desde el formulario de edicion pensados para esto (ver
    Tenant.mission/vision/values/address/phone/email, comentados en el
    modelo como "Landing page del hospital" -- el dato ya existia, lo unico
    que faltaba era esta vista publica) mas los nombres de los modulos
    clinicos activos como "servicios". Nunca dominio/schema/database_name
    ni nada que no sea publico de por si. `Module.category == "app"` ya
    separa los modulos hospitalarios (admision, farmacia...) de los de
    SIGARH (RRHH interno), pero adentro de "app" tambien hay modulos que un
    paciente jamas deberia ver en una pagina publica (Auditoria, Fact -
    Config, Firma Electronica, General...). MODULOS_SERVICIO_PUBLICO acota a
    los que sí son un servicio reconocible desde afuera."""
    from sqlalchemy.orm import selectinload
    from app.tenants.hospitales.models import Tenant
    from app.tenants.modulos.models import Module

    result = await db.execute(
        select(Tenant).options(selectinload(Tenant.modules)).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Hospital no encontrado")

    codigos_activos = set(tenant.active_module_codes) & MODULOS_SERVICIO_PUBLICO
    servicios = []
    if codigos_activos:
        modulos = (await db.scalars(
            select(Module).where(
                Module.code.in_(codigos_activos), Module.is_active.is_(True),
            ).order_by(Module.sort_order, Module.name)
        )).all()
        servicios = [{"code": m.code, "name": m.name, "description": m.description} for m in modulos]

    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "is_active": tenant.is_active,
        "hospital_level": tenant.hospital_level,
        "mission": tenant.mission,
        "vision": tenant.vision,
        "values": tenant.values,
        "address": tenant.address,
        "phone": tenant.phone,
        "email": tenant.email,
        "servicios": servicios,
    }


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    ip = request.client.host if request.client else None
    verificar_limite_login(ip, data.email)

    # --- Panel admin: sigue 100% contra la BD central ---
    if data.panel == "admin":
        from sqlalchemy import func as sa_func
        result = await db.execute(
            select(User).where(sa_func.lower(User.email) == data.email.strip().lower())
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.password):
            registrar_intento_fallido(ip, data.email)
            await _log_audit(db, None, "Sistema", None, "login_failed", "User",
                              f"Intento de inicio de sesión fallido: {data.email}",
                              request.client.host if request.client else None)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales incorrectas")

        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuario inactivo")

        if user.panel != "admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes acceso al panel 'admin'")

        # get_admin_user exige panel="admin" Y role="administrador" para
        # cualquier ruta protegida -- si el login solo comprobara el panel,
        # una cuenta admin con otro rol recibiria un token utilizable para
        # nada (403 en cuanto tocara cualquier endpoint real). Se corta aca
        # con un mensaje claro en vez de dejar que lo descubra despues.
        if user.role != "administrador":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Tu cuenta no tiene rol de administrador")

        # MFA (TOTP) obligatorio para TODA cuenta panel=admin: la
        # contraseña sola ya no basta para terminar el login. No se emite
        # ningun token real todavia -- solo una cookie de corta duracion
        # que prueba "paso la contraseña" y habilita /auth/mfa/verify.
        # limpiar_intentos/auditoria de "login" exitoso se hacen reciEn ahi,
        # cuando el segundo factor tambien se confirma.
        if not user.mfa_enabled:
            if user.mfa_secret:
                secreto_plano = descifrar(user.mfa_secret)
            else:
                secreto_plano = generar_secreto()
                user.mfa_secret = cifrar(secreto_plano)  # nunca en claro en la BD
                await db.commit()
            uri = uri_otpauth(secreto_plano, user.email)
            response.set_cookie(
                # max_age debe coincidir con la duracion real del JWT que
                # create_mfa_pending_token emite para "setup" (15 min, ver
                # security.py) -- si la cookie expira antes que el token, el
                # navegador la descarta y el usuario ve "sesion vencida"
                # aunque el token en si todavia fuera valido.
                # path="/" -- NO path="/auth": ver la nota larga en
                # _set_auth_cookies() mas arriba. Con path="/auth" el
                # navegador NUNCA reenviaba esta cookie (el frontend llama
                # a "/api/auth/mfa/verify", que no matchea el prefijo
                # "/auth"), asi que /auth/mfa/verify fallaba con "sesion
                # expirada" en el 100% de los intentos, sin importar cuanto
                # tardara el usuario en escribir el codigo.
                "mfa_pending", create_mfa_pending_token(str(user.id), "setup"),
                httponly=True, secure=True, samesite="none", max_age=15 * 60, path="/",
            )
            _set_csrf_cookie(response)
            return _json_con_cookies(MfaRequiredResponse(
                mfa_setup=True, otpauth_uri=uri, qr_png_base64=qr_png_base64(uri), secret=secreto_plano,
            ), response)

        response.set_cookie(
            "mfa_pending", create_mfa_pending_token(str(user.id), "verify"),
            httponly=True, secure=True, samesite="none", max_age=5 * 60, path="/",
        )
        _set_csrf_cookie(response)
        return _json_con_cookies(MfaRequiredResponse(mfa_setup=False), response)

    # --- Paneles app / sigarh / portal: requieren hospital resuelto por header ---
    from app.core.tenant_db import get_tenant_by_id, tenant_session

    raw_tenant = request.headers.get("X-Tenant-ID")
    if raw_tenant:
        try:
            tenant_id = uuid_lib.UUID(raw_tenant)
        except ValueError:
            raise HTTPException(400, "X-Tenant-ID inválido")
        tenant = await get_tenant_by_id(tenant_id)
    else:
        from app.tenants.hospitales.service import get_tenant_by_domain
        host = (request.headers.get("host") or "").split(":")[0]
        tenant = await get_tenant_by_domain(db, host)

    if not tenant or not tenant.database_name:
        raise HTTPException(404, "Hospital no encontrado")

    async with tenant_session(tenant.database_name) as tdb:
        if data.panel == "sigarh":
            from sqlalchemy import func, or_
            from app.sigarh.mantenimiento.security import contexto_sigarh
            identifier = data.email.strip().lower()
            matches = (await tdb.scalars(select(UsuarioSigarh).where(or_(
                func.lower(UsuarioSigarh.email) == identifier,
                func.lower(UsuarioSigarh.username) == identifier,
            )).limit(2))).all()
            if len(matches) != 1 or not verify_password(data.password, matches[0].password):
                registrar_intento_fallido(ip, data.email)
                raise HTTPException(401, "Credenciales incorrectas o identificador ambiguo")
            limpiar_intentos(ip, data.email)
            token_data = await contexto_sigarh(tdb, matches[0], hospital=tenant)
            token_data["tenant_id"] = str(tenant.id)
            return _respuesta_sesion(token_data, response)

        from sqlalchemy import func, or_
        identifier = data.email.strip().lower()
        matches = (await tdb.scalars(select(User).where(or_(func.lower(User.email) == identifier,
            func.lower(User.username) == identifier)).limit(2))).all()
        user = matches[0] if len(matches) == 1 else None

        if not user or not verify_password(data.password, user.password):
            registrar_intento_fallido(ip, data.email)
            await _log_audit(db, None, "Sistema", str(tenant.id), "login_failed", "User",
                              f"Intento de inicio de sesión fallido: {data.email}",
                              request.client.host if request.client else None)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales incorrectas")

        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuario inactivo")

        if user.panel != data.panel:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"No tienes acceso al panel '{data.panel}'")

        limpiar_intentos(ip, data.email)
        await _log_audit(db, str(user.id), user.name, str(tenant.id), "login", "User",
                          "Inicio de sesión", request.client.host if request.client else None)

        from app.tenants.hospitales.models import TenantModule
        mods_result = await db.execute(
            select(TenantModule).where(
                TenantModule.tenant_id == tenant.id,
                TenantModule.is_active == True
            )
        )
        active_modules = [m.module_code for m in mods_result.scalars().all()]

        if user.panel == "app":
            from app.auth.hospital_access import contexto_hospital, validar_rol_hospital, limitar_por_rol
            if user.perfil_usuario_id:
                return _respuesta_sesion(await contexto_hospital(tdb, user, tenant, set(active_modules)), response)
            rol = await validar_rol_hospital(db, user.role)
            return _respuesta_sesion(limitar_por_rol(await contexto_hospital(tdb, user, tenant, set(active_modules)), rol), response)

        token_data = {
            "sub": str(user.id), "email": user.email, "name": user.name,
            "role": user.role, "panel": user.panel, "tenant_id": str(tenant.id),
            "active_modules": active_modules, "session_version": user.session_version,
        }
        return _emitir_tokens(token_data, response)


@router.post("/mfa/verify", response_model=SessionResponse)
async def mfa_verify(
    request: Request,
    response: Response,
    data: MfaVerifyRequest,
    db: AsyncSession = Depends(get_db_central),
):
    pending = request.cookies.get("mfa_pending")
    payload = verify_token(pending) if pending else None
    if not payload or payload.get("type") != "mfa_pending":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión de verificación expirada; vuelve a iniciar sesión")

    try:
        uid = uuid_lib.UUID(str(payload.get("sub")))
    except (ValueError, TypeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión de verificación inválida")

    user = await db.get(User, uid)
    if not user or not user.is_active or not user.mfa_secret:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Cuenta no encontrada o inactiva")

    ip = request.client.host if request.client else None
    # Mismo limitador que el login con contraseña: un codigo TOTP de 6
    # digitos son solo 1 millon de combinaciones, probarlo sin limite
    # equivaldria a no tener MFA en absoluto.
    verificar_limite_login(ip, user.email)
    if not verificar_codigo(str(user.id), descifrar(user.mfa_secret), data.code):
        registrar_intento_fallido(ip, user.email)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Código incorrecto")
    limpiar_intentos(ip, user.email)

    if payload.get("purpose") == "setup" and not user.mfa_enabled:
        user.mfa_enabled = True
        await db.commit()

    await _log_audit(db, str(user.id), user.name, None, "login", "User",
                      "Inicio de sesión", ip)

    token_data = {
        "sub": str(user.id), "email": user.email, "name": user.name,
        "role": user.role, "panel": user.panel, "tenant_id": None,
        "active_modules": [], "session_version": user.session_version,
    }
    # ANTES de _emitir_tokens, no despues: _emitir_tokens construye la
    # respuesta final (_json_con_cookies) copiando en ese momento los
    # Set-Cookie ya presentes en `response` -- borrar mfa_pending despues
    # mutaba un objeto que la respuesta ya devuelta no referenciaba para
    # nada, asi que la cookie nunca se borraba de verdad.
    # path debe coincidir EXACTAMENTE con el path usado al crearla (path="/"
    # mas arriba) -- name+path identifican la cookie; borrar con un path
    # distinto no la borra, crea logicamente "otra" instruccion que el
    # navegador ignora porque no encuentra una cookie con ese path.
    response.delete_cookie("mfa_pending", path="/")
    return _emitir_tokens(token_data, response)


@router.post("/refresh", response_model=SessionResponse)
async def refresh_token(
    request: Request,
    response: Response,
    data: RefreshRequest = RefreshRequest(),
    db: AsyncSession = Depends(get_db),
):
    refresh_token_str = data.refresh_token
    if not refresh_token_str and data.panel in PANELES_CON_COOKIE:
        refresh_token_str = request.cookies.get(f"refresh_token_{data.panel}")
    payload = verify_token(refresh_token_str) if refresh_token_str else None

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado"
        )

    # Limite absoluto de sesion: session_started_at viaja intacto desde el
    # login original en cada refresh sucesivo (ver _emitir_tokens), asi que
    # no importa cuantas veces se haya refrescado -- si ya paso el maximo,
    # se corta y hay que volver a autenticarse con contraseña.
    inicio = payload.get("session_started_at")
    if inicio and time.time() - inicio > settings.SESSION_MAX_DURATION_HOURS * 3600:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "La sesión alcanzó su duración máxima; vuelve a iniciar sesión")

    # sid identifica la CADENA de renovaciones de esta sesion en particular
    # (un uuid fijado en el login original, ver _emitir_tokens), no la
    # cuenta -- asi loguearse en un segundo dispositivo no pisa el
    # seguimiento de reuso de la primera sesion. Tokens de antes de este
    # cambio no traen sid: se cae al user_id como sid heredado en vez de
    # rechazarlos de golpe.
    sid = payload.get("sid") or str(payload.get("sub"))

    # Reuso de un refresh token ya rotado: alguna copia vieja del token
    # (robada, o quedada en otra pestaña/dispositivo desincronizado) se esta
    # usando despues de que ya se emitio uno mas nuevo. No hay forma de
    # saber cual copia es la legitima, asi que se revocan TODAS las sesiones
    # de la cuenta -- _revocar_sesion_actual ya sabe resolver donde vive
    # (central o BD del hospital) a partir del propio payload.
    #
    # nuevo_jti se genera y RESERVA aca, antes de cualquier `await` (ver
    # reservar_rotacion): si el chequeo y el registro estuvieran separados
    # por las consultas a la BD de usuario_actual() de abajo, dos
    # renovaciones concurrentes con el mismo token viejo podrian pasar
    # ambas el chequeo antes de que cualquiera se registrara, y una
    # terminaria pisando a la otra sin que nadie detectara el reuso.
    nuevo_jti = str(uuid_lib.uuid4())
    if not reservar_rotacion(sid, payload.get("jti"), nuevo_jti):
        await _revocar_sesion_actual(payload)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión revocada por uso indebido del token; vuelve a iniciar sesión")

    from app.sigarh.mantenimiento.security import usuario_actual
    token_data = await usuario_actual(db, payload)
    token_data["session_started_at"] = inicio
    # contexto_hospital/contexto_sigarh (paneles app/sigarh) arman
    # token_data desde cero, sin heredar del payload original -- sin esto,
    # sid cambiaria en cada refresh para esos dos paneles y el seguimiento
    # de reuso de arriba nunca encontraria una coincidencia real.
    token_data["sid"] = sid
    if token_data.get("auth_source") != "sigarh" and token_data.get("panel") != "app":
        from app.tenants.hospitales.models import TenantModule
        active_modules = []
        if token_data.get("tenant_id"):
            import uuid
            active_modules = list((await db.scalars(select(TenantModule.module_code).where(
                TenantModule.tenant_id == uuid.UUID(token_data["tenant_id"]), TenantModule.is_active.is_(True),
            ))).all())
        token_data["active_modules"] = active_modules
    return _respuesta_sesion(token_data, response, jti=nuevo_jti)


def _respuesta_sesion(token_data, response: Response, jti: str | None = None):
    claims = {k: v for k, v in token_data.items() if k not in {"exp", "type", "iat", "nbf", "jti"}}
    return _emitir_tokens(claims, response, jti=jti)


def _emitir_tokens(claims: dict, response: Response, jti: str | None = None) -> JSONResponse:
    claims.setdefault("session_started_at", time.time())
    claims.setdefault("sid", str(uuid_lib.uuid4()))
    access_token = create_access_token(claims)
    # `jti` viene ya reservado atomicamente cuando esto se llama desde un
    # refresh (ver reservar_rotacion en refresh_token()) -- si se generara
    # OTRO aca, no coincidiria con el que quedo reservado, y el PROXIMO
    # refresh de esta misma sesion se rechazaria como reuso de su propio
    # token legitimo. Al loguearse (sin reserva previa) queda None y
    # create_refresh_token genera uno nuevo por su cuenta.
    refresh_token_str = create_refresh_token(claims, jti=jti)
    nuevo_payload = verify_token(refresh_token_str) or {}
    emitir_jti(claims["sid"], nuevo_payload.get("jti"))
    _set_auth_cookies(response, claims["panel"], access_token, refresh_token_str)
    token_response = SessionResponse(user={"id": claims["sub"], **claims})
    # Se devuelve como JSONResponse construido a mano (no el modelo
    # Pydantic plano) por la misma razon que _json_con_cookies: en rutas
    # sin (o con) response_model, FastAPI a veces solo conserva UN
    # Set-Cookie del `response` inyectado cuando hay mas de uno -- aca
    # siempre hay tres (access_token_<panel>, refresh_token_<panel>,
    # csrf_token), asi que este bug es determinante, no cosmetico.
    return _json_con_cookies(token_response, response)


async def _revocar_sesion_actual(user: dict) -> bool:
    """Revoca (incrementa session_version) la cuenta de la sesion ACTUAL.

    A diferencia de _cuenta_localizada (pensada para cuando un admin busca
    una cuenta por id sin saber donde vive, y por eso recorre cada hospital
    con base fisica propia), el propio JWT de la sesion YA trae panel,
    tenant_id y auth_source resueltos y validados -- no hay motivo para que
    un logout tenga que barrer TODOS los hospitales, ni para que uno ajeno,
    caido o lento, pueda demorar o afectar el logout de otra cuenta.

    El incremento se hace con un UPDATE ... SET session_version =
    session_version + 1 (calculado en el propio SQL), no leyendo el valor
    en Python y sumando 1 antes de guardar: asi el commit de un logout
    concurrente con un cambio de contraseña o un login no puede "perder"
    el incremento del otro.

    Devuelve True solo si una fila fue efectivamente actualizada."""
    from app.core.database import AsyncSessionLocal

    try:
        uid = uuid_lib.UUID(str(user["sub"]))
    except (ValueError, TypeError, KeyError):
        return False

    panel = user.get("panel")
    tenant_id_str = user.get("tenant_id")

    if panel == "admin" or not tenant_id_str:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                update(User).where(User.id == uid).values(session_version=User.session_version + 1)
            )
            await db.commit()
        if result.rowcount > 0:
            olvidar(user.get("sid") or str(uid))
            return True
        return False

    try:
        tenant_uuid = uuid_lib.UUID(str(tenant_id_str))
    except (ValueError, TypeError):
        return False

    from app.tenants.hospitales.models import Tenant
    from app.core.tenant_db import get_tenant_sessionmaker
    async with AsyncSessionLocal() as db:
        hospital = await db.get(Tenant, tenant_uuid)
    if not hospital or not hospital.database_name:
        return False

    TenantSession = get_tenant_sessionmaker(hospital.database_name)
    async with TenantSession() as tdb:
        if panel == "sigarh" or user.get("auth_source") == "sigarh":
            result = await tdb.execute(
                update(UsuarioSigarh).where(UsuarioSigarh.id == uid)
                .values(session_version=UsuarioSigarh.session_version + 1)
            )
        else:
            result = await tdb.execute(
                update(User).where(User.id == uid).values(session_version=User.session_version + 1)
            )
        await tdb.commit()
    if result.rowcount > 0:
        olvidar(user.get("sid") or str(uid))
        return True
    return False


async def _log_audit_seguro(
    user_id: str | None, user_name: str | None, tenant_id: str | None, action: str,
    model: str | None = None, description: str | None = None, ip_address: str | None = None,
) -> None:
    """Como _log_audit, pero en su PROPIA sesion (nunca la que uso la
    operacion que se esta auditando) y sin propagar sus propios errores.

    _revocar_sesion_actual y el registro de auditoria del logout son dos
    resultados independientes: un fallo al escribir el evento de auditoria
    no debe convertir una revocacion ya confirmada en una respuesta de
    error, y si la revocacion fallo porque una sesion quedo en un estado
    invalido tras un commit fallido, reusar esa misma sesion para el
    intento de auditoria solo produce un segundo error que tapa al primero
    y deja sin registrar el evento.

    Si ni siquiera este intento directo funciona, el evento cae a la misma
    cola de recuperacion (audit_log_fallback) que usa la auditoria
    automatica -- antes se quedaba solo en el log tecnico, invisible y sin
    forma de recuperarlo."""
    from app.core.database import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as audit_db:
            await _log_audit(audit_db, user_id, user_name, tenant_id, action,
                             model=model, description=description, ip_address=ip_address)
    except Exception:
        import logging
        logging.getLogger(__name__).exception(
            "No se pudo registrar el evento de auditoria de logout, se guarda en fallback"
        )
        from app.core.audit import guardar_evento_en_fallback
        entrada = {
            "action": action, "model": model, "model_id": None,
            "old_values": None, "new_values": {"description": description} if description else None,
            "tenant_hint": tenant_id, "db_name_hint": None,
        }
        actor = {"user_id": user_id, "user_name": user_name, "tenant_id": tenant_id}
        await guardar_evento_en_fallback(entrada, actor, ip_address)


@router.post("/logout")
async def logout(request: Request, response: Response, user=Depends(get_current_user)):
    if user.get("panel") in PANELES_CON_COOKIE:
        _clear_auth_cookies(response, user["panel"])
    # session_version sube al cerrar sesion para que el token que quedo en el
    # navegador (o una copia filtrada) deje de servir de inmediato -- antes
    # solo pasaba para SIGARH y, ademas, solo si esa cuenta vivia en la BD
    # central: con hospital de base fisica propia (el caso mas comun) la
    # cuenta no se encontraba ahi y la revocacion no hacia nada.
    try:
        revocado = await _revocar_sesion_actual(user)
    except Exception:
        import logging
        logging.getLogger(__name__).exception("No se pudo revocar la sesion de %s", user.get("sub"))
        revocado = False

    modelo = "UsuarioSigarh" if user.get("auth_source") == "sigarh" else "User"
    ip = request.client.host if request.client else None
    if not revocado:
        # No se puede afirmar que la sesion quedo invalidada del lado del
        # servidor -- responder 200 igual (como antes) dejaba creer que el
        # token viejo ya no sirve cuando en realidad puede seguir siendo
        # valido hasta que expire. En un ERP hospitalario eso es
        # inaceptable: se devuelve error explicito para que el cliente lo
        # sepa (aunque de todas formas descarte el token localmente).
        await _log_audit_seguro(user.get("sub"), user.get("name"), user.get("tenant_id"), "logout_fallido",
                                model=modelo,
                                description="No se pudo confirmar la revocación de la sesión en el servidor",
                                ip_address=ip)
        raise HTTPException(500, "No se pudo cerrar la sesión de forma segura en el servidor. Intenta nuevamente.")

    await _log_audit_seguro(user.get("sub"), user.get("name"), user.get("tenant_id"), "logout",
                            model=modelo,
                            description="Cierre de sesión", ip_address=ip)
    return {"ok": True}


async def _log_audit(
    db: AsyncSession,
    user_id: str | None,
    user_name: str | None,
    tenant_id: str | None,
    action: str,
    model: str | None = None,
    description: str | None = None,
    ip_address: str | None = None,
) -> None:
    import uuid
    from app.admin.auditoria.models import AuditLog

    log = AuditLog(
        user_id=uuid.UUID(user_id) if user_id else None,
        user_name=user_name,
        tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
        action=action,
        model=model,
        description=description,
        ip_address=ip_address,
    )
    db.add(log)
    await db.commit()
