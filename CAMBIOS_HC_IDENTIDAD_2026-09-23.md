# Historia clínica e identidad del hospital

## Funcionalidad

- Admin → Hospitales → Crear/Editar: logo opcional, vista previa, reemplazo y eliminación. PNG/JPG/WebP hasta 2 MB y 16 megapíxeles; el backend valida el contenido y lo normaliza a PNG de hasta 768 × 768 conservando proporción. Se reutiliza `Tenant.logo_url`; no requiere nueva migración.
- App y SIGARH: accesos con nombre y logo del hospital resuelto por dominio o `?tenant=UUID`, tipografía Poppins, iconos y diseño adaptable. Sin logo se muestran iniciales. Cambiar de acceso y recuperar contraseña conserva el hospital. Hospital inválido o inactivo bloquea el envío del formulario.
- Archivo clínico: descarga autenticada de ficha o HC completa. Incluye identidad institucional, datos del paciente, código de barras, atenciones, resultados, prescripciones, movimientos y evidencia de cierre disponible. El logo institucional aparece en la portada.
- Para DNI válido de ocho dígitos, el número de HC es el DNI. Otros documentos y pacientes NN usan un identificador único. La búsqueda conserva los números anteriores como alias.
- Los cierres muestran profesional, CMP, fecha y verificación SHA-256 de la evidencia registrada. Esto es un cierre interno; no implementa firma digital certificada. Los adjuntos externos se enumeran como referencias, no se incorporan sus archivos al PDF.

## Validación

- `backend/venv/Scripts/python.exe -m pytest tests/unit -q`: 241 pruebas aprobadas y 12 subtests; advertencias existentes por `datetime.utcnow()`.
- Integración `test_hospital_branding.py`: 12 pruebas aprobadas en PostgreSQL aislado `erp_hc_test_20260922`, incluyendo permisos, creación, edición, eliminación y publicación del logo, además de los casos de HC heredados. No ejecutar estas pruebas contra producción.
- Compilación Nuxt de producción en salida separada `.output-hc-validation`.
- Navegador: App/SIGARH a 1440 y 390 píxeles, con logo/sin logo, resolución por dominio y query, conservación del hospital, error de hospital inválido y ausencia de desbordamiento horizontal. Sin errores JavaScript en estas comprobaciones.
- La migración `d2e3f4a5b6c7` se probó desde base vacía y se aplicó a central y hospitales Lima/Reque. Quince historias de Reque adoptaron DNI conservando alias. No se alteraron los UUID ni las evidencias firmadas.

## Operación

- Respaldos de `clinical_records` y `alembic_version` previos a la migración: `backend/var/hc-release-20260922/`. Son respaldos de esas tablas, no de bases completas.
- Salida frontend anterior a HC: `frontend/.output-before-hc-20260922`.
- Identidad desplegada con reinicio de `HisErpBackend` y `HisErpFrontend`; ambos en ejecución. Respaldo frontend previo: `frontend/.output-before-hc-branding-20260923`. Comprobados HTTP 200 en ambos accesos y campo de logo en el endpoint público del backend activo.
- La nueva identidad no crea un logo ficticio para hospitales reales: el administrador debe cargar el archivo institucional.
- Este trabajo no certifica el ERP completo como terminado; los pendientes generales se documentan en `SCAN_ERP_2026-09-22.md`.
