# Guardias hospitalarias

Importes transcritos de los artículos 3–5 del D.S. 232-2017-EF, reproducidos en
el anexo 7 de la [R.J. 000280-2022-MP-FN-JN-IMLCF](https://cdn.www.gob.pe/uploads/document/file/6792759/5883027-r-j-n-000280-2022-mp-fn-jn-imlcf.pdf).
El archivo `IML_280_2022.pdf` conserva la publicación contrastada.

El D.S. establece factores médicos en el artículo 2 y montos en el artículo 3.
Esta implementación utiliza los montos publicados, no recalcula sobre una
remuneración inferida ni añade el antiguo incremento del 55%.
La aplicación del decreto sigue citada en [resoluciones hospitalarias de 2026](https://cdn.www.gob.pe/uploads/document/file/9921114/8095642-n-291-2026-ogess-especializada.pdf?v=1778079960).

Son 288 tarifas: 72 niveles compatibles por cuatro modalidades hospitalarias.
La equivalencia ordinal del tecnólogo usa TME-1…5 del catálogo del ERP y I…V
de la tabla de guardias. Otras profesiones sin equivalencia comprobada y las
escalas SP/SA de técnicos o SP/ST de auxiliares quedan sin tarifa automática.
Los horarios 07–19 y 19–07 son plantillas operativas editables; el estimador
exige correspondencia entre horario y modalidad y rechaza superposiciones.
En establecimientos del primer nivel las plantillas hospitalarias se crean
inactivas. No se implementa una tarifa hospitalaria para guardia comunitaria,
retén ni servicio complementario.

Se cargan los 16 [feriados nacionales 2026](https://www.gob.pe/feriados),
incluyendo [Semana Santa, 2 y 3 de abril](https://elperuano.pe/noticia/291141-semana-santa-2026-en-peru-cuando-sera-el-proximo-fin-de-semana-largo).
No se incluye el 2 de enero: es día no laborable compensable, no feriado nacional.
El estimador usa además los feriados activos registrados por el hospital.
Otros años quedan pendientes de revisar el calendario antes de estimar.

El detalle de creación/revisión/aprobación de roles incluye una estimación
por empleado, fecha y horario, vinculada a la tarifa vigente y su sustento.
Deduplica un mismo horario compartido por varias actividades. Consulta la
asistencia por empleado/fecha/horario e informa de marcaciones completas;
no considera una marcación como certificación de ejecución ni pago devengado.
Los vínculos distintos de 276 quedan pendientes de revisión documental.
El resumen pertenece a un solo rol, no consolida todos los roles del mes.
La programación médica de APP conserva su flujo clínico existente.

Antes de liquidar, RR. HH. debe acreditar ámbito normativo, plaza, régimen,
ejecución, autorizaciones, presupuesto y consolidación mensual. No se genera
planilla ni se garantiza que una tarifa de referencia resuelva cada caso legal.

Reejecución: desde `backend`, `venv\Scripts\python.exe -m scripts.seed_guardias`.
La carga conserva registros existentes; las tarifas con vigencia iniciada se
cierran y sustituyen mediante el mantenimiento existente, no se sobrescriben.
