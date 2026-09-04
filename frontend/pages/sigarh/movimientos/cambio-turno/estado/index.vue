<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Estado Cambio de Turno' })

const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string

const lista = ref<any[]>([])
const loading = ref(true)
const filtroEstado = ref('')
const search = ref('')
const activeFilter = ref('all')

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: lista.value.length },
  { label: 'Pendientes', value: 'pendiente', count: pendientes.value },
  { label: 'Aprobados', value: 'aprobado', count: aprobados.value },
  { label: 'Rechazados', value: 'rechazado', count: rechazados.value },
])

const pendientes = computed(() => lista.value.filter(i => i.estado === 'pendiente').length)
const aprobados = computed(() => lista.value.filter(i => i.estado === 'aprobado').length)
const rechazados = computed(() => lista.value.filter(i => i.estado === 'rechazado').length)

const filteredLista = computed(() => {
  let result = lista.value

  if (activeFilter.value !== 'all') {
    result = result.filter(i => i.estado === activeFilter.value)
  }

  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    result = result.filter(i =>
      i.solicitante_nombre?.toLowerCase().includes(q) ||
      i.aceptante_nombre?.toLowerCase().includes(q)
    )
  }

  return result
})

const colorEstado: Record<string, string> = {
  pendiente: 'var(--amber)',
  aprobado: 'var(--green)',
  rechazado: 'var(--alert)'
}

const bgColorEstado: Record<string, string> = {
  pendiente: 'var(--amber-soft)',
  aprobado: 'var(--green-soft)',
  rechazado: 'var(--alert-soft)'
}

const formatEstado = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'Pendiente',
    aprobado: 'Aprobado',
    rechazado: 'Rechazado'
  }
  return map[estado] || estado
}

const getEstadoIcon = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'i-heroicons-clock',
    aprobado: 'i-heroicons-check-circle',
    rechazado: 'i-heroicons-x-circle'
  }
  return map[estado] || 'i-heroicons-circle'
}

