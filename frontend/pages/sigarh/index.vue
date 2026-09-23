<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Escritorio', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const tenant = computed(() => route.query.tenant as string || '')

interface Serie { label: string; anio?: number; valor?: number }
interface Tendencia { label: string; vacaciones: number; licencias: number; papeletas: number; cambios_turno: number; total: number }
interface AsistSemana { label: string; presentes: number; ausentes: number; total: number }
interface UltimaVac { id: string; empleado_nombre: string; tipo: string; fecha_inicio: string; fecha_fin: string; estado: string }
interface UltimaLic { id: string; empleado_nombre: string; fecha_tramite: string; fecha_inicio: string; fecha_fin: string; estado: string }
interface Dashboard {
  fecha: string
  kpis: {
    total_empleados: number; empleados_activos: number; empleados_inactivos: number
    asistencia_hoy: number; ausentes_hoy: number; porcentaje_asistencia: number
    solicitudes_pendientes: number; justificaciones_pendientes: number
  }
  movimientos_mes: { vacaciones: number; licencias: number; papeletas: number; cambios_turno: number }
  pendientes: { vacaciones: number; licencias: number; papeletas: number; cambios_turno: number }
  camas: { total: number; disponibles: number; ocupadas: number; mantenimiento: number; reservadas: number; porcentaje_ocupacion: number }
  distribucion_genero: { masculino: number; femenino: number; sin_registrar: number }
  distribucion_estado: { activos: number; inactivos: number; en_vacaciones: number; en_licencia: number }
  empleados_por_mes: Serie[]
  asistencia_semanal: AsistSemana[]
  tendencias_solicitudes: Tendencia[]
  ultimas_vacaciones: UltimaVac[]
  ultimas_licencias: UltimaLic[]
}

const data = ref<Dashboard | null>(null)
const loading = ref(true)
const error = ref('')

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    data.value = await api<Dashboard>('/sigarh/dashboard')
  } catch (e: any) {
    error.value = apiErr(e, 'No se pudo cargar el dashboard')
  } finally {
    loading.value = false
  }
}
onMounted(cargar)

const hoyLabel = computed(() => {
  const d = data.value?.fecha ? new Date(data.value.fecha + 'T00:00:00') : new Date()
  return d.toLocaleDateString('es-PE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
})

// ── Helpers ─────────────────────────────────────────────────────────────────
const estadoColor: Record<string, string> = { pendiente: 'var(--amber)', aprobado: 'var(--green)', rechazado: 'var(--alert)' }
const estadoSoft: Record<string, string> = { pendiente: 'var(--amber-soft)', aprobado: 'var(--green-soft)', rechazado: 'var(--alert-soft)' }
const fmtEstado = (e: string) => ({ pendiente: 'Pendiente', aprobado: 'Aprobado', rechazado: 'Rechazado' }[e] || e)
const fmtTipo = (t: string) => ({ vacacion: 'Vacaciones', justificacion: 'Justificacion', permiso: 'Permiso' }[t] || t)

const avatarColors = ['var(--teal-soft)', 'var(--purple-soft)', 'var(--navy-soft)', 'var(--amber-soft)', 'var(--green-soft)', 'var(--orange-soft)']
const avatarColor = (name: string) => {
  let h = 0
  for (let i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h)
  return avatarColors[Math.abs(h) % avatarColors.length]
}
const initials = (name: string) => (!name ? '?' : name.replace(',', '').split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0]).join('').toUpperCase())

// ── Series de gráficos ─────────────────────────────────────────────────────
const tendencias = computed(() => data.value?.tendencias_solicitudes || [])
const tendenciaCategorias = computed(() => tendencias.value.map(t => t.label))
const tendenciaSeries = computed(() => [
  { name: 'Vacaciones', data: tendencias.value.map(t => t.vacaciones) },
  { name: 'Licencias', data: tendencias.value.map(t => t.licencias) },
  { name: 'Papeletas', data: tendencias.value.map(t => t.papeletas) },
  { name: 'Cambios turno', data: tendencias.value.map(t => t.cambios_turno) },
])

const empleadosPorMes = computed(() => data.value?.empleados_por_mes || [])
const altasSeries = computed(() => [{ name: 'Altas', data: empleadosPorMes.value.map(m => m.valor || 0) }])
const altasCategorias = computed(() => empleadosPorMes.value.map(m => m.label))

