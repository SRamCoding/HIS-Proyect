# Controles del flujo médico ordinario

Fuentes primarias archivadas en este directorio:

- [R.M. 432-2025-MINSA / D.A. 378-MINSA/DGAIN-2025](https://cdn.www.gob.pe/uploads/document/file/8304353/6922180-resolucion-ministerial-n-432-2025-minsa.pdf): numerales 5.15, 5.26, 5.28 y 6.2.1. Jornada ordinaria y consulta externa de hasta cuatro horas continuas; el resto del turno de seis horas corresponde a gestión clínica.
- [R.M. 118-2014-MINSA](https://cdn.www.gob.pe/uploads/document/file/200798/197569_RM118_2014_MINSA.pdf20180926-32492-18oaf1u.pdf): artículos 6, 7, 9, 22 y 23. Guardia ordinaria de hasta doce horas y sesenta horas mensuales; excepciones sujetas a autorización. Restricciones previas y descanso postguardia.
- D.S. 019-83-PCM, artículo 14: descanso postguardia nocturna en el siguiente día laborable. El motor considera laborables lunes a viernes; la evaluación del calendario particular del trabajador requiere ampliación.

## Comportamiento implementado

El envío y aprobación del rol médico requieren jornada mensual documentada (1–150 horas), sustento, vínculo e ingreso, clasificación laboral, colegiatura/habilitación verificada y especialidad compatible validada para generar agenda. Estos datos se verifican por RR. HH.; el ERP no consulta automáticamente la habilitación vigente del CMP ni presume las horas de un contrato CAS.

Se suma el rol actual con los roles pendientes y aprobados del mismo trabajador, incluso de otros servicios y categorías, contando todas sus actividades. Los borradores alternativos no reservan horas. Se bloquean superposiciones y exceso de jornada documentada. Las horas mensuales se imputan al mes de inicio del turno nocturno. Se bloquea consulta externa continua mayor a cuatro horas y se controlan guardias ordinarias y restricciones postguardia. Las horas incompletas no se consideran un exceso: este control de máximo no certifica que se haya completado la jornada laboral del mes.

La misma revisión se aplica al sincronizar, consultar cupos y reservar una cita de origen SIGARH. Una programación que dejó de cumplir las reglas no debe ofrecer nuevas reservas. La sincronización inactiva agendas inválidas y cuenta citas que requieren gestión; no cancela citas existentes automáticamente.

Se cargan horarios editables de seis horas y bloques separados de consulta (cuatro horas) y gestión clínica (dos horas). Las horas de estos ejemplos son configuración operativa del hospital, no horarios universales impuestos por MINSA.

## Alcance y excepciones

Este motor cubre el flujo médico ordinario y bloquea retén, servicios complementarios y ampliaciones excepcionales sin reglas específicas implementadas. No equivale a certificación de cumplimiento integral. Quedan por representar autorizaciones excepcionales, doble empleo y programación externa, calendario laboral individual, exoneraciones de guardia, distribución asistencial de jefaturas (5.20–5.21), emergencias sanitarias, publicación/acto resolutivo, suplencias y normas de residentes/internos. La aprobación informática no sustituye los actos administrativos exigidos por la norma.

Las programaciones manuales sin origen SIGARH todavía pertenecen al flujo independiente de APP. No están incluidas en el cómputo mensual de roles; los controles existentes detectan sus cruces con la agenda del médico. Para trazabilidad normativa, utilizar la agenda procedente del rol aprobado.
