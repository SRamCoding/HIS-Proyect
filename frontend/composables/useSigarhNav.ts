export const useSigarhNav = () => {
  const authStore = useAuthStore()
  const route = useRoute()

  const tenantId = computed(() => route.query.tenant as string || '')
  const link = (path: string) => `${path}?tenant=${tenantId.value}`
  const activo = (path: string) => ({ 'nav-active': route.path === path })
  const tiene = (code: string) => authStore.user?.active_modules?.includes(code) ?? false
  const tieneAlguno = (codes: string[]) => codes.some(c => tiene(c))

  const grupos = computed(() => [
    {
      label: 'Recursos Humanos',
      modulo: 'sigarh_recursos_humanos',
      items: [
        { label: 'Empleados',                       path: '/sigarh/rrhh/empleados' },
        { label: 'Especialidades',                  path: '/sigarh/rrhh/especialidades' },
        { label: 'Dias Feriados',                   path: '/sigarh/rrhh/feriados' },
        { label: 'Registro de Asistencia',          path: '/sigarh/asistencia' },
        { label: 'Tolerancias',                     path: '/sigarh/rrhh/tolerancias' },
        { label: 'Motivos de Justificacion',        path: '/sigarh/rrhh/motivos-justificacion' },
        { label: 'Justificaciones e Inasistencias', path: '/sigarh/rrhh/justificaciones' },
        { label: 'Dependencias',                    path: '/sigarh/mantenimiento/dependencias' },
        { label: 'Usuarios',                        path: '/sigarh/mantenimiento/usuarios' },
        ]
    },
    {
      label: 'Movimientos',
      modulo: 'sigarh_movimientos',
      items: [
        { label: 'Justificacion y Vacaciones',  path: '/sigarh/movimientos/vacaciones' },
        { label: 'Tramitar Licencia',           path: '/sigarh/movimientos/licencias' },
        { label: 'Estado Licencia',             path: '/sigarh/movimientos/estado-licencia' },
      ]
    },
    {
      label: 'Creacion de Roles',
      modulo: 'sigarh_creacion_roles',
      items: [
        { label: 'Prof. Salud - Medicos',   path: '/sigarh/roles-turno/crear/medicos' },
        { label: 'Otros Prof. de la Salud', path: '/sigarh/roles-turno/crear/otros-profesionales' },
        { label: 'Residentes de Medicina',  path: '/sigarh/roles-turno/crear/residentes' },
        { label: 'Tecnicos y Auxiliares',   path: '/sigarh/roles-turno/crear/tecnicos' },
        { label: 'Internos de Medicina',    path: '/sigarh/roles-turno/crear/internos' },
      ]
    },
    {
      label: 'Roles Pendientes',
      modulo: 'sigarh_roles_pendientes',
      items: [
        { label: 'Roles por Aprobar', path: '/sigarh/roles-turno/pendientes' },
      ]
    },
    {
      label: 'Roles Aprobados',
      modulo: 'sigarh_roles_aprobados',
      items: [
        { label: 'Roles Aprobados', path: '/sigarh/roles-turno/aprobados' },
      ]
    },
    {
      label: 'Infraestructura',
      modulo: 'sigarh_infraestructura',
      items: [
        { label: 'Catalogos',    path: '/sigarh/mantenimiento/catalogos' },
        { label: 'Consultorios', path: '/sigarh/mantenimiento/consultorios' },
      ]
    },
    {
      label: 'Infraestructura Hospitalaria',
      modulo: 'sigarh_infraestructura_hosp',
      items: [
        { label: 'Pisos', path: '/sigarh/mantenimiento/pisos' },
        { label: 'Salas', path: '/sigarh/mantenimiento/salas' },
        { label: 'Camas', path: '/sigarh/mantenimiento/camas' },
      ]
    },
    {
      label: 'Configuracion Farmacia',
      modulo: 'sigarh_config_farmacia',
      items: [
        { label: 'Almacenes / Farmacias',  path: '/sigarh/mantenimiento/almacenes' },
        { label: 'Medicamentos e Insumos', path: '/sigarh/mantenimiento/medicamentos' },
      ]
    },
    {
      label: 'Configuracion Financiera',
      modulo: 'sigarh_config_financiera',
      items: [
        { label: 'Seguros',   path: '/sigarh/mantenimiento/seguros' },
        { label: 'Cajas',     path: '/sigarh/mantenimiento/cajas' },
        { label: 'Tarifario', path: '/sigarh/mantenimiento/tarifario' },
      ]
    },
    {
      label: 'Laboratorio',
      modulo: 'sigarh_laboratorio',
      items: [
        { label: 'Examenes de Laboratorio', path: '/sigarh/mantenimiento/examenes-laboratorio' },
      ]
    },
    {
      label: 'Imagenologia',
      modulo: 'sigarh_imagenologia',
      items: [
        { label: 'Examenes de Imagenologia', path: '/sigarh/mantenimiento/examenes-imagenologia' },
      ]
    },
    {
      label: 'Nutricion',
      modulo: 'sigarh_nutricion',
      items: [
        { label: 'Registro de Raciones', path: '/sigarh/nutricion/raciones' },
        { label: 'Generar Reportes',     path: '/sigarh/nutricion/reportes' },
        { label: 'Entrega de Raciones',  path: '/sigarh/nutricion/entrega' },
        { label: 'Cambios de Turno',     path: '/sigarh/nutricion/cambio-turno' },
      ]
    },
    {
      label: 'General',
      modulo: 'sigarh_general',
      items: [
        { label: 'Diagnosticos CIE-10',    path: '/sigarh/general/cie10' },
        { label: 'Paquetes',               path: '/sigarh/general/paquetes' },
        { label: 'Tiempos Procedimientos', path: '/sigarh/general/tiempos' },
      ]
    },
    {
      label: 'Mantenimiento',
      modulo: 'sigarh_mantenimiento',
      items: [
        { label: 'Usuarios',                path: '/sigarh/mantenimiento/usuarios' },
        { label: 'Departamentos',           path: '/sigarh/mantenimiento/departamentos' },
        { label: 'Roles del Sistema',       path: '/sigarh/mantenimiento/roles-sistema' },
        { label: 'Servicios',               path: '/sigarh/mantenimiento/servicios' },
        { label: 'Dependencias',            path: '/sigarh/mantenimiento/dependencias' },
        { label: 'Tipos de Trabajador',     path: '/sigarh/mantenimiento/tipos-trabajador' },
        { label: 'Tipos de Guardia',        path: '/sigarh/mantenimiento/tipos-guardia' },
        { label: 'Niveles Remunerativos',   path: '/sigarh/mantenimiento/niveles-remunerativos' },
        { label: 'Horarios de Guardia',     path: '/sigarh/mantenimiento/horarios-guardia' },
        { label: 'Tipos de Actividad',      path: '/sigarh/mantenimiento/tipos-actividad' },
        { label: 'Actividades',             path: '/sigarh/mantenimiento/actividades' },
        { label: 'Grupos Ocupacionales',    path: '/sigarh/mantenimiento/grupos-ocupacionales' },
        { label: 'Guardias Valorizadas',    path: '/sigarh/mantenimiento/guardias-valorizadas' },
        { label: 'Perfiles de Usuario',     path: '/sigarh/mantenimiento/perfiles-usuario' },
      ]
    },
  ])

  const gruposVisibles = computed(() =>
    grupos.value.filter(g => tieneAlguno([g.modulo]))
  )

  return { tenantId, link, activo, gruposVisibles }
}