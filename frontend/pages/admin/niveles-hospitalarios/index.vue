<template>
  <div class="niveles-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-building-library" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Niveles Hospitalarios</h1>
          <p class="page-subtitle">Niveles MINSA con sus módulos por defecto</p>
        </div>
      </div>
      <NuxtLink to="/admin/niveles-hospitalarios/create" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Nivel
      </NuxtLink>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Levels Widget -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--teal)">
        <div class="stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ niveles.length }}</span>
          <span class="stat-label">Total Niveles</span>
        </div>
      </div>

      <!-- Active Levels Widget -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ activeCount }}</span>
          <span class="stat-label">Activos</span>
        </div>
      </div>

      <!-- Inactive Levels Widget -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ inactiveCount }}</span>
          <span class="stat-label">Inactivos</span>
        </div>
      </div>

      <!-- Total Modules Widget -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--purple)">
        <div class="stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-squares-plus" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ totalModules }}</span>
          <span class="stat-label">Módulos Configurados</span>
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
              placeholder="Buscar nivel..."
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
          <span class="result-count">{{ filteredNiveles.length }} resultados</span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando niveles hospitalarios...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button class="btn-secondary" @click="fetchData">Reintentar</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredNiveles.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-building-library" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay niveles registrados</h3>
        <p style="color: var(--ink-soft)">Comienza creando tu primer nivel hospitalario</p>
        <NuxtLink to="/admin/niveles-hospitalarios/create" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Crear Nivel
        </NuxtLink>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="niveles-table">
          <thead>
            <tr>
              <th class="col-code">
                <span class="th-content">Código</span>
              </th>
              <th class="col-name">
                <span class="th-content">Nombre</span>
              </th>
              <th class="col-modules">
                <span class="th-content">Módulos</span>
              </th>
              <th class="col-order">
                <span class="th-content">Orden</span>
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
              v-for="nivel in filteredNiveles"
              :key="nivel.id"
              class="table-row"
              @click="navigateToEdit(nivel.id)"
            >
              <td class="col-code">
                <span
                  class="code-badge"
                  :style="{
                    background: nivel.color || '#6B7280',
                    color: getContrastColor(nivel.color || '#6B7280')
                  }"
                >
                  {{ nivel.code }}
                </span>
              </td>
              <td class="col-name">
                <div class="name-cell">
                  <div
                    class="color-dot"
                    :style="{ background: nivel.color || '#6B7280' }"
                  />
                  <span class="name-text">{{ nivel.name }}</span>
                </div>
              </td>
              <td class="col-modules">
                <div class="modules-cell">
                  <div class="module-stats">
                    <span class="module-count">{{ getTotalModules(nivel) }}</span>
                    <span class="module-detail">
                      App: {{ nivel.default_modules?.app?.length || 0 }} · SIGARH: {{ nivel.default_modules?.sigarh?.length || 0 }}
                    </span>
                  </div>
                  <div class="module-bar">
                    <div
                      class="module-bar-fill app"
                      :style="{
                        width: getModulePercentage(nivel, 'app') + '%',
                        background: 'var(--teal)'
                      }"
                    />
                    <div
                      class="module-bar-fill sigarh"
                      :style="{
                        width: getModulePercentage(nivel, 'sigarh') + '%',
                        background: 'var(--navy)'
                      }"
                    />
                  </div>
                </div>
              </td>
              <td class="col-order">
                <span class="order-badge">{{ nivel.sort_order }}</span>
              </td>
              <td class="col-status">
                <span class="status-badge" :class="nivel.is_active ? 'status-active' : 'status-inactive'">
                  <span class="status-dot" :class="nivel.is_active ? 'dot-active' : 'dot-inactive'" />
                  {{ nivel.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="col-actions">
                <div class="action-buttons" @click.stop>
                  <NuxtLink
                    :to="`/admin/niveles-hospitalarios/${nivel.id}`"
                    class="action-btn action-edit"
                    title="Editar nivel"
                  >
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
                  </NuxtLink>
                  <button
                    class="action-btn action-toggle"
                    :title="nivel.is_active ? 'Desactivar' : 'Activar'"
                    @click="toggleStatus(nivel)"
                  >
                    <UIcon
                      :name="nivel.is_active ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                      class="w-4 h-4"
                    />
                  </button>
                  <button
                    class="action-btn action-delete"
                    title="Eliminar nivel"
                    @click="confirmDelete(nivel)"
                  >
                    <UIcon name="i-heroicons-trash" class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table Footer -->
      <div v-if="filteredNiveles.length > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ filteredNiveles.length }}</strong> de <strong>{{ niveles.length }}</strong> niveles
        </span>
        <div class="footer-actions">
          <button
            v-if="filteredNiveles.length < niveles.length"
            class="btn-secondary btn-sm"
            @click="searchQuery = ''"
          >
            Limpiar filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-content" style="background: var(--paper); border-radius: var(--radius-lg)">
        <div class="modal-header">
          <div class="modal-icon" style="background: var(--alert-soft)">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6" style="color: var(--alert)" />
          </div>
          <h3 class="modal-title">Confirmar Eliminación</h3>
        </div>
        <p class="modal-body">
          ¿Estás seguro de que deseas eliminar el nivel <strong>{{ nivelToDelete?.name }}</strong>?
          <br>
          <span style="color: var(--ink-soft); font-size: 0.875rem">
            Esta acción no se puede deshacer y eliminará todas las configuraciones asociadas.
          </span>
        </p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-danger" @click="deleteNivel">
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Nivel {
  id: number
  code: string
  name: string
  color: string
  sort_order: number
  is_active: boolean
  default_modules?: {
    app: string[]
    sigarh: string[]
  }
}

const { api } = useApi()
const router = useRouter()

const niveles = ref<Nivel[]>([])
const loading = ref(true)
const error = ref('')
const searchQuery = ref('')
const activeFilter = ref('all')
const showDeleteModal = ref(false)
const nivelToDelete = ref<Nivel | null>(null)

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: niveles.value.length },
  { label: 'Activos', value: 'active', count: activeCount.value },
  { label: 'Inactivos', value: 'inactive', count: inactiveCount.value },
])

