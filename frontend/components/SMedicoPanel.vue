<template>
  <div class="dash-container">
    <!-- ============ BANNER ============ -->
    <div class="dash-banner">
      <div class="banner-content">
        <div class="header-badge">
          <UIcon name="i-heroicons-user-circle" class="w-4 h-4" />
          <span>Panel del médico</span>
        </div>
        <h1 class="dash-title">{{ saludo }}, Dr(a). {{ nombreCorto }}</h1>
        <p class="dash-subtitle cap">{{ fechaLarga }}</p>
        <div class="banner-actions">
          <div class="live-pill">
            <span class="live-dot" />
            <span>En vivo</span>
          </div>
          <button class="btn-secondary btn-sm" :disabled="cargando" @click="cargar">
            <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" :class="{ 'animate-spin': cargando }" />
            Actualizar
          </button>
        </div>
      </div>
      <div class="banner-art">
        <svg class="banner-svg" viewBox="0 0 440 190" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
          <circle class="banner-float banner-float--1" cx="370" cy="35" r="50" fill="rgba(255,255,255,0.06)" />
          <circle class="banner-float banner-float--2" cx="290" cy="140" r="34" fill="rgba(255,255,255,0.05)" />
          <circle class="banner-float banner-float--3" cx="405" cy="148" r="22" fill="rgba(255,255,255,0.08)" />
          <g transform="translate(340,60)" opacity="0.35">
            <circle cx="0" cy="0" r="26" fill="none" stroke="#eef4ff" stroke-width="2" />
            <path d="M -10 0 a 10 10 0 1 0 20 0 a 10 10 0 1 0 -20 0" fill="none" stroke="#eef4ff" stroke-width="1.5" />
          </g>
          <path
            class="banner-pulse"
            d="M0,105 L75,105 L95,105 L112,55 L130,150 L150,100 L170,100 L188,72 L206,100 L410,100"
            fill="none" stroke="#eef4ff" stroke-width="2.5"
            stroke-linecap="round" stroke-linejoin="round" pathLength="1"
          />
          <circle cx="150" cy="30" r="3" fill="rgba(255,255,255,0.18)" class="banner-particle" />
          <circle cx="220" cy="160" r="2.5" fill="rgba(255,255,255,0.1)" class="banner-particle banner-particle--delay" />
        </svg>
      </div>
    </div>

    <div v-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <!-- ============ KPIs ============ -->
    <section class="stats-row">
      <div class="stat-card" style="border-left-color: var(--teal)">
        <div class="stat-top">
          <div class="stat-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-clipboard-document-check" class="w-5 h-5" style="color: var(--teal)" />
          </div>
        </div>
        <span class="stat-num">{{ cargando ? '—' : kpis.citas_hoy_total }}</span>
        <span class="stat-label">Citas de hoy</span>
      </div>
      <div class="stat-card" style="border-left-color: var(--navy)">
        <div class="stat-top">
          <div class="stat-icon" style="background: rgba(62,92,147,0.1)">
            <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--navy)" />
          </div>
        </div>
        <span class="stat-num">{{ cargando ? '—' : kpis.citas_hoy_pendientes }}</span>
        <span class="stat-label">Por atender hoy</span>
      </div>
      <div class="stat-card" style="border-left-color: var(--green)">
        <div class="stat-top">
          <div class="stat-icon" style="background: var(--green-soft)">
            <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
          </div>
        </div>
        <span class="stat-num">{{ cargando ? '—' : kpis.citas_hoy_atendidas }}</span>
        <span class="stat-label">Atendidas hoy</span>
      </div>
      <div class="stat-card" style="border-left-color: var(--purple)">
        <div class="stat-top">
          <div class="stat-icon" style="background: var(--purple-soft)">
            <UIcon name="i-heroicons-user-group" class="w-5 h-5" style="color: var(--purple)" />
          </div>
        </div>
        <span class="stat-num">{{ cargando ? '—' : kpis.pacientes_semana }}</span>
        <span class="stat-label">Pacientes esta semana</span>
      </div>
      <div class="stat-card" style="border-left-color: var(--amber)">
        <div class="stat-top">
          <div class="stat-icon" style="background: var(--amber-soft)">
            <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--amber)" />
          </div>
        </div>
        <span class="stat-num">{{ cargando ? '—' : kpis.jornadas_mes }}</span>
        <span class="stat-label">Jornadas este mes</span>
      </div>
    </section>

    <!-- ============ CHARTS ============ -->
    <section class="charts-row">
      <div class="panel chart-panel chart-panel--wide">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-presentation-chart-line" class="w-4 h-4" />
            Mis citas de la semana
          </h2>
          <span class="panel-tag panel-tag--accent">
            <UIcon name="i-heroicons-check-circle" class="w-3 h-3" /> Datos reales · 7 días
          </span>
        </div>
        <div class="chart-body">
          <ClientOnly>
            <ApexChart type="area" height="260" :options="serieChartOptions" :series="[{ name: 'Citas', data: serieSemana.map(d => d.citas) }]" />
          </ClientOnly>
        </div>
      </div>

      <div class="panel chart-panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-chart-pie" class="w-4 h-4" />
            Citas de hoy
          </h2>
          <span class="panel-tag">{{ kpis.citas_hoy_total }} total</span>
        </div>
        <div class="chart-body">
          <ClientOnly>
            <ApexChart
              v-if="kpis.citas_hoy_total"
              type="donut" height="200" :options="citasChartOptions"
              :series="[kpis.citas_hoy_atendidas, kpis.citas_hoy_pendientes]"
            />
            <p v-else class="empty-hint">Sin citas programadas para hoy.</p>
          </ClientOnly>
        </div>
      </div>
    </section>

    <!-- ============ DASH GRID ============ -->
    <div class="dash-grid">
      <!-- Próximas citas de hoy -->
      <section class="panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-clipboard-document-list" class="w-4 h-4" />
            Próximas citas de hoy
          </h2>
        </div>
        <div v-if="cargando" class="loading-state">
          <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
        </div>
        <ul v-else-if="proximasCitas.length" class="activity-list">
          <li v-for="c in proximasCitas" :key="c.id" class="activity-item">
            <span class="activity-dot">
              <UIcon name="i-heroicons-clock" class="w-3 h-3" />
            </span>
            <div class="activity-body">
              <span class="activity-text">
                <b>{{ c.hora }}</b> · {{ c.paciente }}
              </span>
              <NuxtLink
                v-if="c.estado === 'confirmada' && estados[c.id]?.triaje_registrado"
                class="panel-link"
                :to="link('/app/consulta-externa/atenciones-medicas/' + c.id)"
              >
                Abrir atención →
              </NuxtLink>
              <span v-else class="activity-time">
                {{ c.estado === 'separada' ? 'Pendiente de confirmación' : 'Pendiente de triaje' }}
              </span>
            </div>
          </li>
        </ul>
        <p v-else class="empty-hint">No tienes más citas pendientes por hoy.</p>
      </section>

      <!-- Próximas jornadas -->
      <section class="panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-calendar-days" class="w-4 h-4" />
            Próximas jornadas
          </h2>
          <NuxtLink :to="link('/app/admision/programacion-medica')" class="panel-link">Ver todas →</NuxtLink>
        </div>
        <div v-if="cargando" class="loading-state">
          <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
        </div>
        <ul v-else-if="proximasJornadas.length" class="activity-list">
          <li v-for="p in proximasJornadas" :key="p.id" class="activity-item">
            <span class="activity-dot dot-crear">
              <UIcon name="i-heroicons-sun" class="w-3 h-3" />
            </span>
            <div class="activity-body">
              <span class="activity-text">
                <b>{{ fechaTexto(p.fecha) }}</b> · {{ p.hora_inicio }}–{{ p.hora_fin }}
              </span>
              <span class="activity-time">{{ p.servicio_nombre }}{{ p.especialidad_nombre ? ' · ' + p.especialidad_nombre : '' }}</span>
            </div>
          </li>
        </ul>
        <p v-else class="empty-hint">No tienes jornadas programadas próximamente.</p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
