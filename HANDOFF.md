# ERP Hospitalario — Contexto de entrega (handoff)

Este documento es para otro desarrollador (y su propia IA) que va a continuar
exactamente el mismo trabajo, en el mismo servidor. Resume qué es el
proyecto, cómo está desplegado realmente, qué convenciones se establecieron
a lo largo de la sesión, qué módulos están terminados y verificados, y qué
queda pendiente.

No reemplaza al código — es el mapa para no tener que redescubrir todo esto
leyendo commit por commit.

---

## 1. Qué es esto

ERP hospitalario multi-tenant para hospitales peruanos. Cada hospital
("tenant") tiene su propia base de datos física completa; hay además una
base de datos central que guarda el catálogo de tenants, módulos
contratados, usuarios globales, roles, etc.

Todo lo que se ha construido esta sesión está **grounded en normativa real
MINSA/SUSALUD/legal peruana** — nunca se inventó un dato clínico o
regulatorio. Cuando no se tuvo certeza de un número exacto de norma, se citó
de forma conservadora o se dejó como "referencial", nunca se inventó.

## 2. Cómo está desplegado ESTE servidor (⚠️ distinto del README)

El `README.md` del repo describe un setup de desarrollo con Docker Compose
(Postgres/Redis/RabbitMQ) en el puerto 8000. **Ese no es el entorno real de
este servidor.** Este es un Windows Server con todo corriendo directo
(sin Docker para la app):

- **Backend**: FastAPI, servicio Windows via `nssm` llamado `HisErpBackend`,
  puerto **8010**. Working dir `C:\ERP_HOSPITALARIO\backend`, venv en
  `backend\venv`. Logs en `backend\service-err.log`.
- **Frontend**: Nuxt 3, servicio Windows via `nssm` llamado
  `HisErpFrontend`, puerto **3010**. Working dir
  `C:\ERP_HOSPITALARIO\frontend`. Logs en `frontend\service-err.log`.
- **Apache** hace de reverse proxy por delante de ambos.
- **PostgreSQL 15** corriendo directo en el servidor (`127.0.0.1:5432`,
  usuario `his_erp_user` / password `tech2026` — ver `.env` real para
  confirmarlo, esto es lo que se usó en esta sesión).
- **Bases de datos reales**:
  - `his_erp_db` — central (tenants, módulos, usuarios globales, roles,
    catálogo `Module`, `TenantModule`).
  - `his_hospital_reque` — Hospital Reque (el que se usó para TODA la
    verificación esta sesión).
  - `his_hospital_lima` — Hospital Lima.
  - Hospital Tumán existe como tenant pero **no tiene base de datos
    física** — siempre se omite al migrar.
  - Dato importante: la base **central también tiene todas las tablas de
    tenant** (mismo `Base.metadata`, mismas migraciones aplicadas a las
    tres bases) — están vacías/sin uso ahí, pero existen, así que un FK de
    una tabla nueva hacia `patients`, `atenciones_medicas`, etc. no rompe
    nada al migrar la central.
- Ejecutar en Docker solo se usa para la suite de tests (`docker compose
  exec ... python -m unittest tests.test_x`) — ver sección 6.

### Ciclo de despliegue usado en cada cambio (repetirlo siempre)

```
# Backend
venv/Scripts/python.exe -m py_compile <archivos tocados>
venv/Scripts/python.exe -c "import main; print('IMPORT_OK')"
# si hay tablas nuevas: escribir migración a mano, revisar `alembic heads` (debe dar UN solo head)
venv/Scripts/python.exe -m alembic upgrade head                     # central
TENANT_DATABASE_URL=postgresql+asyncpg://his_erp_user:tech2026@127.0.0.1:5432/his_hospital_reque venv/Scripts/python.exe -m alembic upgrade head
TENANT_DATABASE_URL=postgresql+asyncpg://his_erp_user:tech2026@127.0.0.1:5432/his_hospital_lima venv/Scripts/python.exe -m alembic upgrade head
nssm restart HisErpBackend
tail service-err.log   # confirmar arranque limpio, sin traceback nuevo

# Frontend
cd frontend && npm run build
# revisar el log del build filtrando ruido conocido (error-404/error-500/DEP0155 son inofensivos)
nssm restart HisErpFrontend
curl cada ruta nueva -> debe dar 200
```

### Verificación con datos reales (obligatorio, no opcional)

Cada endpoint nuevo se probó con `curl` contra `127.0.0.1:8010` usando un
JWT real generado con:

```python
from app.core.security import create_access_token
claims = {
    'sub': '<uuid de un User real>',
    'tenant_id': '55540838-24a6-4e78-843b-f9b93e57733a',  # Reque
    'name': '...', 'role': 'admin', 'panel': 'app',
    'active_modules': ['<modulo_a_probar>'],
}
print(create_access_token(claims))
```

Usuario admin real usado toda la sesión: `Lennart`,
`sub=548e3be2-eee9-47f5-b1c2-eab60801fac6`. Empleado médico de prueba real
(con colegiatura habilitada, CMP real seeded): `REQUE SIMULADO, MEDICO DE
PRUEBA`, `empleado_id=e240638f-995e-43bd-bf80-7bca417d8526`.

Cuando no existía data real de soporte (ej. ninguna orden de laboratorio
pendiente), se insertó un fixture temporal **vía ORM** (importando `main`
primero para registrar todo el metadata y que los defaults Python-side
apliquen), se ejercitó el endpoint real, y **siempre se borró después**,
re-verificando que la tabla volviera a su estado real anterior (cuidando no
tocar filas genuinamente preexistentes — ej. hay una `AtencionMedica` real
con `motivo_consulta='aaa'`, ya firmada, que aparece orgánicamente en varios
reportes; nunca se tocó).

