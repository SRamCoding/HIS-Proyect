<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Estado de Licencias' })

const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string

const licencias = ref<any[]>([])
const loading = ref(true)
const filtroEstado = ref('')
const search = ref('')
const activeFilter = ref('all')

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: licencias.value.length },
  { label: 'Pendientes', value: 'pendiente', count: pendientes.value },
  { label: 'Aprobados', value: 'aprobado', count: aprobados.value },
  { label: 'Rechazados', value: 'rechazado', count: rechazados.value },
])

const pendientes = computed(() => licencias.value.filter(l => l.estado === 'pendiente').length)
const aprobados = computed(() => licencias.value.filter(l => l.estado === 'aprobado').length)
const rechazados = computed(() => licencias.value.filter(l => l.estado === 'rechazado').length)

const filteredLicencias = computed(() => {
  let result = licencias.value

  if (activeFilter.value !== 'all') {
    result = result.filter(l => l.estado === activeFilter.value)
  }

  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    result = result.filter(l =>
      l.nombre_empleado?.toLowerCase().includes(q) ||
      l.tipo_licencia?.toLowerCase().includes(q)
    )
  }

  return result
})

const estadoColor: Record<string, string> = {
  pendiente: 'var(--amber)',
  aprobado: 'var(--green)',
  rechazado: 'var(--alert)'
}

const estadoBgColor: Record<string, string> = {
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

const getTipoColor = (tipo: string) => {
  const map: Record<string, string> = {
    'CON GOCE DE HABER': 'var(--green)',
    'SIN GOCE DE HABER': 'var(--alert)',
    'POR ENFERMEDAD': 'var(--amber)',
    'POR MATERNIDAD': 'var(--purple)',
    'POR PATERNIDAD': 'var(--teal)',
    'POR FALLECIMIENTO': 'var(--navy)'
  }
  return map[tipo] || 'var(--ink-soft)'
}

const getTipoBgColor = (tipo: string) => {
  const map: Record<string, string> = {
    'CON GOCE DE HABER': 'var(--green-soft)',
    'SIN GOCE DE HABER': 'var(--alert-soft)',
    'POR ENFERMEDAD': 'var(--amber-soft)',
    'POR MATERNIDAD': 'var(--purple-soft)',
    'POR PATERNIDAD': 'var(--teal-soft)',
    'POR FALLECIMIENTO': 'var(--navy-soft)'
  }
  return map[tipo] || 'var(--mist)'
}

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

const clearFilters = () => {
  search.value = ''
  activeFilter.value = 'all'
  filtroEstado.value = ''
}

async function cargar() {
  loading.value = true
  try {
    const params = filtroEstado.value ? `?estado=${filtroEstado.value}` : ''
    licencias.value = await $api(`/sigarh/movimientos/licencias${params}`, { tenant })
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <div class="licencias-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-document-text" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Estado de Licencias</h1>
          <p class="page-subtitle">Seguimiento de licencias tramitadas</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/movimientos/licencias/create?tenant=${tenant}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Tramitar Licencia
      </NuxtLink>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--teal)">
        <div class="stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-document-text" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ licencias.length }}</span>
          <span class="stat-label">Total Licencias</span>
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
            placeholder="Buscar por empleado o tipo..."
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
        <span class="result-count">{{ filteredLicencias.length }} resultados</span>
        <button
          v-if="filteredLicencias.length < licencias.length || search || activeFilter !== 'all'"
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
        <p style="color: var(--ink-soft)">Cargando licencias...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredLicencias.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-document-text" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay licencias registradas</h3>
        <p style="color: var(--ink-soft)">Comienza tramitando una licencia</p>
        <NuxtLink :to="`/sigarh/movimientos/licencias/create?tenant=${tenant}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Tramitar Licencia
        </NuxtLink>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="licencias-table">
          <thead>
            <tr>
              <th class="col-employee">
                <span class="th-content">Empleado</span>
              </th>
              <th class="col-type">
                <span class="th-content">Tipo</span>
              </th>
              <th class="col-start">
                <span class="th-content">Desde</span>
              </th>
              <th class="col-end">
                <span class="th-content">Hasta</span>
              </th>
              <th class="col-days">
                <span class="th-content">Días</span>
              </th>
              <th class="col-status">
                <span class="th-content">Estado</span>
              </th>
              <th class="col-actions">
                <span class="th-content">Acciones</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in filteredLicencias" :key="l.id" class="table-row">
              <td class="col-employee">
                <div class="employee-cell">
                  <div class="employee-avatar" :style="{ background: getEmployeeColor(l.nombre_empleado || '') }">
                    <span>{{ getInitials(l.nombre_empleado || '—') }}</span>
                  </div>
                  <span class="employee-name">{{ l.nombre_empleado || '—' }}</span>
                </div>
              </td>
              <td class="col-type">
                <span class="type-badge" :style="{ background: getTipoBgColor(l.tipo_licencia), color: getTipoColor(l.tipo_licencia) }">
                  {{ l.tipo_licencia }}
                </span>
              </td>
              <td class="col-start">
                <span class="date-text font-mono-data">{{ formatDate(l.fecha_inicio) }}</span>
              </td>
              <td class="col-end">
                <span class="date-text font-mono-data">{{ formatDate(l.fecha_fin) }}</span>
              </td>
              <td class="col-days">
                <span class="days-badge">{{ l.dias_solicitados || '—' }}</span>
              </td>
              <td class="col-status">
                <span class="status-badge" :style="{ background: estadoBgColor[l.estado] || 'var(--mist)', color: estadoColor[l.estado] || 'var(--ink-soft)' }">
                  <UIcon :name="getEstadoIcon(l.estado)" class="w-3.5 h-3.5" />
                  {{ formatEstado(l.estado) }}
                </span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <NuxtLink
                    :to="`/sigarh/movimientos/licencias/${l.id}?tenant=${tenant}`"
                    class="action-btn action-view"
                    title="Ver detalle"
                  >
                    <UIcon name="i-heroicons-eye" class="w-4 h-4" />
                  </NuxtLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table Footer -->
      <div v-if="filteredLicencias.length > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ filteredLicencias.length }}</strong> de <strong>{{ licencias.length }}</strong> licencias
          <span v-if="filteredLicencias.length < licencias.length">(filtradas)</span>
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
.licencias-container {
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

.licencias-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.licencias-table thead {
  background: var(--mist);
}

.licencias-table th {
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

.licencias-table td {
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

.col-employee { width: 20%; }
.col-type { width: 18%; }
.col-start { width: 13%; }
.col-end { width: 13%; }
.col-days { width: 8%; }
.col-status { width: 15%; }
.col-actions { width: 13%; text-align: right; }

/* Employee Cell */
.employee-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.employee-avatar {
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

.employee-name {
  font-weight: 500;
  color: var(--ink);
}

/* Type Badge */
.type-badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Date */
.date-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Days Badge */
.days-badge {
  display: inline-block;
  padding: 0.1875rem 0.5rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--mist);
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

/* Action Buttons */
.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.25rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.action-btn:hover {
  background: var(--mist);
}

.action-view:hover {
  color: var(--teal);
  border-color: var(--teal-soft);
  background: var(--teal-soft);
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
  .licencias-container {
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
  .licencias-container {
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

  .col-actions {
    min-width: 60px;
  }

  .col-type {
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

  .licencias-table td,
  .licencias-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }

  .col-employee {
    min-width: 120px;
  }

  .col-actions {
    min-width: 50px;
  }

  .action-btn {
    width: 28px;
    height: 28px;
  }
}
</style>