const { api } = useApi()
const { link } = useHospitalNav()
const auth = useAuthStore()

const ACCENT = '#6495ed'
const GRIS = '#c7ccd1'

const cargando = ref(false)
const error = ref('')

interface KpisMedico {
  citas_hoy_total: number
  citas_hoy_pendientes: number
  citas_hoy_atendidas: number
  jornadas_mes: number
  pacientes_semana: number
}
const kpis = reactive<KpisMedico>({
  citas_hoy_total: 0, citas_hoy_pendientes: 0, citas_hoy_atendidas: 0, jornadas_mes: 0, pacientes_semana: 0,
})
const serieSemana = ref<{ label: string; citas: number }[]>([])
const proximasCitas = ref<any[]>([])
const proximasJornadas = ref<any[]>([])
const estados = ref<Record<string, { triaje_registrado: boolean; atencion_estado: string | null }>>({})

const hoyISO = new Date().toISOString().slice(0, 10)
const nombreCorto = computed(() => (auth.user?.name || 'Usuario').replace(/^REQUE SIMULADO,\s*/i, '').split(' ')[0])
const horaActual = new Date().getHours()
const saludo = computed(() => horaActual < 12 ? 'Buenos días' : horaActual < 19 ? 'Buenas tardes' : 'Buenas noches')
const fechaLarga = computed(() => new Date().toLocaleDateString('es-PE', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' }))
const fechaTexto = (valor: string) => valor ? valor.slice(0, 10).split('-').reverse().join('/') : '—'

const serieChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, fontFamily: 'inherit', zoom: { enabled: false } },
  colors: [ACCENT],
  stroke: { curve: 'smooth', width: 2.5 },
  fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.3, opacityTo: 0.02, stops: [0, 90, 100] } },
  markers: { size: 4, strokeWidth: 2, strokeColors: '#fff', hover: { size: 6 } },
  dataLabels: { enabled: false },
  legend: { show: false },
  xaxis: {
    categories: serieSemana.value.map(d => d.label),
    labels: { style: { colors: '#8a97a0', fontSize: '11px' } },
    axisBorder: { show: false }, axisTicks: { show: false },
  },
  yaxis: { labels: { style: { colors: '#8a97a0', fontSize: '11px' } }, forceNiceScale: true },
  grid: { borderColor: '#e6ebef', strokeDashArray: 3 },
  tooltip: { theme: 'light', x: { show: true } },
}))

