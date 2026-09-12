# Plantilla de actividades por hospital

Marco de programación: [R.M. 432-2025-MINSA, D.A. 378-MINSA/DGAIN-2025](https://www.gob.pe/institucion/minsa/normas-legales/6922180-432-2025-minsa).
La agrupación y los códigos TA-/ACT- son decisiones de configuración del ERP;
no representan un nomenclador oficial ni una cartera obligatoria por categoría.

| Tipo | Actividades |
| --- | --- |
| Atención ambulatoria | Consulta externa |
| Atención hospitalaria | Interconsulta, Visita médica, Atención en hospitalización |
| Atención de emergencia | Atención de emergencia |
| Procedimientos diagnósticos y terapéuticos | Procedimientos diagnósticos, Procedimientos terapéuticos |
| Trabajo no asistencial | Gestión, Docencia, Investigación |

Consulta externa requiere consultorio y genera agenda en APP cuando se aprueba
y sincroniza un rol válido. Las otras actividades no generan agenda de consulta
externa. Interconsulta queda en atención hospitalaria en esta plantilla; una
interconsulta ambulatoria necesita configuración específica si el hospital la ofrece.
Los procedimientos son agrupaciones para programación, no códigos de prestaciones
ni autorización para ejecutar cualquier procedimiento.

La plantilla hospitalaria queda activa para categorías II/III; en el primer nivel
las actividades marcadas hospitalarias se crean inactivas. La habilitación definitiva
depende de la cartera y organización del establecimiento, no solo de su categoría.
Se mantienen las opciones existentes de crear y editar tipos y actividades.

Carga desde backend: `venv\Scripts\python.exe -m scripts.seed_actividades`.
La carga conserva los registros existentes y sus modificaciones; también forma
parte de la provisión de nuevos hospitales. No requiere cambios de esquema.
