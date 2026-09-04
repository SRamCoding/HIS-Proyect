<template>
  <div class="vacaciones-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Justificaciones y Vacaciones</h1>
          <p class="page-subtitle">Gestión de solicitudes de vacaciones del personal</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/movimientos/vacaciones/create?tenant=${tenant}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nueva Solicitud
      </NuxtLink>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Requests -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--navy)">
        <div class="stat-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-document-text" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ vacaciones.length }}</span>
          <span class="stat-label">Total Solicitudes</span>
        </div>
      </div>

      <!-- Pending -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ solicitudesPendientes }}</span>
          <span class="stat-label">Pendientes</span>
        </div>
      </div>

      <!-- Approved -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ solicitudesAprobadas }}</span>
          <span class="stat-label">Aprobadas</span>
        </div>
      </div>

      <!-- Rejected -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--alert)">
        <div class="stat-icon" style="background: var(--alert-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--alert)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ solicitudesRechazadas }}</span>
          <span class="stat-label">Rechazadas</span>
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
              v-model="search"
              type="text"
              placeholder="Buscar por empleado..."
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
          <span class="result-count">{{ vacacionesFiltradas.length }} resultados</span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando solicitudes...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button class="btn-secondary" @click="cargar">Reintentar</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="vacacionesFiltradas.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-calendar-days" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay solicitudes registradas</h3>
        <p style="color: var(--ink-soft)">Comienza registrando la primera solicitud de vacaciones</p>
        <NuxtLink :to="`/sigarh/movimientos/vacaciones/create?tenant=${tenant}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Nueva Solicitud
        </NuxtLink>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="vacaciones-table">
          <thead>
            <tr>
              <th class="col-employee">
                <span class="th-content">Empleado</span>
              </th>
              <th class="col-type">
                <span class="th-content">Tipo</span>
              </th>
              <th class="col-dates">
                <span class="th-content">Período</span>
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
            <tr
              v-for="v in vacacionesFiltradas"
              :key="v.id"
              class="table-row"
            >
              <td class="col-employee">
                <div class="employee-cell">
                  <div class="employee-avatar" :style="{ background: getEmployeeColor(v.nombre_empleado) }">
                    <span>{{ getInitials(v.nombre_empleado) }}</span>
                  </div>
                  <div class="employee-info">
                    <span class="employee-name">{{ v.nombre_empleado }}</span>
                  </div>
                </div>
              </td>
              <td class="col-type">
                <span class="type-text">{{ v.tipo }}</span>
              </td>
              <td class="col-dates">
                <div class="dates-cell">
                  <span class="date-text">{{ v.fecha_inicio }}</span>
                  <span class="date-separator">→</span>
                  <span class="date-text">{{ v.fecha_fin }}</span>
                </div>
              </td>
              <td class="col-days">
                <span class="days-badge">{{ v.dias_solicitados }} día{{ v.dias_solicitados > 1 ? 's' : '' }}</span>
              </td>
              <td class="col-status">
                <span class="status-badge" :class="estadoClase(v.estado)">
                  <span class="status-dot" :class="estadoDot(v.estado)" />
                  {{ estadoLabel(v.estado) }}
                </span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <NuxtLink
                    :to="`/sigarh/movimientos/vacaciones/${v.id}?tenant=${tenant}`"
                    class="action-btn action-view"
                    title="Ver solicitud"
                  >
                    <UIcon name="i-heroicons-eye" class="w-4 h-4" />
                  </NuxtLink>
                  <button
                    v-if="v.estado === 'pendiente'"
                    class="action-btn action-edit"
                    title="Editar solicitud"
                    @click="editarSolicitud(v)"
                  >
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
                  </button>
                  <button
                    v-if="v.estado === 'pendiente'"
                    class="action-btn action-delete"
                    title="Eliminar solicitud"
                    @click="confirmarEliminar(v)"
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
      <div v-if="vacacionesFiltradas.length > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ vacacionesFiltradas.length }}</strong> de <strong>{{ vacaciones.length }}</strong> solicitudes
          <span v-if="vacacionesFiltradas.length < vacaciones.length">(filtrados)</span>
        </span>
        <div class="footer-actions">
          <button
            v-if="vacacionesFiltradas.length < vacaciones.length || search || activeFilter !== 'all'"
            class="btn-secondary btn-sm"
            @click="clearFilters"
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
          ¿Estás seguro de que deseas eliminar la solicitud de <strong>{{ solicitudToDelete?.nombre_empleado }}</strong>?
          <br>
          <span style="color: var(--ink-soft); font-size: 0.875rem">
            Esta acción no se puede deshacer.
          </span>
        </p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-danger" @click="deleteSolicitud">
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Justificaciones y Vacaciones' })

const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string

interface Vacacion {
  id: number
  nombre_empleado: string
  tipo: string
  fecha_inicio: string
  fecha_fin: string
  dias_solicitados: number
  estado: 'pendiente' | 'aprobado' | 'rechazado'
}

