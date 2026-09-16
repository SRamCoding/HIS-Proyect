"""
Informes: capa de reportes de solo lectura.

Ninguno de los 6 submodulos (Reporte por Medico, Reportes de Hospitalizacion,
Gestion Cupos, Gestion Tickets, Visor Colas, Externos) persiste datos propios
-- todos se calculan en vivo sobre tablas reales de otros modulos ya
existentes (Consulta Externa, Hospitalizacion, Emergencia, Admision,
Laboratorio, Imagenologia, Farmacia, Referencias), igual que Formato HIS.
No se duplica ninguna tabla de negocio aqui.
"""
