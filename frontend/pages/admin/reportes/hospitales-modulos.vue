<template>
  <div class="auditoria-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-squares-plus" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <h1 class="page-title">Reporte de Hospitales y Módulos</h1>
          <p class="page-subtitle">Módulos activos por cada hospital habilitado en el sistema.</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="exportCsv">
          <UIcon name="i-heroicons-arrow-down-tray" class="w-4 h-4" />
          Exportar CSV
        </button>
      </div>
    </div>

    <!-- Resumen: antes el reporte arrancaba directo en la tabla, sin ningun
         numero de conjunto -- un vistazo del total antes de entrar hospital
         por hospital. -->
    <div v-if="!loading && !error && rows.length" class="summary-grid">
      <div class="summary-card">
        <div class="summary-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <p class="summary-value">{{ rows.length }}</p>
          <p class="summary-label">Hospitales activos</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="summary-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-squares-2x2" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <p class="summary-value">{{ promedioModulos }}</p>
          <p class="summary-label">Promedio de módulos por hospital</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="summary-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-cube" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <p class="summary-value">{{ totalModulosDistintos }}</p>
          <p class="summary-label">Módulos distintos en uso</p>
        </div>
      </div>
    </div>

    <div class="search-bar-wrap">
      <div class="search-wrapper" style="max-width: 320px;">
        <UIcon name="i-heroicons-magnifying-glass" class="search-icon" />
        <input v-model="search" class="search-input" placeholder="Buscar hospital..." />
      </div>
    </div>

    <div v-if="loading" class="state-card">
      <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
      <p style="color: var(--ink-soft)">Cargando reporte...</p>
    </div>
    <div v-else-if="error" class="state-card">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
      <p style="color: var(--alert)">{{ error }}</p>
    </div>
    <div v-else-if="!filtrados.length" class="state-card">
      <UIcon name="i-heroicons-squares-plus" class="w-10 h-10" style="color: var(--ink-soft)" />
      <h3 style="color: var(--ink)">{{ search ? 'Sin resultados' : 'Sin hospitales activos' }}</h3>
    </div>

    <div v-else class="hospitales-grid">
      <div v-for="row in filtrados" :key="row.domain" class="hospital-card">
        <div class="hospital-card-header">
          <div class="min-w-0">
            <h3 class="hospital-name">{{ row.hospital_name }}</h3>
            <p class="hospital-domain">{{ row.domain }}</p>
          </div>
          <span v-if="row.hospital_level" class="level-badge">{{ row.hospital_level }}</span>
        </div>

        <div class="coverage-bar" :title="`${row.app_modules} App · ${row.sigarh_modules} SIGARH`">
          <div class="coverage-bar-app" :style="{ width: `${(row.app_modules / (row.total_modules || 1)) * 100}%` }" />
          <div class="coverage-bar-sigarh" :style="{ width: `${(row.sigarh_modules / (row.total_modules || 1)) * 100}%` }" />
        </div>

        <div class="stat-row">
          <span class="stat-chip stat-chip--app">
            <span class="stat-dot stat-dot--app" />
            {{ row.app_modules }} App
          </span>
          <span class="stat-chip stat-chip--sigarh">
            <span class="stat-dot stat-dot--sigarh" />
            {{ row.sigarh_modules }} SIGARH
          </span>
          <span class="stat-total">{{ row.total_modules }} en total</span>
        </div>

        <button class="toggle-modules" @click="toggle(row.domain)">
          {{ abiertos.has(row.domain) ? 'Ocultar módulos' : 'Ver módulos' }}
          <UIcon name="i-heroicons-chevron-down" class="w-3.5 h-3.5 toggle-chevron" :class="{ 'toggle-chevron--open': abiertos.has(row.domain) }" />
        </button>

        <div v-if="abiertos.has(row.domain)" class="modules-detail">
          <template v-for="grupo in agruparPorCategoria(row.modules)" :key="grupo.categoria">
            <p class="modules-group-label" :class="`modules-group-label--${grupo.categoria}`">
              {{ grupo.categoria === 'app' ? 'Panel Hospitalario' : 'SIGARH' }}
            </p>
            <div class="module-tags-wrap">
              <span v-for="mod in grupo.items" :key="mod.code" class="module-tag" :class="`module-tag--${grupo.categoria}`">
                {{ mod.name }}
              </span>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface ModuleReportItem {
  code: string
  name: string
  category: string
}

interface HospitalModuleReport {
  hospital_name: string
  domain: string
  hospital_level: string | null
  modules: ModuleReportItem[]
  total_modules: number
  app_modules: number
  sigarh_modules: number
}

const { api } = useApi()