const citasChartOptions = computed(() => ({
  chart: { fontFamily: 'inherit' },
  colors: [ACCENT, GRIS],
  labels: ['Atendidas', 'Pendientes'],
  legend: { position: 'bottom', fontSize: '12px' },
  plotOptions: { pie: { donut: { size: '68%', labels: { show: true, total: { show: true, label: 'Total', color: '#101c24', fontSize: '13px' } } } } },
  stroke: { width: 2, colors: ['#fff'] },
  dataLabels: { enabled: false },
  tooltip: { theme: 'light' },
}))

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const [resumen, estadosHoy, programaciones] = await Promise.all([
      api<any>('/app/dashboard/medico'),
      api<any[]>('/app/consulta-externa/estado-citas-medico', { query: { fecha: hoyISO } }).catch(() => []),
      api<any[]>('/app/consulta-externa/programacion-medica').catch(() => []),
    ])
    Object.assign(kpis, resumen.kpis)
    serieSemana.value = resumen.serie_semana
    proximasCitas.value = resumen.proximas_citas
    estados.value = Object.fromEntries(estadosHoy.map((e: any) => [e.cita_id, e]))
    proximasJornadas.value = programaciones
      .filter((p: any) => p.fecha >= hoyISO)
      .sort((a: any, b: any) => a.fecha.localeCompare(b.fecha) || a.hora_inicio.localeCompare(b.hora_inicio))
      .slice(0, 6)
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar tu escritorio'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.dash-container { max-width: 1400px; margin: 0 auto; padding: 1.5rem 2rem 3rem; }