const formatDate = (date: string) => {
  if (!date) return '—'
  const d = new Date(date)
  return d.toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const clearFilters = () => {
  search.value = ''
  activeFilter.value = 'all'
  filtroEstado.value = ''
}

async function cargar() {
  loading.value = true
  try {
    const q = filtroEstado.value ? `?estado=${filtroEstado.value}` : ''
    lista.value = await $api(`/sigarh/movimientos/cambio-turno${q}`, { tenant })
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <div class="cambio-turno-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-arrows-right-left" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <h1 class="page-title">Estado Cambio de Turno</h1>
          <p class="page-subtitle">Seguimiento de cambios de turno tramitados</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/movimientos/cambio-turno/tramitar?tenant=${tenant}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Tramitar Cambio
      </NuxtLink>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--navy)">
        <div class="stat-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-arrows-right-left" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ lista.length }}</span>
          <span class="stat-label">Total Solicitudes</span>
        </div>
      </div>

      <!-- Pendientes -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ pendientes }}</span>
          <span class="stat-label">Pendientes</span>
        </div>
      </div>

      <!-- Aprobados -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ aprobados }}</span>
          <span class="stat-label">Aprobados</span>
        </div>
      </div>

      <!-- Rechazados -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--alert)">
        <div class="stat-icon" style="background: var(--alert-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--alert)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ rechazados }}</span>
          <span class="stat-label">Rechazados</span>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <div class="search-wrapper">
          <UIcon name="i-heroicons-magnifying-glass" class="search-icon" />
          <input
            v-model="search"
            type="text"
            placeholder="Buscar por solicitante o aceptante..."
            class="search-input"
            style="border: 1px solid var(--line); background: var(--paper)"
          />
        </div>
        <div class="filter-group">
          <button
            v-for="filter in filters"
            :key="filter.value"
            class="filter-chip"
            :class="{ 'filter-chip--active': activeFilter === filter.value }"
            @click="activeFilter = filter.value; filtroEstado = filter.value === 'all' ? '' : filter.value; cargar()"
          >
            {{ filter.label }}
            <span class="filter-count" :style="{ background: activeFilter === filter.value ? 'var(--teal)' : 'var(--mist)' }">
              {{ filter.count }}
            </span>
          </button>
        </div>
      </div>
      <div class="filter-right">
        <span class="result-count">{{ filteredLista.length }} resultados</span>
        <button
          v-if="filteredLista.length < lista.length || search || activeFilter !== 'all'"
          class="btn-secondary btn-sm"
          @click="clearFilters"
        >
          <UIcon name="i-heroicons-arrow-path" class="w-3.5 h-3.5" />
          Resetear
        </button>
      </div>
    </div>

    <!-- Main Table Card -->
    <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
      <!-- Loading State -->
      <div v-if="loading" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando solicitudes...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredLista.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-arrows-right-left" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay solicitudes de cambio de turno</h3>
        <p style="color: var(--ink-soft)">Comienza tramitando un cambio de turno</p>
        <NuxtLink :to="`/sigarh/movimientos/cambio-turno/tramitar?tenant=${tenant}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Tramitar Cambio
        </NuxtLink>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="cambio-turno-table">
          <thead>
            <tr>
              <th class="col-solicitante">
                <span class="th-content">Solicitante</span>
              </th>
              <th class="col-aceptante">
                <span class="th-content">Aceptante</span>
              </th>
              <th class="col-fecha-original">
                <span class="th-content">Fecha Original</span>
              </th>
              <th class="col-fecha-reemplazo">
                <span class="th-content">Fecha Reemplazo</span>
              </th>
              <th class="col-estado">
                <span class="th-content">Estado</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in filteredLista" :key="c.id" class="table-row">
              <td class="col-solicitante">
                <div class="solicitante-cell">
                  <div class="solicitante-avatar" :style="{ background: getEmployeeColor(c.solicitante_nombre || '') }">
                    <span>{{ getInitials(c.solicitante_nombre || '—') }}</span>
                  </div>
                  <span class="solicitante-name">{{ c.solicitante_nombre || '—' }}</span>
                </div>
              </td>
              <td class="col-aceptante">
                <div class="aceptante-cell">
                  <div class="aceptante-avatar" :style="{ background: getEmployeeColor(c.aceptante_nombre || '') }">
                    <span>{{ getInitials(c.aceptante_nombre || '—') }}</span>
                  </div>
                  <span class="aceptante-name">{{ c.aceptante_nombre || '—' }}</span>
                </div>
              </td>
              <td class="col-fecha-original">
                <span class="fecha-text font-mono-data">{{ formatDate(c.fecha_original) }}</span>
              </td>
              <td class="col-fecha-reemplazo">
                <span class="fecha-text font-mono-data">{{ formatDate(c.fecha_reemplazo) }}</span>
              </td>
              <td class="col-estado">
                <span class="status-badge" :style="{ background: bgColorEstado[c.estado] || 'var(--mist)', color: colorEstado[c.estado] || 'var(--ink-soft)' }">
                  <UIcon :name="getEstadoIcon(c.estado)" class="w-3.5 h-3.5" />
                  {{ formatEstado(c.estado) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table Footer -->
      <div v-if="filteredLista.length > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ filteredLista.length }}</strong> de <strong>{{ lista.length }}</strong> solicitudes
          <span v-if="filteredLista.length < lista.length">(filtradas)</span>
        </span>
        <span class="footer-summary">
          <span class="summary-dot" style="background: var(--amber)" />
          {{ pendientes }} pendientes
          <span class="summary-dot" style="background: var(--green)" />
          {{ aprobados }} aprobados
          <span class="summary-dot" style="background: var(--alert)" />
          {{ rechazados }} rechazados
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cambio-turno-container {
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

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--teal);
  color: white;
  border: none;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--teal-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--mist);
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

/* Widgets Grid */
.widgets-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-widget {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.stat-widget:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Filter Bar */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  flex: 1;
}

.search-wrapper {
  position: relative;
  min-width: 200px;
  flex: 1;
  max-width: 300px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: var(--ink-soft);
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.filter-group {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: transparent;
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-chip:hover {
  background: var(--mist);
}

.filter-chip--active {
  background: var(--teal-soft);
  border-color: var(--teal);
  color: var(--teal);
}

.filter-count {
  padding: 0.0625rem 0.375rem;
  border-radius: 10px;
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--ink-soft);
  background: var(--mist);
  transition: all 0.2s ease;
}

.filter-chip--active .filter-count {
  background: var(--teal);
  color: white;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.result-count {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Table States */
.table-loading,
.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.table-empty h3 {
  font-size: 1.125rem;
  margin: 0;
}

.table-empty p {
  margin: 0;
}

/* Table Card */
.table-card {
  overflow: hidden;
}

.table-responsive {
  overflow-x: auto;
}

.cambio-turno-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.cambio-turno-table thead {
  background: var(--mist);
}

.cambio-turno-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--ink-soft);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--line);
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.cambio-turno-table td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--line);
  vertical-align: middle;
}

.table-row {
  transition: background 0.15s ease;
}

.table-row:hover {
  background: var(--mist);
}

.col-solicitante { width: 22%; }
.col-aceptante { width: 22%; }
.col-fecha-original { width: 18%; }
.col-fecha-reemplazo { width: 18%; }
.col-estado { width: 20%; }

/* Solicitante Cell */
.solicitante-cell,
.aceptante-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.solicitante-avatar,
.aceptante-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--ink);
  flex-shrink: 0;
}

.solicitante-name,
.aceptante-name {
  font-weight: 500;
  color: var(--ink);
}

/* Fecha */
.fecha-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Table Footer */
.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  border-top: 1px solid var(--line);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.footer-info {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.footer-summary {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.summary-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

/* Responsive */
@media (max-width: 1200px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .cambio-turno-container {
    padding: 1rem 1.5rem;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-left {
    flex-direction: column;
    align-items: stretch;
  }

  .search-wrapper {
    max-width: none;
  }
}

@media (max-width: 768px) {
  .cambio-turno-container {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-header .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .widgets-grid {
    grid-template-columns: 1fr 1fr;
  }

  .filter-group {
    flex-wrap: wrap;
  }

  .col-solicitante,
  .col-aceptante {
    min-width: 120px;
  }

  .table-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .footer-summary {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .widgets-grid {
    grid-template-columns: 1fr;
  }

  .filter-chip {
    font-size: 0.6875rem;
    padding: 0.25rem 0.5rem;
  }

  .table-responsive {
    margin: 0 -0.5rem;
  }

  .cambio-turno-table td,
  .cambio-turno-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }

  .col-solicitante,
  .col-aceptante {
    min-width: 100px;
  }
}
</style>