<template>
  <div class="dash-container">
    <section class="quick-start" aria-labelledby="quick-start-title">
      <h1 id="quick-start-title">&iquest;Qu&eacute; deseas <span>realizar hoy?</span></h1>
      <div class="quick-grid">
        <NuxtLink v-for="action in accesos" :key="action.path" :to="link(action.path)" class="quick-card">
          <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path v-for="(d, index) in action.paths" :key="index" :d="d" />
          </svg>
          <span>{{ action.label }}</span>
        </NuxtLink>
      </div>
      <p v-if="!accesos.length" class="quick-empty">Los accesos se mostrar&aacute;n seg&uacute;n los m&oacute;dulos habilitados para tu cuenta.</p>
    </section>
    <header class="workspace-header">
      <div>
        <p class="workspace-section">Gesti&oacute;n asistencial</p>
        <h2 class="dash-title">Resumen hospitalario</h2>
        <p class="dash-subtitle">{{ fechaLarga }}</p>
      </div>
      <div class="workspace-actions">
        <span class="update-time" role="status">{{ cargando ? 'Actualizando...' : ultimaActualizacion ? `Actualizado ${ultimaActualizacion}` : 'Sin actualizar' }}</span>
        <button class="btn-secondary" :disabled="cargando" @click="cargar">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" :class="{ 'animate-spin': cargando }" />
          Actualizar
        </button>
      </div>
    </header>
    <div class="section-heading"><h2>Estado de la atenci&oacute;n</h2><span>Jornada actual</span></div>

    <!-- ============ ERROR ============ -->
    <div v-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <!-- ============ KPIs ============ -->
    <section v-if="tarjetas.length" class="stats-row">
      <NuxtLink
        v-for="t in tarjetas"
        :key="t.label"
        :to="link(t.path)"
        class="stat-card"

      >
        <div class="stat-top">
          <div class="stat-icon">
            <UIcon :name="t.icon" class="w-5 h-5"  />
          </div>
          <span v-if="t.badge" class="stat-badge" :class="{ 'stat-badge--alert': t.alerta }">{{ t.badge }}</span>
        </div>
        <span class="stat-num">{{ cargando ? '—' : t.valor }}</span>
        <span class="stat-label">{{ t.label }}</span>
        <div v-if="t.progreso !== undefined" class="stat-progress">
          <div class="stat-progress-fill" :style="{ width: t.progreso + '%', background: t.color }" />
        </div>
        <span v-else-if="t.hint" class="stat-hint">{{ t.hint }}</span>
      </NuxtLink>
    </section>

    <!-- ============ CHARTS ROW ============ -->
    <section v-if="tarjetas.length" class="charts-row">
      <!-- Curva de movimiento semanal -->
      <div v-if="serieChart" class="panel chart-panel chart-panel--wide">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-presentation-chart-line" class="w-4 h-4" />
            {{ serieChart.titulo }}
          </h2>
          <span class="panel-tag panel-tag--accent">
            <UIcon name="i-heroicons-check-circle" class="w-3 h-3" /> Datos reales · 7 días
          </span>
        </div>
        <div class="chart-body">
          <ClientOnly>
            <ApexChart type="area" height="260" :options="serieChartOptions" :series="serieChart.series" />
          </ClientOnly>
        </div>
      </div>

      <!-- Ocupación de camas -->
      <div v-if="puedeHospitalizacion" class="panel chart-panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" />
            Ocupación de camas
          </h2>
          <span class="panel-tag">Hoy</span>
        </div>
        <div class="chart-body">
          <ClientOnly>
            <ApexChart type="radialBar" height="200" :options="ocupacionChartOptions" :series="[ocupacionPct]" />
          </ClientOnly>
          <div class="donut-legend">
            <div class="legend-item">
              <span class="legend-dot" :style="{ background: ACCENT }" />
              <span>Ocupadas</span>
              <b>{{ kpis.camas_ocupadas }}</b>
            </div>
            <div class="legend-item">
              <span class="legend-dot" :style="{ background: GRIS }" />
              <span>No ocupadas</span>
              <b>{{ Math.max(kpis.camas_total - kpis.camas_ocupadas, 0) }}</b>
            </div>
          </div>
        </div>
      </div>

      <!-- Citas de hoy -->
      <div v-if="puedeConsultaExterna" class="panel chart-panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-clipboard-document-check" class="w-4 h-4" />
            Citas de hoy
          </h2>
          <span class="panel-tag">{{ kpis.citas_hoy_total }} total</span>
        </div>
        <div class="chart-body">
          <ClientOnly>
            <ApexChart
              v-if="kpis.citas_hoy_total"
              type="donut"
              height="200"
              :options="citasChartOptions"
              :series="[kpis.citas_hoy_atendidas, kpis.citas_hoy_pendientes]"
            />
            <p v-else class="empty-hint">Sin citas programadas para hoy.</p>
          </ClientOnly>
        </div>
      </div>
    </section>

    <!-- ============ SECOND CHARTS ROW ============ -->
    <section v-if="tarjetas.length" class="charts-row charts-row--secondary">
      <!-- Barras del día -->
      <div v-if="barrasDia.categorias.length" class="panel chart-panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-chart-bar" class="w-4 h-4" />
            Movimiento del día
          </h2>
        </div>
        <div class="chart-body">
          <ClientOnly>
            <ApexChart type="bar" height="200" :options="barrasChartOptions" :series="barrasDia.series" />
          </ClientOnly>
        </div>
      </div>

      <!-- Actividad por hora -->
      <div v-if="puedeAuditoria" class="panel chart-panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-clock" class="w-4 h-4" />
            Actividad por hora
          </h2>
          <span class="panel-tag">últimas 24h</span>
        </div>
        <div class="chart-body">
          <div v-if="totalActividadHora" class="hour-bars">
            <div v-for="h in actividadHora" :key="h.label" class="hour-bar">
              <div
                class="hour-bar-fill"
                :style="{ height: `${20 + hourBarAltura(h.valor)}px`, background: `rgba(100, 149, 237, ${hourBarOpacidad(h.valor)})` }"
                :title="`${h.valor} eventos`"
              />
              <span class="hour-bar-label">{{ h.label }}</span>
            </div>
          </div>
          <p v-else class="empty-hint">Sin actividad registrada en las últimas 24h.</p>
        </div>
      </div>
    </section>

    <!-- ============ DASH GRID ============ -->
    <div class="dash-grid">
      <!-- Actividad reciente -->
      <section v-if="puedeAuditoria" class="panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-document-magnifying-glass" class="w-4 h-4" />
            Actividad reciente
          </h2>
          <NuxtLink :to="link('/app/auditoria/auditoria')" class="panel-link">Ver todo →</NuxtLink>
        </div>
        <div v-if="cargando" class="loading-state">
          <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
        </div>
        <ul v-else-if="actividad.length" class="activity-list">
          <li v-for="a in actividad" :key="a.id" class="activity-item">
            <span class="activity-dot" :class="'dot-' + (a.action || '').toLowerCase()">
              <UIcon :name="iconoAccion(a.action)" class="w-3 h-3" />
            </span>
            <div class="activity-body">
              <span class="activity-text">
                <b>{{ a.user_name || 'Usuario' }}</b> {{ accionTexto(a.action) }}
                <b>{{ a.model }}</b>
              </span>
              <span class="activity-time">{{ formatFechaHora(a.created_at) }}</span>
            </div>
          </li>
        </ul>
        <p v-else class="empty-hint">Sin actividad registrada todavía.</p>
      </section>

      <!-- Pacientes recientes -->
      <section v-if="puedeAdmision" class="panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-user-group" class="w-4 h-4" />
            Pacientes recientes
          </h2>
          <NuxtLink :to="link('/app/admision/pacientes')" class="panel-link">Ver todo →</NuxtLink>
        </div>
        <div v-if="cargando" class="loading-state">
          <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
        </div>
        <ul v-else-if="pacientesRecientes.length" class="patient-list">
          <li v-for="p in pacientesRecientes" :key="p.id" class="patient-item">
            <span class="patient-avatar" :style="{ background: avatarColor(p.nombre) }">{{ iniciales(p.nombre) }}</span>
            <div class="patient-body">
              <span class="patient-text">
                <b>{{ p.nombre }}</b>
                <span class="patient-meta">{{ p.dni ? `DNI ${p.dni}` : 'Sin documento' }} · {{ p.edad }} años</span>
              </span>
              <span class="activity-time">{{ formatFechaHora(p.created_at) }}</span>
            </div>
          </li>
        </ul>
        <p v-else class="empty-hint">Sin pacientes registrados todavía.</p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
