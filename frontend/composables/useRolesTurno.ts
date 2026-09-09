/**
 * Configuración compartida de Roles de Turno (Creación / Pendientes / Aprobados).
 * Las 15 modalidades = combinaciones válidas de categoria_personal x tipo_rol.
 */
export interface Modalidad { categoria: string; tipo: string }

export const CATEGORIAS_PERSONAL = [
  { key: 'medicos', label: 'Prof. Salud - Médicos', icon: 'i-heroicons-user-group' },
  { key: 'otros_profesionales', label: 'Otros Prof. de la Salud', icon: 'i-heroicons-user-group' },
  { key: 'residentes', label: 'Residentes de Medicina', icon: 'i-heroicons-academic-cap' },
  { key: 'tecnicos', label: 'Técnicos y Auxiliares', icon: 'i-heroicons-wrench-screwdriver' },
  { key: 'internos', label: 'Internos de Medicina', icon: 'i-heroicons-identification' },
] as const

export const MODALIDADES: Record<string, string[]> = {
  medicos: ['ordinario', 'complementario', 'reten', 'ordinario_sin_actividad'],
  otros_profesionales: ['ordinario', 'complementario', 'reten', 'ordinario_con_actividad', 'complementario_con_actividad'],
  residentes: ['ordinario'],
  tecnicos: ['ordinario', 'complementario', 'reten', 'ordinario_con_actividad'],
  internos: ['turnos'],
}

export const TIPO_ROL_LABEL: Record<string, string> = {
  ordinario: 'Rol Ordinario',
  complementario: 'Rol Horas Complementarias',
  reten: 'Rol de Retén',
  ordinario_sin_actividad: 'Rol Ordinario sin Actividad',
  ordinario_con_actividad: 'Rol Ordinario con Actividad',
  complementario_con_actividad: 'Rol Horas Complementarias con Actividad',
  turnos: 'Rol de Turnos',
}

export const ESTADO_ROL: Record<string, { label: string; badge: string }> = {
  draft: { label: 'Borrador', badge: 'badge--neutral' },
  pending: { label: 'Pendiente', badge: 'badge--warning' },
  approved: { label: 'Aprobado', badge: 'badge--ok' },
  rejected: { label: 'Rechazado', badge: 'badge--danger' },
}

export const ESTADO_SOLICITUD: Record<string, { label: string; badge: string }> = {
  pendiente: { label: 'Pendiente', badge: 'badge--warning' },
  aprobado: { label: 'Aprobado', badge: 'badge--ok' },
  rechazado: { label: 'Rechazado', badge: 'badge--danger' },
}

export const MESES = [
  '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]

export const DIAS_SEMANA = [
  { v: 0, label: 'Dom' }, { v: 1, label: 'Lun' }, { v: 2, label: 'Mar' },
  { v: 3, label: 'Mié' }, { v: 4, label: 'Jue' }, { v: 5, label: 'Vie' }, { v: 6, label: 'Sáb' },
]

export const useRolesTurno = () => {
  const categoriaLabel = (k: string) => CATEGORIAS_PERSONAL.find(c => c.key === k)?.label || k
  const tipoLabel = (t: string) => TIPO_ROL_LABEL[t] || t
  const modalidadLabel = (cat: string, tipo: string) => `${categoriaLabel(cat)} · ${tipoLabel(tipo)}`
  const periodoLabel = (mes: number, anio: number) => `${MESES[mes] || mes} ${anio}`
  const diasLabel = (dias: number[]) => (dias || []).map(d => DIAS_SEMANA[d]?.label).filter(Boolean).join(', ') || '—'
  const estadoRol = (s: string) => ESTADO_ROL[s] || { label: s, badge: 'badge--neutral' }
  const estadoSolicitud = (s: string) => ESTADO_SOLICITUD[s] || { label: s, badge: 'badge--neutral' }
  const tiposDe = (categoria: string) => MODALIDADES[categoria] || []
  const categoriaValida = (k: string) => k in MODALIDADES
  const tipoValido = (cat: string, tipo: string) => (MODALIDADES[cat] || []).includes(tipo)

  return {
    CATEGORIAS_PERSONAL, MODALIDADES, MESES, DIAS_SEMANA,
    categoriaLabel, tipoLabel, modalidadLabel, periodoLabel, diasLabel,
    estadoRol, estadoSolicitud, tiposDe, categoriaValida, tipoValido,
  }
}