const estado = computed(() => data.value?.distribucion_estado || { activos: 0, inactivos: 0, en_vacaciones: 0, en_licencia: 0 })
const trabajando = computed(() => Math.max(estado.value.activos - estado.value.en_vacaciones - estado.value.en_licencia, 0))
const estadoSeries = computed(() => [trabajando.value, estado.value.en_vacaciones, estado.value.en_licencia, estado.value.inactivos])

const genero = computed(() => data.value?.distribucion_genero || { masculino: 0, femenino: 0, sin_registrar: 0 })
const generoSeries = computed(() => [genero.value.masculino, genero.value.femenino, genero.value.sin_registrar])

const asistenciaSemanal = computed(() => data.value?.asistencia_semanal || [])
const maxSemana = computed(() => Math.max(...asistenciaSemanal.value.map(s => s.total), 1))

const camas = computed(() => data.value?.camas)
const camaSegmentos = computed(() => {
  const c = camas.value
  if (!c || !c.total) return []
  return [
    { label: 'Ocupadas', valor: c.ocupadas, color: 'var(--navy)' },
    { label: 'Disponibles', valor: c.disponibles, color: 'var(--green)' },
    { label: 'Reservadas', valor: c.reservadas, color: 'var(--amber)' },
    { label: 'Mantenimiento', valor: c.mantenimiento, color: 'var(--ink-soft)' },
  ]
})

// ── Opciones ApexCharts (modo claro) ───────────────────────────────────────
const ejeComun = {
  fontFamily: 'Inter, system-ui, sans-serif',
  foreColor: '#4a5c66',
}
const areaOptions = computed(() => ({
  chart: { ...ejeComun, toolbar: { show: false }, stacked: true, zoom: { enabled: false } },
  colors: ['#c2571e', '#0c7c74', '#6b4fa3', '#123a52'],
  stroke: { curve: 'smooth', width: 2 },
  fill: { type: 'gradient', gradient: { opacityFrom: 0.35, opacityTo: 0.05 } },
  dataLabels: { enabled: false },
  legend: { position: 'top', horizontalAlign: 'left', fontSize: '12px', markers: { radius: 4 } },
  xaxis: { categories: tendenciaCategorias.value, axisBorder: { show: false }, axisTicks: { show: false } },
  grid: { borderColor: '#dce5e7', strokeDashArray: 3 },
  tooltip: { theme: 'light' },
}))
const altasOptions = computed(() => ({
  chart: { ...ejeComun, toolbar: { show: false }, sparkline: { enabled: false }, zoom: { enabled: false } },
  colors: ['#0c7c74'],
  plotOptions: { bar: { borderRadius: 4, columnWidth: '45%' } },
  dataLabels: { enabled: false },
  xaxis: { categories: altasCategorias.value, axisBorder: { show: false }, axisTicks: { show: false } },
  grid: { borderColor: '#dce5e7', strokeDashArray: 3 },
  tooltip: { theme: 'light' },
}))
const donutBase = {
  chart: { ...ejeComun },
  stroke: { width: 0 },
  dataLabels: { enabled: false },
  legend: { position: 'bottom', fontSize: '12px', markers: { radius: 4 } },
  plotOptions: { pie: { donut: { size: '68%', labels: { show: true, total: { show: true, label: 'Total', fontSize: '13px' } } } } },
}
const estadoOptions = computed(() => ({ ...donutBase, colors: ['#0c7c74', '#c2571e', '#6b4fa3', '#9aa7ad'], labels: ['Trabajando', 'En vacaciones', 'En licencia', 'Inactivos'] }))
const generoOptions = computed(() => ({ ...donutBase, colors: ['#123a52', '#6b4fa3', '#c9d4d8'], labels: ['Masculino', 'Femenino', 'Sin registrar'] }))
</script>