const { api } = useApi()
const { link, gruposVisibles } = useHospitalNav()
// Poppins se carga globalmente via assets/css/hospital-theme.css.
const accesos = computed(() => {
  const allowed = new Set(gruposVisibles.value.flatMap(group => group.items.map(item => item.path)))
  return [
    { label: 'Agendar una cita', path: '/app/admision/agendamiento', paths: ['M13 14h38v40H13z M13 25h38 M22 9v10 M42 9v10', 'M25 39h14 M32 32v14'] },
    { label: 'Gestionar pacientes', path: '/app/admision/pacientes', paths: ['M40 21a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z', 'M16 53v-6a16 16 0 0 1 32 0v6H16Z M48 15a7 7 0 0 1 0 14 M52 36a12 12 0 0 1 7 11v6'] },
    { label: 'Consultar el panel de camas', path: '/app/hospitalizacion/panel-camas', paths: ['M9 20v35 M55 31v24 M9 46h46 M9 31h40a6 6 0 0 1 6 6v9', 'M16 25h10v6H16z M32 20h17v11'] },
    { label: 'Atender emergencias', path: '/app/emergencia/atenciones', paths: ['M24 8h16v16h16v16H40v16H24V40H8V24h16V8Z', 'M26 32h12 M32 26v12'] },
    { label: 'Revisar citas pendientes', path: '/app/consulta-externa/citas-por-confirmar', paths: ['M12 14h39v18 M12 14v40h21 M12 25h39 M21 9v10 M42 9v10', 'M57 46a12 12 0 1 1-24 0 12 12 0 0 1 24 0Z M45 39v8l5 3'] },
    { label: 'Consultar laboratorio', path: '/app/laboratorio/ordenes', paths: ['M23 9h18 M27 9v20L13 50q-3 5 3 5h32q6 0 3-5L37 29V9 M21 39h22', 'M27 46h1 M37 49h1'] },
    { label: 'Gestionar recetas', path: '/app/farmacia/recetas', paths: ['M16 8h25l9 9v39H16V8Z M40 8v12h10 M24 37h18 M24 44h14', 'M24 25h10 M29 20v10'] },
  ].filter(action => allowed.has(action.path))
})
const authStore = useAuthStore()