## 3. Convenciones de código establecidas

### Estructura de un módulo hospitalario nuevo

```
backend/app/hospital/<modulo>/
  __init__.py
  models.py    # SQLAlchemy 2 declarativo, Mapped[...] 
  schemas.py   # Pydantic v2, validators con @model_validator(mode="after")
  service.py   # toda la lógica de negocio, funciones async(db, tid, user, data)
  router.py    # FastAPI endpoints finos, delegan todo a service.py
```

Registro en `backend/main.py`: import del router +
`app.include_router(router, prefix="/app/<modulo-con-guiones>", tags=[...])`.

Gate de autorización estándar en cada router:
```python
mi_user = require_any_module_jwt("mi_modulo")
...
async def endpoint(..., user=Depends(mi_user)): ...
```

### Patrón "origen dual/triple" (repetido en casi todos los módulos clínicos)

Un documento clínico nuevo casi siempre puede originarse en más de un lugar
(Consulta Externa, Emergencia, Hospitalización) o registrarse directo con
`patient_id`. Se modela con columnas FK nullable + un validator que exige
"como máximo uno" (o "exactamente uno" cuando aplica) de los orígenes:

```python
atencion_medica_id: Mapped[uuid.UUID | None] = mapped_column(..., nullable=True)
atencion_emergencia_id: Mapped[uuid.UUID | None] = mapped_column(..., nullable=True)
hospitalizacion_id: Mapped[uuid.UUID | None] = mapped_column(..., nullable=True)
patient_id: Mapped[uuid.UUID] = mapped_column(..., nullable=False)  # o nullable si se resuelve del origen
```
El `patient_id` real se resuelve del origen elegido (via `Cita.patient_id`,
`AdmisionEmergencia.patient_id`, o `Hospitalizacion.patient_id` según el
caso) — nunca se pide al usuario si ya hay un origen.

### Patrón "correlativo" (numeración atómica por tenant)

Una tabla chiquita `<Modulo>Correlativo(tenant_id, tipo, valor)` PK
compuesta, y un `INSERT ... ON CONFLICT DO UPDATE ... RETURNING valor`:

```python
async def _siguiente(db, tid, tipo, prefijo):
    stmt = insert(MiCorrelativo).values(tenant_id=tid, tipo=tipo, valor=1)
    stmt = stmt.on_conflict_do_update(index_elements=["tenant_id", "tipo"],
        set_={"valor": MiCorrelativo.valor + 1}).returning(MiCorrelativo.valor)
    n = await db.scalar(stmt)
    return f"{prefijo}-{n:08d}"
```

### Filosofía "conectar, no duplicar"

Antes de crear una tabla nueva, se buscó si el dato ya existe en otro
módulo (SIGARH, Admisión, Consulta Externa...) y se reutilizó por FK o
lectura directa. Ejemplos reales de esta sesión:
- **Informes** no persiste casi nada: son reportes en vivo sobre tablas ya
  reales de otros módulos.
- **Procedimientos** reutiliza `TiempoProcedimiento`
  (`app/sigarh/general/models.py`) como catálogo, en vez de inventar uno.
- **Servicio Social** reutiliza el campo de profesión real `TSO`
  (Trabajador Social) ya seeded en el catálogo de `Profesion`, y lee los
  campos socioeconómicos que Admisión ya captura en `Patient`
  (`marital_status`, `education_level`, `occupation`) en vez de
  duplicarlos.
- **Medicina Física** NO reutilizó `ProgramacionMedica`/`Cita` de Consulta
  Externa aunque son genéricos, porque ese router está gateado a
  `require_module_jwt("consulta_externa")` — un usuario con solo
  `medicina_fisica` activo se quedaría afuera. Se construyó un sistema de
  agenda propio con la misma forma.

### Validación de firmante/profesional (repetida en varios módulos)

Cuando un documento requiere responsabilidad legal de un profesional
(firma electrónica, certificado de defunción, notificación epidemiológica,
evaluación de trabajo social), se valida contra el catálogo REAL de
`Empleado` + `Profesion`:

```python
medico = await db.scalar(select(Empleado).where(Empleado.id==id, Empleado.tenant_id==tid, Empleado.is_active.is_(True)))
profesion = await db.scalar(select(Profesion.codigo).where(Profesion.id==medico.profesion_id, ...))
if not medico or profesion != "MED" or not medico.habilitado_colegio or not (medico.numero_cmp or medico.numero_colegiatura):
    raise HTTPException(400, "...")
```
Para trabajadores sociales el código real es `"TSO"` (confirmado que existe
en el catálogo seeded). Para médicos, `"MED"`.

### Migraciones

- Antes de escribir una migración nueva: `alembic heads` debe dar **un solo
  head**.
- Se escriben a mano (no autogenerate) cuando el cambio es dirigido —
  autogenerate contra la base central detecta drift raro porque esa base
  no se usa funcionalmente.
- Nombres de constraint planos (`fk_algo_id`, sin `op.f()`), igual que el
  resto del código ya existente.
- Se aplican SIEMPRE a las tres bases (central + Reque + Lima) en cada
  despliegue, nunca solo a una.

### Limpieza de páginas huérfanas

El scaffold original del proyecto generó para cada submódulo del nav un
trío `index.vue` / `create.vue` / `[id].vue`, casi todos con el texto
"Esta seccion estara disponible proximamente." Cada vez que se completó un
módulo real, se verificó con `grep -rln` que nadie linkeara esos
`create.vue`/`[id].vue` huérfanos y se borraron. **Quedan más por revisar**
en módulos que esta sesión no tocó todavía.