/* Banner */
.dash-banner {
  position: relative; overflow: hidden; display: flex; align-items: stretch;
  margin-bottom: 1.5rem; border-radius: var(--radius-lg); box-shadow: var(--shadow-card);
  min-height: 190px; background: linear-gradient(135deg, var(--navy) 0%, var(--navy-hover) 100%);
}
.banner-content { position: relative; z-index: 1; display: flex; flex-direction: column; justify-content: center; gap: 0.5rem; padding: 1.75rem 2rem; flex: 1; min-width: 0; color: white; }
.header-badge { display: inline-flex; align-items: center; gap: 0.375rem; font-size: 0.6875rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: white; background: rgba(255,255,255,0.14); padding: 0.25rem 0.625rem; border-radius: 999px; width: fit-content; }
.dash-title { font-size: 1.75rem; font-weight: 800; color: white; margin: 0; line-height: 1.15; letter-spacing: -0.02em; }
.dash-subtitle { font-size: 0.875rem; color: rgba(255,255,255,0.75); margin: 0; }
.dash-subtitle.cap { text-transform: capitalize; }
.banner-actions { display: flex; align-items: center; gap: 0.75rem; margin-top: 0.5rem; }
.live-pill { display: inline-flex; align-items: center; gap: 0.4rem; font-size: 0.75rem; font-weight: 600; color: #bdf5cf; background: rgba(255,255,255,0.1); padding: 0.35rem 0.75rem; border-radius: 999px; }
.live-dot { width: 7px; height: 7px; border-radius: 999px; background: #4ade80; box-shadow: 0 0 0 0 rgba(74,222,128,0.6); animation: pulse 1.8s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(74,222,128,0.6); } 70% { box-shadow: 0 0 0 8px rgba(74,222,128,0); } 100% { box-shadow: 0 0 0 0 rgba(74,222,128,0); } }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.9rem; border-radius: 8px; font-size: 0.8125rem; font-weight: 500; border: 1px solid rgba(255,255,255,0.18); background: rgba(255,255,255,0.08); color: white; cursor: pointer; transition: all 0.15s ease; }
.btn-secondary:hover:not(:disabled) { background: rgba(255,255,255,0.16); }
.btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.banner-art { position: relative; display: none; flex-shrink: 0; width: 42%; max-width: 420px; }
@media (min-width: 640px) { .banner-art { display: block; } }
.banner-svg { position: absolute; inset: 0; width: 100%; height: 100%; }
.banner-pulse { stroke-dasharray: 1; stroke-dashoffset: 1; animation: banner-draw 4s ease-in-out infinite; }
@keyframes banner-draw { 0% { stroke-dashoffset: 1; opacity: 0.3; } 50% { stroke-dashoffset: 0; opacity: 1; } 100% { stroke-dashoffset: -1; opacity: 0.3; } }
.banner-float { animation: banner-drift 6s ease-in-out infinite; }
.banner-float--1 { animation-duration: 7s; } .banner-float--2 { animation-duration: 5.5s; animation-delay: 0.5s; } .banner-float--3 { animation-duration: 6.5s; animation-delay: 1s; }
@keyframes banner-drift { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.banner-particle { animation: banner-particle-float 8s ease-in-out infinite; }
.banner-particle--delay { animation-delay: 2s; }
@keyframes banner-particle-float { 0%, 100% { transform: translate(0,0) scale(1); opacity: 0.3; } 50% { transform: translate(5px,-20px) scale(0.8); opacity: 0.8; } }

.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 10px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.empty-hint { color: var(--ink-soft); font-size: 0.875rem; padding: 1rem 0; }

/* KPIs */
.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { display: flex; flex-direction: column; gap: 0.375rem; padding: 1.125rem 1.25rem; border-radius: var(--radius-lg); border: 1px solid var(--line); border-left: 3px solid var(--teal); background: var(--paper); box-shadow: var(--shadow-card); }
.stat-top { display: flex; align-items: center; justify-content: space-between; }
.stat-icon { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-num { font-size: 1.5rem; font-weight: 800; color: var(--ink); line-height: 1.2; letter-spacing: -0.02em; }
.stat-label { font-size: 0.8125rem; color: var(--ink-soft); font-weight: 500; }

/* Charts */
.charts-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; align-items: stretch; }
.chart-panel { display: flex; flex-direction: column; min-height: 400px; }
.chart-panel--wide { grid-column: span 2; }
@media (max-width: 900px) { .chart-panel--wide { grid-column: span 1; } }
.chart-body { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.panel-tag { font-size: 0.6875rem; font-weight: 600; color: var(--ink-soft); background: var(--mist); padding: 0.2rem 0.5rem; border-radius: 999px; }
.panel-tag--accent { display: inline-flex; align-items: center; gap: 0.25rem; color: var(--teal); background: var(--teal-soft); }

/* Panels */
.dash-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; align-items: start; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; box-shadow: var(--shadow-card); }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.panel-title { font-size: 0.9375rem; font-weight: 700; color: var(--ink); margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.panel-link { font-size: 0.75rem; color: var(--teal); text-decoration: none; font-weight: 600; }
.panel-link:hover { text-decoration: underline; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 1.5rem; }

/* Activity-style lists (próximas citas / jornadas) */
.activity-list { display: flex; flex-direction: column; gap: 0.875rem; list-style: none; margin: 0; padding: 0; }
.activity-item { display: flex; align-items: flex-start; gap: 0.75rem; }
.activity-dot { width: 26px; height: 26px; border-radius: 999px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; background: var(--teal-soft); color: var(--teal); margin-top: 0.125rem; }
.dot-crear { background: var(--amber-soft); color: var(--amber); }
.activity-body { display: flex; flex-direction: column; min-width: 0; gap: 0.125rem; }
.activity-text { font-size: 0.8125rem; color: var(--ink); line-height: 1.4; }
.activity-text b { font-weight: 700; }
.activity-time { font-size: 0.6875rem; color: var(--ink-soft); }

@media (max-width: 900px) { .dash-grid { grid-template-columns: 1fr; } }
@media (max-width: 640px) {
  .dash-container { padding: 1rem 1rem 2rem; }
  .dash-title { font-size: 1.5rem; }
  .charts-row { grid-template-columns: 1fr; }
  .chart-panel { min-height: 0; }
  .stats-row { grid-template-columns: 1fr; }
}
</style>
