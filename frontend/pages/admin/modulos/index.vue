<template>
  <div class="modulos-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-squares-plus" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <h1 class="page-title">Catálogo de Módulos</h1>
          <p class="page-subtitle">Módulos disponibles en el ERP</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="refreshData">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" :class="{ 'animate-spin': refreshing }" />
          Refrescar
        </button>
      </div>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Modules -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--purple)">
        <div class="stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-squares-plus" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ modulos.length }}</span>
          <span class="stat-label">Total Módulos</span>
        </div>
      </div>

      <!-- Active Modules -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ activeModules }}</span>
          <span class="stat-label">Activos</span>
        </div>
      </div>

      <!-- Inactive Modules -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ inactiveModules }}</span>
          <span class="stat-label">Inactivos</span>
        </div>
      </div>

      <!-- Module Distribution -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--teal)">
        <div class="stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-chart-pie" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ distributionPercentage }}%</span>
          <span class="stat-label">App / SIGARH</span>
        </div>
      </div>
    </div>

    <!-- Main Table Card -->
    <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
      <!-- Table Header with Search & Filters -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <div class="search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar módulo por nombre o código..."
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
        <div class="toolbar-right">
          <span class="result-count">{{ filteredModulos.length }} resultados</span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando catálogo de módulos...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button class="btn-secondary" @click="refreshData">Reintentar</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredModulos.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-squares-plus" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay módulos registrados</h3>
        <p style="color: var(--ink-soft)">El catálogo de módulos está vacío</p>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="modulos-table">
          <thead>
            <tr>
              <th class="col-code">
                <span class="th-content">Código</span>
              </th>
              <th class="col-name">
                <span class="th-content">Nombre</span>
              </th>
              <th class="col-panel">
                <span class="th-content">Panel</span>
              </th>
              <th class="col-category">
                <span class="th-content">Categoría</span>
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
            <tr
              v-for="modulo in filteredModulos"
              :key="modulo.id"
              class="table-row"
            >
              <td class="col-code">
                <span class="code-badge font-mono-data">{{ modulo.code }}</span>
              </td>
              <td class="col-name">
                <div class="name-cell">
                  <div class="module-icon" :style="{ background: getCategoryColor(modulo.category) + '22' }">
                    <UIcon 
                      :name="getCategoryIcon(modulo.category)" 
                      class="w-4 h-4" 
                      :style="{ color: getCategoryColor(modulo.category) }" 
                    />
                  </div>
                  <span class="name-text">{{ modulo.name }}</span>
                </div>
              </td>
              <td class="col-panel">
                <span class="panel-badge" :class="modulo.category === 'app' ? 'panel-app' : 'panel-sigarh'">
                  <UIcon 
                    :name="modulo.category === 'app' ? 'i-heroicons-squares-2x2' : 'i-heroicons-folder-open'" 
                    class="w-3.5 h-3.5" 
                  />
                  {{ modulo.category === 'app' ? 'Hospitalario' : 'SIGARH' }}
                </span>
              </td>
              <td class="col-category">
                <span class="category-badge" :class="modulo.category === 'app' ? 'cat-app' : 'cat-sigarh'">
                  {{ modulo.category === 'app' ? 'App' : 'SIGARH' }}
                </span>
              </td>
              <td class="col-status">
                <span class="status-badge" :class="modulo.is_active ? 'status-active' : 'status-inactive'">
                  <span class="status-dot" :class="modulo.is_active ? 'dot-active' : 'dot-inactive'" />
                  {{ modulo.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <button
                    class="action-btn action-toggle"
                    :title="modulo.is_active ? 'Desactivar' : 'Activar'"
                    @click="handleToggle(modulo)"
                    :disabled="togglingId === modulo.id"
                  >
                    <UIcon
                      v-if="togglingId === modulo.id"
                      name="i-heroicons-arrow-path" 
                      class="w-4 h-4 animate-spin"
                    />
                    <UIcon
                      v-else
                      :name="modulo.is_active ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                      class="w-4 h-4"
                    />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table Footer -->
      <div v-if="filteredModulos.length > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ filteredModulos.length }}</strong> de <strong>{{ modulos.length }}</strong> módulos
        </span>
        <div class="footer-actions">
          <button
            v-if="filteredModulos.length < modulos.length"
            class="btn-secondary btn-sm"
            @click="searchQuery = ''; activeFilter = 'all'"
          >
            Limpiar filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Module Details Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content" style="background: var(--paper); border-radius: var(--radius-lg)">
        <div class="modal-header">
          <div class="modal-icon" :style="{ background: getCategoryColor(selectedModule?.category || '') + '22' }">
            <UIcon 
              :name="getCategoryIcon(selectedModule?.category || '')" 
              class="w-6 h-6" 
              :style="{ color: getCategoryColor(selectedModule?.category || '') }" 
            />
          </div>
          <div>
            <h3 class="modal-title">{{ selectedModule?.name }}</h3>
            <p class="modal-subtitle font-mono-data">{{ selectedModule?.code }}</p>
          </div>
          <button class="modal-close" @click="showModal = false">
            <UIcon name="i-heroicons-x-mark" class="w-5 h-5" style="color: var(--ink-soft)" />
          </button>
        </div>
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">Panel</span>
              <span class="panel-badge" :class="selectedModule?.category === 'app' ? 'panel-app' : 'panel-sigarh'">
                <UIcon 
                  :name="selectedModule?.category === 'app' ? 'i-heroicons-squares-2x2' : 'i-heroicons-folder-open'" 
                  class="w-3.5 h-3.5" 
                />
                {{ selectedModule?.category === 'app' ? 'Hospitalario' : 'SIGARH' }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Estado</span>
              <span class="status-badge" :class="selectedModule?.is_active ? 'status-active' : 'status-inactive'">
                <span class="status-dot" :class="selectedModule?.is_active ? 'dot-active' : 'dot-inactive'" />
                {{ selectedModule?.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
            <div class="detail-item full-width">
              <span class="detail-label">ID</span>
              <span class="detail-value font-mono-data" style="font-size: 0.75rem; color: var(--ink-soft)">{{ selectedModule?.id }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showModal = false">Cerrar</button>
          <button 
            class="btn-primary" 
            @click="handleToggle(selectedModule!); showModal = false"
            :disabled="togglingId === selectedModule?.id"
          >
            <UIcon v-if="togglingId === selectedModule?.id" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            <UIcon v-else :name="selectedModule?.is_active ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4 h-4" />
            {{ selectedModule?.is_active ? 'Desactivar' : 'Activar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Modulo {
  id: string
  code: string
  name: string
  category: 'app' | 'sigarh'
  is_active: boolean
}

const { api } = useApi()

const modulos = ref<Modulo[]>([])
const loading = ref(true)
const refreshing = ref(false)
const error = ref('')
const searchQuery = ref('')
const activeFilter = ref('all')
const togglingId = ref<string | null>(null)
const showModal = ref(false)
const selectedModule = ref<Modulo | null>(null)

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: modulos.value.length },
  { label: 'Activos', value: 'active', count: activeModules.value },
  { label: 'Inactivos', value: 'inactive', count: inactiveModules.value },
  { label: 'App', value: 'app', count: appModules.value },
  { label: 'SIGARH', value: 'sigarh', count: sigarhModules.value },
])

const activeModules = computed(() => modulos.value.filter(m => m.is_active).length)
const inactiveModules = computed(() => modulos.value.filter(m => !m.is_active).length)
const appModules = computed(() => modulos.value.filter(m => m.category === 'app').length)
const sigarhModules = computed(() => modulos.value.filter(m => m.category === 'sigarh').length)

const distributionPercentage = computed(() => {
  if (!modulos.value.length) return 0
  return Math.round((appModules.value / modulos.value.length) * 100)
})

const filteredModulos = computed(() => {
  let result = modulos.value

  // Filter by status/category
  if (activeFilter.value === 'active') {
    result = result.filter(m => m.is_active)
  } else if (activeFilter.value === 'inactive') {
    result = result.filter(m => !m.is_active)
  } else if (activeFilter.value === 'app') {
    result = result.filter(m => m.category === 'app')
  } else if (activeFilter.value === 'sigarh') {
    result = result.filter(m => m.category === 'sigarh')
  }

  // Filter by search
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(m =>
      m.name.toLowerCase().includes(query) ||
      m.code.toLowerCase().includes(query)
    )
  }

  return result
})

const getCategoryColor = (category: string) => {
  return category === 'app' ? 'var(--teal)' : 'var(--purple)'
}

const getCategoryIcon = (category: string) => {
  return category === 'app' ? 'i-heroicons-squares-2x2' : 'i-heroicons-folder-open'
}

const getContrastColor = (hex: string) => {
  // For CSS variable colors, return white
  if (hex.startsWith('var(')) return '#FFFFFF'
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.5 ? '#000000' : '#FFFFFF'
}

const openModal = (modulo: Modulo) => {
  selectedModule.value = modulo
  showModal.value = true
}

const refreshData = async () => {
  refreshing.value = true
  await loadModules()
  refreshing.value = false
}

const loadModules = async () => {
  loading.value = true
  error.value = ''
  try {
    modulos.value = await api<Modulo[]>('/admin/modulos/catalogo')
  } catch (e: any) {
    error.value = apiErr(e, 'Error de conexión')
  } finally {
    loading.value = false
  }
}

const handleToggle = async (modulo: Modulo) => {
  togglingId.value = modulo.id
  try {
    await api(`/admin/modulos/${modulo.id}/toggle`, {
      method: 'PATCH',
      body: { is_active: !modulo.is_active }
    })
    modulo.is_active = !modulo.is_active
  } catch (e: any) {
    error.value = apiErr(e, 'No se pudo actualizar el estado')
  } finally {
    togglingId.value = null
  }
}

onMounted(loadModules)
</script>

<style scoped>
.modulos-container {
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

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* Widgets Grid */

/* Table Card */

/* Table States */

/* Table Styles */

.modulos-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.modulos-table thead {
  background: var(--mist);
}

.modulos-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--ink-soft);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--line);
}

.modulos-table td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--line);
  vertical-align: middle;
}