// Paleta del panel: un solo azul (#6495ED) como acento, gris neutro para contexto
const ACCENT = '#00a6bc'
const GRIS = '#c7ccd1'
const INK_SOFT = '#8a97a0'

const tieneAlguno = (codes: string[]) =>
  codes.some(c => authStore.user?.active_modules?.some((p: string) => p === c || p.startsWith(c + '.')) ?? false)

const puedeHospitalizacion = computed(() => tieneAlguno(['hospitalizacion']))
const puedeConsultaExterna = computed(() => tieneAlguno(['consulta_externa']))
const puedeEmergencia = computed(() => tieneAlguno(['emergencia']))
const puedeLaboratorio = computed(() => tieneAlguno(['laboratorio']))
const puedeFarmacia = computed(() => tieneAlguno(['farmacia']))
const puedeAuditoria = computed(() => tieneAlguno(['auditoria']))
const puedeAdmision = computed(() => tieneAlguno(['admision']))

const ultimaActualizacion = ref('')
const cargando = ref(false)
const error = ref('')
const actividad = ref<any[]>([])
const pacientesRecientes = ref<any[]>([])

function iniciales(nombre: string) {
  return (nombre || '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((w: string) => w[0]?.toUpperCase())
    .join('') || '?'
}

const AVATAR_COLORES = ['#e3ecfc', '#e6f3ec', '#faf1e0', '#efeaf7', '#fbeae7']
function avatarColor(nombre: string) {
  let hash = 0
  for (let i = 0; i < (nombre || '').length; i++) hash = nombre.charCodeAt(i) + ((hash << 5) - hash)
  return AVATAR_COLORES[Math.abs(hash) % AVATAR_COLORES.length]
}

interface Kpis {
  camas_total: number
  camas_ocupadas: number
  citas_hoy_total: number
  citas_hoy_pendientes: number
  citas_hoy_atendidas: number
  emergencias_en_atencion: number
  lab_pendientes: number
  recetas_pendientes: number
}
interface PuntoSemana {
  label: string
  ingresos: number
  altas: number
  citas: number
  emergencias: number
}
interface PuntoHora { label: string; valor: number }

const kpis = reactive<Kpis>({
  camas_total: 0,
  camas_ocupadas: 0,
  citas_hoy_total: 0,
  citas_hoy_pendientes: 0,
  citas_hoy_atendidas: 0,
  emergencias_en_atencion: 0,
  lab_pendientes: 0,
  recetas_pendientes: 0,
})
const serieSemana = ref<PuntoSemana[]>([])
const actividadHora = ref<PuntoHora[]>([])

function hoy() {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Lima',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(new Date())
}

const nombreCorto = computed(() => (authStore.user?.name || 'Usuario').split(' ')[0])
const horaActual = new Date().getHours()
const saludo = computed(() =>
  horaActual < 12 ? 'Buenos días' : horaActual < 19 ? 'Buenas tardes' : 'Buenas noches'
)
const fechaLarga = computed(() =>
  new Date().toLocaleDateString('es-PE', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  })
)

