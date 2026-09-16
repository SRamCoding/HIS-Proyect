"""Sin schemas de entrada: Auditoría es de solo lectura, reutiliza AuditLog
(app.admin.auditoria.models) que ya llenan Consulta Externa, Laboratorio,
Imagenología, Caja, Hospitalización y Referencias. No hay nada que crear ni
editar aquí -- por diseño, un registro de auditoría no se modifica."""