const activeCount = computed(() => niveles.value.filter(n => n.is_active).length)
const inactiveCount = computed(() => niveles.value.filter(n => !n.is_active).length)
const totalModules = computed(() => {
  return niveles.value.reduce((acc, n) => {
    const app = n.default_modules?.app?.length || 0
    const sigarh = n.default_modules?.sigarh?.length || 0
    return acc + app + sigarh
  }, 0)
})

const filteredNiveles = computed(() => {
  let result = niveles.value

  // Filter by status
  if (activeFilter.value === 'active') {
    result = result.filter(n => n.is_active)
  } else if (activeFilter.value === 'inactive') {
    result = result.filter(n => !n.is_active)
  }

  // Filter by search
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(n =>
      n.code.toLowerCase().includes(query) ||
      n.name.toLowerCase().includes(query)
    )
  }

  return result
})

const getTotalModules = (nivel: Nivel) => {
  const app = nivel.default_modules?.app?.length || 0
  const sigarh = nivel.default_modules?.sigarh?.length || 0
  return app + sigarh
}

const getModulePercentage = (nivel: Nivel, type: 'app' | 'sigarh') => {
  const total = getTotalModules(nivel)
  if (total === 0) return 0
  const count = nivel.default_modules?.[type]?.length || 0
  return Math.round((count / total) * 100)
}

const getContrastColor = (hex: string) => {
  // Simple contrast checker - returns white or black
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.5 ? '#000000' : '#FFFFFF'
}

const navigateToEdit = (id: number) => {
  router.push(`/admin/niveles-hospitalarios/${id}`)
}

const toggleStatus = async (nivel: Nivel) => {
  try {
    await api(`/admin/niveles-hospitalarios/${nivel.id}`, {
      method: 'PATCH',
      body: { is_active: !nivel.is_active }
    })
    nivel.is_active = !nivel.is_active
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al actualizar el estado'
  }
}

const confirmDelete = (nivel: Nivel) => {
  nivelToDelete.value = nivel
  showDeleteModal.value = true
}

const deleteNivel = async () => {
  if (!nivelToDelete.value) return
  try {
    await api(`/admin/niveles-hospitalarios/${nivelToDelete.value.id}`, {
      method: 'DELETE'
    })
    niveles.value = niveles.value.filter(n => n.id !== nivelToDelete.value?.id)
    showDeleteModal.value = false
    nivelToDelete.value = null
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al eliminar el nivel'
  }
}

const fetchData = async () => {
  loading.value = true
  error.value = ''
  try {
    niveles.value = await api<Nivel[]>('/admin/niveles-hospitalarios')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.niveles-container {
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

.btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--alert);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background: var(--alert-dark);
}

/* Widgets Grid */
.widgets-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
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

/* Table Card */
.table-card {
  overflow: hidden;
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--line);
  flex-wrap: wrap;
  gap: 1rem;
}

.toolbar-left {
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

.toolbar-right {
  display: flex;
  align-items: center;
}

.result-count {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Table Styles */
.table-responsive {
  overflow-x: auto;
}

.niveles-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.niveles-table thead {
  background: var(--mist);
}

.niveles-table th {
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

.niveles-table td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--line);
  vertical-align: middle;
}

.table-row {
  cursor: pointer;
  transition: background 0.15s ease;
}

.table-row:hover {
  background: var(--mist);
}

.col-code {
  width: 12%;
}

.col-name {
  width: 20%;
}

.col-modules {
  width: 30%;
}

.col-order {
  width: 8%;
}

.col-status {
  width: 12%;
}

.col-actions {
  width: 16%;
  text-align: right;
}

/* Code Badge */
.code-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  font-family: monospace;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1px solid var(--line);
  flex-shrink: 0;
}

.name-text {
  font-weight: 500;
  color: var(--ink);
}

/* Modules Cell */
.modules-cell {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.module-stats {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.module-count {
  font-weight: 600;
  color: var(--ink);
}

.module-detail {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.module-bar {
  display: flex;
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
  background: var(--mist);
}

.module-bar-fill {
  height: 100%;
  transition: width 0.6s ease;
}

/* Order Badge */
.order-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--mist);
  color: var(--ink-soft);
  font-family: monospace;
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
}

.action-btn:hover {
  background: var(--mist);
}

.action-edit:hover {
  color: var(--teal);
  border-color: var(--teal-soft);
  background: var(--teal-soft);
}

.action-toggle:hover {
  color: var(--amber);
  border-color: var(--amber-soft);
  background: var(--amber-soft);
}

.action-delete:hover {
  color: var(--alert);
  border-color: var(--alert-soft);
  background: var(--alert-soft);
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

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  max-width: 420px;
  width: 100%;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.modal-body {
  color: var(--ink);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Responsive */
@media (max-width: 1200px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .niveles-container {
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
  .niveles-container {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .widgets-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-group {
    flex-wrap: wrap;
  }
  
  .col-modules {
    min-width: 150px;
  }
  
  .col-actions {
    min-width: 80px;
  }
  
  .action-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .filter-chip {
    font-size: 0.6875rem;
    padding: 0.25rem 0.5rem;
  }
  
  .module-detail {
    display: none;
  }
  
  .table-responsive {
    margin: 0 -0.5rem;
  }
  
  .niveles-table td,
  .niveles-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }
}
</style>