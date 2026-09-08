# Pruebas de Archivo Clínico

Desde `infra/`, con PostgreSQL y el backend en ejecución y las migraciones existentes aplicadas:

```powershell
docker compose exec -T -e RUN_ARCHIVO_DB_TESTS=1 backend python -m unittest discover -s tests -v
```

Las pruebas usan la API mediante ASGI y PostgreSQL real. Cada caso crea hospitales y pacientes sintéticos dentro de una transacción externa. Las sesiones HTTP usan savepoints; incluso los servicios que hacen commit quedan dentro de esa transacción, que se revierte al terminar. No se crean tablas ni se aplican migraciones.

Se comprueban búsqueda, filtros, paginación, digitalización, historial, traslados, atribución del responsable, aislamiento entre hospitales, módulos desactivados y rechazo de tokens de refresco como credenciales de acceso.

No son pruebas de navegador ni de carga concurrente.
