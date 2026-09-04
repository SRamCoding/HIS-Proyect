<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Escritorio', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const tenant = route.query.tenant as string

const data = ref<any>(null)
const loading = ref(true)
const error = ref('')

const cargarDashboard = async () => {
  loading.value = true
  error.value = ''
  try {
    data.value = await api('/sigarh/dashboard')
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar el dashboard'
  } finally {
    loading.value = false
  }
}

onMounted(cargarDashboard)

const porcentajeAsistencia = computed(() => {
  if (!data.value?.total_empleados) return 0
  return Math.round((data.value.asistencia_hoy / data.value.total_empleados) * 100)
})

const porcentajeCamas = computed(() => {
  if (!data.value?.camas?.total) return 0
  return Math.round((data.value.camas.ocupadas / data.value.camas.total) * 100)
})

const totalPendientes = computed(() => {
  if (!data.value?.pendientes) return 0
  return (data.value.pendientes.vacaciones + data.value.pendientes.licencias + data.value.pendientes.papeletas)
})

const estadoColor: Record<string, string> = {
  pendiente: '#f59e0b',
  aprobado: '#10b981',
  rechazado: '#ef4444',
}

const hoy = new Date().toLocaleDateString('es-PE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

const getEmployeeColor = (name: string) => {
  const colors = [
    'var(--teal-soft)',
    'var(--purple-soft)',
    'var(--navy-soft)',
    'var(--amber-soft)',
    'var(--green-soft)',
    'var(--pink-soft)',
    'var(--blue-soft)',
    'var(--orange-soft)'
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const getInitials = (name: string) => {
  if (!name || name === '—') return '?'
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

// ── Datos para gráficos ──
const empleadosPorMes = computed(() => data.value?.empleados_por_mes || [])
const areaChartSeries = computed(() => [
  { name: 'Empleados', data: empleadosPorMes.value.map((m: any) => m.valor) },
])
const areaChartCategories = computed(() => empleadosPorMes.value.map((m: any) => m.label))

const distribucionGenero = computed(() => ({
  masculino: data.value?.distribucion_genero?.masculino || 0,
  femenino: data.value?.distribucion_genero?.femenino || 0,
}))

const distribucionEstado = computed(() => ({
  activos: data.value?.empleados_activos || 0,
  inactivos: (data.value?.total_empleados || 0) - (data.value?.empleados_activos || 0),
  vacaciones: data.value?.estado_empleados?.vacaciones || 0,
  licencias: data.value?.estado_empleados?.licencias || 0,
}))

const asistenciaSemanal = computed(() => data.value?.asistencia_semanal || [])
const maxAsistencia = computed(() => {
  const values = asistenciaSemanal.value.map((d: any) => d.asistencia)
  return Math.max(...values, 1)
})

const tendenciasSolicitudes = computed(() => data.value?.tendencias_solicitudes || [])

// ── ApexCharts ──
const areaOptions = computed(() => ({
  chart: {
    toolbar: { show: false },
    fontFamily: 'IBM Plex Sans, sans-serif',
    zoom: { enabled: false },
  },
  colors: ['#0891b2'],
  stroke: { curve: 'smooth', width: 3 },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.35,
      opacityTo: 0.03,
      stops: [0, 90, 100],
    },
  },
  markers: {
    size: 4,
    colors: ['#fff'],
    strokeColors: '#0891b2',
    strokeWidth: 2,
    hover: { size: 6 },
  },
  dataLabels: { enabled: false },
  xaxis: {
    categories: areaChartCategories.value,
    labels: { style: { colors: '#4a5c66', fontSize: '12px' } },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: { labels: { style: { colors: '#4a5c66', fontSize: '11px' } } },
  grid: { borderColor: '#dce5e7', strokeDashArray: 3 },
  tooltip: { theme: 'light' },
}))

const donutOptions = computed(() => ({
  chart: { fontFamily: 'IBM Plex Sans, sans-serif' },
  colors: ['#0891b2', '#6366f1'],
  labels: ['Masculino', 'Femenino'],
  legend: { position: 'bottom', fontSize: '12px' },
  plotOptions: {
    pie: {
      donut: {
        size: '70%',
        labels: {
          show: true,
          total: { show: true, label: 'Total', color: '#1a2e3b', fontSize: '14px' },
        },
      },
    },
  },
  stroke: { width: 0 },
  dataLabels: { enabled: false },
}))

const donutEstadoOptions = computed(() => ({
  chart: { fontFamily: 'IBM Plex Sans, sans-serif' },
  colors: ['#10b981', '#6b7280', '#f59e0b', '#0891b2'],
  labels: ['Activos', 'Inactivos', 'Vacaciones', 'Licencias'],
  legend: { position: 'bottom', fontSize: '11px' },
  plotOptions: {
    pie: {
      donut: {
        size: '70%',
        labels: {
          show: true,
          total: { show: true, label: 'Total', color: '#1a2e3b', fontSize: '14px' },
        },
      },
    },
  },
  stroke: { width: 0 },
  dataLabels: { enabled: false },
}))
</script>

<template>
  <div class="dashboard-sigarh-container">
    <!-- Header con saludo personalizado -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-chart-bar" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <h1 class="page-title">Escritorio SIGARH</h1>
          <p class="page-subtitle capitalize">{{ hoy }}</p>
        </div>
      </div>
      <div v-if="totalPendientes > 0" class="alert-badge">
        <UIcon name="i-heroicons-bell-alert" class="w-4 h-4" />
        <span>{{ totalPendientes }} solicitudes pendientes</span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-grid">
      <div v-for="i in 4" :key="i" class="skeleton-card" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <template v-else-if="data">
      <!-- Fila 1: KPIs principales -->
      <div class="kpi-grid">
        <!-- Total Empleados -->
        <div class="kpi-card" style="border-left: 4px solid var(--navy)">
          <div class="kpi-content">
            <div>
              <span class="kpi-label">Total Empleados</span>
              <span class="kpi-value">{{ data.total_empleados }}</span>
              <span class="kpi-sub">
                <span class="text-green-600 font-medium">{{ data.empleados_activos }}</span> activos
                <span class="trend-up">↑ 12 este mes</span>
              </span>
            </div>
            <div class="kpi-icon" style="background: var(--navy-soft)">
              <UIcon name="i-heroicons-users" class="w-5 h-5" style="color: var(--navy)" />
            </div>
          </div>
        </div>

        <!-- Asistencia Hoy -->
        <div class="kpi-card" style="border-left: 4px solid var(--green)">
          <div class="kpi-content">
            <div>
              <span class="kpi-label">Asistencia Hoy</span>
              <span class="kpi-value">{{ data.asistencia_hoy }}</span>
              <span class="kpi-sub">
                <span class="font-medium" :style="{ color: porcentajeAsistencia >= 80 ? 'var(--green)' : 'var(--amber)' }">
                  {{ porcentajeAsistencia }}%
                </span> del personal
              </span>
            </div>
            <div class="kpi-icon" style="background: var(--green-soft)">
              <UIcon name="i-heroicons-clipboard-document-check" class="w-5 h-5" style="color: var(--green)" />
            </div>
          </div>
          <div class="kpi-progress">
            <div class="progress-bar" :style="{ width: porcentajeAsistencia + '%', background: porcentajeAsistencia >= 80 ? 'var(--green)' : 'var(--amber)' }" />
          </div>
        </div>

        <!-- Solicitudes Pendientes -->
        <div class="kpi-card" style="border-left: 4px solid var(--amber)">
          <div class="kpi-content">
            <div>
              <span class="kpi-label">Solicitudes Pendientes</span>
              <span class="kpi-value">{{ totalPendientes }}</span>
              <div class="kpi-badges">
                <span class="badge-mini" style="background: var(--amber-soft); color: var(--amber)">V:{{ data.pendientes.vacaciones }}</span>
                <span class="badge-mini" style="background: var(--teal-soft); color: var(--teal)">L:{{ data.pendientes.licencias }}</span>
                <span class="badge-mini" style="background: var(--purple-soft); color: var(--purple)">P:{{ data.pendientes.papeletas }}</span>
              </div>
            </div>
            <div class="kpi-icon" style="background: var(--amber-soft)">
              <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" />
            </div>
          </div>
        </div>

        <!-- Justificaciones Pendientes -->
        <div class="kpi-card" style="border-left: 4px solid var(--purple)">
          <div class="kpi-content">
            <div>
              <span class="kpi-label">Justificaciones Pend.</span>
              <span class="kpi-value">{{ data.justificaciones_pendientes }}</span>
              <span class="kpi-sub">Por revisar</span>
            </div>
            <div class="kpi-icon" style="background: var(--purple-soft)">
              <UIcon name="i-heroicons-document-text" class="w-5 h-5" style="color: var(--purple)" />
            </div>
          </div>
        </div>
      </div>

      <!-- Fila 2: Gráficos principales -->
      <div class="row-charts-grid">
        <!-- Tendencias de solicitudes -->
        <div class="chart-card">
          <div class="card-header-simple">
            <h3 class="card-title-simple">Tendencias de solicitudes</h3>
            <span class="card-badge">Últimos 6 meses</span>
          </div>
          <ClientOnly>
            <ApexChart
              type="area"
              height="220"
              :options="areaOptions"
              :series="areaChartSeries"
            />
          </ClientOnly>
        </div>

        <!-- Distribución por estado -->
        <div class="chart-card">
          <div class="card-header-simple">
            <h3 class="card-title-simple">Empleados por estado</h3>
            <span class="card-badge">Distribución</span>
          </div>
          <div class="chart-container">
            <ClientOnly>
              <ApexChart
                type="donut"
                height="180"
                :options="donutEstadoOptions"
                :series="[distribucionEstado.activos, distribucionEstado.inactivos, distribucionEstado.vacaciones, distribucionEstado.licencias]"
              />
            </ClientOnly>
          </div>
          <div class="estado-legend">
            <div class="legend-item">
              <span class="legend-dot" style="background: var(--green)" />
              <span class="legend-label">Activos</span>
              <span class="legend-value">{{ distribucionEstado.activos }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: var(--ink-soft)" />
              <span class="legend-label">Inactivos</span>
              <span class="legend-value">{{ distribucionEstado.inactivos }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: var(--amber)" />
              <span class="legend-label">Vacaciones</span>
              <span class="legend-value">{{ distribucionEstado.vacaciones }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: var(--teal)" />
              <span class="legend-label">Licencias</span>
              <span class="legend-value">{{ distribucionEstado.licencias }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Fila 3: Asistencia mensual + Movimientos -->
      <div class="row-three-grid">
        <!-- Asistencia mensual -->
        <div class="asistencia-card">
          <div class="card-header-simple">
            <h3 class="card-title-simple">Asistencia mensual</h3>
            <span class="card-badge">Últimas 5 semanas</span>
          </div>
          <div v-if="!asistenciaSemanal.length" class="empty-state-small">
            <UIcon name="i-heroicons-clipboard-document-check" class="w-8 h-8" style="color: var(--ink-soft)" />
            <span>Sin datos de asistencia</span>
          </div>
          <div v-else class="asistencia-bars">
            <div v-for="dia in asistenciaSemanal" :key="dia.dia" class="asistencia-bar-item">
              <span class="asistencia-value">{{ dia.asistencia }}</span>
              <div class="bar-wrapper">
                <div
                  class="asistencia-bar-fill"
                  :style="{
                    height: (dia.asistencia / maxAsistencia) * 100 + '%',
                    background: dia.asistencia / maxAsistencia > 0.8 ? 'var(--green)' : 'var(--amber)'
                  }"
                />
              </div>
              <span class="asistencia-label">{{ dia.dia.slice(0, 3) }}</span>
            </div>
          </div>
        </div>

        <!-- Movimientos del mes -->
        <div class="movimientos-card">
          <div class="card-header-simple">
            <h3 class="card-title-simple">Movimientos del Mes</h3>
            <span class="card-badge">Actualizado</span>
          </div>
          <div class="movimientos-grid">
            <NuxtLink :to="`/sigarh/movimientos/vacaciones?tenant=${tenant}`" class="movimiento-item">
              <div class="movimiento-icon" style="background: var(--orange-soft)">
                <UIcon name="i-heroicons-sun" class="w-4 h-4" style="color: var(--orange)" />
              </div>
              <div>
                <span class="movimiento-value">{{ data.movimientos_mes.vacaciones }}</span>
                <span class="movimiento-label">Vacaciones</span>
                <span class="movimiento-trend trend-up">↑ 18%</span>
              </div>
            </NuxtLink>

            <NuxtLink :to="`/sigarh/movimientos/licencias?tenant=${tenant}`" class="movimiento-item">
              <div class="movimiento-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-paper-airplane" class="w-4 h-4" style="color: var(--teal)" />
              </div>
              <div>
                <span class="movimiento-value">{{ data.movimientos_mes.licencias }}</span>
                <span class="movimiento-label">Licencias</span>
                <span class="movimiento-trend trend-down">↓ 6%</span>
              </div>
            </NuxtLink>

            <NuxtLink :to="`/sigarh/movimientos/papeletas/estado?tenant=${tenant}`" class="movimiento-item">
              <div class="movimiento-icon" style="background: var(--purple-soft)">
                <UIcon name="i-heroicons-document-duplicate" class="w-4 h-4" style="color: var(--purple)" />
              </div>
              <div>
                <span class="movimiento-value">{{ data.movimientos_mes.papeletas }}</span>
                <span class="movimiento-label">Papeletas</span>
                <span class="movimiento-trend trend-down">↓ 11%</span>
              </div>
            </NuxtLink>

            <NuxtLink :to="`/sigarh/movimientos/cambio-turno/estado?tenant=${tenant}`" class="movimiento-item">
              <div class="movimiento-icon" style="background: var(--navy-soft)">
                <UIcon name="i-heroicons-arrows-right-left" class="w-4 h-4" style="color: var(--navy)" />
              </div>
              <div>
                <span class="movimiento-value">{{ data.movimientos_mes.cambios_turno }}</span>
                <span class="movimiento-label">Cambios Turno</span>
                <span class="movimiento-trend trend-down">↓ 8%</span>
              </div>
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Fila 4: Últimas solicitudes -->
      <div class="row-four-grid">
        <!-- Últimas Vacaciones -->
        <div class="solicitudes-card">
          <div class="card-header-simple">
            <h3 class="card-title-simple">Últimas Vacaciones</h3>
            <NuxtLink :to="`/sigarh/movimientos/vacaciones?tenant=${tenant}`" class="link-ver-todas">
              Ver todas
            </NuxtLink>
          </div>
          <div v-if="!data.ultimas_vacaciones.length" class="empty-state-small">
            <UIcon name="i-heroicons-sun" class="w-8 h-8" style="color: var(--ink-soft)" />
            <span>No hay solicitudes recientes</span>
          </div>
          <div v-else class="solicitudes-list">
            <div v-for="v in data.ultimas_vacaciones" :key="v.id" class="solicitud-item">
              <div class="solicitud-avatar" :style="{ background: getEmployeeColor(v.empleado_nombre || '') }">
                <span>{{ getInitials(v.empleado_nombre || '—') }}</span>
              </div>
              <div class="solicitud-info">
                <span class="solicitud-nombre">{{ v.empleado_nombre || 'Empleado' }}</span>
                <span class="solicitud-detalle">{{ v.tipo }} · {{ v.fecha_inicio }} → {{ v.fecha_fin }}</span>
              </div>
              <span class="solicitud-estado" :style="{ background: estadoColor[v.estado] || '#6b7280', color: '#fff' }">
                {{ v.estado }}
              </span>
            </div>
          </div>
        </div>

        <!-- Últimas Licencias -->
        <div class="solicitudes-card">
          <div class="card-header-simple">
            <h3 class="card-title-simple">Últimas Licencias</h3>
            <NuxtLink :to="`/sigarh/movimientos/licencias?tenant=${tenant}`" class="link-ver-todas">
              Ver todas
            </NuxtLink>
          </div>
          <div v-if="!data.ultimas_licencias.length" class="empty-state-small">
            <UIcon name="i-heroicons-paper-airplane" class="w-8 h-8" style="color: var(--ink-soft)" />
            <span>No hay licencias recientes</span>
          </div>
          <div v-else class="solicitudes-list">
            <div v-for="l in data.ultimas_licencias" :key="l.id" class="solicitud-item">
              <div class="solicitud-avatar" :style="{ background: getEmployeeColor(l.empleado_nombre || '') }">
                <span>{{ getInitials(l.empleado_nombre || '—') }}</span>
              </div>
              <div class="solicitud-info">
                <span class="solicitud-nombre">{{ l.empleado_nombre || 'Empleado' }}</span>
                <span class="solicitud-detalle">Tramitada: {{ l.fecha_tramite }}</span>
              </div>
              <span class="solicitud-estado" :style="{ background: estadoColor[l.estado] || '#6b7280', color: '#fff' }">
                {{ l.estado }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Fila 5: Accesos rápidos -->
      <div class="accesos-card">
        <h3 class="card-title-simple">Accesos Rápidos</h3>
        <div class="accesos-grid">
          <NuxtLink
            v-for="acceso in [
              { label: 'Empleados', icon: 'i-heroicons-users', path: '/sigarh/rrhh/empleados' },
              { label: 'Asistencia', icon: 'i-heroicons-clipboard-document-check', path: '/sigarh/rrhh/asistencia' },
              { label: 'Vacaciones', icon: 'i-heroicons-sun', path: '/sigarh/movimientos/vacaciones' },
              { label: 'Licencias', icon: 'i-heroicons-paper-airplane', path: '/sigarh/movimientos/licencias' },
              { label: 'Camas', icon: 'i-heroicons-home', path: '/sigarh/infraestructura-hosp/camas' },
              { label: 'CIE-10', icon: 'i-heroicons-document-magnifying-glass', path: '/sigarh/general/cie10' },
            ]"
            :key="acceso.path"
            :to="`${acceso.path}?tenant=${tenant}`"
            class="acceso-item"
          >
            <div class="acceso-icon" style="background: var(--navy-soft)">
              <UIcon :name="acceso.icon" class="w-4 h-4" style="color: var(--navy)" />
            </div>
            <span class="acceso-label">{{ acceso.label }}</span>
          </NuxtLink>
        </div>
      </div>

      <!-- Fila 6: Estado de Camas (nuevo) -->
      <div v-if="data.camas" class="camas-row">
        <div class="camas-card-full">
          <div class="card-header-simple">
            <h3 class="card-title-simple">Estado de Camas</h3>
            <NuxtLink :to="`/sigarh/infraestructura-hosp/camas?tenant=${tenant}`" class="link-ver-todas">
              Ver todas
            </NuxtLink>
          </div>

          <div v-if="data.camas.total === 0" class="empty-state-small">
            <UIcon name="i-heroicons-home" class="w-8 h-8" style="color: var(--ink-soft)" />
            <span>No hay camas registradas</span>
          </div>

          <div v-else class="camas-content">
            <div class="camas-ring-container">
              <div class="camas-ring">
                <svg viewBox="0 0 120 120" class="ring-svg">
                  <circle cx="60" cy="60" r="52" fill="none" stroke="var(--mist)" stroke-width="8" />
                  <circle
                    cx="60" cy="60" r="52" fill="none"
                    stroke="var(--navy)"
                    stroke-width="8"
                    stroke-linecap="round"
                    :stroke-dasharray="`${(porcentajeCamas / 100) * 326.7} 326.7`"
                    :style="{ transform: 'rotate(-90deg)', transformOrigin: 'center' }"
                  />
                </svg>
                <div class="ring-center">
                  <span class="ring-percentage">{{ porcentajeCamas }}%</span>
                  <span class="ring-label">Ocupación</span>
                </div>
              </div>

              <div class="camas-legend">
                <div class="legend-item">
                  <span class="legend-dot" style="background: var(--green)" />
                  <span class="legend-label">Disponibles</span>
                  <span class="legend-value">{{ data.camas.disponibles }}</span>
                </div>
                <div class="legend-item">
                  <span class="legend-dot" style="background: var(--alert)" />
                  <span class="legend-label">Ocupadas</span>
                  <span class="legend-value">{{ data.camas.ocupadas }}</span>
                </div>
                <div class="legend-item">
                  <span class="legend-dot" style="background: var(--amber)" />
                  <span class="legend-label">Mantenimiento</span>
                  <span class="legend-value">{{ data.camas.mantenimiento }}</span>
                </div>
                <div class="legend-divider" />
                <div class="legend-item total">
                  <span class="legend-label">Total</span>
                  <span class="legend-value total-value">{{ data.camas.total }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dashboard-sigarh-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
  line-height: 1.2;
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
}

.alert-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  background: var(--amber-soft);
  border: 1px solid var(--amber-soft);
  color: var(--amber);
  font-size: 0.8125rem;
  font-weight: 500;
}

/* Loading */
.loading-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.skeleton-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1.5rem;
  height: 120px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Error */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: var(--radius);
  background: var(--alert-soft);
  color: var(--alert);
  font-size: 0.875rem;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.kpi-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.kpi-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.kpi-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-soft);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.kpi-value {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.2;
  margin-top: 0.25rem;
}

.kpi-sub {
  display: block;
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin-top: 0.25rem;
}

.trend-up {
  color: var(--green);
  margin-left: 0.25rem;
}

.trend-down {
  color: var(--alert);
  margin-left: 0.25rem;
}

.kpi-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-badges {
  display: flex;
  gap: 0.25rem;
  margin-top: 0.25rem;
}

.badge-mini {
  padding: 0.0625rem 0.375rem;
  border-radius: 8px;
  font-size: 0.625rem;
  font-weight: 600;
}

.kpi-progress {
  margin-top: 0.75rem;
  height: 4px;
  border-radius: 2px;
  background: var(--mist);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.6s ease;
}

/* Charts Row */
.row-charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.chart-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow-sm);
}

.chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Estado Legend */
.estado-legend {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.25rem 0.75rem;
  margin-top: 0.5rem;
  width: 100%;
}

.estado-legend .legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.estado-legend .legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.estado-legend .legend-label {
  flex: 1;
  color: var(--ink-soft);
}

.estado-legend .legend-value {
  font-weight: 600;
  color: var(--ink);
}

/* Asistencia mensual */
.asistencia-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow-sm);
}

