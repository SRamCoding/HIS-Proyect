<!-- pages/admin/index.vue -->
<template>
  <div>
    <!-- Banner de bienvenida -->
    <div
      class="relative overflow-hidden mb-6 flex items-stretch"
      style="border-radius: var(--radius-lg); box-shadow: var(--shadow-card); height: 160px; background: linear-gradient(120deg, #0b5fa8 0%, #0d3f6e 100%)"
    >
      <!-- Columna izquierda: texto -->
      <div class="relative z-10 flex flex-col justify-center px-8 py-6 flex-1 min-w-0">
        <h1 class="text-2xl font-bold text-white mb-1 truncate">Hola, {{ nombreUsuario }}</h1>
        <p class="text-sm text-white/85">{{ saludoHora }}</p>
      </div>

      <!-- Columna derecha: animación, contenida en su propio espacio -->
      <div class="relative hidden sm:block shrink-0" style="width: 42%; max-width: 380px">
        <svg class="absolute inset-0 w-full h-full" viewBox="0 0 400 160" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
          <circle class="banner-float banner-float--1" cx="330" cy="35" r="42" fill="rgba(255,255,255,0.06)" />
          <circle class="banner-float banner-float--2" cx="270" cy="120" r="26" fill="rgba(255,255,255,0.05)" />
          <circle class="banner-float banner-float--3" cx="365" cy="125" r="16" fill="rgba(255,255,255,0.08)" />

          <g class="banner-cross" transform="translate(300,45)" opacity="0.5">
            <rect x="-3" y="-14" width="6" height="28" rx="2" fill="#e0f2fe" />
            <rect x="-14" y="-3" width="28" height="6" rx="2" fill="#e0f2fe" />
          </g>
          <g class="banner-cross banner-cross--delay" transform="translate(360,80)" opacity="0.35">
            <rect x="-2.5" y="-11" width="5" height="22" rx="2" fill="#e0f2fe" />
            <rect x="-11" y="-2.5" width="22" height="5" rx="2" fill="#e0f2fe" />
          </g>

          <path
            class="banner-pulse"
            d="M0,90 L60,90 L80,90 L92,45 L108,135 L124,90 L150,90 L162,68 L174,90 L400,90"
            fill="none"
            stroke="#5fd4c6"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            pathLength="1"
          />
        </svg>
      </div>

      
    </div>

    <!-- Stat cards con tendencia -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div v-for="i in 4" :key="i" class="stat-card animate-pulse">
        <div class="h-3 w-20 rounded mb-3" style="background: var(--line)" />
        <div class="h-6 w-14 rounded" style="background: var(--line)" />
      </div>
    </div>

    <div v-else-if="error" class="text-sm rounded-lg px-4 py-3 mb-6" style="background: var(--alert-soft); color: var(--alert)">
      No se pudo cargar el dashboard: {{ error }}
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 18px">
        <div class="flex items-start justify-between mb-3">
          <div class="w-9 h-9 rounded-lg flex items-center justify-center" style="background: var(--mist)">
            <UIcon name="i-heroicons-building-office-2" class="w-4.5 h-4.5" style="color: var(--navy)" />
          </div>
          <span class="text-xs font-medium flex items-center gap-0.5" style="color: var(--ok)">
            <UIcon name="i-heroicons-arrow-trending-up" class="w-3.5 h-3.5" />
            {{ stats?.hospitales_activos_delta ?? 0 }}%
          </span>
        </div>
        <p class="text-2xl font-bold font-mono-data leading-tight" style="color: var(--ink)">
          {{ stats?.hospitales_activos ?? '—' }}
        </p>
        <p class="text-xs mt-0.5" style="color: var(--ink-soft)">Hospitales activos</p>
      </div>

      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 18px">
        <div class="flex items-start justify-between mb-3">
          <div class="w-9 h-9 rounded-lg flex items-center justify-center" style="background: var(--ok-soft)">
            <UIcon name="i-heroicons-users" class="w-4.5 h-4.5" style="color: var(--ok)" />
          </div>
          <span class="text-xs font-medium flex items-center gap-0.5" style="color: var(--ok)">
            <UIcon name="i-heroicons-arrow-trending-up" class="w-3.5 h-3.5" />
            {{ stats?.usuarios_delta ?? 0 }}%
          </span>
        </div>
        <p class="text-2xl font-bold font-mono-data leading-tight" style="color: var(--ink)">
          {{ stats?.usuarios_totales ?? '—' }}
        </p>
        <p class="text-xs mt-0.5" style="color: var(--ink-soft)">Usuarios totales</p>
      </div>

      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 18px">
        <div class="flex items-start justify-between mb-3">
          <div class="w-9 h-9 rounded-lg flex items-center justify-center" style="background: var(--warn-soft)">
            <UIcon name="i-heroicons-squares-plus" class="w-4.5 h-4.5" style="color: var(--warn)" />
          </div>
          <span class="text-xs font-medium flex items-center gap-0.5" style="color: var(--ink-soft)">
            <UIcon name="i-heroicons-minus" class="w-3.5 h-3.5" />
            0%
          </span>
        </div>
        <p class="text-2xl font-bold font-mono-data leading-tight" style="color: var(--ink)">
          {{ stats?.modulos_activos ?? '—' }}
        </p>
        <p class="text-xs mt-0.5" style="color: var(--ink-soft)">Módulos activos</p>
      </div>

      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 18px">
        <div class="flex items-start justify-between mb-3">
          <div class="w-9 h-9 rounded-lg flex items-center justify-center" style="background: var(--alert-soft)">
            <UIcon name="i-heroicons-shield-exclamation" class="w-4.5 h-4.5" style="color: var(--alert)" />
          </div>
          <span class="text-xs font-medium flex items-center gap-0.5" style="color: var(--alert)">
            <UIcon name="i-heroicons-arrow-trending-down" class="w-3.5 h-3.5" />
            {{ stats?.eventos_delta ?? 0 }}%
          </span>
        </div>
        <p class="text-2xl font-bold font-mono-data leading-tight" style="color: var(--ink)">
          {{ stats?.eventos_auditoria_24h ?? '—' }}
        </p>
        <p class="text-xs mt-0.5" style="color: var(--ink-soft)">Eventos auditoría (24h)</p>
      </div>
    </div>

    <!-- Fila: barras + anillos (ApexCharts) -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">

      <!-- Barras: hospitales creados por mes -->
      <div class="lg:col-span-2" style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <div class="flex items-center justify-between mb-2">
          <p class="text-sm font-semibold" style="color: var(--ink)">Hospitales registrados por mes</p>
          <span class="text-xs font-mono-data" style="color: var(--ink-soft)">últimos 6 meses</span>
        </div>
        <ClientOnly>
          <ApexChart
            type="bar"
            height="220"
            :options="barChartOptions"
            :series="barChartSeries"
          />
        </ClientOnly>
      </div>

      <!-- Anillo: uso de módulos -->
      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <p class="text-sm font-semibold mb-2" style="color: var(--ink)">Uso de módulos</p>
        <ClientOnly>
          <ApexChart
            type="radialBar"
            height="240"
            :options="radialChartOptions"
            :series="[usoModulos.app, usoModulos.sigarh]"
          />
        </ClientOnly>
        <div class="space-y-2 text-xs -mt-2">
          <div class="flex items-center justify-between">
            <span class="flex items-center gap-1.5" style="color: var(--ink-soft)">
              <span class="w-2 h-2 rounded-full" style="background: var(--teal)" />
              Panel admin
            </span>
            <span class="font-mono-data" style="color: var(--ink)">{{ usoModulos.app }}%</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="flex items-center gap-1.5" style="color: var(--ink-soft)">
              <span class="w-2 h-2 rounded-full" style="background: #6366f1" />
              Panel SIGARH
            </span>
            <span class="font-mono-data" style="color: var(--ink)">{{ usoModulos.sigarh }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Fila: distribución por nivel + top hospitales -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">

      <!-- Distribución por nivel MINSA -->
      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <p class="text-sm font-semibold mb-4" style="color: var(--ink)">Hospitales por nivel MINSA</p>
        <div class="space-y-3">
          <div v-for="nivel in distribucionNiveles" :key="nivel.code">
            <div class="flex items-center justify-between text-xs mb-1">
              <span class="font-medium" style="color: var(--ink)">{{ nivel.code }}</span>
              <span style="color: var(--ink-soft)">{{ nivel.cantidad }}</span>
            </div>
            <div class="h-1.5 rounded-full overflow-hidden" style="background: var(--mist)">
              <div
                class="h-full rounded-full"
                :style="{ width: `${(nivel.cantidad / maxNivel) * 100}%`, background: nivel.color }"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Top hospitales por módulos -->
      <div class="lg:col-span-2" style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <p class="text-sm font-semibold mb-4" style="color: var(--ink)">Hospitales con más módulos activos</p>
        <div class="space-y-3">
          <div
            v-for="(h, i) in topHospitalesModulos"
            :key="h.id"
            class="flex items-center gap-3"
          >
            <span class="text-xs font-bold w-4 shrink-0" style="color: var(--ink-soft)">{{ i + 1 }}</span>
            <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style="background: var(--mist)">
              <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" style="color: var(--navy)" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium truncate" style="color: var(--ink)">{{ h.nombre }}</p>
              <div class="h-1.5 rounded-full overflow-hidden mt-1" style="background: var(--mist)">
                <div class="h-full rounded-full" :style="{ width: `${(h.modulos / maxModulosTop) * 100}%`, background: 'var(--teal)' }" />
              </div>
            </div>
            <span class="text-sm font-mono-data font-semibold shrink-0" style="color: var(--ink)">{{ h.modulos }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Hospitales recientes -->
    <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
      <div class="flex items-center justify-between px-5 py-4" style="border-bottom: 1px solid var(--line)">
        <h2 class="text-sm font-semibold" style="color: var(--ink)">Hospitales recientes</h2>
        <NuxtLink to="/admin/hospitales" class="text-sm font-medium flex items-center gap-1" style="color: var(--teal)">
          Ver todos
          <UIcon name="i-heroicons-arrow-right" class="w-3.5 h-3.5" />
        </NuxtLink>
      </div>

      <div v-if="loadingHospitales" class="flex items-center gap-2 p-5 text-sm" style="color: var(--ink-soft)">
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
        Cargando…
      </div>

      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-semibold px-5 py-2.5 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">Nombre</th>
            <th class="text-left font-semibold px-5 py-2.5 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">Nivel MINSA</th>
            <th class="text-left font-semibold px-5 py-2.5 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="h in hospitalesRecientes"
            :key="h.id"
            style="border-bottom: 1px solid var(--line)"
          >
            <td class="px-5 py-3">
              <div class="flex items-center gap-2.5">
                <div class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0" style="background: var(--mist)">
                  <UIcon name="i-heroicons-building-office-2" class="w-3.5 h-3.5" style="color: var(--navy)" />
                </div>
                <span style="color: var(--ink)">{{ h.nombre }}</span>
              </div>
            </td>
            <td class="px-5 py-3 font-mono-data" style="color: var(--ink-soft)">{{ h.nivel_minsa ?? '—' }}</td>
            <td class="px-5 py-3">
              <span class="badge" :class="h.activo ? 'badge--ok' : 'badge--neutral'">
                {{ h.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
          </tr>
      <tr v-if="!hospitalesRecientes.length">
  <td colspan="3" class="py-10">
    <div class="flex flex-col items-center gap-3">
      <div
        class="w-56 h-28 bg-no-repeat bg-center bg-contain opacity-90"
        style="background-image: url('/hospital-empty.svg')"
      />
      <p class="text-sm" style="color: var(--ink-soft)">Sin hospitales registrados todavía.</p>
      <NuxtLink to="/admin/hospitales/create" class="btn-primary text-sm mt-1">
        Crear el primero
      </NuxtLink>
    </div>
  </td>
</tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface DashboardStats {
  hospitales_activos: number
  hospitales_activos_delta?: number
  usuarios_totales: number
  usuarios_delta?: number
  modulos_activos: number
  eventos_auditoria_24h: number
  eventos_delta?: number
}

interface Hospital {
  id: string
  nombre: string
  nivel_minsa?: string
  activo: boolean
}

const { api } = useApi()
const authStore = useAuthStore()

const stats = ref<DashboardStats | null>(null)
const hospitalesRecientes = ref<Hospital[]>([])
const loading = ref(true)
const loadingHospitales = ref(true)
const error = ref('')
const minutosDesdeActualizacion = ref(2)

const nombreUsuario = computed(() => authStore.user?.name || 'bienvenido')

const saludoHora = computed(() => {
  const hora = new Date().getHours()
  if (hora < 12) return 'Buenos días, aquí tienes el resumen de la plataforma.'
  if (hora < 19) return 'Buenas tardes, aquí tienes el resumen de la plataforma.'
  return 'Buenas noches, aquí tienes el resumen de la plataforma.'
})

// ── MOCK: datos para gráficos que aún no expone el backend ──
// Reemplazar por endpoints reales cuando estén disponibles:
//   /admin/dashboard/registros-por-mes
//   /admin/dashboard/uso-modulos
//   /admin/dashboard/distribucion-niveles
//   /admin/dashboard/top-hospitales-modulos

const registrosPorMes = ref([
  { label: 'Abr', valor: 2 },
  { label: 'May', valor: 3 },
  { label: 'Jun', valor: 1 },
  { label: 'Jul', valor: 4 },
  { label: 'Ago', valor: 3 },
  { label: 'Sep', valor: 5 },
])

const usoModulos = ref({ app: 68, sigarh: 45 })

const distribucionNiveles = ref([
  { code: 'I-1', cantidad: 4, color: 'var(--teal)' },
  { code: 'I-4', cantidad: 3, color: 'var(--navy)' },
  { code: 'II-1', cantidad: 5, color: '#6366f1' },
  { code: 'II-2', cantidad: 2, color: 'var(--warn)' },
  { code: 'III-1', cantidad: 1, color: 'var(--alert)' },
])
const maxNivel = computed(() => Math.max(...distribucionNiveles.value.map(n => n.cantidad), 1))

const topHospitalesModulos = ref([
  { id: '1', nombre: 'Hospital Regional Lambayeque', modulos: 22 },
  { id: '2', nombre: 'Hospital Túmán', modulos: 18 },
  { id: '3', nombre: 'Hospital Naylamp', modulos: 15 },
  { id: '4', nombre: 'Centro de Salud Pátapo', modulos: 9 },
])
const maxModulosTop = computed(() => Math.max(...topHospitalesModulos.value.map(h => h.modulos), 1))

// ── ApexCharts: opciones y series ──

const barChartSeries = computed(() => [
  { name: 'Hospitales', data: registrosPorMes.value.map(m => m.valor) },
])

const barChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, fontFamily: 'IBM Plex Sans, sans-serif' },
  colors: ['#0891b2'],
  plotOptions: {
    bar: {
      borderRadius: 6,
      columnWidth: '55%',
      distributed: false,
    },
  },
  dataLabels: { enabled: false },
  xaxis: {
    categories: registrosPorMes.value.map(m => m.label),
    labels: { style: { colors: '#4a5c66', fontSize: '12px' } },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: { labels: { style: { colors: '#4a5c66', fontSize: '11px' } } },
  grid: { borderColor: '#dce5e7', strokeDashArray: 3 },
  tooltip: { theme: 'light' },
}))

const radialChartOptions = computed(() => ({
  chart: { fontFamily: 'IBM Plex Sans, sans-serif' },
  colors: ['#0891b2', '#6366f1'],
  plotOptions: {
    radialBar: {
      hollow: { size: '45%' },
      track: { background: '#eef3f4' },
      dataLabels: {
        name: { show: false },
        value: { show: false },
      },
    },
  },
  labels: ['Panel admin', 'Panel SIGARH'],
  legend: { show: false },
  stroke: { lineCap: 'round' },
}))

// ── FIN MOCK / ApexCharts ──

onMounted(async () => {
  try {
    stats.value = await api<DashboardStats>('/admin/dashboard')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }

  try {
    const data = await api<Hospital[]>('/admin/hospitales')
    hospitalesRecientes.value = data.slice(0, 5)
  } finally {
    loadingHospitales.value = false
  }
})
</script>

<style scoped>
.banner-pulse {
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  animation: banner-draw 4s ease-in-out infinite;
}

@keyframes banner-draw {
  0% { stroke-dashoffset: 1; opacity: 0.3; }
  50% { stroke-dashoffset: 0; opacity: 1; }
  100% { stroke-dashoffset: -1; opacity: 0.3; }
}

.banner-float {
  animation: banner-drift 6s ease-in-out infinite;
}
.banner-float--1 { animation-duration: 7s; }
.banner-float--2 { animation-duration: 5.5s; animation-delay: 0.5s; }
.banner-float--3 { animation-duration: 6.5s; animation-delay: 1s; }

@keyframes banner-drift {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.banner-cross {
  animation: banner-pulse-fade 3s ease-in-out infinite;
}
.banner-cross--delay {
  animation-delay: 1.5s;
}

@keyframes banner-pulse-fade {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}
</style>