const rows = ref<HospitalModuleReport[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const abiertos = reactive(new Set<string>())

const toggle = (domain: string) => {
  if (abiertos.has(domain)) abiertos.delete(domain)
  else abiertos.add(domain)
}

const agruparPorCategoria = (modules: ModuleReportItem[]) => {
  const app = modules.filter(m => m.category === 'app')
  const sigarh = modules.filter(m => m.category === 'sigarh')
  const grupos = []
  if (app.length) grupos.push({ categoria: 'app', items: app })
  if (sigarh.length) grupos.push({ categoria: 'sigarh', items: sigarh })
  return grupos
}

const filtrados = computed(() => {
  if (!search.value.trim()) return rows.value
  const q = search.value.toLowerCase()
  return rows.value.filter(r =>
    r.hospital_name.toLowerCase().includes(q) ||
    r.domain.toLowerCase().includes(q)
  )
})

const promedioModulos = computed(() => {
  if (!rows.value.length) return 0
  return Math.round(rows.value.reduce((acc, r) => acc + r.total_modules, 0) / rows.value.length)
})

const totalModulosDistintos = computed(() => {
  const codigos = new Set<string>()
  rows.value.forEach(r => r.modules.forEach(m => codigos.add(m.code)))
  return codigos.size
})

// Mismo escape que ya usa reportes/exportar.vue: una celda que empieza con
// = + - @ o tab puede interpretarse como formula al abrir el CSV en Excel/
// Sheets -- se le antepone un apostrofe para forzarla a texto plano.
const celdaSegura = (v: string) => /^[=+\-@\t]/.test(v) ? `'${v}` : v

const exportCsv = () => {
  const headers = ['Hospital', 'Dominio', 'Nivel MINSA', 'Módulos App', 'Módulos SIGARH', 'Total', 'Módulos Activos']
  const rowsCsv = filtrados.value.map(r => [
    r.hospital_name,
    r.domain,
    r.hospital_level ?? '',
    String(r.app_modules),
    String(r.sigarh_modules),
    String(r.total_modules),
    r.modules.map(m => m.name).join(' | '),
  ])
  const csv = [
    headers.join(','),
    ...rowsCsv.map(r => r.map(v => `"${celdaSegura(String(v ?? '')).replace(/"/g, '""')}"`).join(',')),
  ].join('\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `hospitales_modulos_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    rows.value = await api<HospitalModuleReport[]>('/admin/reportes/hospitales-modulos')
  } catch (e: any) {
    error.value = apiErr(e, 'Error de conexión')
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.summary-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 1.1rem 1.25rem;
}
.summary-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.summary-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.1;
}
.summary-label {
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin-top: 0.15rem;
}

.search-bar-wrap {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
}

.state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 3.5rem 1rem;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.hospitales-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1rem;
}

.hospital-card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 1.25rem;
  transition: box-shadow 0.15s ease, transform 0.15s ease;
}
.hospital-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md, var(--shadow-card));
}

.hospital-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.9rem;
}
.hospital-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.hospital-domain {
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin-top: 0.1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.level-badge {
  flex-shrink: 0;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: var(--mist);
  color: var(--ink-soft);
}

.coverage-bar {
  display: flex;
  height: 6px;
  border-radius: 999px;
  overflow: hidden;
  background: var(--mist);
  margin-bottom: 0.75rem;
}
.coverage-bar-app { background: var(--teal); }
.coverage-bar-sigarh { background: #6366f1; }

.stat-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 0.9rem;
}
.stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
}
.stat-chip--app { background: var(--teal-soft); color: var(--teal); }
.stat-chip--sigarh { background: rgba(99,102,241,0.12); color: #4f46e5; }
.stat-dot { width: 6px; height: 6px; border-radius: 50%; }
.stat-dot--app { background: var(--teal); }
.stat-dot--sigarh { background: #6366f1; }
.stat-total { font-size: 0.75rem; color: var(--ink-soft); margin-left: auto; }

.toggle-modules {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--teal);
  padding: 0;
  border-top: 1px solid var(--line);
  padding-top: 0.75rem;
  width: 100%;
}
.toggle-chevron { transition: transform 0.15s ease; }
.toggle-chevron--open { transform: rotate(180deg); }

.modules-detail {
  margin-top: 0.75rem;
  padding-top: 0.15rem;
}
.modules-group-label {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0.6rem 0 0.4rem;
}
.modules-group-label--app { color: var(--teal); }
.modules-group-label--sigarh { color: #4f46e5; }
.modules-group-label:first-child { margin-top: 0; }

.module-tags-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.module-tag {
  font-size: 0.7rem;
  font-weight: 500;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}
.module-tag--app { background: var(--teal-soft); color: var(--teal); }
.module-tag--sigarh { background: rgba(99,102,241,0.1); color: #4f46e5; }
</style>