function accionTexto(accion: string) {
  const mapa: Record<string, string> = {
    crear: 'creó',
    editar: 'editó',
    actualizar: 'actualizó',
    anular: 'anuló',
    firmar: 'firmó',
    confirmar: 'confirmó',
    dispensar: 'dispensó',
    resultados: 'registró resultados en',
  }
  return mapa[accion] || (accion || 'modificó')
}

function iconoAccion(accion: string) {
  const mapa: Record<string, string> = {
    crear: 'i-heroicons-plus',
    editar: 'i-heroicons-pencil',
    actualizar: 'i-heroicons-arrow-path',
    anular: 'i-heroicons-x-mark',
    firmar: 'i-heroicons-pencil-square',
    confirmar: 'i-heroicons-check',
    dispensar: 'i-heroicons-beaker',
    resultados: 'i-heroicons-clipboard-document-list',
  }
  return mapa[accion] || 'i-heroicons-ellipsis-horizontal'
}

function formatFechaHora(f: string) {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// ============ TARJETAS KPI ============
const tarjetas = computed(() => {
  const items: any[] = []
  if (puedeHospitalizacion.value) {
    items.push({
      label: 'Camas ocupadas',
      valor: `${kpis.camas_ocupadas} / ${kpis.camas_total}`,
      icon: 'i-heroicons-building-office-2',
      color: 'var(--teal)',
      colorSoft: 'var(--teal-soft)',
      path: '/app/hospitalizacion/panel-camas',
      progreso: ocupacionPct.value,
    })
  }
  if (puedeConsultaExterna.value) {
    items.push({
      label: 'Citas de hoy',
      valor: kpis.citas_hoy_total,
      hint: `${kpis.citas_hoy_pendientes} por atender · ${kpis.citas_hoy_atendidas} atendidas`,
      icon: 'i-heroicons-clipboard-document-check',
      color: 'var(--navy)',
      colorSoft: 'rgba(62,92,147,0.1)',
      path: '/app/consulta-externa/citas-por-confirmar',
    })
  }
  if (puedeEmergencia.value) {
    items.push({
      label: 'Emergencias en atención',
      valor: kpis.emergencias_en_atencion,
      icon: 'i-heroicons-exclamation-triangle',
      color: 'var(--alert)',
      colorSoft: 'var(--alert-soft)',
      path: '/app/emergencia/atenciones',
      alerta: kpis.emergencias_en_atencion > 0,
      badge: kpis.emergencias_en_atencion > 0 ? 'Atender' : undefined,
    })
  }
  if (puedeLaboratorio.value) {
    items.push({
      label: 'Órdenes de laboratorio pendientes',
      valor: kpis.lab_pendientes,
      icon: 'i-heroicons-beaker',
      color: 'var(--amber)',
      colorSoft: 'var(--amber-soft)',
      path: '/app/laboratorio/ordenes',
    })
  }
  if (puedeFarmacia.value) {
    items.push({
      label: 'Recetas pendientes',
      valor: kpis.recetas_pendientes,
      icon: 'i-heroicons-document-text',
      color: 'var(--green)',
      colorSoft: 'var(--green-soft)',
      path: '/app/farmacia/recetas',
    })
  }
  return items
})

// ============ GRÁFICOS ============
const ocupacionPct = computed(() => {
  if (!kpis.camas_total) return 0
  return Math.round((kpis.camas_ocupadas / kpis.camas_total) * 100)
})

const ocupacionChartOptions = computed(() => ({
  chart: { fontFamily: 'inherit', sparkline: { enabled: true } },
  colors: [ACCENT],
  plotOptions: {
    radialBar: {
      hollow: { size: '55%' },
      track: { background: '#eef1f2' },
      dataLabels: {
        name: { show: false },
        value: {
          show: true,
          fontSize: '1.5rem',
          fontWeight: 500,
          color: '#101c24',
          offsetY: 8,
          formatter: (v: number) => `${v}%`,
        },
      },
    },
  },
  stroke: { lineCap: 'round' },
}))

const serieChart = computed(() => {
  const datos = serieSemana.value
  if (!datos.length) return null
  const categorias = datos.map(d => d.label)
  if (puedeHospitalizacion.value) {
    return {
      titulo: 'Ingresos y altas de la semana',
      categorias,
      series: [
        { name: 'Ingresos', data: datos.map(d => d.ingresos) },
        { name: 'Altas', data: datos.map(d => d.altas) },
      ],
      colores: [ACCENT, INK_SOFT],
    }
  }
  if (puedeConsultaExterna.value) {
    return {
      titulo: 'Citas de la semana',
      categorias,
      series: [{ name: 'Citas', data: datos.map(d => d.citas) }],
      colores: [ACCENT],
    }
  }
  if (puedeEmergencia.value) {
    return {
      titulo: 'Emergencias de la semana',
      categorias,
      series: [{ name: 'Emergencias', data: datos.map(d => d.emergencias) }],
      colores: [ACCENT],
    }
  }
  return null
})

const serieChartOptions = computed(() => {
  const s = serieChart.value
  return {
    chart: { toolbar: { show: false }, fontFamily: 'inherit', zoom: { enabled: false } },
    colors: s?.colores || [ACCENT],
    stroke: { curve: 'smooth', width: 2.5 },
    fill: {
      type: 'solid', opacity: 0.06,
    },
    markers: { size: 4, strokeWidth: 2, strokeColors: '#fff', hover: { size: 6 } },
    dataLabels: { enabled: false },
    legend: {
      show: (s?.series.length || 0) > 1,
      position: 'top',
      horizontalAlign: 'right',
      fontSize: '12px',
    },
    xaxis: {
      categories: s?.categorias || [],
      labels: { style: { colors: '#8a97a0', fontSize: '11px' } },
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: {
      labels: { style: { colors: '#8a97a0', fontSize: '11px' } },
      forceNiceScale: true,
    },
    grid: { borderColor: '#e6ebef', strokeDashArray: 3 },
    tooltip: { theme: 'light', x: { show: true } },
  }
})

const citasChartOptions = computed(() => ({
  chart: { fontFamily: 'inherit' },
  colors: [ACCENT, GRIS],
  labels: ['Atendidas', 'Pendientes'],
  legend: { position: 'bottom', fontSize: '12px' },
  plotOptions: {
    pie: {
      donut: {
        size: '68%',
        labels: {
          show: true,
          total: {
            show: true,
            label: 'Total',
            color: '#101c24',
            fontSize: '13px',
          },
        },
      },
    },
  },
  stroke: { width: 2, colors: ['#fff'] },
  dataLabels: { enabled: false },
  tooltip: { theme: 'light' },
}))

const barrasDia = computed(() => {
  const datos = serieSemana.value
  const hoyPunto = datos[datos.length - 1]
  if (!hoyPunto) return { categorias: [], series: [] }
  const items: { label: string; valor: number }[] = []
  if (puedeHospitalizacion.value) {
    items.push({ label: 'Ingresos', valor: hoyPunto.ingresos })
    items.push({ label: 'Altas', valor: hoyPunto.altas })
  }
  if (puedeConsultaExterna.value) items.push({ label: 'Citas', valor: hoyPunto.citas })
  if (puedeEmergencia.value) items.push({ label: 'Emergencias', valor: hoyPunto.emergencias })
  return {
    categorias: items.map(i => i.label),
    series: [{ name: 'Hoy', data: items.map(i => i.valor) }],
  }
})

const barrasChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, fontFamily: 'inherit' },
  colors: [ACCENT],
  plotOptions: { bar: { borderRadius: 6, columnWidth: '45%', distributed: false } },
  dataLabels: { enabled: false },
  legend: { show: false },
  xaxis: {
    categories: barrasDia.value.categorias,
    labels: { style: { colors: '#8a97a0', fontSize: '11px' } },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: { labels: { style: { colors: '#8a97a0', fontSize: '11px' } } },
  grid: { borderColor: '#e6ebef', strokeDashArray: 3 },
  tooltip: { theme: 'light' },
}))