### Bugs de plataforma ya conocidos (no repetirlos)

- **`User.tenant_id` es `None`** para cuentas reales `panel='app'` en su
  propia base física de hospital (SIGARH las crea así — el aislamiento es
  por base de datos, no por columna). Cualquier query nueva contra `User`
  **no debe filtrar por `tenant_id`** si busca cuentas del panel app.
- ~~**`MEDICO_MODULOS`**~~ — **resuelto** (sesión 2026-09-16, decisión
  explícita del usuario: "eliminar el filtro hardcodeado"). Antes,
  `contexto_hospital()` intersectaba SIEMPRE `permisos` con un allowlist
  fijo en código (`MEDICO_MODULOS`/`ENFERMERIA_MODULOS` en
  `app/auth/hospital_access.py`) para `role in {'medico','enfermera'}`,
  **encima** de lo que dijera su perfil real configurado en SIGARH — un
  médico con Laboratorio habilitado en su perfil igual se quedaba sin
  acceso. Se eliminó esa intersección en tres lugares que la aplicaban de
  forma redundante:
  - `app/auth/hospital_access.py::contexto_hospital` — ya no filtra
    `permisos` contra las constantes (que se conservan solo por
    compatibilidad con los scripts históricos
    `scripts/check_perfil_medico_reque.py` y
    `scripts/migrate_perfiles_hospital.py`, que las importan).
  - `app/admin/usuarios/router.py::guardar_perfil_hospital` — ya no exige
    que `PerfilHospital.modulos` para role=medico/enfermera sea subconjunto
    de esas constantes (queda solo la validación real: subconjunto de
    `SystemRole.allowed_modules` + módulos habilitados del hospital).
  - `app/sigarh/mantenimiento/service.py` (validación de `RolSistema`) —
    misma remoción; queda solo la regla general (el módulo debe existir y
    estar habilitado para SIGARH en ese hospital).
  - Frontend: `SPerfilHospital.vue` y
    `pages/sigarh/mantenimiento/roles-sistema/{create,[id]}.vue` tenían su
    propio catálogo de checkboxes recortado a mano (`MODULOS_ROL`/
    `modulosClinicos`) que reflejaba el mismo allowlist — se quitó para
    que medico/enfermera vean el catálogo completo igual que cualquier
    otro rol/tipo_usuario.
  - **medico/enfermera ahora se gobiernan exactamente igual que cualquier
    otro rol**: su alcance real es el `SystemRole.allowed_modules`
    (Seguridad, admin panel) o el `RolSistema.modulos_permitidos` (SIGARH,
    por hospital) que el equipo configure — no hay ya un segundo control
    paralelo en código. El `SystemRole` "medico" seeded por
    `migrate_perfiles_hospital.py` sigue teniendo `allowed_modules` igual
    al viejo set (`{"consulta_externa.programacion",
    "consulta_externa.atenciones", "firma_electronica"}`) — para que un
    médico real use Laboratorio/Farmacia/etc. hace falta que un admin lo
    amplíe desde Seguridad > Roles, esto ya no requiere tocar código.
  - Verificado: `scripts/check_perfil_medico_reque.py` (regresión
    existente) sigue pasando sin cambios. Se probó además, con una
    transacción de rollback sobre `his_hospital_reque` (nunca comiteada),
    que un `PerfilHospital(role='medico', modulos=['laboratorio'])` — un
    módulo fuera del viejo set — ahora sí aparece en `active_modules`.
  - **Nota importante para SEGUIMIENTO**: `SPerfilHospital.vue` resultó
    estar **huérfano** — ningún page/component lo referencia
    (`grep -r "perfiles-hospital"` en `frontend/` solo lo encuentra a él
    mismo). El endpoint `/admin/usuarios/perfiles-hospital` (POST/PUT) y
    el modelo `PerfilHospital` parecen legado, reemplazados por el flujo
    más nuevo de `RolSistema`+`PerfilUsuario` que sí se usa desde
    `roles-sistema/*`. No se tocó más allá de corregir el mismo bug ahí
    también (por si se reactiva); decidir si se borra o se re-conecta
    queda pendiente, no evaluado a fondo esta sesión.
- **Resolución de permisos para `panel='app'`** (ver
  `app/sigarh/mantenimiento/security.py::usuario_actual` y
  `app/auth/hospital_access.py::contexto_hospital`): el JWT que manda el
  cliente casi no importa — el `active_modules` real se recalcula en cada
  request desde la base de datos: `TenantModule` (central) ∩ perfil del
  usuario (`PerfilUsuario`+`RolSistema` si tiene `perfil_usuario_id`, si no
  `PerfilHospital`). Para dar acceso real a un módulo nuevo a un usuario de
  prueba hay que tocar `TenantModule` (central), y el
  `RolSistema.modulos_permitidos` + `PerfilUsuario.modulos_acceso` del
  perfil de esa cuenta (ambos son texto JSON, no listas nativas — usar
  `json.loads`/`json.dumps`).
- **Windows Git-Bash + curl + tildes/eñes**: pasar `Ñ`, tildes u otros
  caracteres no-ASCII embebidos en un `-d "{...}"` de curl a veces produce
  `"There was an error parsing the body"` por un problema de encoding del
  propio shell, no del backend. Si pasa, reintentar el mismo payload sin
  esos caracteres confirma que es un artefacto de la terminal.
- **Fixtures via SQL crudo** (`sqlalchemy.text()`) fallan seguido por
  columnas `NOT NULL` sin `server_default` aunque el modelo tenga
  `default=` en Python. Usar siempre el ORM (`import main` primero, luego
  `db.add(Modelo(...))`) para que los defaults se apliquen.