<template>
  <div class="dash">
      <!-- Accesos rapidos -->
      <section class="sigarh-launcher">
        <h1>&iquest;Qu&eacute; deseas <span>realizar hoy?</span></h1><p>Gestiona las personas y la actividad de tu hospital.</p>
        <div class="accesos-grid">
          <NuxtLink
            v-for="a in [
              { label: 'Empleados', icon: 'i-heroicons-users', path: '/sigarh/rrhh/empleados' },
              { label: 'Asistencia', icon: 'i-heroicons-clipboard-document-check', path: '/sigarh/rrhh/asistencia' },
              { label: 'Vacaciones', icon: 'i-heroicons-sun', path: '/sigarh/movimientos/vacaciones' },
              { label: 'Licencias', icon: 'i-heroicons-paper-airplane', path: '/sigarh/movimientos/licencias' },
              { label: 'Papeletas', icon: 'i-heroicons-document-duplicate', path: '/sigarh/movimientos/papeletas/estado' },
              { label: 'Camas', icon: 'i-heroicons-home-modern', path: '/sigarh/infraestructura-hosp/camas' },
            ]"
            :key="a.path"
            :to="`${a.path}?tenant=${tenant}`"
            class="acceso-item"
          >
            <div class="acceso-icon"><UIcon :name="a.icon" class="w-4 h-4" style="color: var(--navy)" /></div>
            <span>{{ a.label }}</span>
          </NuxtLink>
        </div>
      </section>

    <div class="dash-header">
      <div class="dash-header-left">
        <div class="dash-header-icon">
          <UIcon name="i-heroicons-chart-bar" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <h2 class="page-title">Resumen SIGARH</h2>
          <p class="page-subtitle" style="text-transform: capitalize">{{ hoyLabel }}</p>
        </div>
      </div>
      <div v-if="data && data.kpis.solicitudes_pendientes > 0" class="dash-alert">
        <UIcon name="i-heroicons-bell-alert" class="w-4 h-4" />
        {{ data.kpis.solicitudes_pendientes }} solicitudes pendientes
      </div>
    </div>

    <div v-if="loading" class="dash-skeleton-grid">
      <div v-for="i in 4" :key="i" class="dash-skeleton" />
    </div>

    <div v-else-if="error" class="dash-error">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
      <button class="btn-outline" @click="cargar">Reintentar</button>
    </div>

    <template v-else-if="data">
      <!-- KPIs -->
      <div class="kpi-grid">
        <div class="kpi-card" style="border-left-color: var(--navy)">
          <div>
            <span class="kpi-label">Total Empleados</span>
            <span class="kpi-value">{{ data.kpis.total_empleados }}</span>
            <span class="kpi-sub"><b style="color: var(--green)">{{ data.kpis.empleados_activos }}</b> activos · {{ data.kpis.empleados_inactivos }} inactivos</span>
          </div>
          <div class="kpi-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-users" class="w-5 h-5" style="color: var(--navy)" /></div>
        </div>

        <div class="kpi-card" style="border-left-color: var(--green)">
          <div>
            <span class="kpi-label">Asistencia Hoy</span>
            <span class="kpi-value">{{ data.kpis.asistencia_hoy }}</span>
            <span class="kpi-sub">
              <b :style="{ color: data.kpis.porcentaje_asistencia >= 80 ? 'var(--green)' : 'var(--amber)' }">{{ data.kpis.porcentaje_asistencia }}%</b>
              del personal activo · {{ data.kpis.ausentes_hoy }} ausentes
            </span>
            <div class="kpi-progress"><div class="kpi-progress-fill" :style="{ width: Math.min(data.kpis.porcentaje_asistencia, 100) + '%', background: data.kpis.porcentaje_asistencia >= 80 ? 'var(--green)' : 'var(--amber)' }" /></div>
          </div>
          <div class="kpi-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-clipboard-document-check" class="w-5 h-5" style="color: var(--green)" /></div>
        </div>

        <div class="kpi-card" style="border-left-color: var(--amber)">
          <div>
            <span class="kpi-label">Solicitudes Pendientes</span>
            <span class="kpi-value">{{ data.kpis.solicitudes_pendientes }}</span>
            <div class="kpi-badges">
              <span class="badge-mini" style="background: var(--orange-soft); color: var(--orange)">Vac {{ data.pendientes.vacaciones }}</span>
              <span class="badge-mini" style="background: var(--teal-soft); color: var(--teal)">Lic {{ data.pendientes.licencias }}</span>
              <span class="badge-mini" style="background: var(--purple-soft); color: var(--purple)">Pap {{ data.pendientes.papeletas }}</span>
              <span class="badge-mini" style="background: var(--navy-soft); color: var(--navy)">CT {{ data.pendientes.cambios_turno }}</span>
            </div>
          </div>
          <div class="kpi-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" /></div>
        </div>

        <div class="kpi-card" style="border-left-color: var(--purple)">
          <div>
            <span class="kpi-label">Justificaciones Pend.</span>
            <span class="kpi-value">{{ data.kpis.justificaciones_pendientes }}</span>
            <span class="kpi-sub">Por revisar en RRHH</span>
          </div>
          <div class="kpi-icon" style="background: var(--purple-soft)"><UIcon name="i-heroicons-document-text" class="w-5 h-5" style="color: var(--purple)" /></div>
        </div>
      </div>

      <!-- Tendencias + estado -->
      <div class="grid-2-1">
        <div class="card">
          <div class="card-head">
            <h3 class="card-title">Tendencia de solicitudes</h3>
            <span class="card-badge">Ultimos 6 meses</span>
          </div>
          <ClientOnly>
            <ApexChart type="area" height="260" :options="areaOptions" :series="tendenciaSeries" />
          </ClientOnly>
        </div>
        <div class="card">
          <div class="card-head"><h3 class="card-title">Empleados por estado</h3></div>
          <ClientOnly>
            <ApexChart type="donut" height="240" :options="estadoOptions" :series="estadoSeries" />
          </ClientOnly>
        </div>
      </div>

      <!-- Asistencia semanal + movimientos del mes -->
      <div class="grid-2">
        <div class="card">
          <div class="card-head">
            <h3 class="card-title">Asistencia semanal</h3>
            <span class="card-badge">Ultimas 5 semanas</span>
          </div>
          <div v-if="!asistenciaSemanal.length" class="mini-empty">
            <UIcon name="i-heroicons-clipboard-document-check" class="w-7 h-7" style="color: var(--ink-soft)" />
            <span>Sin registros de asistencia</span>
          </div>
          <div v-else class="asist-bars">
            <div v-for="s in asistenciaSemanal" :key="s.label" class="asist-bar">
              <span class="asist-val">{{ s.presentes }}</span>
              <div class="asist-track">
                <div class="asist-fill" :style="{ height: (s.presentes / maxSemana) * 100 + '%', background: s.total && s.presentes / s.total >= 0.8 ? 'var(--green)' : 'var(--amber)' }" />
              </div>
              <span class="asist-lbl">{{ s.label }}</span>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-head"><h3 class="card-title">Movimientos del mes</h3></div>
          <div class="mov-grid">
            <NuxtLink :to="`/sigarh/movimientos/vacaciones?tenant=${tenant}`" class="mov-item">
              <div class="mov-icon" style="background: var(--orange-soft)"><UIcon name="i-heroicons-sun" class="w-4 h-4" style="color: var(--orange)" /></div>
              <div><span class="mov-value">{{ data.movimientos_mes.vacaciones }}</span><span class="mov-label">Vacaciones</span></div>
            </NuxtLink>
            <NuxtLink :to="`/sigarh/movimientos/licencias?tenant=${tenant}`" class="mov-item">
              <div class="mov-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-paper-airplane" class="w-4 h-4" style="color: var(--teal)" /></div>
              <div><span class="mov-value">{{ data.movimientos_mes.licencias }}</span><span class="mov-label">Licencias</span></div>
            </NuxtLink>
            <NuxtLink :to="`/sigarh/movimientos/papeletas/estado?tenant=${tenant}`" class="mov-item">
              <div class="mov-icon" style="background: var(--purple-soft)"><UIcon name="i-heroicons-document-duplicate" class="w-4 h-4" style="color: var(--purple)" /></div>
              <div><span class="mov-value">{{ data.movimientos_mes.papeletas }}</span><span class="mov-label">Papeletas</span></div>
            </NuxtLink>
            <NuxtLink :to="`/sigarh/movimientos/cambio-turno/estado?tenant=${tenant}`" class="mov-item">
              <div class="mov-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-arrows-right-left" class="w-4 h-4" style="color: var(--navy)" /></div>
              <div><span class="mov-value">{{ data.movimientos_mes.cambios_turno }}</span><span class="mov-label">Cambios turno</span></div>
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Altas por mes + genero + camas -->
      <div class="grid-3">
        <div class="card">
          <div class="card-head"><h3 class="card-title">Altas de empleados</h3><span class="card-badge">Por mes</span></div>
          <ClientOnly>
            <ApexChart type="bar" height="200" :options="altasOptions" :series="altasSeries" />
          </ClientOnly>
        </div>

        <div class="card">
          <div class="card-head"><h3 class="card-title">Distribucion por genero</h3></div>
          <ClientOnly>
            <ApexChart type="donut" height="220" :options="generoOptions" :series="generoSeries" />
          </ClientOnly>
        </div>

        <div class="card">
          <div class="card-head">
            <h3 class="card-title">Estado de camas</h3>
            <NuxtLink :to="`/sigarh/infraestructura-hosp/camas?tenant=${tenant}`" class="card-link">Ver todas</NuxtLink>
          </div>
          <div v-if="!camas || !camas.total" class="mini-empty">
            <UIcon name="i-heroicons-home-modern" class="w-7 h-7" style="color: var(--ink-soft)" />
            <span>Sin camas registradas</span>
          </div>
          <template v-else>
            <div class="camas-top">
              <span class="camas-pct">{{ camas.porcentaje_ocupacion }}%</span>
              <span class="camas-pct-lbl">ocupacion · {{ camas.total }} camas</span>
            </div>
            <div class="camas-bar">
              <div v-for="seg in camaSegmentos" :key="seg.label" class="camas-seg" :style="{ width: (seg.valor / camas.total) * 100 + '%', background: seg.color }" />
            </div>
            <div class="camas-legend">
              <div v-for="seg in camaSegmentos" :key="seg.label" class="camas-leg-item">
                <span class="camas-dot" :style="{ background: seg.color }" />
                <span class="camas-leg-lbl">{{ seg.label }}</span>
                <span class="camas-leg-val">{{ seg.valor }}</span>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Ultimas solicitudes -->
      <div class="grid-2">
        <div class="card">
          <div class="card-head">
            <h3 class="card-title">Ultimas vacaciones</h3>
            <NuxtLink :to="`/sigarh/movimientos/vacaciones?tenant=${tenant}`" class="card-link">Ver todas</NuxtLink>
          </div>
          <div v-if="!data.ultimas_vacaciones.length" class="mini-empty">
            <UIcon name="i-heroicons-sun" class="w-7 h-7" style="color: var(--ink-soft)" />
            <span>Sin solicitudes recientes</span>
          </div>
          <div v-else class="sol-list">
            <NuxtLink v-for="v in data.ultimas_vacaciones" :key="v.id" :to="`/sigarh/movimientos/vacaciones/${v.id}?tenant=${tenant}`" class="sol-item">
              <div class="sol-avatar" :style="{ background: avatarColor(v.empleado_nombre) }">{{ initials(v.empleado_nombre) }}</div>
              <div class="sol-info">
                <span class="sol-name">{{ v.empleado_nombre }}</span>
                <span class="sol-detail">{{ fmtTipo(v.tipo) }} · {{ v.fecha_inicio }} → {{ v.fecha_fin }}</span>
              </div>
              <span class="sol-estado" :style="{ background: estadoSoft[v.estado] || 'var(--mist)', color: estadoColor[v.estado] || 'var(--ink-soft)' }">{{ fmtEstado(v.estado) }}</span>
            </NuxtLink>
          </div>
        </div>

        <div class="card">
          <div class="card-head">
            <h3 class="card-title">Ultimas licencias</h3>
            <NuxtLink :to="`/sigarh/movimientos/licencias?tenant=${tenant}`" class="card-link">Ver todas</NuxtLink>
          </div>
          <div v-if="!data.ultimas_licencias.length" class="mini-empty">
            <UIcon name="i-heroicons-paper-airplane" class="w-7 h-7" style="color: var(--ink-soft)" />
            <span>Sin licencias recientes</span>
          </div>
          <div v-else class="sol-list">
            <NuxtLink v-for="l in data.ultimas_licencias" :key="l.id" :to="`/sigarh/movimientos/licencias/${l.id}?tenant=${tenant}`" class="sol-item">
              <div class="sol-avatar" :style="{ background: avatarColor(l.empleado_nombre) }">{{ initials(l.empleado_nombre) }}</div>
              <div class="sol-info">
                <span class="sol-name">{{ l.empleado_nombre }}</span>
                <span class="sol-detail">Tramite {{ l.fecha_tramite }} · {{ l.fecha_inicio }} → {{ l.fecha_fin }}</span>
              </div>
              <span class="sol-estado" :style="{ background: estadoSoft[l.estado] || 'var(--mist)', color: estadoColor[l.estado] || 'var(--ink-soft)' }">{{ fmtEstado(l.estado) }}</span>
            </NuxtLink>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<style scoped>