// Actividad por hora (auditoría real del tenant, últimas 24h en bloques de 3h)
const totalActividadHora = computed(() => actividadHora.value.reduce((a, h) => a + h.valor, 0))
const maxActividadHora = computed(() => Math.max(...actividadHora.value.map(h => h.valor), 1))
function hourBarAltura(valor: number) {
  return (valor / maxActividadHora.value) * 40
}
function hourBarOpacidad(valor: number) {
  return 0.25 + (valor / maxActividadHora.value) * 0.75
}

// ============ CARGA DE DATOS ============
async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const tareas: Promise<any>[] = []

    tareas.push(
      api<any>('/app/dashboard/resumen').then(d => {
        Object.assign(kpis, d.kpis)
        serieSemana.value = d.serie_semana
        actividadHora.value = d.actividad_por_hora
        pacientesRecientes.value = d.pacientes_recientes
      })
    )

    if (puedeAuditoria.value) {
      tareas.push(
        api<any>('/app/auditoria/auditoria', { query: { page: 1, page_size: 6 } }).then(d => {
          actividad.value = d.items
        })
      )
    }

    await Promise.all(tareas)
    ultimaActualizacion.value = new Date().toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudieron cargar algunos indicadores del escritorio'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
/* ============ CONTENEDOR ============ */
/* Colores y tipografía: heredados de .app-shell (assets/css/hospital-theme.css),
   no se redefinen acá. */