const vacaciones = ref<Vacacion[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const activeFilter = ref('all')
const showDeleteModal = ref(false)
const solicitudToDelete = ref<Vacacion | null>(null)

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: vacaciones.value.length },
  { label: 'Pendientes', value: 'pendiente', count: solicitudesPendientes.value },
  { label: 'Aprobadas', value: 'aprobado', count: solicitudesAprobadas.value },
  { label: 'Rechazadas', value: 'rechazado', count: solicitudesRechazadas.value },
])

const solicitudesPendientes = computed(() => vacaciones.value.filter(v => v.estado === 'pendiente').length)
const solicitudesAprobadas = computed(() => vacaciones.value.filter(v => v.estado === 'aprobado').length)
const solicitudesRechazadas = computed(() => vacaciones.value.filter(v => v.estado === 'rechazado').length)

const vacacionesFiltradas = computed(() => {
  let result = vacaciones.value

  if (activeFilter.value !== 'all') {
    result = result.filter(v => v.estado === activeFilter.value)
  }

  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    result = result.filter(v =>
      v.nombre_empleado.toLowerCase().includes(q) ||
      v.tipo.toLowerCase().includes(q)
    )
  }

  return result
})

const getInitials = (name: string) => {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
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

const estadoLabel = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'Pendiente',
    aprobado: 'Aprobado',
    rechazado: 'Rechazado'
  }
  return map[estado] || estado
}

const estadoClase = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'status-pending',
    aprobado: 'status-approved',
    rechazado: 'status-rejected'
  }
  return map[estado] || ''
}

const estadoDot = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'dot-pending',
    aprobado: 'dot-approved',
    rechazado: 'dot-rejected'
  }
  return map[estado] || ''
}

const clearFilters = () => {
  search.value = ''
  activeFilter.value = 'all'
}

const editarSolicitud = (v: Vacacion) => {
  router.push(`/sigarh/movimientos/vacaciones/${v.id}/edit?tenant=${tenant}`)
}

const confirmarEliminar = (v: Vacacion) => {
  solicitudToDelete.value = v
  showDeleteModal.value = true
}

const deleteSolicitud = async () => {
  if (!solicitudToDelete.value) return
  try {
    await $api(`/sigarh/movimientos/vacaciones/${solicitudToDelete.value.id}`, {
      method: 'DELETE',
      tenant
    })
    vacaciones.value = vacaciones.value.filter(v => v.id !== solicitudToDelete.value?.id)
    showDeleteModal.value = false
    solicitudToDelete.value = null
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo eliminar la solicitud'
  }
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    vacaciones.value = await $api('/sigarh/movimientos/vacaciones', { tenant })
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar las solicitudes'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.vacaciones-container {
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

.vacaciones-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.vacaciones-table thead {
  background: var(--mist);
}

.vacaciones-table th {
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

.vacaciones-table td {
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

.col-employee { width: 22%; }
.col-type { width: 15%; }
.col-dates { width: 25%; }
.col-days { width: 10%; }
.col-status { width: 15%; }
.col-actions { width: 13%; text-align: right; }

/* Employee Cell */
.employee-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.employee-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink);
  flex-shrink: 0;
}

.employee-info {
  display: flex;
  flex-direction: column;
}

.employee-name {
  font-weight: 500;
  color: var(--ink);
}

/* Dates Cell */
.dates-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-text {
  font-size: 0.8125rem;
  color: var(--ink);
}

.date-separator {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

/* Type Text */
.type-text {
  color: var(--ink);
}

/* Days Badge */
.days-badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--mist);
  color: var(--ink);
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

.status-pending {
  background: var(--amber-soft);
  color: var(--amber);
}

.status-approved {
  background: var(--green-soft);
  color: var(--green);
}

.status-rejected {
  background: var(--alert-soft);
  color: var(--alert);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.dot-pending {
  background: var(--amber);
}

.dot-approved {
  background: var(--green);
}

.dot-rejected {
  background: var(--alert);
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

.action-edit:hover {
  color: var(--navy);
  border-color: var(--navy-soft);
  background: var(--navy-soft);
}

.action-delete:hover {
  color: var(--alert);
  border-color: var(--alert-soft);
  background: var(--alert-soft);
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
  .vacaciones-container {
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
  .vacaciones-container {
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

  .col-dates {
    min-width: 160px;
  }

  .col-actions {
    min-width: 80px;
  }

  .col-employee {
    min-width: 180px;
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

  .vacaciones-table td,
  .vacaciones-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }

  .dates-cell {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.125rem;
  }

  .date-separator {
    display: none;
  }

  .col-actions {
    min-width: 70px;
  }

  .action-buttons {
    gap: 0.125rem;
  }

  .action-btn {
    width: 28px;
    height: 28px;
  }

  .modal-content {
    margin: 1rem;
  }
}
</style>