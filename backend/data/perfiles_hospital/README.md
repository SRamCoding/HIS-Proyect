# Perfiles hospitalarios

Cada hospital conserva sus cuentas y perfiles en su base física. El catálogo de roles del sistema y los módulos contratados se consultan en la base central.

En **SIGARH > Mantenimiento**, crear el Rol del Sistema con panel Hospitalario y tipo de cuenta; crear el Perfil de Usuario seleccionando ese rol; crear el Usuario con ese perfil y el empleado. Toda la gesti?n operativa ocurre en SIGARH. Editar un perfil afecta a todas sus cuentas. Desactivarlo bloquea sus solicitudes posteriores; el servidor vuelve a consultar el perfil, el rol y los módulos habilitados en cada solicitud y renovación de sesión.

El administrador general existente conserva los módulos habilitados del hospital cuando no tiene un perfil asignado. Las demás cuentas requieren un perfil explícito. No se concede acceso utilizando los módulos declarados por un token antiguo.

## Médico

El perfil inicial **Médico de consulta externa** permite:

- `consulta_externa.programacion`: leer programación.
- `consulta_externa.atenciones`: consultar sus citas, antecedentes del paciente de esa cita, triaje, CIE-10; registrar atención y sus documentos clínicos.

Debe vincularse a un empleado activo con profesión `MED`. El guardado y cierre verifican además colegiatura y habilitación mediante las reglas clínicas existentes. Los listados fuerzan el empleado de la cuenta; los identificadores de citas y agendas se verifican antes de responder. Otro identificador de médico en la consulta no permite ampliar el alcance.

El escritorio muestra sus jornadas y citas. Antes de habilitar el enlace para iniciar atención requiere confirmación y triaje registrados. Las citas atendidas permiten consultar la atención. Crear/modificar agendas, confirmar citas, registrar triaje y operar otros módulos se bloquea para este perfil.

Los permisos de consulta externa se separan en programación, atención, confirmación, triaje y agendamiento. Los restantes módulos hospitalarios se asignan a nivel de módulo. El flujo y escritorio específico de enfermería se implementan en la siguiente etapa; no se afirma que ya estén completos.

Los usuarios SIGARH mantienen su mecanismo independiente de perfiles y permisos. Una cuenta hospitalaria no concede acceso a SIGARH.

## Despliegue y verificación

`scripts/migrate_perfiles_hospital.py` verifica la cabeza Alembic, migra central y hospitales activos con base existente, registra los roles básicos y crea el perfil médico sin crear cuentas ni sustituir al administrador.

`scripts/check_perfil_medico_reque.py` prueba los endpoints del médico con un perfil y una cuenta simulados dentro de una transacción revertida. `tests/unit/test_hospital_perfiles.py` verifica separación de operaciones, revocación y lectura de permisos desde BD.

`check_accesos_sigarh_hospital.py` prueba con transacci?n revertida la creaci?n de rol, perfil y usuario desde SIGARH, login App por username, programaci?n propia y bloqueo de modificaci?n de agendas.
