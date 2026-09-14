# Revisión de roles, perfiles y cuentas — 14/09/2026

La pantalla SIGARH de creación de roles ofrecía `app` por defecto mientras su esquema backend solo acepta `sigarh` y su catálogo contiene módulos SIGARH. Se corrigieron creación y edición para presentar exclusivamente SIGARH y se explican los dos flujos en roles, perfiles y usuarios.

Flujos actuales:

- SIGARH: `RolSistema` → `PerfilUsuario` → `UsuarioSigarh` → permisos SIGARH. El rol delimita módulos y acciones; el perfil selecciona módulos dentro de ese límite.
- Hospitalario: `SystemRole` central → `PerfilHospital` en la base del hospital → `User` con empleado vinculado → panel hospitalario. El médico usa el rol existente `medico`; no debe recrearlo en SIGARH.

Son cuentas de paneles distintos, no credenciales intercambiables. El empleado del hospital conecta la identidad laboral con la programación SIGARH y la atención hospitalaria. No se fusionaron ni borraron registros existentes.

Se corrigieron la selección de todos los módulos de un perfil cuando su rol solo permite submódulos, la limpieza de permisos al cambiar de rol, la obligatoriedad del rol y los selectores de perfiles activos. El catálogo del hospital, en lugar de una intersección exacta con los permisos del operador, determina los módulos configurables; el backend continúa comprobando el hospital y el límite del rol.

Los mensajes de error de las pantallas usan el formato real de la API. Los códigos de roles centrales se normalizan y se comprueba su duplicidad. Los perfiles hospitalarios rechazan nombres existentes en el mismo hospital. Estas comprobaciones de nombres son de aplicación; la creación concurrente de perfiles aún no tiene un índice único por nombre normalizado en BD.

Auditoría de las bases activas Reque y Lima:

- Sin códigos de roles o nombres de perfiles duplicados, comparando espacios y mayúsculas.
- Sin roles SIGARH de otro panel.
- Sin perfiles SIGARH con rol inexistente o de otro panel.
- Sin usuarios SIGARH activos con perfil inexistente o inactivo.
- Una cuenta hospitalaria administrativa y un perfil médico en cada hospital; aún no hay cuenta hospitalaria médica creada.

Se comprobaron los rechazos HTTP 409 de roles y perfiles duplicados contra el servicio real, sin crear registros. La migración no es necesaria para estas correcciones. El formulario hospitalario continúa en Admin → Usuarios; el escritorio específico de enfermería queda para la siguiente etapa.
