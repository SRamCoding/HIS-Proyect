export const useSigarhNav = () => {
  const authStore = useAuthStore()
  const route = useRoute()

  const tenantId = computed(() => (route.query.tenant as string) || authStore.user?.tenant_id || '')
  const link = (path: string) => `${path}?tenant=${tenantId.value}`
  const activeModules = computed(() => authStore.user?.active_modules ?? [])
  // Un rol con el codigo completo del modulo ("sigarh_recursos_humanos") tiene
  // acceso a todos sus submodulos; uno con solo un submodulo puntual
  // ("sigarh_recursos_humanos.empleados") ya alcanza para que el grupo del
  // menu aparezca, aunque solo tenga permiso sobre una parte de el.
  const tiene = (code: string) => activeModules.value.some(
    (m: string) => m === code || m.startsWith(`${code}.`)
  )
  const tieneAlguno = (codes: string[]) => codes.some(c => tiene(c))
  // Direccion opuesta a tiene(): ¿el codigo puntual de un ITEM del menu
  // (ej. "sigarh_recursos_humanos.empleados") esta cubierto por lo que el
  // usuario tiene? Cubre si esta exacto, o si tiene el modulo padre completo
  // ("sigarh_recursos_humanos") -- igual que permiso_incluye() en el backend.
  const cubreItem = (codigoCompleto: string) => {
    if (activeModules.value.includes(codigoCompleto)) return true
    const padre = codigoCompleto.split('.')[0]
    return padre !== codigoCompleto && activeModules.value.includes(padre)
  }

  const grupos = computed(() => [
    {
      label: 'Recursos Humanos',
      modulo: 'sigarh_recursos_humanos',
      icon: 'i-heroicons-users',
      items: [
        { label: 'Empleados',                       path: '/sigarh/rrhh/empleados',              icon: 'i-heroicons-user', sub: 'empleados' },
        { label: 'Especialidades',                  path: '/sigarh/rrhh/especialidades',          icon: 'i-heroicons-academic-cap', sub: 'especialidades' },
        { label: 'Dias Feriados',                   path: '/sigarh/rrhh/feriados',                icon: 'i-heroicons-calendar', sub: 'feriados' },
        { label: 'Registro de Asistencia',          path: '/sigarh/rrhh/asistencia',              icon: 'i-heroicons-clipboard-document-check', sub: 'asistencia' },
        { label: 'Tolerancias',                     path: '/sigarh/rrhh/tolerancias',             icon: 'i-heroicons-clock', sub: 'tolerancias' },
        { label: 'Motivos de Justificacion',        path: '/sigarh/rrhh/motivos-justificacion',   icon: 'i-heroicons-document-text', sub: 'motivos_justificacion' },
        { label: 'Justificaciones e Inasistencias', path: '/sigarh/rrhh/justificaciones',         icon: 'i-heroicons-exclamation-circle', sub: 'justificaciones' },
      ]
    },
    {
      label: 'Movimientos',
      modulo: 'sigarh_movimientos',
      icon: 'i-heroicons-arrows-right-left',
      items: [
        { label: 'Justificacion y Vacaciones', path: '/sigarh/movimientos/vacaciones',          icon: 'i-heroicons-sun', sub: 'vacaciones' },
        { label: 'Tramitar Licencia',          path: '/sigarh/movimientos/licencias/create',    icon: 'i-heroicons-paper-airplane', sub: 'licencias_tramitar' },
        { label: 'Estado Licencia',            path: '/sigarh/movimientos/licencias',            icon: 'i-heroicons-list-bullet', sub: 'licencias_estado' },
        {
          label: 'Cambio de Turno',
          subgrupo: true,
          icon: 'i-heroicons-arrows-right-left',
          children: [
            { label: 'Tramitar Cambio de Turno', path: '/sigarh/movimientos/cambio-turno/tramitar', icon: 'i-heroicons-paper-airplane', sub: 'cambio_turno_tramitar' },
            { label: 'Estado Cambio Turno',      path: '/sigarh/movimientos/cambio-turno/estado',   icon: 'i-heroicons-list-bullet', sub: 'cambio_turno_estado' },
          ]
        },
        {
          label: 'Papeletas',
          subgrupo: true,
          icon: 'i-heroicons-document-duplicate',
          children: [
            { label: 'Tramitar Papeleta',   path: '/sigarh/movimientos/papeletas/tramitar', icon: 'i-heroicons-paper-airplane', sub: 'papeletas_tramitar' },
            { label: 'Estado de Papeletas', path: '/sigarh/movimientos/papeletas/estado',   icon: 'i-heroicons-list-bullet', sub: 'papeletas_estado' },
          ]
        },
      ]
    },
    {
      label: 'Creacion de Roles',
      modulo: 'sigarh_creacion_roles',
      icon: 'i-heroicons-calendar-days',
      // Sin submodulos migrados: la restriccion es a nivel de fila
      // (categoria_personal), no de endpoint, asi que aqui no se filtra por
      // item -- ver la nota en creacion_roles/router.py.
      sinSubmodulos: true,
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
        { label: 'Bandeja de Roles',          path: '/sigarh/roles-pendientes',              icon: 'i-heroicons-inbox-stack', sub: 'bandeja' },
        { label: 'Solicitudes de Modificacion', path: '/sigarh/roles-pendientes/solicitudes', icon: 'i-heroicons-pencil-square', sub: 'solicitudes' },
      ]
    },
    {
      label: 'Roles Aprobados',
      modulo: 'sigarh_roles_aprobados',
      icon: 'i-heroicons-check-badge',
      items: [
        { label: 'Roles Aprobados', path: '/sigarh/roles-aprobados', icon: 'i-heroicons-check-circle', sub: 'roles_aprobados' },
      ]
    },
    {
      label: 'Infraestructura',
      modulo: 'sigarh_infraestructura',
      icon: 'i-heroicons-building-office',
      items: [
        { label: 'Catalogos',    path: '/sigarh/infraestructura/catalogos',    icon: 'i-heroicons-squares-2x2', sub: 'catalogos' },
        { label: 'Consultorios', path: '/sigarh/infraestructura/consultorios', icon: 'i-heroicons-building-storefront', sub: 'consultorios' },
      ]
    },
    {
      label: 'Infraestructura Hospitalaria',
      modulo: 'sigarh_infraestructura_hosp',
      icon: 'i-heroicons-building-office-2',
      items: [
        { label: 'Pisos', path: '/sigarh/infraestructura-hosp/pisos', icon: 'i-heroicons-building-office-2', sub: 'pisos' },
        { label: 'Salas', path: '/sigarh/infraestructura-hosp/salas', icon: 'i-heroicons-rectangle-group', sub: 'salas' },
        { label: 'Camas', path: '/sigarh/infraestructura-hosp/camas', icon: 'i-heroicons-home', sub: 'camas' },
      ]
    },
    {
      label: 'Config. Farmacia',
      modulo: 'sigarh_config_farmacia',
      icon: 'i-heroicons-beaker',
      items: [
        { label: 'Almacenes / Farmacias',  path: '/sigarh/config-farmacia/almacenes',    icon: 'i-heroicons-archive-box', sub: 'almacenes' },
        { label: 'Medicamentos e Insumos', path: '/sigarh/config-farmacia/medicamentos',  icon: 'i-heroicons-beaker', sub: 'medicamentos' },
      ]
    },
    {
      label: 'Config. Financiera',
      modulo: 'sigarh_config_financiera',
      icon: 'i-heroicons-banknotes',
      items: [
        { label: 'Seguros',   path: '/sigarh/config-financiera/seguros',   icon: 'i-heroicons-shield-check', sub: 'seguros' },
        { label: 'Cajas',     path: '/sigarh/config-financiera/cajas',     icon: 'i-heroicons-banknotes', sub: 'cajas' },
        { label: 'Tarifario', path: '/sigarh/config-financiera/tarifario', icon: 'i-heroicons-currency-dollar', sub: 'tarifario' },
      ]
    },
    {
      label: 'Laboratorio',
      modulo: 'sigarh_laboratorio',
      icon: 'i-heroicons-beaker',
      items: [
        { label: 'Examenes de Laboratorio', path: '/sigarh/laboratorio/examenes', icon: 'i-heroicons-beaker', sub: 'examenes' },
      ]
    },
    {
      label: 'Imagenologia',
      modulo: 'sigarh_imagenologia',
      icon: 'i-heroicons-photo',
      items: [
        { label: 'Examenes de Imagenologia', path: '/sigarh/imagenologia/examenes', icon: 'i-heroicons-photo', sub: 'examenes' },
      ]
    },
    {
      label: 'Nutricion',
      modulo: 'sigarh_nutricion',
      icon: 'i-heroicons-clipboard-document-list',
      items: [
        { label: 'Registro de Raciones', path: '/sigarh/nutricion/raciones',     icon: 'i-heroicons-clipboard-document-list', sub: 'raciones' },
        { label: 'Generar Reportes',     path: '/sigarh/nutricion/reportes',     icon: 'i-heroicons-chart-bar', sub: 'reportes' },
        { label: 'Entrega de Raciones',  path: '/sigarh/nutricion/entrega',      icon: 'i-heroicons-check-circle', sub: 'entrega' },
        { label: 'Cambios de Turno',     path: '/sigarh/nutricion/cambio-turno', icon: 'i-heroicons-arrows-right-left', sub: 'cambio_turno' },
      ]
    },
    {
      label: 'General',
      modulo: 'sigarh_general',
      icon: 'i-heroicons-globe-alt',
      items: [
        { label: 'Diagnosticos CIE-10',    path: '/sigarh/general/cie10',    icon: 'i-heroicons-document-magnifying-glass', sub: 'cie10' },
        { label: 'Paquetes',               path: '/sigarh/general/paquetes', icon: 'i-heroicons-archive-box', sub: 'paquetes' },
        { label: 'Tiempos Procedimientos', path: '/sigarh/general/tiempos',  icon: 'i-heroicons-clock', sub: 'tiempos' },
      ]
    },
    {
      label: 'Mantenimiento',
      modulo: 'sigarh_mantenimiento',
      icon: 'i-heroicons-wrench-screwdriver',
      items: [
        { label: 'Usuarios',              path: '/sigarh/mantenimiento/usuarios',              icon: 'i-heroicons-users', sub: 'usuarios' },
        { label: 'Departamentos',         path: '/sigarh/mantenimiento/departamentos',         icon: 'i-heroicons-building-office', sub: 'departamentos' },
        { label: 'Servicios',             path: '/sigarh/mantenimiento/servicios',             icon: 'i-heroicons-squares-2x2', sub: 'servicios' },
        { label: 'Dependencias',          path: '/sigarh/mantenimiento/dependencias',          icon: 'i-heroicons-link', sub: 'dependencias' },
        { label: 'Tipos de Trabajador',   path: '/sigarh/mantenimiento/tipos-trabajador',      icon: 'i-heroicons-identification', sub: 'tipos_trabajador' },
        { label: 'Tipos de Guardia',      path: '/sigarh/mantenimiento/tipos-guardia',         icon: 'i-heroicons-shield-check', sub: 'tipos_guardia' },
        { label: 'Niveles Remunerativos', path: '/sigarh/mantenimiento/niveles-remunerativos', icon: 'i-heroicons-currency-dollar', sub: 'niveles_remunerativos' },
        { label: 'Horarios de Guardia',   path: '/sigarh/mantenimiento/horarios-guardia',      icon: 'i-heroicons-clock', sub: 'horarios_guardia' },
        { label: 'Tipos de Actividad',    path: '/sigarh/mantenimiento/tipos-actividad',       icon: 'i-heroicons-tag', sub: 'tipos_actividad' },
        { label: 'Actividades',           path: '/sigarh/mantenimiento/actividades',           icon: 'i-heroicons-bolt', sub: 'actividades' },
        { label: 'Guardias Valorizadas',  path: '/sigarh/mantenimiento/guardias-valorizadas',  icon: 'i-heroicons-star', sub: 'guardias_valorizadas' },
        { label: 'Roles del Sistema',     path: '/sigarh/mantenimiento/roles-sistema',         icon: 'i-heroicons-key', sub: 'roles_sistema' },
        { label: 'Perfiles de Usuario',   path: '/sigarh/mantenimiento/perfiles-usuario',      icon: 'i-heroicons-user-circle', sub: 'perfiles_usuario' },
        { label: 'Grupos Ocupacionales',    path: '/sigarh/mantenimiento/grupos-ocupacionales',  icon: 'i-heroicons-users', sub: 'grupos_ocupacionales' },
      ]
    },
  ])

  // El grupo aparece si hay acceso a algun submodulo suyo, pero dentro del
  // grupo solo se listan los items (y children de subgrupo) cuyo submodulo
  // puntual esta realmente concedido -- antes se mostraban los 14 items de
  // Mantenimiento con solo tener 1 concedido, porque el filtro paraba en el
  // grupo y nunca bajaba al item.
  const gruposVisibles = computed(() =>
    grupos.value
      .filter(g => tieneAlguno([g.modulo]))
      .map(g => {
        if ((g as any).sinSubmodulos) return g
        const items = g.items
          .map((item: any) => {
            if (item.subgrupo) {
              const children = item.children.filter((child: any) => !child.sub || cubreItem(`${g.modulo}.${child.sub}`))
              return children.length ? { ...item, children } : null
            }
            return (!item.sub || cubreItem(`${g.modulo}.${item.sub}`)) ? item : null
          })
          .filter(Boolean)
        return { ...g, items }
      })
      .filter(g => g.items.length)
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