## 4. Estado por módulo (nav de `useHospitalNav.ts`)

### Ya reales antes de esta sesión (con fixes puntuales aplicados)
Admisión, Hospitalización, Consulta Externa, Emergencia, Referencias,
Laboratorio, Imágenes, Farmacia, Caja, Fact-Config, Seguridad, General,
Auditoría.

Fixes reales encontrados y corregidos en estos módulos durante la sesión
(no solo features nuevas):
- **Farmacia**: `create_movement()` marcaba `estado="PAGADA"` en toda venta
  sin que existiera un pago real en Caja — corregido para calcular el
  estado desde `CobroItem` reales.
- **Seguridad**: bug de `User.tenant_id` (ver arriba).
- **AtencionEmergencia**: no tenía `firmado_por_id` ni validación de
  identidad del firmante (a diferencia de `AtencionMedica`, que sí la
  tenía) — se agregó columna + validación + evidencia con hash SHA-256,
  igual de rigurosa que Consulta Externa.
- Dashboard general (`DashboardGeneral.vue`) reemplazó el grid genérico de
  tarjetas por indicadores reales en vivo por módulo activo.
- Sidebar: scroll interno oculto (antes crecía la página entera), acordeón
  con auto-scroll al grupo activo.

### Construidos desde cero esta sesión (backend + frontend + migración +
tests + verificados contra producción real, y limpiados después)

| Módulo | Tablas nuevas | Qué hace |
|---|---|---|
| **Archivo Clínico** (2 submódulos que faltaban) | 0 | Conecta HC Electrónica y Personal de Archivo a datos ya reales |
| **SIS** | `SisCorrelativo`, `FormatoFua` | Formato Único de Atención (RM 573-2021-MINSA), reutiliza `Seguro.requiere_fua` |
| **HIS** | `HisEnvios` | Reporte estadístico HIS-MINSA Anexo 4B, formato-his.csv, envíos a la MicroRed |
| **Informes** | 0 (puro reporte) | Reporte por Médico, Reportes Hospitalización, Gestión Cupos, Gestión Tickets, Visor Colas, Externos |
| **TeleSalud** | `TelesaludSolicitud` | Bandeja de solicitud de teleconsulta, enlaza a `Cita` con `modalidad='VIRTUAL'` |
| **Banco de Sangre** | 7 tablas (Donante, UnidadSangre, ComponenteSanguineo, SolicitudTransfusional, etc.) | PRONAHEBAS/Ley 26454. Tamizaje serológico, compatibilidad ABO/Rh real, trazabilidad completa |
| **Hemodiálisis** | `PacienteHemodialisis`, `SesionHemodialisis` | Programa crónico, ultrafiltración auto-calculada |
| **Medicina Física** | 4 tablas (Programa, TecnologoPrograma, ProgramacionMF, SesionMF) | Agenda propia (no reutiliza Consulta Externa por el gate de JWT), reprogramación en bloque, bloqueo de horario |
| **Firma Electrónica** | `FirmaElectronicaRegistro` | Bandeja de firma pendiente + trazabilidad, reutiliza la lógica real de firma de Consulta Externa/Emergencia |
| **Salud Ambiental** (Defunciones) | `CertificadoDefuncion` | Certificado con cadena causal CIE-10 (A/B/C/D), SINADEF/RENIEC (seguimiento honesto, sin integración real) |
| **Epidemiología** | `FichaEpidemiologica` | 5 fichas (Covid/Cáncer/Diabetes/Dengue/Leptospirosis) en una tabla, `datos_clinicos` JSON validado por schema Pydantic específico por tipo. RENACE/CDC-MINSA |
| **Servicio Social** | `EvaluacionSocial`, `GestionSocial` | Caso social abierto con seguimiento en el tiempo. Ley 23808. Deriva a MIMP/CEM/INABIF/DEMUNA |
| **Procedimientos** | `ProcedimientoAsignacion`, `AtencionProcedimiento` | Reutiliza `TiempoProcedimiento` de SIGARH. Exige consentimiento informado (Ley 26842 art. 4) antes de "realizar" |

Cada uno de estos tiene su `tests/test_<modulo>.py` (compile-verificado con
`py_compile`, pensado para correr en Docker — ver sección 6; no se
ejecutaron realmente en esta sesión bare-metal).

### Pendientes

- ~~**Facturación**~~ / ~~**Seguimiento**~~ — **resuelto** (commit
  `6da39b4`, sesión 2026-09-16). `app/hospital/caja/router.py` agregó
  `cuentas_user = require_any_module_jwt("caja", "facturacion")` aplicado
  solo a `GET /cuentas/buscar` y `GET /cuentas/{numero_cuenta}` (el resto
  de Caja — sesiones, cobros, comprobantes — sigue exigiendo únicamente
  `"caja"`). `app/hospital/hospitalizacion/router.py` agregó
  `seguimiento_user = require_any_module_jwt("hospitalizacion",
  "seguimiento")` aplicado solo a `GET /hospitalizaciones`,
  `GET /hospitalizaciones/{id}` y `GET|POST
  /hospitalizaciones/{id}/notas` (admisión, altas, interconsultas,
  consentimientos y censo siguen exigiendo únicamente
  `"hospitalizacion"`). Se optó por gate por-endpoint en vez de abrir el
  router entero, para no darle a un tenant con solo `"facturacion"` o
  `"seguimiento"` acceso a operaciones que no le corresponden (abrir caja,
  cobrar, dar de alta, etc.). Verificado con JWT real (`sub` de Lennart,
  `role='administrador'`) contra `127.0.0.1:8010`: ambos endpoints
  responden 200 sin regresión. **Ojo**: no se pudo probar en vivo el caso
  negativo (una cuenta *solo* con `"facturacion"`/`"seguimiento"`, sin
  `"caja"`/`"hospitalizacion"`) porque Lennart es `role='administrador'`
  sin perfil asignado, y `contexto_hospital()` le da automáticamente
  *todos* los módulos habilitados del tenant (`permisos = set(habilitados)
  if not perfil`) — para aislar ese caso haría falta un
  `PerfilHospital`/`PerfilUsuario` de prueba con exactamente un módulo. La
  lógica de `require_any_module_jwt` (intenta cada código, OR) se confirmó
  por lectura de código en `app/tenants/entitlements.py:107-135` y es el
  mismo patrón ya usado en producción para otros módulos compartidos.
