"""Sin schemas de entrada: Seguridad es un consultor de solo lectura sobre las
cuentas del panel hospitalario ('app') que ya administra SIGARH > Mantenimiento
> Usuarios (vincula Empleado + Perfil Hospitalario a cada cuenta). Crear,
editar o desactivar una cuenta sigue siendo trabajo de SIGARH -- duplicar esa
gestión aquí crearía dos lugares editando la misma tabla de usuarios, un
riesgo real de seguridad, no una mejora.

A diferencia de Referencias o Archivo Clínico, este módulo no corresponde a
una Norma Técnica MINSA específica de control de accesos: es gobierno interno
de TI del hospital, respaldado por la Ley N.° 29733 de Protección de Datos
Personales en cuanto a quién puede ver qué información del paciente -- no se
inventa una norma más específica que no existe."""
