<template>
  <div class="hospitales-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Hospitales</h1>
          <p class="page-subtitle">Establecimientos registrados en la plataforma</p>
        </div>
      </div>
      <NuxtLink to="/admin/hospitales/create" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Hospital
      </NuxtLink>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Hospitals -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--navy)">
        <div class="stat-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ hospitales.length }}</span>
          <span class="stat-label">Total Hospitales</span>
        </div>
      </div>

      <!-- Active Hospitals -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ activos }}</span>
          <span class="stat-label">Activos</span>
        </div>
      </div>

      <!-- Inactive Hospitals -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ inactivos }}</span>
          <span class="stat-label">Inactivos</span>
        </div>
      </div>

      <!-- Avg Modules -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--purple)">
        <div class="stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-squares-plus" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ promedioModulos }}</span>
          <span class="stat-label">Módulos / Hospital</span>
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
              placeholder="Buscar hospital por nombre..."
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
          <span class="result-count">{{ filteredHospitales.length }} resultados</span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando hospitales...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button class="btn-secondary" @click="loadHospitales">Reintentar</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredHospitales.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-building-office-2" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay hospitales registrados</h3>
        <p style="color: var(--ink-soft)">Comienza registrando tu primer establecimiento</p>
        <NuxtLink to="/admin/hospitales/create" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Crear Hospital
        </NuxtLink>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="hospitales-table">
          <thead>
            <tr>
              <th class="col-name">
                <span class="th-content">Hospital</span>
              </th>
              <th class="col-domain">
                <span class="th-content">Dominio</span>
              </th>
              <th class="col-level">
                <span class="th-content">Nivel</span>
              </th>
              <th class="col-modules">
                <span class="th-content">Módulos</span>
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
              v-for="hospital in filteredHospitales"
              :key="hospital.id"
              class="table-row"
            >
              <td class="col-name">
                <div class="name-cell">
                  <div class="hospital-icon" style="background: var(--mist)">
                    <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" style="color: var(--navy)" />
                  </div>
                  <span class="name-text">{{ hospital.name }}</span>
                </div>
              </td>
              <td class="col-domain">
                <span class="domain-text font-mono-data">{{ hospital.domain }}</span>
              </td>
              <td class="col-level">
                <span
                  v-if="hospital.hospital_level"
                  class="level-badge"
                  :style="{
                    background: getLevelColor(hospital.hospital_level),
                    color: getContrastColor(getLevelColor(hospital.hospital_level))
                  }"
                >
                  {{ hospital.hospital_level }}
                </span>
                <span v-else class="level-empty">—</span>
              </td>
              <td class="col-modules">
                <div class="modules-cell">
                  <span class="module-count">{{ hospital.active_modules?.length || 0 }}</span>
                  <div class="module-bar">
                    <div
                      class="module-bar-fill"
                      :style="{
                        width: getModulePercentage(hospital) + '%',
                        background: 'var(--teal)'
                      }"
                    />
                  </div>
                </div>
              </td>
              <td class="col-status">
                <span class="status-badge" :class="hospital.is_active ? 'status-active' : 'status-inactive'">
                  <span class="status-dot" :class="hospital.is_active ? 'dot-active' : 'dot-inactive'" />
                  {{ hospital.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <button
                    class="action-btn action-view"
                    title="Ver landing"
                    @click="irA(hospital, '')"
                  >
                    <UIcon name="i-heroicons-globe-alt" class="w-4 h-4" />
                  </button>
                    <button
                      class="action-btn action-app"
                      title="Panel Hospitalario"
                      @click="irA(hospital, '/app')"
                    >
                    <UIcon name="i-heroicons-squares-2x2" class="w-4 h-4" />
                  </button>
                  <button
                    class="action-btn action-sigarh"
                    title="Panel SIGARH"
                    @click="irA(hospital, '/sigarh')"
                  >
                    <UIcon name="i-heroicons-folder-open" class="w-4 h-4" />
                  </button>
                  <NuxtLink
                    :to="`/admin/hospitales/${hospital.id}`"
                    class="action-btn action-edit"
                    title="Editar hospital"
                  >
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
                  </NuxtLink>
                  <button
                    class="action-btn action-toggle"
                    :title="hospital.is_active ? 'Desactivar' : 'Activar'"
                    @click="handleToggle(hospital)"
                    :disabled="togglingId === hospital.id"
                  >
                    <UIcon
                      v-if="togglingId === hospital.id"
                      name="i-heroicons-arrow-path" 
                      class="w-4 h-4 animate-spin"
                    />
                    <UIcon
                      v-else
                      :name="hospital.is_active ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
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
      <div v-if="filteredHospitales.length > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ filteredHospitales.length }}</strong> de <strong>{{ hospitales.length }}</strong> hospitales
        </span>
        <div class="footer-actions">
          <button
            v-if="filteredHospitales.length < hospitales.length"
            class="btn-secondary btn-sm"
            @click="searchQuery = ''; activeFilter = 'all'"
          >
            Limpiar filtros
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Hospital {
  id: string
  name: string
  domain: string
  hospital_level?: string
  active_modules: string[]
  is_active: boolean
  created_at: string
}

const { api } = useApi()
const router = useRouter()

const hospitales = ref<Hospital[]>([])
const loading = ref(true)
const error = ref('')
const searchQuery = ref('')
const activeFilter = ref('all')
const togglingId = ref<string | null>(null)

const levelColors: Record<string, string> = {
  'I-1': '#6b7280',
  'I-2': '#6b7280',
  'I-3': '#6b7280',
  'II-1': '#3b82f6',
  'II-2': '#3b82f6',
  'III-1': '#8b5cf6',
  'III-2': '#8b5cf6',
  'IV-1': '#ec4899',
  'IV-2': '#ec4899',
}

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: hospitales.value.length },
  { label: 'Activos', value: 'active', count: activos.value },
  { label: 'Inactivos', value: 'inactive', count: inactivos.value },
])

