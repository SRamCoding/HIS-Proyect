export const useSigarhNav = () => {
  const authStore = useAuthStore()
  const route = useRoute()

  const tenantId = computed(() => (route.query.tenant as string) || authStore.user?.tenant_id || '')
  const link = (path: string) => `${path}?tenant=${tenantId.value}`
  const tiene = (code: string) => authStore.user?.active_modules?.includes(code) ?? false
  const tieneAlguno = (codes: string[]) => codes.some(c => tiene(c))

  const grupos = computed(() => [
    {
      label: 'Recursos Humanos',
      modulo: 'sigarh_recursos_humanos',
      icon: 'i-heroicons-users',
      items: [
        { label: 'Empleados',                       path: '/sigarh/rrhh/empleados',              icon: 'i-heroicons-user' },
        { label: 'Especialidades',                  path: '/sigarh/rrhh/especialidades',          icon: 'i-heroicons-academic-cap' },
        { label: 'Dias Feriados',                   path: '/sigarh/rrhh/feriados',                icon: 'i-heroicons-calendar' },
        { label: 'Registro de Asistencia',          path: '/sigarh/rrhh/asistencia',              icon: 'i-heroicons-clipboard-document-check' },
        { label: 'Tolerancias',                     path: '/sigarh/rrhh/tolerancias',             icon: 'i-heroicons-clock' },
        { label: 'Motivos de Justificacion',        path: '/sigarh/rrhh/motivos-justificacion',   icon: 'i-heroicons-document-text' },
        { label: 'Justificaciones e Inasistencias', path: '/sigarh/rrhh/justificaciones',         icon: 'i-heroicons-exclamation-circle' },
      ]
    },
    {
      label: 'Movimientos',
      modulo: 'sigarh_movimientos',
      icon: 'i-heroicons-arrows-right-left',
      items: [
        { label: 'Justificacion y Vacaciones', path: '/sigarh/movimientos/vacaciones',          icon: 'i-heroicons-sun' },
        { label: 'Tramitar Licencia',          path: '/sigarh/movimientos/licencias/create',    icon: 'i-heroicons-paper-airplane' },
        { label: 'Estado Licencia',            path: '/sigarh/movimientos/licencias',            icon: 'i-heroicons-list-bullet' },
        {
          label: 'Cambio de Turno',
          subgrupo: true,
          icon: 'i-heroicons-arrows-right-left',
          children: [
            { label: 'Tramitar Cambio de Turno', path: '/sigarh/movimientos/cambio-turno/tramitar', icon: 'i-heroicons-paper-airplane' },
            { label: 'Estado Cambio Turno',      path: '/sigarh/movimientos/cambio-turno/estado',   icon: 'i-heroicons-list-bullet' },
          ]
        },
        {
          label: 'Papeletas',
          subgrupo: true,
          icon: 'i-heroicons-document-duplicate',
          children: [
            { label: 'Tramitar Papeleta',   path: '/sigarh/movimientos/papeletas/tramitar', icon: 'i-heroicons-paper-airplane' },
            { label: 'Estado de Papeletas', path: '/sigarh/movimientos/papeletas/estado',   icon: 'i-heroicons-list-bullet' },
          ]
        },
      ]
    },
    {
      label: 'Creacion de Roles',
      modulo: 'sigarh_creacion_roles',
      icon: 'i-heroicons-calendar-days',
      items: CATEGORIAS_PERSONAL.map(c => ({
        label: c.label,
        subgrupo: true,
        icon: c.icon,
        children: (MODALIDADES[c.key] || []).map(t => ({
          label: TIPO_ROL_LABEL[t] || t,
          path: `/sigarh/creacion-roles/${c.key}/${t}`,
          icon: 'i-heroicons-document-plus',
        })),
      })),
    },
    {
      label: 'Roles Pendientes',
      modulo: 'sigarh_roles_pendientes',
      icon: 'i-heroicons-clock',
      items: [
        { label: 'Bandeja de Roles',          path: '/sigarh/roles-pendientes',              icon: 'i-heroicons-inbox-stack' },
        { label: 'Solicitudes de Modificacion', path: '/sigarh/roles-pendientes/solicitudes', icon: 'i-heroicons-pencil-square' },
      ]
    },
    {
      label: 'Roles Aprobados',
      modulo: 'sigarh_roles_aprobados',
      icon: 'i-heroicons-check-badge',
      items: [
        { label: 'Roles Aprobados', path: '/sigarh/roles-aprobados', icon: 'i-heroicons-check-circle' },
      ]
    },
    {
      label: 'Infraestructura',
      modulo: 'sigarh_infraestructura',
      icon: 'i-heroicons-building-office',
      items: [
        { label: 'Catalogos',    path: '/sigarh/infraestructura/catalogos',    icon: 'i-heroicons-squares-2x2' },
        { label: 'Consultorios', path: '/sigarh/infraestructura/consultorios', icon: 'i-heroicons-building-storefront' },
      ]
    },
    {
      label: 'Infraestructura Hospitalaria',
      modulo: 'sigarh_infraestructura_hosp',
      icon: 'i-heroicons-building-office-2',
      items: [
        { label: 'Pisos', path: '/sigarh/infraestructura-hosp/pisos', icon: 'i-heroicons-building-office-2' },
        { label: 'Salas', path: '/sigarh/infraestructura-hosp/salas', icon: 'i-heroicons-rectangle-group' },
        { label: 'Camas', path: '/sigarh/infraestructura-hosp/camas', icon: 'i-heroicons-home' },
      ]
    },
    {
      label: 'Config. Farmacia',
      modulo: 'sigarh_config_farmacia',
      icon: 'i-heroicons-beaker',
      items: [
        { label: 'Almacenes / Farmacias',  path: '/sigarh/config-farmacia/almacenes',    icon: 'i-heroicons-archive-box' },
        { label: 'Medicamentos e Insumos', path: '/sigarh/config-farmacia/medicamentos',  icon: 'i-heroicons-beaker' },
      ]
    },
    {
      label: 'Config. Financiera',
      modulo: 'sigarh_config_financiera',
      icon: 'i-heroicons-banknotes',
      items: [
        { label: 'Seguros',   path: '/sigarh/config-financiera/seguros',   icon: 'i-heroicons-shield-check' },
        { label: 'Cajas',     path: '/sigarh/config-financiera/cajas',     icon: 'i-heroicons-banknotes' },
        { label: 'Tarifario', path: '/sigarh/config-financiera/tarifario', icon: 'i-heroicons-currency-dollar' },
      ]
    },
    {
      label: 'Laboratorio',
      modulo: 'sigarh_laboratorio',
      icon: 'i-heroicons-beaker',
      items: [
        { label: 'Examenes de Laboratorio', path: '/sigarh/laboratorio/examenes', icon: 'i-heroicons-beaker' },
      ]
    },
    {
      label: 'Imagenologia',
      modulo: 'sigarh_imagenologia',
      icon: 'i-heroicons-photo',
      items: [
        { label: 'Examenes de Imagenologia', path: '/sigarh/imagenologia/examenes', icon: 'i-heroicons-photo' },
      ]
    },
    {
      label: 'Nutricion',
      modulo: 'sigarh_nutricion',
      icon: 'i-heroicons-clipboard-document-list',
      items: [
        { label: 'Registro de Raciones', path: '/sigarh/nutricion/raciones',     icon: 'i-heroicons-clipboard-document-list' },
        { label: 'Generar Reportes',     path: '/sigarh/nutricion/reportes',     icon: 'i-heroicons-chart-bar' },
        { label: 'Entrega de Raciones',  path: '/sigarh/nutricion/entrega',      icon: 'i-heroicons-check-circle' },
        { label: 'Cambios de Turno',     path: '/sigarh/nutricion/cambio-turno', icon: 'i-heroicons-arrows-right-left' },
      ]
    },
    {
      label: 'General',
      modulo: 'sigarh_general',
      icon: 'i-heroicons-globe-alt',
      items: [
        { label: 'Diagnosticos CIE-10',    path: '/sigarh/general/cie10',    icon: 'i-heroicons-document-magnifying-glass' },
        { label: 'Paquetes',               path: '/sigarh/general/paquetes', icon: 'i-heroicons-archive-box' },
        { label: 'Tiempos Procedimientos', path: '/sigarh/general/tiempos',  icon: 'i-heroicons-clock' },
      ]
    },
    {
      label: 'Mantenimiento',
      modulo: 'sigarh_mantenimiento',
      icon: 'i-heroicons-wrench-screwdriver',
      items: [
        { label: 'Usuarios',              path: '/sigarh/mantenimiento/usuarios',              icon: 'i-heroicons-users' },
        { label: 'Departamentos',         path: '/sigarh/mantenimiento/departamentos',         icon: 'i-heroicons-building-office' },
        { label: 'Servicios',             path: '/sigarh/mantenimiento/servicios',             icon: 'i-heroicons-squares-2x2' },
        { label: 'Dependencias',          path: '/sigarh/mantenimiento/dependencias',          icon: 'i-heroicons-link' },
        { label: 'Tipos de Trabajador',   path: '/sigarh/mantenimiento/tipos-trabajador',      icon: 'i-heroicons-identification' },
        { label: 'Tipos de Guardia',      path: '/sigarh/mantenimiento/tipos-guardia',         icon: 'i-heroicons-shield-check' },
        { label: 'Niveles Remunerativos', path: '/sigarh/mantenimiento/niveles-remunerativos', icon: 'i-heroicons-currency-dollar' },
        { label: 'Horarios de Guardia',   path: '/sigarh/mantenimiento/horarios-guardia',      icon: 'i-heroicons-clock' },
        { label: 'Tipos de Actividad',    path: '/sigarh/mantenimiento/tipos-actividad',       icon: 'i-heroicons-tag' },
        { label: 'Actividades',           path: '/sigarh/mantenimiento/actividades',           icon: 'i-heroicons-bolt' },
        { label: 'Guardias Valorizadas',  path: '/sigarh/mantenimiento/guardias-valorizadas',  icon: 'i-heroicons-star' },
        { label: 'Roles del Sistema',     path: '/sigarh/mantenimiento/roles-sistema',         icon: 'i-heroicons-key' },
        { label: 'Perfiles de Usuario',   path: '/sigarh/mantenimiento/perfiles-usuario',      icon: 'i-heroicons-user-circle' },
        { label: 'Grupos Ocupacionales',    path: '/sigarh/mantenimiento/grupos-ocupacionales',  icon: 'i-heroicons-users' },
      ]
    },
  ])

  const gruposVisibles = computed(() =>
    grupos.value.filter(g => tieneAlguno([g.modulo]))
  )

  const rutasVisibles = computed(() => gruposVisibles.value.flatMap(g =>
    g.items.flatMap((item: any) => item.subgrupo ? item.children.map((child: any) => child.path) : [item.path])
  ))
  const rutaMenuActual = computed(() => route.path === '/sigarh'
    ? '/sigarh'
    : rutasVisibles.value
      .filter(path => route.path === path || route.path.startsWith(`${path}/`))
      .sort((a, b) => b.length - a.length)[0] || '')
  const activo = (path: string) => ({ 'nav-active': rutaMenuActual.value === path })

  return { tenantId, link, activo, gruposVisibles, rutaMenuActual }
}
