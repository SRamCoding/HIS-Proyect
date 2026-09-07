// frontend/composables/useHospitalNav.ts
export const useHospitalNav = () => {
  const authStore = useAuthStore()
  const route = useRoute()

  const tenantId = computed(() => route.query.tenant as string || '')
  const link = (path: string) => `${path}?tenant=${tenantId.value}`
  const activo = (path: string) => ({ 'nav-active': route.path === path })
  const tiene = (code: string) => authStore.user?.active_modules?.includes(code) ?? false
  const tieneAlguno = (codes: string[]) => codes.some(c => tiene(c))

  const grupos = computed(() => [
    {
      label: 'Admisión',
      modulo: 'gestion_pacientes',
      icon: 'i-heroicons-user',
      items: [
        { label: 'Pacientes', path: '/app/gestion-pacientes/pacientes', icon: 'i-heroicons-user' },
        { label: 'Altas de Pacientes', path: '/app/gestion-pacientes/altas-pacientes', icon: 'i-heroicons-arrow-right-on-rectangle' },
      ]
    },
    {
      label: 'Cobros',
      modulo: 'cobros',
      icon: 'i-heroicons-banknotes',
      items: [
        { label: 'Cobro por Paciente', path: '/app/cobros/cobro-por-paciente', icon: 'i-heroicons-credit-card' },
        { label: 'Mi Caja', path: '/app/cobros/mi-caja', icon: 'i-heroicons-computer-desktop' },
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
        { label: 'Admision Consulta Externa', path: '/app/consulta-externa/admision', icon: 'i-heroicons-clipboard-document' },
        { label: 'Programacion Medica', path: '/app/consulta-externa/programacion-medica', icon: 'i-heroicons-calendar' },
        { label: 'Calendario Medico', path: '/app/consulta-externa/calendario-medico', icon: 'i-heroicons-calendar-days' },
        { label: 'Triaje', path: '/app/consulta-externa/triaje', icon: 'i-heroicons-heart' },
        { label: 'Citas por Confirmar', path: '/app/consulta-externa/admision/pendientes', icon: 'i-heroicons-clock' },
        { label: 'Atenciones Medicas', path: '/app/consulta-externa/atenciones-medicas', icon: 'i-heroicons-clipboard-document-check' },
        { label: 'Bandeja Electronica', path: '/app/consulta-externa/bandeja-electronica', icon: 'i-heroicons-inbox' },
      ]
    },
    {
      label: 'Emergencia',
      modulo: 'emergencia',
      icon: 'i-heroicons-exclamation-triangle',
      items: [
        { label: 'Admisiones', path: '/app/emergencia/admisiones', icon: 'i-heroicons-exclamation-triangle' },
        { label: 'Observacion', path: '/app/emergencia/observacion', icon: 'i-heroicons-eye' },
        { label: 'Referencias', path: '/app/emergencia/referencias', icon: 'i-heroicons-arrow-right-circle' },
      ]
    },
    {
      label: 'Laboratorio',
      modulo: 'laboratorio',
      icon: 'i-heroicons-beaker',
      items: [
        { label: 'Ordenes de Laboratorio', path: '/app/laboratorio/ordenes', icon: 'i-heroicons-beaker' },
      ]
    },
    {
      label: 'Imagenologia',
      modulo: 'imagenologia',
      icon: 'i-heroicons-photo',
      items: [
        { label: 'Atenciones', path: '/app/imagenologia/atenciones', icon: 'i-heroicons-photo' },
        { label: 'Tickets', path: '/app/imagenologia/tickets', icon: 'i-heroicons-ticket' },
        { label: 'Hospitalizados', path: '/app/imagenologia/hospitalizados', icon: 'i-heroicons-building-office-2' },
        { label: 'Reimpresiones', path: '/app/imagenologia/reimpresiones', icon: 'i-heroicons-printer' },
      ]
    },
    {
      label: 'Farmacia',
      modulo: 'farmacia',
      icon: 'i-heroicons-beaker',
      items: [
        { label: 'Recetas Medicas', path: '/app/farmacia/recetas-medicas', icon: 'i-heroicons-document-text' },
        { label: 'Recetas Farmacotecnia', path: '/app/farmacia/recetas-farmacotecnia', icon: 'i-heroicons-beaker' },
        { label: 'Ventas / Despacho', path: '/app/farmacia/ventas-despacho', icon: 'i-heroicons-shopping-cart' },
        { label: 'Notas de Ingreso', path: '/app/farmacia/notas-ingreso', icon: 'i-heroicons-arrow-down-tray' },
        { label: 'Kardex / Movimientos', path: '/app/farmacia/kardex-movimientos', icon: 'i-heroicons-arrows-right-left' },
        { label: 'Notas de Salida', path: '/app/farmacia/notas-salida', icon: 'i-heroicons-arrow-up-tray' },
        { label: 'Saldos Farmacia', path: '/app/farmacia/saldos', icon: 'i-heroicons-archive-box' },
        { label: 'Reportes', path: '/app/farmacia/reportes', icon: 'i-heroicons-chart-bar' },
        { label: 'Panel DIGEMID', path: '/app/farmacia/panel-digemid', icon: 'i-heroicons-shield-exclamation' },
        { label: 'ICI Diario', path: '/app/farmacia/ici-diario', icon: 'i-heroicons-clock' },
      ]
    },
    {
      label: 'Caja',
      modulo: 'caja',
      icon: 'i-heroicons-banknotes',
      items: [
        { label: 'Comprobantes de Pago', path: '/app/caja/comprobantes-pago', icon: 'i-heroicons-receipt-percent' },
        { label: 'Cuentas', path: '/app/caja/cuentas', icon: 'i-heroicons-document-text' },
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
      label: 'Reportes',
      modulo: 'reportes',
      icon: 'i-heroicons-chart-bar',
      items: [
        { label: 'Reporte por Medico', path: '/app/reportes/reporte-medico', icon: 'i-heroicons-chart-bar' },
        { label: 'Reportes de Hospitalizacion', path: '/app/reportes/reportes-hospitalizacion', icon: 'i-heroicons-chart-bar-square' },
      ]
    },
    {
      label: 'Telemedicina',
      modulo: 'telemedicina',
      icon: 'i-heroicons-video-camera',
      items: [
        { label: 'Resumen Teleconsultas', path: '/app/telemedicina/resumen-teleconsultas', icon: 'i-heroicons-video-camera' },
        { label: 'Guia Rapida MINSA', path: '/app/telemedicina/guia-rapida-minsa', icon: 'i-heroicons-book-open' },
      ]
    },
  ])

  const gruposVisibles = computed(() =>
    grupos.value.filter(g => tieneAlguno([g.modulo]))
  )

  return { tenantId, link, activo, tieneAlguno, grupos, gruposVisibles }
}