.dash-container {
  background: var(--mist);
  max-width: none;
  min-height: 100%;
  margin: 0 auto;
  padding: 1.5rem 2rem 3rem;
}

.quick-start { max-width:1280px; margin:0 auto; padding:40px 0 48px; }
.quick-start h1 { margin:0 0 52px; text-align:center; color:#081b3d; font-size:clamp(25px, 2.5vw, 36px); font-weight:600; line-height:1.35; letter-spacing:-.7px; }
.quick-start h1 span { color:#009eb2; }
.quick-grid { display:flex; flex-wrap:wrap; justify-content:center; gap:24px; }
.quick-card { flex:0 1 calc((100% - 72px) / 4); min-width:0; min-height:174px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:18px; padding:24px 18px; border:1px solid transparent; border-radius:20px; background:#fff; color:#081b3d; box-shadow:0 16px 30px rgba(22,38,62,.08); text-decoration:none; text-align:center; font-size:16px; font-weight:400; line-height:1.4; transition:border-color .15s, box-shadow .15s; }
.quick-card svg { width:66px; height:66px; color:#00abc4; flex-shrink:0; }
.quick-card:hover { border-color:#00abc4; box-shadow:0 12px 24px rgba(22,38,62,.12); }
.quick-empty { text-align:center; color:var(--ink-soft); font-size:14px; }
@media(max-width:1100px) { .quick-card { flex-basis:calc((100% - 24px) / 2); } }
@media(max-width:540px) { .quick-start { padding:20px 0 32px; } .quick-start h1 { margin-bottom:28px; } .quick-grid { gap:14px; } .quick-card { flex-basis:100%; min-height:148px; } }
.workspace-header { display:flex; justify-content:space-between; align-items:center; gap:24px; padding:4px 0 24px; margin-bottom:24px; border-bottom:1px solid var(--line); }
.workspace-section { font-size:12px; color:var(--ink-soft); margin:0 0 6px; }
.dash-title { font-size:24px; line-height:1.3; font-weight:600; color:var(--ink); margin:0; }
.dash-subtitle { font-size:13px; color:var(--ink-soft); margin:8px 0 0; }
.dash-subtitle::first-letter { text-transform:uppercase; }
.workspace-actions { display:flex; align-items:center; gap:16px; flex-wrap:wrap; }
.update-time { font-size:12px; color:var(--ink-soft); }
.btn-secondary { display:inline-flex; align-items:center; gap:8px; background:var(--paper); border:1px solid var(--line); border-radius:6px; padding:9px 14px; color:var(--ink); font-size:13px; cursor:pointer; }
.btn-secondary:hover { background:var(--mist); }
.btn-secondary:disabled { opacity:.6; cursor:wait; }
.section-heading { display:flex; justify-content:space-between; gap:12px; align-items:center; margin-bottom:12px; }
.section-heading h2 { font-size:14px; font-weight:500; margin:0; }
.section-heading span { color:var(--ink-soft); font-size:12px; }
a:focus-visible, button:focus-visible { outline:2px solid var(--teal); outline-offset:3px; }

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  background: var(--alert-soft);
  color: var(--alert);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

.empty-hint {
  color: var(--ink-soft);
  font-size: 0.875rem;
  padding: 1rem 0;
}

/* ============ KPIs ============ */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  padding: 1.125rem 1.25rem;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--paper);
  box-shadow: none;
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  border-color: var(--teal);
  background: #f9fbfd;
}

.stat-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-icon {
  width: 24px;
  height: 24px;
  color: var(--ink-soft);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-badge {
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--ink-soft);
  background: var(--mist);
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
}

.stat-badge--alert {
  color: var(--alert);
  background: var(--alert-soft);
}

.stat-num {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--ink);
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
  font-weight: 500;
}

.stat-hint {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  opacity: 0.85;
}

.stat-progress {
  height: 4px;
  border-radius: 999px;
  background: var(--mist);
  overflow: hidden;
  margin-top: 0.125rem;
}

.stat-progress-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.6s ease;
}

/* ============ CHARTS ============ */
.charts-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: stretch;
}