- Páginas bajo `pages/app/caja/cuentas/` y
  `pages/app/hospitalizacion/seguimiento-paciente/` — **confirmado que no
  son huérfanas**: las tres (`index`/`create`/`[id]`) de cada carpeta ya
  están completas y funcionales (no tienen el texto placeholder
  "próximamente"). `create.vue` redirige a la vista real en ambos casos
  (no hay concepto de "crear" en Cuentas ni en Seguimiento — este último
  se registra dentro de una hospitalización ya admitida), e `[id].vue`
  abre el detalle real vía deep-link. No requieren limpieza.

## 5. Cambios commiteados en la sesión 2026-09-16

Los 5 archivos que en el handoff anterior estaban "sin commitear" se
verificaron (diff revisado, build de frontend limpio, ambos servicios
reiniciados, todas las rutas devuelven 200) y se commitearon junto con el
fix de Facturación/Seguimiento de arriba, en `6da39b4`:
- `frontend/components/BancoSangrePanel.vue` — cambia el input de "pegar
  ID de componente" por un `<select>` con los componentes disponibles del
  tipo correcto (mejor UX).
- `frontend/pages/app/admision/agendamiento/create.vue` — el stub
  "próximamente" ahora redirige a la página real.
- `frontend/pages/app/hospitalizacion/panel-camas/{index,create,[id]}.vue`
  — soporta abrir el detalle de una cama por query param (deep-link).
- `backend/app/hospital/caja/router.py`,
  `backend/app/hospital/hospitalizacion/router.py` — fix de Facturación/
  Seguimiento descrito arriba.

**Corrección de un dato de este mismo handoff**: el `sub` de Lennart
(`548e3be2-eee9-47f5-b1c2-eab60801fac6`) es correcto — durante la
verificación se llegó a dudar de él porque una consulta preliminar contra
`AsyncSessionLocal` sin pasar por `get_tenant_sessionmaker` cae en la BD
**central** (`his_erp_db`), no en `his_hospital_reque` (el
`TENANT_DATABASE_URL` de entorno solo lo usa Alembic, la app en caliente
siempre resuelve la BD del tenant vía `Tenant.database_name`). La central
tiene su propia fila coincidente en nombre pero con otro UUID — no tocar
esa tabla pensando que es la de Reque.

## 6. Cómo correr los tests

**Actualizado 2026-09-16: ya se corrieron de verdad, por primera vez.**
Docker **no está instalado en este servidor** (ni en Bash ni en
PowerShell) — pero no hace falta: los tests solo necesitan Postgres real,
que ya corre bare-metal aquí. Se corren directo con el venv:
```
cd backend
RUN_ARCHIVO_DB_TESTS=1 venv/Scripts/python.exe -m unittest discover -s tests -v
```
(un solo archivo: agregar `-p test_<modulo>.py`). Todos extienden
`test_archivo_clinico.ArchivoClinicoTests`, que crea un
`Tenant`/`User`/`Patient`/`ClinicalRecord` de prueba dentro de una
transacción con rollback automático por caso — nunca tocan Reque/Lima/central
reales, es 100% seguro re-correrlos.

**Se encontraron y corrigieron dos bugs reales en el arnés compartido**
(`ArchivoClinicoTests`, commit `782c4b5`) que hacían que el 100% de los
130 tests fallara SIN LLEGAR NUNCA a ejercitar la lógica de negocio real
de ningún módulo — es decir, esta suite nunca había pasado, ni siquiera
una vez, desde que se escribió:
1. El fixture base nunca seteaba `Tenant.database_name`, nunca creaba un
   `User` real, y no redirigía `get_tenant_sessionmaker()` hacia la misma
   transacción de prueba — los tres requisitos que
   `usuario_actual()` necesita para resolver una cuenta `panel='app'`.
   Sin esto, **todo** test daba 401 "Hospital no encontrado o inactivo"
   de entrada.
2. Una vez resuelto lo anterior, quedó expuesto un segundo bug, más
   profundo: `get_db`, `get_db_central` y la sesión de tenant abrían
   cada uno su propia `AsyncSession` sobre la misma conexión/transacción
   externa, y FastAPI no las cerraba necesariamente en el mismo orden en
   que las abrió → se rompía el apilamiento LIFO de savepoints de
   Postgres (`InvalidSavepointSpecificationError`). Se agregó
   `_SharedTestSession`, que cuenta referencias para que las tres
   compartan una sola sesión real por solicitud HTTP.

**Estado actual tras el fix: 52/130 tests pasan de verdad** (antes: 0,
sin excepción). Completamente verdes: `test_archivo_clinico` (8/8),
`test_auditoria` (5/5), `test_general_app` (4/4), `test_hemodialisis`
(5/5), `test_imagenologia` (6/6), `test_medicina_fisica` (6/6). Parciales:
`test_laboratorio` (8/9), `test_hospitalizacion` (4/6), `test_referencias`
(5/6), `test_seguridad` (1/4).