.asistencia-bars {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 160px;
  padding-top: 0.5rem;
}

.asistencia-bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  gap: 0.25rem;
}

.bar-wrapper {
  display: flex;
  align-items: flex-end;
  height: 100px;
  width: 100%;
  max-width: 40px;
}

.asistencia-bar-fill {
  width: 100%;
  min-height: 4px;
  border-radius: 4px 4px 0 0;
  transition: height 0.6s ease;
}

.asistencia-label {
  font-size: 0.625rem;
  color: var(--ink-soft);
  font-weight: 500;
}

.asistencia-value {
  font-size: 0.625rem;
  color: var(--ink-soft);
}

/* Movimientos */
.movimientos-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow-sm);
}

.card-header-simple {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-title-simple {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.card-badge {
  font-size: 0.625rem;
  font-weight: 500;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  background: var(--green-soft);
  color: var(--green);
}

.link-ver-todas {
  font-size: 0.75rem;
  color: var(--teal);
  text-decoration: none;
}

.link-ver-todas:hover {
  text-decoration: underline;
}

.movimientos-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.movimiento-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  text-decoration: none;
  transition: all 0.15s ease;
  position: relative;
}

.movimiento-item:hover {
  background: var(--mist);
  border-color: var(--teal);
}

.movimiento-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.movimiento-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--ink);
  display: block;
  line-height: 1.2;
}