const activos = computed(() => hospitales.value.filter(h => h.is_active).length)
const inactivos = computed(() => hospitales.value.filter(h => !h.is_active).length)

const promedioModulos = computed(() => {
  if (!hospitales.value.length) return 0
  const total = hospitales.value.reduce((sum, h) => sum + (h.active_modules?.length ?? 0), 0)
  return Math.round(total / hospitales.value.length)
})

const filteredHospitales = computed(() => {
  let result = hospitales.value

  // Filter by status
  if (activeFilter.value === 'active') {
    result = result.filter(h => h.is_active)
  } else if (activeFilter.value === 'inactive') {
    result = result.filter(h => !h.is_active)
  }

  // Filter by search
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(h =>
      h.name.toLowerCase().includes(query) ||
      h.domain.toLowerCase().includes(query)
    )
  }

  return result
})

const getLevelColor = (level: string) => {
  return levelColors[level] || '#6b7280'
}

const getContrastColor = (hex: string) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.5 ? '#000000' : '#FFFFFF'
}

const getModulePercentage = (hospital: Hospital) => {
  const total = hospital.active_modules?.length || 0
  // Use a reference max for percentage (e.g., 20 modules max)
  const maxModules = 20
  return Math.min((total / maxModules) * 100, 100)
}

const irA = (hospital: Hospital, path: string) => {
  const baseUrl = window.location.origin
  if (path === '') {
    window.open(`${baseUrl}?tenant=${hospital.id}`, '_blank')
  } else if (path === '/sigarh') {
    window.open(`${baseUrl}/sigarh/login?tenant=${hospital.id}`, '_blank')
  } else if (path === '/app') {
    window.open(`${baseUrl}/app/login?tenant=${hospital.id}`, '_blank')
  } else {
    window.open(`${baseUrl}${path}?tenant=${hospital.id}`, '_blank')
  }
}

const loadHospitales = async () => {
  loading.value = true
  error.value = ''
  try {
    hospitales.value = await api<Hospital[]>('/admin/hospitales')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }
}

const handleToggle = async (hospital: Hospital) => {
  togglingId.value = hospital.id
  try {
    await api(`/admin/hospitales/${hospital.id}/toggle`, {
      method: 'PATCH',
      body: { is_active: !hospital.is_active }
    })
    hospital.is_active = !hospital.is_active
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo actualizar el estado'
  } finally {
    togglingId.value = null
  }
}

onMounted(loadHospitales)
</script>

<style scoped>
.hospitales-container {
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

/* Table Styles */
.table-responsive {
  overflow-x: auto;
}

.hospitales-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.hospitales-table thead {
  background: var(--mist);
}

.hospitales-table th {
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

.hospitales-table td {
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

.col-name {
  width: 22%;
}

.col-domain {
  width: 18%;
}

.col-level {
  width: 12%;
}

.col-modules {
  width: 18%;
}

.col-status {
  width: 12%;
}

.col-actions {
  width: 18%;
  text-align: right;
}

/* Name Cell */
.name-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.hospital-icon {
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

/* Domain */
.domain-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Level Badge */
.level-badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 700;
  font-family: monospace;
}

.level-empty {
  color: var(--ink-soft);
  font-size: 0.8125rem;
}

/* Modules Cell */
.modules-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.module-count {
  font-weight: 600;
  color: var(--ink);
  min-width: 24px;
}

.module-bar {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: var(--mist);
  overflow: hidden;
}

.module-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.6s ease;
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

.action-view:hover {
  color: var(--navy);
  border-color: var(--navy-soft);
  background: var(--navy-soft);
}

.action-app:hover {
  color: var(--teal);
  border-color: var(--teal-soft);
  background: var(--teal-soft);
}

.action-sigarh:hover {
  color: var(--purple);
  border-color: var(--purple-soft);
  background: var(--purple-soft);
}

.action-edit:hover {
  color: var(--amber);
  border-color: var(--amber-soft);
  background: var(--amber-soft);
}

.action-toggle:hover {
  color: var(--alert);
  border-color: var(--alert-soft);
  background: var(--alert-soft);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  .hospitales-container {
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
  .hospitales-container {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .widgets-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .filter-group {
    flex-wrap: wrap;
  }
  
  .col-modules {
    min-width: 120px;
  }
  
  .col-actions {
    min-width: 120px;
  }
  
  .action-buttons {
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.125rem;
  }
  
  .action-btn {
    width: 28px;
    height: 28px;
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
  
  .hospitales-table td,
  .hospitales-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }
  
  .col-domain {
    min-width: 120px;
  }
}
</style>