.charts-row--secondary {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.chart-panel {
  display: flex;
  flex-direction: column;
  min-height: 300px;
}

.chart-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.chart-panel--wide {
  grid-column: span 2;
}

@media (max-width: 900px) {
  .charts-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .chart-panel--wide {
    grid-column: span 2;
  }
}

.panel-tag {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--ink-soft);
  background: var(--mist);
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
}

.panel-tag--accent {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--teal);
  background: var(--teal-soft);
}

.donut-legend {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.legend-item b {
  margin-left: 0.25rem;
  color: var(--ink);
  font-weight: 500;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  flex-shrink: 0;
}

/* ============ ACTIVIDAD POR HORA ============ */
.hour-bars {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 0.375rem;
  padding-top: 0.25rem;
}

.hour-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.hour-bar-fill {
  width: 100%;
  border-radius: 6px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.hour-bar-fill:hover {
  transform: scale(1.08);
}

.hour-bar-label {
  font-size: 0.625rem;
  color: var(--ink-soft);
}

/* ============ PANELS ============ */
.dash-grid {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 1.25rem;
  align-items: start;
}

.panel {
  background: var(--paper);
  border-radius: 8px;
  border: 1px solid var(--line);
  padding: 1.25rem;
  min-width: 0;
  box-shadow: none;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.panel-title {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--ink);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.panel-link {
  font-size: 0.75rem;
  color: var(--teal);
  text-decoration: none;
  font-weight: 600;
}

.panel-link:hover {
  text-decoration: underline;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

/* ============ ACTIVITY ============ */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.activity-dot {
  width: 26px;
  height: 26px;
  border-radius: 999px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--teal-soft, rgba(100, 149, 237, 0.12));
  color: var(--teal);
  margin-top: 0.125rem;
}

.dot-anular {
  background: var(--alert-soft);
  color: var(--alert);
}

.dot-crear {
  background: var(--green-soft);
  color: var(--green);
}

.dot-firmar,
.dot-confirmar {
  background: var(--amber-soft);
  color: var(--amber);
}

.activity-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.activity-text {
  font-size: 0.8125rem;
  color: var(--ink);
  line-height: 1.4;
}

.activity-text b {
  font-weight: 600;
}

.activity-time {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  margin-top: 0.125rem;
}

/* ============ PACIENTES RECIENTES ============ */
.patient-list {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.patient-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.patient-avatar {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--ink);
}

.patient-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.patient-text {
  font-size: 0.8125rem;
  color: var(--ink);
  line-height: 1.4;
  display: flex;
  flex-direction: column;
}

.patient-meta {
  font-size: 0.75rem;
  color: var(--ink-soft);
  font-weight: 400;
}

/* ============ RESPONSIVE ============ */
@media (max-width: 900px) {
  .dash-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .dash-container {
    padding: 1rem 1rem 2rem;
  }

  .workspace-header { align-items:flex-start; flex-direction:column; gap:16px; }
  .chart-panel--wide { grid-column: span 1; }
  .dash-title {
    font-size: 1.5rem;
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .chart-panel {
    min-height: 0;
  }

  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