.movimiento-label {
  font-size: 0.6875rem;
  color: var(--ink-soft);
}

.movimiento-trend {
  font-size: 0.5625rem;
  font-weight: 600;
  display: block;
}

.trend-up {
  color: var(--green);
}

.trend-down {
  color: var(--alert);
}

.movimiento-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  padding: 0.125rem 0.375rem;
  border-radius: 10px;
  font-size: 0.5625rem;
  font-weight: 700;
  background: var(--alert);
  color: white;
}

/* Row Three */
.row-three-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

/* Row Four */
.row-four-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

/* Solicitudes */
.solicitudes-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow-sm);
}

.solicitudes-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.solicitud-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  transition: all 0.15s ease;
}

.solicitud-item:hover {
  background: var(--mist);
}

.solicitud-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--ink);
  flex-shrink: 0;
}

.solicitud-info {
  flex: 1;
  min-width: 0;
}

.solicitud-nombre {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.solicitud-detalle {
  display: block;
  font-size: 0.6875rem;
  color: var(--ink-soft);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.solicitud-estado {
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: capitalize;
  flex-shrink: 0;
}

/* Accesos Rápidos */
.accesos-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow-sm);
  margin-bottom: 1.5rem;
}

.accesos-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.75rem;
  margin-top: 1rem;
}