.dash { max-width: 1400px; margin: 0 auto; padding: 1.5rem 2rem; display: flex; flex-direction: column; gap: 1.25rem; }

.dash-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }
.dash-header-left { display: flex; align-items: center; gap: 1rem; }
.dash-header-icon { width: 44px; height: 44px; border-radius: 12px; background: var(--navy-soft); display: flex; align-items: center; justify-content: center; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; }
.page-subtitle { font-size: 0.875rem; color: var(--ink-soft); margin: 0.125rem 0 0; }
.dash-alert { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.875rem; border-radius: 999px; background: var(--amber-soft); color: var(--amber); font-size: 0.8125rem; font-weight: 600; }

.dash-skeleton-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.dash-skeleton { height: 110px; border-radius: var(--radius-lg); background: linear-gradient(90deg, var(--mist) 25%, #f4f8f9 50%, var(--mist) 75%); background-size: 200% 100%; animation: sk 1.4s infinite; }
@keyframes sk { to { background-position: -200% 0; } }
.dash-error { display: flex; align-items: center; gap: 0.75rem; padding: 1rem; border-radius: var(--radius-lg); background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; }

/* KPIs */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.kpi-card { background: var(--paper); border: 1px solid var(--line); border-left: 4px solid var(--navy); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1.1rem 1.25rem; display: flex; justify-content: space-between; gap: 0.75rem; }
.kpi-label { display: block; font-size: 0.75rem; color: var(--ink-soft); font-weight: 500; }
.kpi-value { display: block; font-size: 1.75rem; font-weight: 700; color: var(--ink); line-height: 1.15; margin: 0.15rem 0; }
.kpi-sub { display: block; font-size: 0.75rem; color: var(--ink-soft); }
.kpi-icon { width: 40px; height: 40px; border-radius: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.kpi-badges { display: flex; flex-wrap: wrap; gap: 0.25rem; margin-top: 0.35rem; }
.badge-mini { font-size: 0.625rem; font-weight: 600; padding: 0.1rem 0.4rem; border-radius: 6px; }
.kpi-progress { height: 5px; border-radius: 3px; background: var(--mist); margin-top: 0.5rem; overflow: hidden; }
.kpi-progress-fill { height: 100%; border-radius: 3px; transition: width 0.4s ease; }

/* Layout grids */
.grid-2-1 { display: grid; grid-template-columns: 2fr 1fr; gap: 1rem; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }

.card { background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1.25rem; }
.card-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem; }
.card-title { font-size: 0.9375rem; font-weight: 600; color: var(--ink); margin: 0; }
.card-badge { font-size: 0.6875rem; font-weight: 500; color: var(--ink-soft); background: var(--mist); padding: 0.15rem 0.5rem; border-radius: 6px; }
.card-link { font-size: 0.75rem; font-weight: 500; color: var(--teal); text-decoration: none; }
.card-link:hover { text-decoration: underline; }

.mini-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.5rem; padding: 2.5rem 1rem; color: var(--ink-soft); font-size: 0.8125rem; }

/* Asistencia semanal */
.asist-bars { display: flex; align-items: flex-end; justify-content: space-around; gap: 0.5rem; height: 200px; padding-top: 0.5rem; }
.asist-bar { display: flex; flex-direction: column; align-items: center; gap: 0.35rem; flex: 1; height: 100%; }
.asist-val { font-size: 0.75rem; font-weight: 700; color: var(--ink); }
.asist-track { flex: 1; width: 60%; max-width: 38px; background: var(--mist); border-radius: 6px; display: flex; align-items: flex-end; overflow: hidden; }
.asist-fill { width: 100%; border-radius: 6px; transition: height 0.4s ease; min-height: 4px; }
.asist-lbl { font-size: 0.6875rem; color: var(--ink-soft); }

/* Movimientos */
.mov-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.mov-item { display: flex; align-items: center; gap: 0.65rem; padding: 0.85rem; border: 1px solid var(--line); border-radius: var(--radius); text-decoration: none; transition: background 0.15s ease; }
.mov-item:hover { background: var(--mist); }
.mov-icon { width: 34px; height: 34px; border-radius: 9px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.mov-value { display: block; font-size: 1.25rem; font-weight: 700; color: var(--ink); line-height: 1.1; }
.mov-label { display: block; font-size: 0.75rem; color: var(--ink-soft); }

/* Camas */
.camas-top { display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 0.75rem; }
.camas-pct { font-size: 1.75rem; font-weight: 700; color: var(--ink); }
.camas-pct-lbl { font-size: 0.75rem; color: var(--ink-soft); }
.camas-bar { display: flex; height: 12px; border-radius: 999px; overflow: hidden; background: var(--mist); }
.camas-seg { height: 100%; }
.camas-legend { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem 1rem; margin-top: 0.85rem; }
.camas-leg-item { display: flex; align-items: center; gap: 0.4rem; font-size: 0.75rem; }
.camas-dot { width: 8px; height: 8px; border-radius: 3px; flex-shrink: 0; }
.camas-leg-lbl { color: var(--ink-soft); flex: 1; }
.camas-leg-val { font-weight: 700; color: var(--ink); }

/* Solicitudes */
.sol-list { display: flex; flex-direction: column; }
.sol-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0; border-bottom: 1px solid var(--line); text-decoration: none; }
.sol-item:last-child { border-bottom: none; }
.sol-avatar { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; color: var(--ink); flex-shrink: 0; }
.sol-info { flex: 1; min-width: 0; }
.sol-name { display: block; font-size: 0.8125rem; font-weight: 600; color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sol-detail { display: block; font-size: 0.6875rem; color: var(--ink-soft); }
.sol-estado { font-size: 0.6875rem; font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 6px; flex-shrink: 0; }

/* Accesos */
.accesos-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 0.65rem; }
.acceso-item { display: flex; flex-direction: column; align-items: center; gap: 0.4rem; padding: 0.9rem 0.5rem; border: 1px solid var(--line); border-radius: var(--radius); text-decoration: none; font-size: 0.75rem; font-weight: 500; color: var(--ink); transition: all 0.15s ease; }
.acceso-item:hover { background: var(--mist); border-color: var(--navy-soft); }
.acceso-icon { width: 34px; height: 34px; border-radius: 9px; background: var(--navy-soft); display: flex; align-items: center; justify-content: center; }

@media (max-width: 1100px) {
  .kpi-grid, .dash-skeleton-grid { grid-template-columns: 1fr 1fr; }
  .grid-2-1, .grid-2, .grid-3 { grid-template-columns: 1fr; }
  .accesos-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 640px) {
  .dash { padding: 1rem; }
  .kpi-grid, .dash-skeleton-grid, .mov-grid { grid-template-columns: 1fr; }
  .accesos-grid { grid-template-columns: repeat(2, 1fr); }
}

.sigarh-launcher { text-align:center; padding:12px 0 20px; }
.sigarh-launcher h1 { font-size:clamp(26px,2.7vw,36px); line-height:1.3; font-weight:600; margin-bottom:12px; }
.sigarh-launcher h1 span { color:var(--teal); }
.sigarh-launcher>p { color:var(--ink-soft); font-size:14px; margin-bottom:24px; }
.sigarh-launcher .accesos-grid { grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; }
.sigarh-launcher .acceso-item { background:white; min-height:132px; padding:20px; border:1px solid transparent; border-radius:20px; font-size:16px; font-weight:400; justify-content:center; gap:12px; box-shadow:var(--shadow-card); }
.sigarh-launcher .acceso-item:hover { border-color:var(--teal); }
.sigarh-launcher .acceso-icon { background:transparent; width:40px; height:40px; }
.sigarh-launcher .acceso-icon :deep(span) { width:38px; height:38px; }
@media(max-width:800px) { .sigarh-launcher .accesos-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
@media(max-width:480px) { .sigarh-launcher .accesos-grid { grid-template-columns:1fr; } }
</style>
