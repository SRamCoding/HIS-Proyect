<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Seguros' })

const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string

const lista = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const activeFilter = ref('all')

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: lista.value.length },
  { label: 'Activos', value: 'active', count: activeItems.value },
  { label: 'Inactivos', value: 'inactive', count: inactiveItems.value },
])

const activeItems = computed(() => lista.value.filter(s => s.is_active).length)
const inactiveItems = computed(() => lista.value.filter(s => !s.is_active).length)

const filteredLista = computed(() => {
  let result = lista.value

  if (activeFilter.value === 'active') {
    result = result.filter(s => s.is_active)
  } else if (activeFilter.value === 'inactive') {
    result = result.filter(s => !s.is_active)
  }

  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    result = result.filter(s =>
      s.nombre?.toLowerCase().includes(q) ||
      s.ruc?.includes(q) ||
      s.tipo?.toLowerCase().includes(q)
    )
  }

  return result
})

const getTipoColor = (tipo: string) => {
  const map: Record<string, string> = {
    privado: 'var(--teal)',
    publico: 'var(--navy)',
    essalud: 'var(--green)',
    sis: 'var(--purple)',
    eps: 'var(--amber)',
  }
  return map[tipo?.toLowerCase()] || 'var(--ink-soft)'
}

const getTipoBgColor = (tipo: string) => {
  const map: Record<string, string> = {
    privado: 'var(--teal-soft)',
    publico: 'var(--navy-soft)',
    essalud: 'var(--green-soft)',
    sis: 'var(--purple-soft)',
    eps: 'var(--amber-soft)',
  }
  return map[tipo?.toLowerCase()] || 'var(--mist)'
}

const formatTipo = (tipo: string) => {
  if (!tipo) return '—'
  return tipo.charAt(0).toUpperCase() + tipo.slice(1).toLowerCase()
}

const formatPorcentaje = (valor: number | null) => {
  if (valor === null || valor === undefined) return '—'
  return `${valor}%`
}

const clearFilters = () => {
  search.value = ''
  activeFilter.value = 'all'
}

onMounted(async () => {
  try {
    lista.value = await $api('/sigarh/config-financiera/seguros', { tenant })
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar datos'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="seguros-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Seguros</h1>
          <p class="page-subtitle">Seguros y convenios del hospital</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/config-financiera/seguros/create?tenant=${tenant}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Seguro
      </NuxtLink>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--teal)">
        <div class="stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ lista.length }}</span>
          <span class="stat-label">Total Seguros</span>
        </div>
      </div>

      <!-- Activos -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ activeItems }}</span>
          <span class="stat-label">Activos</span>
        </div>
      </div>

      <!-- Inactivos -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ inactiveItems }}</span>
          <span class="stat-label">Inactivos</span>
        </div>
      </div>

      <!-- Tipos -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--purple)">
        <div class="stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-list-bullet" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ new Set(lista.map(s => s.tipo)).size }}</span>
          <span class="stat-label">Tipos Diferentes</span>
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
            placeholder="Buscar por nombre, RUC o tipo..."
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
            @click="activeFilter = filter.value"
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
        <p style="color: var(--ink-soft)">Cargando seguros...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button class="btn-secondary" @click="onMounted">Reintentar</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredLista.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-shield-check" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay seguros registrados</h3>
        <p style="color: var(--ink-soft)">Comienza creando un seguro o convenio</p>
        <NuxtLink :to="`/sigarh/config-financiera/seguros/create?tenant=${tenant}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Nuevo Seguro
        </NuxtLink>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="seguros-table">
          <thead>
            <tr>
              <th class="col-name">
                <span class="th-content">Nombre</span>
              </th>
              <th class="col-ruc">
                <span class="th-content">RUC</span>
              </th>
              <th class="col-type">
                <span class="th-content">Tipo</span>
              </th>
              <th class="col-coverage">
                <span class="th-content">Cobertura</span>
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
            <tr v-for="s in filteredLista" :key="s.id" class="table-row">
              <td class="col-name">
                <div class="name-cell">
                  <div class="seguro-icon" :style="{ background: s.is_active ? getTipoBgColor(s.tipo) : 'var(--mist)' }">
                    <UIcon name="i-heroicons-shield-check" class="w-4 h-4" :style="{ color: s.is_active ? getTipoColor(s.tipo) : 'var(--ink-soft)' }" />
                  </div>
                  <span class="name-text">{{ s.nombre }}</span>
                </div>
              </td>
              <td class="col-ruc">
                <span class="ruc-text font-mono-data">{{ s.ruc || '—' }}</span>
              </td>
              <td class="col-type">
                <span class="type-badge" :style="{ background: getTipoBgColor(s.tipo), color: getTipoColor(s.tipo) }">
                  {{ formatTipo(s.tipo) }}
                </span>
              </td>
              <td class="col-coverage">
                <span class="coverage-text">{{ formatPorcentaje(s.porcentaje_cobertura) }}</span>
              </td>
              <td class="col-status">
                <span class="status-badge" :class="s.is_active ? 'status-active' : 'status-inactive'">
                  <span class="status-dot" :class="s.is_active ? 'dot-active' : 'dot-inactive'" />
                  {{ s.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <NuxtLink
                    :to="`/sigarh/config-financiera/seguros/${s.id}?tenant=${tenant}`"
                    class="action-btn action-edit"
                    title="Editar seguro"
                  >
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
                  </NuxtLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table Footer -->
      <div v-if="filteredLista.length > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ filteredLista.length }}</strong> de <strong>{{ lista.length }}</strong> seguros
          <span v-if="filteredLista.length < lista.length">(filtrados)</span>
        </span>
        <div class="footer-actions">
          <button
            v-if="filteredLista.length < lista.length || search || activeFilter !== 'all'"
            class="btn-secondary btn-sm"
            @click="clearFilters"
          >
            Limpiar filtros
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.seguros-container {
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
.table-error,
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

.seguros-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.seguros-table thead {
  background: var(--mist);
}

.seguros-table th {
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

.seguros-table td {
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

.col-name { width: 25%; }
.col-ruc { width: 15%; }
.col-type { width: 15%; }
.col-coverage { width: 15%; }
.col-status { width: 15%; }
.col-actions { width: 15%; text-align: right; }

/* Name Cell */
.name-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.seguro-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.name-text {
  font-weight: 500;
  color: var(--ink);
}

/* RUC */
.ruc-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Type Badge */
.type-badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Coverage */
.coverage-text {
  font-weight: 500;
  color: var(--teal);
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

.status-active {
  background: var(--green-soft);
  color: var(--green);
}

.status-inactive {
  background: var(--mist);
  color: var(--ink-soft);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.dot-active {
  background: var(--green);
}

.dot-inactive {
  background: var(--ink-soft);
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

.action-edit:hover {
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

.footer-actions {
  display: flex;
  gap: 0.5rem;
}

/* Responsive */
@media (max-width: 1200px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .seguros-container {
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
  .seguros-container {
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

  .col-name {
    min-width: 140px;
  }

  .table-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
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

  .seguros-table td,
  .seguros-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }

  .col-name {
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