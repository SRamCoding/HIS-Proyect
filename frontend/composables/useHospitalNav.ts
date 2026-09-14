// frontend/composables/useHospitalNav.ts
export const useHospitalNav = () => {
  const authStore = useAuthStore()
  const route = useRoute()

  const tenantId = computed(() => route.query.tenant as string || '')
  const link = (path: string) => {
    const separator = path.includes('?') ? '&' : '?'
    return `${path}${separator}tenant=${tenantId.value}`
  }
  const activo = (path: string) => ({ 'nav-active': route.path === path })
  const tiene = (code: string) => authStore.user?.active_modules?.includes(code) ?? false
  const tieneAlguno = (codes: string[]) => codes.some(c => tiene(c))

  const grupos = computed(() => [
    {
      label: 'Admisión',
      modulo: 'admision',
      icon: 'i-heroicons-user',
      items: [
        { label: 'Citados', path: '/app/admision/citados', icon: 'i-heroicons-calendar' },
        { label: 'Pacientes', path: '/app/admision/pacientes', icon: 'i-heroicons-user' },
        { label: 'Altas', path: '/app/admision/altas-pacientes', icon: 'i-heroicons-arrow-right-on-rectangle' },
        { label: 'Agendamiento', path: '/app/admision/agendamiento', icon: 'i-heroicons-calendar-days' },
        { label: 'Anuncios', path: '/app/admision/anuncios', icon: 'i-heroicons-speaker-wave' },
        { label: 'Programacion Medica', path: '/app/admision/programacion-medica', icon: 'i-heroicons-clipboard-document-list' },
        { label: 'Lista Espera', path: '/app/admision/lista-espera', icon: 'i-heroicons-clock' },
        { label: 'Mensajito', path: '/app/admision/mensajito', icon: 'i-heroicons-paper-airplane' },
      ]
    },
    {
      label: 'Hospitalizacion',
      modulo: 'hospitalizacion',
      icon: 'i-heroicons-building-office-2',
      items: [
        { label: 'Hospitalizaciones', path: '/app/hospitalizacion/hospitalizaciones', icon: 'i-heroicons-building-office-2' },
        { label: 'Panel de Camas', path: '/app/hospitalizacion/panel-camas', icon: 'i-heroicons-home' },
        { label: 'Seguimiento Paciente', path: '/app/hospitalizacion/seguimiento-paciente', icon: 'i-heroicons-magnifying-glass-circle' },
        { label: 'Censo Diario', path: '/app/hospitalizacion/censo-diario', icon: 'i-heroicons-clipboard-document' },
        { label: 'Interconsultas', path: '/app/hospitalizacion/interconsultas', icon: 'i-heroicons-arrow-path-rounded-square' },
        { label: 'Consentimientos Inf.', path: '/app/hospitalizacion/consentimientos', icon: 'i-heroicons-check-badge' },
      ]
    },
    {
      label: 'Consulta Externa',
      modulo: 'consulta_externa',
      icon: 'i-heroicons-clipboard-document-check',
      items: [
        { label: 'Citas por Confirmar', path: '/app/consulta-externa/citas-por-confirmar', icon: 'i-heroicons-clock' },
        { label: 'Registro de Triaje', path: '/app/consulta-externa/triaje', icon: 'i-heroicons-heart' },
        { label: 'Registro de atenciones', path: '/app/consulta-externa/atenciones-medicas', icon: 'i-heroicons-clipboard-document-check' },
        { label: 'Ficha Covid', path: '/app/consulta-externa/ficha-covid', icon: 'i-heroicons-document-text' },
        { label: 'Calendario Medico', path: '/app/consulta-externa/calendario-medico', icon: 'i-heroicons-calendar-days' },
        { label: 'Bandeja electronica', path: '/app/consulta-externa/bandeja-electronica', icon: 'i-heroicons-inbox' },
      ]
    },
    {
      label: 'Emergencia',
      modulo: 'emergencia',
      icon: 'i-heroicons-exclamation-triangle',
      items: [
        { label: 'Admisión de emergencia', path: '/app/emergencia/admisiones', icon: 'i-heroicons-exclamation-triangle' },
        { label: 'Atenciones', path: '/app/emergencia/atenciones', icon: 'i-heroicons-clipboard-document-check' },
        { label: 'ObservaciÃ³n / HospitalizaciÃ³n', path: '/app/emergencia/observacion', icon: 'i-heroicons-building-office-2' },
        { label: 'Interconsultas', path: '/app/emergencia/interconsultas', icon: 'i-heroicons-arrow-path-rounded-square' },
        { label: 'Referencias', path: '/app/emergencia/referencias', icon: 'i-heroicons-arrow-top-right-on-square' },
      ]
    },
    {
      label: 'Laboratorio',
      modulo: 'laboratorio',
      icon: 'i-heroicons-beaker',
      items: [
          { label: 'Ordenes de Laboratorio', path: '/app/laboratorio/ordenes', icon: 'i-heroicons-beaker' },
          { label: 'Movimientos', path: '/app/laboratorio/movimientos', icon: 'i-heroicons-arrows-right-left' },
          { label: 'Cupos', path: '/app/laboratorio/cupos', icon: 'i-heroicons-calendar-days' },
          { label: 'Ficha Covid', path: '/app/laboratorio/ficha-covid', icon: 'i-heroicons-document-text' },
      ]
    },
    {
      label: 'Imagenes',
      modulo: 'imagenes',
      icon: 'i-heroicons-photo',
      items: [
        { label: 'Atenciones', path: '/app/imagenes/atenciones', icon: 'i-heroicons-photo' },
        { label: 'Tickets', path: '/app/imagenes/tickets', icon: 'i-heroicons-ticket' },
        { label: 'Hospitalizados', path: '/app/imagenes/hospitalizados', icon: 'i-heroicons-building-office-2' },
        { label: 'Reimpresiones', path: '/app/imagenes/reimpresiones', icon: 'i-heroicons-printer' },
      ]
    },
    {
      label: 'Farmacia',
      modulo: 'farmacia',
      icon: 'i-heroicons-beaker',
      items: [
        { label: 'Recetas', path: '/app/farmacia/recetas', icon: 'i-heroicons-document-text' },
        { label: 'Ingreso Almacén', path: '/app/farmacia/ingreso-almacen', icon: 'i-heroicons-arrow-down-tray' },
        { label: 'Salida Almacén', path: '/app/farmacia/salida-almacen', icon: 'i-heroicons-arrow-up-tray' },
        { label: 'Ingreso Farmacia', path: '/app/farmacia/ingreso-farmacia', icon: 'i-heroicons-arrow-down-tray' },
        { label: 'Salida Farmacia', path: '/app/farmacia/salida-farmacia', icon: 'i-heroicons-arrow-up-tray' },
        { label: 'Medicamentos', path: '/app/farmacia/medicamentos', icon: 'i-heroicons-cube' },
        { label: 'Farmacotecnia', path: '/app/farmacia/farmacotecnia', icon: 'i-heroicons-beaker' },
        { label: 'ICI Diario', path: '/app/farmacia/ici-diario', icon: 'i-heroicons-clock' },
        { label: 'IDI Diario', path: '/app/farmacia/idi-diario', icon: 'i-heroicons-clock' },
        { label: 'Saldos', path: '/app/farmacia/saldos', icon: 'i-heroicons-archive-box' },
        { label: 'Kardex - PDF', path: '/app/farmacia/kardex', icon: 'i-heroicons-document-arrow-down' },
        { label: 'Saldo Almacén', path: '/app/farmacia/saldo-almacen', icon: 'i-heroicons-building-storefront' },
        { label: 'DIGEMID', path: '/app/farmacia/digemid', icon: 'i-heroicons-shield-check' },
        { label: 'Venta Farmacia', path: '/app/farmacia/venta-farmacia', icon: 'i-heroicons-shopping-cart' },
      ]
    },
    {
      label: 'Caja',
      modulo: 'caja',
      icon: 'i-heroicons-banknotes',
      items: [
        { label: 'Comprobantes de Pago', path: '/app/caja/comprobantes-pago', icon: 'i-heroicons-receipt-percent' },
        { label: 'Cuentas', path: '/app/caja/cuentas', icon: 'i-heroicons-document-text' },
        { label: 'Cobro por Paciente', path: '/app/caja/cobro-por-paciente', icon: 'i-heroicons-credit-card' },
        { label: 'Mi Caja', path: '/app/caja/mi-caja', icon: 'i-heroicons-computer-desktop' },
      ]
    },
    {
      label: 'Archivo Clinico',
      modulo: 'archivo_clinico',
      icon: 'i-heroicons-folder',
      items: [
        { label: 'HC Electronica', path: '/app/archivo-clinico/hc-electronica', icon: 'i-heroicons-folder-open' },
        { label: 'Historias Clinicas', path: '/app/archivo-clinico/historias-clinicas', icon: 'i-heroicons-folder' },
        { label: 'Movimientos de H.C.', path: '/app/archivo-clinico/movimientos-hc', icon: 'i-heroicons-arrows-right-left' },
        { label: 'Personal de Archivo', path: '/app/archivo-clinico/personal-archivo', icon: 'i-heroicons-user-group' },
      ]
    },
    {
      label: 'SIS',
      modulo: 'sis',
      icon: 'i-heroicons-document-text',
      items: [
        { label: 'Formato FUA', path: '/app/sis/formato-fua', icon: 'i-heroicons-document-text' },
        { label: 'Afiliaciones SIS', path: '/app/sis/afiliaciones', icon: 'i-heroicons-shield-check' },
      ]
    },
    {
      label: 'HIS',
      modulo: 'his',
      icon: 'i-heroicons-server-stack',
      items: [
        { label: 'Registro HIS de la MicroRed', path: '/app/his/registro-microred', icon: 'i-heroicons-server-stack' },
        { label: 'Formato HIS', path: '/app/his/formato-his', icon: 'i-heroicons-document-text' },
      ]
    },
    {
      label: 'Informes',
      modulo: 'informes',
      icon: 'i-heroicons-chart-bar',
      items: [
        { label: 'Reporte por Medico', path: '/app/informes/reporte-medico', icon: 'i-heroicons-chart-bar' },
        { label: 'Reportes de Hospitalizacion', path: '/app/informes/reportes-hospitalizacion', icon: 'i-heroicons-chart-bar-square' },
        { label: 'Gestion Cupos', path: '/app/informes/gestion-cupos', icon: 'i-heroicons-list-bullet' },
        { label: 'Gestion Tickets', path: '/app/informes/gestion-tickets', icon: 'i-heroicons-ticket' },
        { label: 'Visor Colas', path: '/app/informes/visor-colas', icon: 'i-heroicons-queue-list' },
        { label: 'Externos', path: '/app/informes/externos', icon: 'i-heroicons-computer-desktop' },
      ]
    },
    {
      label: 'TeleSalud',
      modulo: 'telesalud',
      icon: 'i-heroicons-video-camera',
      items: [
        { label: 'Resumen Teleconsultas', path: '/app/telesalud/resumen-teleconsultas', icon: 'i-heroicons-video-camera' },
        { label: 'Guia Rapida MINSA', path: '/app/telesalud/guia-rapida-minsa', icon: 'i-heroicons-book-open' },
        { label: 'Formulario Solicitud', path: '/app/telesalud/formulario-solicitud', icon: 'i-heroicons-pencil-square' },
        { label: 'Monitor', path: '/app/telesalud/monitor', icon: 'i-heroicons-tv' },
        { label: 'Medicos', path: '/app/telesalud/medicos', icon: 'i-heroicons-user-group' },
      ]
    },

    // ===== GRUPOS NUEVOS (agregados, no existian antes) =====
    {
      label: 'Servicio Social',
      modulo: 'servicio_social',
      icon: 'i-heroicons-user-group',
      items: [
        { label: 'Servicio Social', path: '/app/servicio-social/servicio-social', icon: 'i-heroicons-user-group' },
      ]
    },
    {
      label: 'Facturación',
      modulo: 'facturacion',
      icon: 'i-heroicons-receipt-percent',
      items: [
        { label: 'Estado de Cuenta', path: '/app/facturacion/estado-cuenta', icon: 'i-heroicons-document-text' },
      ]
    },
    {
      label: 'Fact - Config',
      modulo: 'fact_config',
      icon: 'i-heroicons-cog-6-tooth',
      items: [
        { label: 'Catalogo de Bienes e Insumos', path: '/app/fact-config/catalogo-bienes-insumos', icon: 'i-heroicons-cube' },
        { label: 'Catalogo de Servicios', path: '/app/fact-config/catalogo-servicios', icon: 'i-heroicons-list-bullet' },
      ]
    },
    {
      label: 'Seguridad',
      modulo: 'seguridad',
      icon: 'i-heroicons-shield-check',
      items: [
        { label: 'Empleados', path: '/app/seguridad/empleados', icon: 'i-heroicons-user-group' },
      ]
    },
    {
      label: 'General',
      modulo: 'general',
      icon: 'i-heroicons-computer-desktop',
      items: [
        { label: 'Servicios', path: '/app/general/servicios', icon: 'i-heroicons-clipboard-document' },
        { label: 'Diagnósticos', path: '/app/general/diagnosticos', icon: 'i-heroicons-list-bullet' },
        { label: 'Paquetes', path: '/app/general/paquetes', icon: 'i-heroicons-list-bullet' },
      ]
    },
    {
      label: 'Epidemiologia',
      modulo: 'epidemiologia',
      icon: 'i-heroicons-briefcase',
      items: [
        { label: 'Ficha Covid', path: '/app/epidemiologia/ficha-covid', icon: 'i-heroicons-document-text' },
        { label: 'Ficha Cancer', path: '/app/epidemiologia/ficha-cancer', icon: 'i-heroicons-document-text' },
        { label: 'Ficha Diabetes', path: '/app/epidemiologia/ficha-diabetes', icon: 'i-heroicons-document-text' },
        { label: 'Ficha Dengue', path: '/app/epidemiologia/ficha-dengue', icon: 'i-heroicons-document-text' },
        { label: 'Ficha Leptospirosis', path: '/app/epidemiologia/ficha-leptospirosis', icon: 'i-heroicons-document-text' },
      ]
    },
    {
      label: 'Procedimientos',
      modulo: 'procedimientos',
      icon: 'i-heroicons-briefcase',
      items: [
        { label: 'Atenciones', path: '/app/procedimientos/atenciones', icon: 'i-heroicons-user' },
        { label: 'Asignaciones', path: '/app/procedimientos/asignaciones', icon: 'i-heroicons-document-text' },
      ]
    },
    {
      label: 'Auditoria',
      modulo: 'auditoria',
      icon: 'i-heroicons-document-magnifying-glass',
      items: [
        { label: 'Auditoria', path: '/app/auditoria/auditoria', icon: 'i-heroicons-user' },
        { label: 'Auditoria General', path: '/app/auditoria/auditoria-general', icon: 'i-heroicons-user-group' },
      ]
    },
    {
      label: 'Hemodialisis',
      modulo: 'hemodialisis',
      icon: 'i-heroicons-user-group',
      items: [
        { label: 'Hemodialis', path: '/app/hemodialisis/hemodialis', icon: 'i-heroicons-list-bullet' },
        { label: 'Sesiones', path: '/app/hemodialisis/sesiones', icon: 'i-heroicons-list-bullet' },
      ]
    },
    {
      label: 'Banco de Sangre',
      modulo: 'banco_sangre',
      icon: 'i-heroicons-beaker',
      items: [
        { label: 'Solicitud Transfusional', path: '/app/banco-sangre/solicitud-transfusional', icon: 'i-heroicons-list-bullet' },
        { label: 'Movimientos', path: '/app/banco-sangre/movimientos', icon: 'i-heroicons-arrows-right-left' },
      ]
    },
    {
      label: 'Salud Ambiental',
      modulo: 'salud_ambiental',
      icon: 'i-heroicons-globe-alt',
      items: [
        { label: 'Defunciones', path: '/app/salud-ambiental/defunciones', icon: 'i-heroicons-list-bullet' },
      ]
    },
    {
      label: 'Medicina Fisica',
      modulo: 'medicina_fisica',
      icon: 'i-heroicons-user',
      items: [
        { label: 'Sesiones M. Física', path: '/app/medicina-fisica/sesiones-m-fisica', icon: 'i-heroicons-list-bullet' },
        { label: 'Programas', path: '/app/medicina-fisica/programas', icon: 'i-heroicons-list-bullet' },
        { label: 'Tablero Control', path: '/app/medicina-fisica/tablero-control', icon: 'i-heroicons-list-bullet' },
        { label: 'Tecnologo por Programa', path: '/app/medicina-fisica/tecnologo-por-programa', icon: 'i-heroicons-briefcase' },
        { label: 'Reprogramaciones Bloque', path: '/app/medicina-fisica/reprogramaciones-bloque', icon: 'i-heroicons-briefcase' },
        { label: 'Bloqueo de Programación', path: '/app/medicina-fisica/bloqueo-programacion', icon: 'i-heroicons-briefcase' },
      ]
    },
    {
      label: 'Firma Electronica',
      modulo: 'firma_electronica',
      icon: 'i-heroicons-pencil-square',
      items: [
        { label: 'Bandeja', path: '/app/firma-electronica/bandeja', icon: 'i-heroicons-inbox' },
      ]
    },
    {
      label: 'Seguimiento',
      modulo: 'seguimiento',
      icon: 'i-heroicons-magnifying-glass-circle',
      items: [
        { label: 'Seguimiento', path: '/app/seguimiento/seguimiento', icon: 'i-heroicons-magnifying-glass-circle' },
      ]
    },
  ])

  const gruposVisibles = computed(() =>
    grupos.value.filter(g => tieneAlguno([g.modulo]))
  )

  return { tenantId, link, activo, tieneAlguno, grupos, gruposVisibles }
}