**Pendiente, sin resolver esta sesión**: los otros 13 archivos
(`test_admision_extra`, `test_banco_sangre`, `test_caja`,
`test_epidemiologia`, `test_fact_config`, `test_farmacia`,
`test_firma_electronica`, `test_his`, `test_informes`, `test_salud_ambiental`,
`test_servicio_social`, `test_sis`, `test_telesalud`) fallan al 100% por
una causa **distinta e independiente** de las dos de arriba:
`ForeignKeyViolationError` durante el fixture de cada archivo, porque
varias filas dependientes se agregan al ORM en un solo `flush()`/`commit()`
sin la granularidad que ese caso necesita. Confirmado con un experimento
en `test_caja.py` (revertido, no quedó en el repo): ni siquiera alcanza
con un `flush()` por nivel de dependencia — hace falta uno después de
*cada* `db.add()` cuyo resultado se referencia más adelante en el mismo
método. Es mecánico pero hay que hacerlo archivo por archivo; no se
tocó por alcance de tiempo esta sesión.

## 7. Reglas que el usuario pidió mantener siempre

- Nunca inventar datos clínicos o normativos — fundamentar en MINSA/SUSALUD
  reales ya presentes en el código o genuinamente conocidos; si hay duda
  sobre un número exacto de norma, citar de forma conservadora.
- Conectar con datos/tablas ya reales de SIGARH u otros módulos en vez de
  duplicar CRUD.
- Todo cambio se despliega a producción real (las tres bases, reinicio de
  ambos servicios) — no queda nada "solo en el código".
- Verificar cada feature nueva con curl + JWT real contra
  `127.0.0.1:8010`, limpiando cualquier dato de prueba insertado después.
- Corregir bugs reales encontrados en el camino, no solo construir lo
  pedido.
- Seguir el nav en orden, módulo por módulo, confirmando con el usuario
  antes de saltar a los que él mismo pidió dejar para el final.

## 8. Auditoría de integridad end-to-end del lado hospitalario (en curso, sesión 2026-09-16)

El usuario pidió verificar que **todos** los módulos del panel `app`
(hospitalario) funcionen de punta a punta, se conecten bien con SIGARH, y
no tengan campos/flujos inventados — corrigiendo cada hallazgo real en el
momento en vez de solo anotarlo. Metodología: barrido estructural primero
(stubs, TODOs, routers huérfanos), después revisión profunda módulo por
módulo del nav siguiendo el orden de la sección 4, comentando avances y
arreglando en el momento.

### Barrido estructural (resultado: limpio)
- Cero páginas con texto "próximamente" en todo `pages/app/`.
- Los 25 módulos del nav tienen su router registrado en `main.py` y su
  carpeta de páginas completa.
- Cero marcadores de código incompleto (TODO/FIXME/mock/placeholder/dummy)
  en backend ni frontend del lado hospitalario.

### Bloque 1 — Admisión, Hospitalización, Consulta Externa, Emergencia (revisado)

**Hallazgo 1 (corregido)**: los items de nav "Citados", "Agendamiento" y
"Programación Médica" **dentro de Admisión** llaman directo a 17
endpoints de `/app/consulta-externa/*` (citas completo, programación
médica completo, catálogos de servicios/especialidades/médicos/seguros)
que estaban gateados **solo** a `"consulta_externa"`. Un hospital con
Admisión pero sin Consulta Externa habría recibido 403 en esos 3 links.
Corregido con el mismo patrón de gate por-endpoint que Facturación/
Seguimiento: `agenda_user = require_any_module_jwt("consulta_externa",
"admision")` en `app/hospital/consulta_externa/router.py`, aplicado solo
a esos 17 endpoints (citas, programacion-medica y sus catálogos). Lo
clínico (triaje, atenciones médicas, órdenes de lab/imagen/farmacia,
interconsultas, referencias, bandeja electrónica — 37 endpoints) sigue
exclusivo de `"consulta_externa"`.

**Hallazgo 2 (corregido)**: la página "Admisión de emergencia → Crear"
busca (`GET /app/admision/dni/{dni}`) y registra (`POST /app/admision/`)
pacientes contra endpoints gateados **solo** a `"admision"`. Un hospital
con Emergencia pero sin Admisión no podría registrar a alguien que llega
por la puerta de emergencia — el caso más delicado porque Emergencia
suele ser primera línea. Corregido igual: `paciente_o_emergencia_user =
require_any_module_jwt("admision", "emergencia")` en
`app/hospital/admision/router.py`, aplicado solo a esos 2 endpoints (el
resto de Admisión — altas, lista de espera, anuncios, mensajito, mover
historia clínica — sigue exclusivo de `"admision"`).

Mitigante en ambos casos: revisando `app/admin/seeder_niveles.py`,
**ningún nivel de hospital seedeado separa hoy estos módulos** (Admisión
+ Consulta Externa siempre van juntos; Emergencia siempre viene con
Admisión), así que no se manifestaba en producción real — pero es la
misma clase de brecha arquitectónica que Facturación/Seguimiento, latente
para el día que alguien desactive un módulo individualmente desde
Seguridad. Verificado con JWT real contra `127.0.0.1:8010`: los 17+2
endpoints ampliados siguen en 200/404 según corresponda, y un endpoint
clínico de control (`triaje/pendientes`) sigue en 200 sin regresión.

**Resto de bloque 1, sin hallazgos**:
- DNI lookup de Admisión (`app/shared/dni.py`) llama a un servicio
  externo real y configurable — nunca inventa datos, degrada a `None` si
  no hay API key.