.acceso-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  text-decoration: none;
  transition: all 0.15s ease;
}

.acceso-item:hover {
  background: var(--mist);
  border-color: var(--teal);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.acceso-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.acceso-label {
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--ink-soft);
  text-align: center;
}

/* Camas Row */
.camas-row {
  margin-bottom: 1.5rem;
}

.camas-card-full {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow-sm);
}

.camas-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.camas-ring-container {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  width: 100%;
}

.camas-ring {
  position: relative;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.ring-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ring-percentage {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.2;
}

.ring-label {
  font-size: 0.625rem;
  color: var(--ink-soft);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.camas-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  color: var(--ink-soft);
}

.legend-value {
  font-weight: 600;
  color: var(--ink);
}

.legend-divider {
  height: 1px;
  background: var(--line);
  margin: 0.25rem 0;
}

.legend-item.total {
  font-weight: 600;
}

.legend-item.total .legend-label {
  color: var(--ink);
}

.total-value {
  font-size: 0.9375rem;
}

.empty-state-small {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem 0;
  color: var(--ink-soft);
  font-size: 0.875rem;
}

.empty-state-small .w-8 {
  opacity: 0.5;
}

/* Responsive */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .row-charts-grid {
    grid-template-columns: 1fr;
  }

  .row-three-grid {
    grid-template-columns: 1fr;
  }

  .row-four-grid {
    grid-template-columns: 1fr;
  }

  .accesos-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .camas-content {
    flex-direction: column;
    align-items: stretch;
  }

  .camas-ring-container {
    flex-direction: row;
    justify-content: center;
  }
}

@media (max-width: 1024px) {
  .dashboard-sigarh-container {
    padding: 1rem 1.5rem;
  }
}

@media (max-width: 768px) {
  .dashboard-sigarh-container {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .movimientos-grid {
    grid-template-columns: 1fr;
  }

  .accesos-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .camas-ring-container {
    flex-direction: column;
    align-items: center;
  }

  .camas-legend {
    width: 100%;
  }

  .estado-legend {
    grid-template-columns: 1fr;
  }

  .asistencia-bars {
    height: 120px;
  }

  .bar-wrapper {
    height: 80px;
  }
}

@media (max-width: 480px) {
  .accesos-grid {
    grid-template-columns: 1fr 1fr;
  }

  .solicitud-item {
    flex-wrap: wrap;
  }

  .solicitud-estado {
    margin-left: auto;
  }
}
</style>