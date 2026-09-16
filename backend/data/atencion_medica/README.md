# Atención médica de consulta externa

El sistema conserva un expediente por consulta: enfermedad actual, examen, plan,
diagnósticos y tipos, antecedentes, destino y prestaciones independientes. Un borrador
no completa la cita. El cierre interno requiere el médico programado, una cuenta
hospitalaria vinculada a su empleado activo de profesión MED y habilitación registrada.
No se asignan credenciales ni se presume habilitación de empleados existentes.

Para cerrar se exige el registro de los campos clínicos, antecedentes explícitos,
triaje, CIE-10 activo del hospital, indicaciones de alta cuando corresponde y documentos
de las prestaciones/destinos seleccionados. Son controles de integridad del flujo,
no una evaluación automática de la corrección del juicio clínico. Los antecedentes
pueden documentar desconocimiento o inaplicabilidad expresamente; nunca se rellenan
con “sin antecedentes” automáticamente. Observaciones son opcionales.

El cierre registra usuario, médico, colegiatura, fecha, contenido y SHA-256, y se audita.
El hash permite comparar el contenido conservado; no constituye una firma criptográfica
ni impide a un administrador de BD modificar datos. Las atenciones cerradas se bloquean
para edición y generación de nuevas órdenes; las operaciones posteriores, como alta de
hospitalización y dispensación, mantienen su flujo propio. No existe todavía un flujo
de adendas/correcciones de un expediente cerrado.

La migración no reconstruye antecedentes históricos ni atribuye un firmante a registros
antiguos. Las prestaciones históricas se conservan; los destinos antiguos solo se
normalizan en borradores, nunca en atenciones ya cerradas.

Fuentes oficiales de referencia:

- [NTS 139 y modificatoria](https://repositorio.minsa.gob.pe/handle/MINSA/81631).
- [R.M. 080-2022-MINSA / SIHCE](https://www.gob.pe/institucion/minsa/noticias/584767-minsa-aprueba-documento-tecnico-para-la-implementacion-del-sistema-de-informacion-de-historias-clinicas-electronicas).
- [R.M. 462-2023-MINSA / firmas](https://www.gob.pe/institucion/minsa/normas-legales/4234106-462-2023-minsa).
- [R.M. 188-2026-MINSA / plazos de acreditación](https://www.gob.pe/institucion/minsa/normas-legales/7845808-188-2026-minsa).

Pendientes externos: integración con certificado y proveedor de firma, evaluación
institucional de riesgos de refrendo, acreditación SIHCE e interoperabilidad RENHICE.
También requieren desarrollo los formatos por especialidad/etapa de vida, adendas,
resultados auxiliares y evolución longitudinal. No se afirma cumplimiento integral
MINSA ni acreditación por el hecho de pasar pruebas de software.