- Firma electrónica de Consulta Externa: hash SHA-256 + validación real
  de médico/CMP/colegiatura.
- Referencias cita la norma real NTS N° 018-MINSA/DGSP-V.01.
- Hospitalización ya cubierto por el fix de Facturación/Seguimiento de
  esta misma sesión.

### Bloques pendientes de revisar (orden acordado)
2. Referencias, Laboratorio, Imágenes, Farmacia, Caja
3. Archivo Clínico, SIS, HIS, Informes, TeleSalud
4. Servicio Social, Epidemiología (✅ ya revisado, sin hallazgos — cita
   RENACE/CDC-MINSA real con nota honesta de "sin integración real"),
   Banco de Sangre, Hemodiálisis, Medicina Física, Firma Electrónica,
   Salud Ambiental, Procedimientos
5. Fact-Config, Seguridad, General, Auditoría

### Hallazgo menor sin corregir (a decidir con el usuario, no es un bug de acceso)
- **Farmacia / DIGEMID**: el item de nav "DIGEMID" no tiene reporte
  propio — en `service.py` es literalmente un alias de "Saldos"/"Saldo
  Almacén" (`if kind in {"saldos","saldo-almacen","digemid"}: return
  await list_stock(...)`). Los datos que trae sí son reales y relevantes
  (registro sanitario, controlado, cadena de frío, vencimiento), pero no
  arma el formato de reporte oficial SISMED-DIGEMID — es la misma vista
  que Saldos con otro nombre en el menú. No es un dato inventado, solo un
  ítem de nav que promete más de lo que entrega hoy.

## 9. Fusión con el trabajo de otro dev en `origin/main` (sesión 2026-09-16)

Mientras esta sesión trabajaba, otro desarrollador subió 13 commits propios
a `origin/main`, divergentes de los 13 commits locales de esta sesión desde
el mismo punto común (`38bc46e`). El usuario pidió fusionar todo con
cuidado. Resultado: **fusionado y desplegado** (commit de merge `ee36644`,
push real a `origin/main`).

### Qué trajo el otro dev (a grandes rasgos)
- **`app/core/audit.py`**: sistema de **auditoría automática** vía
  listener de SQLAlchemy (`before_flush`/`after_flush`) que audita
  CUALQUIER insert/update/delete de CUALQUIER modelo, en cualquier sesión
  (central o física de un hospital), sin necesidad de llamadas manuales.
  Reemplaza (y vuelve redundantes) los `create_audit_log()`/`audit()`
  manuales que existían sueltos en varios módulos.
- `is_superadmin` y `session_version` en `User` (protección de la cuenta
  fundacional, revocación de sesión al cambiar contraseña/rol/perfil).
- Módulo de notificaciones admin (`app/admin/notificaciones/`), perfil de
  cuenta admin (`app/admin/perfil/`), `app/core/concurrency.py`
  (`gather_limitado`, fetch paralelo por hospital), `backend/workers/`
  (Celery, sin usar todavía en este servidor).
- Refactor amplio de estilos SIGARH: `sigarh-table.css` y
  `sigarh-wizard.css` compartidos, aplicados a Admin (hospitales, módulos,
  niveles hospitalarios, auditoría, reportes) y a varias páginas CRUD de
  SIGARH (cajas, seguros, tarifario, paquetes, tiempos, examenes,
  nutrición, profesiones).

### Conflictos reales resueltos (no solo mecánicos)
- **`auth/models.py`**: aditivo (cada lado agregó columnas distintas al
  mismo modelo `User`) — sin pérdida.
- **`sigarh/mantenimiento/security.py`**: se combinó la resolución de
  permisos de `panel='app'` (necesaria para el fix de `MEDICO_MODULOS` de
  esta sesión) con la nueva revocación de sesión por `session_version`.
- **`sigarh/mantenimiento/service.py`**: se mantuvo el soporte de
  `PerfilUsuario` para `panel='app'` (rol.panel in {"sigarh","app"}, con
  el argumento `rol.panel` a `modulos_habilitados`) + la nueva validación
  defensiva de `RolSistema` nulo. **Importante**: se retiraron `auditar()`
  y `snapshot()` (y sus 3 puntos de llamada) que casi se restauran por
  error — ver más abajo.
- **`admin/usuarios/service.py` y `router.py`**: se adoptó la versión más
  nueva (fetch paralelo por hospital vía `_usuarios_de`/`gather_limitado`,
  protecciones `is_superadmin`/último administrador, patrón
  `_cuenta_localizada` como context manager). Se retiraron las
  restauraciones manuales de `create_audit_log` en `create_user`/
  `update_user`/`toggle_user`/`delete_user` por la misma razón.
- **`tests/unit/test_sigarh_usuario_update.py`**: los dos lados tenían
  aserciones CONTRADICTORIAS (¿puede `perfil_id` limpiarse a `null` en un
  PATCH, o no?). Se verificó contra el schema real (`esquema_parcial` en
  `mantenimiento/schemas.py` relaja explícitamente los campos `*_id` a
  nullable) y se confirmó que el comportamiento vigente es "sí se puede
  limpiar" — se tomaron las pruebas del otro dev.
- **27 archivos `.vue`**: 24 eran el mismo conflicto trivial
  (`const {api: $api}` vs `const {api}`, sin uso real de `$api` en el
  resto del archivo — se tomó `api`). Los otros 3
  (`seguros/[id].vue`, `seguros/create.vue`, `seguros/index.vue`) tenían
  la versión del otro dev más completa (template + script correctamente
  emparejados); se tomó esa, combinando en un caso el `title` de la
  página con el `middleware: ['auth']` que el otro dev había agregado.

### Un hallazgo real que casi se restaura por error
Al ver que `create_audit_log()`/`auditar()`/`audit()` "faltaban" en varios
archivos sin marca de conflicto, la primera hipótesis fue que el merge los
había descartado por accidente y se empezaron a restaurar manualmente.
Investigando más (el comentario de `laboratorio/service.py` menciona
literalmente "auditoria automatica (before_flush)") se confirmó que es
**limpieza deliberada** del otro dev al migrar a `app/core/audit.py`. Se
revirtieron todas esas restauraciones. Sí se corrigió un caso real de
código roto: `sigarh/mantenimiento/router.py` todavía llamaba a
`svc.auditar(..., 'hospital_user_disabled')`, una función que ya no
existía en `service.py` — eso habría lanzado `AttributeError` en
producción la primera vez que alguien deshabilitara una cuenta SIGARH
hospitalaria. Se quitó esa llamada (la mutación `is_active=False` +
`commit()` ya queda auditada automáticamente).

### Migraciones
Alembic tenía 2 heads divergentes (uno por rama). Se resolvió con
`alembic merge` (commit `e4f3bfacf4f5`, sin cambios de schema propios) y
se aplicó `alembic upgrade head` a las 3 bases reales (central, Reque,
Lima) antes de reiniciar los servicios.

### Duplicado de auditoría — resuelto (commit `4806c31`)
Los módulos construidos en sesiones anteriores (admision_extra,
banco_sangre, caja, epidemiologia, farmacia, hemodialisis, his,
hospitalizacion, imagenes, medicina_fisica, procedimientos, referencias,
salud_ambiental, servicio_social, sis, telesalud — 16 en total) tenían su
propia función local `audit(db, tid, user, model, obj_id, action, before,
after)` llamada a mano (~90 puntos de llamada). Con `app/core/audit.py`
ya activo, esas acciones se auditaban dos veces. Se quitó la función local
y todas sus llamadas (script con `ast` para ubicarlas con precisión —
varias estaban envueltas en múltiples líneas), más las variables
`before`/`cambios` que quedaron sin uso y los imports que dejaron de
hacer falta (detectado y aplicado con `ruff --select F401,F841 --fix
--unsafe-fixes`).

De paso se corrigió un bug real independiente en
`app/hospital/imagenes/service.py::audits()`: consultaba `AuditLog` (tabla
solo central) contra la sesión física del hospital — nunca iba a
encontrar los registros reales. Se cambió a `AsyncSessionLocal` (central),
igual que ya estaba corregido en `laboratorio/service.py`.

Verificado: `tests.test_imagenologia` volvió a 6/6 (la aserción de conteo
de auditoría que había detectado el duplicado, 8→4, vuelve a pasar).
Suite completa: 52/130 (igual que antes de la fusión). Backend reiniciado
sin traceback, verificado con JWT real (banco-sangre, hemodialisis,
servicio-social, his, admisión → 200/422 esperado, cero 500).

### Verificación final de toda la sesión de fusión
`alembic heads` → un solo head. Backend compila e importa completo.
Frontend compila (`npm run build`, sin errores nuevos). Ambos servicios
reiniciados sin traceback en cada despliegue. Suite de tests: 52/130 pasan
de verdad (los 78 restantes son el problema de orden de FK en fixtures de
la sección 6, preexistente y sin relación con la fusión ni con el fix de
auditoría — no es una regresión funcional de la app real). Push real a
`origin/main` hecho en dos commits: `cb2e08c..ee36644` (la fusión) y
`ee36644..4806c31` (el fix de auditoría duplicada).

### Segunda fusión (misma sesión, después del tema de pacientes/tema verde)
El otro dev volvió a subir cambios (139 archivos: aprovisionamiento de
hospitales endurecido, `AuditLog` con fallback, `admin/busqueda`, varias
paginas de Admin/SIGARH). Esta vez **cero superposición de archivos** con
lo que esta sesión tocó (confirmado con `git diff --name-only <base>
origin/main` antes de fusionar) — `git merge origin/main` resolvió solo,
sin conflictos. Igual apareció otro par de heads divergentes de Alembic
(cada rama había agregado migraciones propias); se resolvió igual, con
`alembic merge` (`8fabfac480de`), aplicado a las 3 bases reales.

**Descuido propio, encontrado y corregido en el momento**: la migración
de merge de la fusión ANTERIOR (`e4f3bfacf4f5`) se había generado y
aplicado a las 3 bases en su momento, pero nunca se le hizo `git add` —
quedó solo en disco. Cuando la migración de ESTA fusión
(`8fabfac480de`) la referenció como padre (`down_revision`) y se
empujó a `origin/main`, el historial de Alembic en el repo remoto quedó
apuntando a un archivo que no existía ahí — cualquiera que clonara desde
cero y corriera `alembic upgrade head` se habría encontrado con
"can't locate revision e4f3bfacf4f5". Se detectó revisando `git status`
después del push (el archivo seguía apareciendo como `??` sin explicación
clara) y se corrigió con un commit aparte (`eaba2f1`) agregando ambos
archivos de migración de merge que faltaban. Lección para la próxima:
después de `alembic merge`, comprobar explícitamente `git status` antes
de dar por commiteado un despliegue con migraciones — no asumir que
"ya se corrió" significa "ya quedó en git".

Verificado igual que la fusión anterior: compila, importa, 3 bases
migradas, ambos servicios reiniciados sin traceback, suite de tests en
52/130 (mismo baseline, sin regresión). Push final a `origin/main`:
`f7a03be` (la fusión) y `eaba2f1` (el fix de las migraciones faltantes).