.table-row {
  transition: background 0.15s ease;
  cursor: default;
}

.col-code {
  width: 12%;
}

.col-name {
  width: 30%;
}

.col-panel {
  width: 18%;
}

.col-category {
  width: 12%;
}

.col-status {
  width: 14%;
}

.col-actions {
  width: 14%;
  text-align: right;
}

/* Code Badge */
.code-badge {
  display: inline-block;
  padding: 0.1875rem 0.5rem;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 600;
  background: var(--mist);
  color: var(--ink-soft);
}

/* Name Cell */
.name-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.module-icon {
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

/* Panel Badge */
.panel-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.panel-app {
  background: var(--teal-soft);
  color: var(--teal);
}

.panel-sigarh {
  background: var(--purple-soft);
  color: var(--purple);
}

/* Category Badge */
.category-badge {
  display: inline-block;
  padding: 0.1875rem 0.5rem;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.cat-app {
  background: var(--teal-soft);
  color: var(--teal);
}

.cat-sigarh {
  background: var(--purple-soft);
  color: var(--purple);
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

.action-toggle:hover {
  color: var(--amber);
  border-color: var(--amber-soft);
  background: var(--amber-soft);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Table Footer */

.footer-actions {
  display: flex;
  gap: 0.5rem;
}

/* Modal */

.modal-content {
  max-width: 480px;
  width: 100%;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  position: relative;
}

.modal-subtitle {
  font-size: 0.8125rem;
  color: var(--ink-soft);
  margin: 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .modulos-container {
    padding: 1rem 1.5rem;
  }
  
  .table-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-left {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-wrapper {
    max-width: none;
  }
}

@media (max-width: 768px) {
  .modulos-container {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .header-actions .btn-secondary {
    width: 100%;
    justify-content: center;
  }
  
  .widgets-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .filter-group {
    flex-wrap: wrap;
  }
  
  .col-panel {
    min-width: 100px;
  }
  
  .col-actions {
    min-width: 60px;
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
  
  .modulos-table td,
  .modulos-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }
  
  .col-code {
    min-width: 80px;
  }
  
  .col-name {
    min-width: 120px;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>