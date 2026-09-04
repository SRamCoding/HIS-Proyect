<template>
  <div class="empleados-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-users" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Empleados</h1>
          <p class="page-subtitle">Personal registrado en el hospital</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/rrhh/empleados/create?tenant=${tenantId}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Empleado
      </NuxtLink>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Employees -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--navy)">
        <div class="stat-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-users" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ empleados.length }}</span>
          <span class="stat-label">Total Empleados</span>
        </div>
      </div>

      <!-- Active Employees -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ activeEmployees }}</span>
          <span class="stat-label">Activos</span>
        </div>
      </div>

      <!-- Inactive Employees -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ inactiveEmployees }}</span>
          <span class="stat-label">Inactivos</span>
        </div>
      </div>

      <!-- Avg Seniority -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--purple)">
        <div class="stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ avgSeniority }}</span>
          <span class="stat-label">Antigüedad Promedio</span>
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
              placeholder="Buscar por nombre o DNI..."
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
          <span class="result-count">{{ empleadosFiltrados.length }} resultados</span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando empleados...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button class="btn-secondary" @click="cargar">Reintentar</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="empleadosFiltrados.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-users" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay empleados registrados</h3>
        <p style="color: var(--ink-soft)">Comienza registrando el personal del hospital</p>
        <NuxtLink :to="`/sigarh/rrhh/empleados/create?tenant=${tenantId}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Nuevo Empleado
        </NuxtLink>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="empleados-table">
          <thead>
            <tr>
              <th class="col-employee">
                <span class="th-content">Empleado</span>
              </th>
              <th class="col-dni">
                <span class="th-content">DNI</span>
              </th>
              <th class="col-position">
                <span class="th-content">Cargo</span>
              </th>
              <th class="col-modality">
                <span class="th-content">Modalidad</span>
              </th>
              <th class="col-seniority">
                <span class="th-content">Antigüedad</span>
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
              v-for="emp in empleadosFiltrados"
              :key="emp.id"
              class="table-row"
            >
              <td class="col-employee">
                <div class="employee-cell">
                  <div class="employee-avatar" :style="{ background: getEmployeeColor(emp.nombre_completo) }">
                    <span>{{ getInitials(emp.nombre_completo) }}</span>
                  </div>
                  <div class="employee-info">
                    <span class="employee-name">{{ emp.nombre_completo }}</span>
                    <span class="employee-email" v-if="emp.email">{{ emp.email }}</span>
                  </div>
                </div>
              </td>
              <td class="col-dni">
                <span class="dni-text font-mono-data">{{ emp.dni }}</span>
              </td>
              <td class="col-position">
                <span class="position-text">{{ emp.cargo_laboral || '—' }}</span>
              </td>
              <td class="col-modality">
                <span class="modality-badge" :class="getModalityClass(emp.modalidad)">
                  {{ emp.modalidad || '—' }}
                </span>
              </td>
              <td class="col-seniority">
                <span class="seniority-text">{{ emp.antiguedad || '—' }}</span>
              </td>
              <td class="col-status">
                <span class="status-badge" :class="emp.is_active ? 'status-active' : 'status-inactive'">
                  <span class="status-dot" :class="emp.is_active ? 'dot-active' : 'dot-inactive'" />
                  {{ emp.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <NuxtLink
                    :to="`/sigarh/rrhh/empleados/${emp.id}?tenant=${tenantId}`"
                    class="action-btn action-edit"
                    title="Editar empleado"
                  >
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
                  </NuxtLink>
                  <button
                    class="action-btn action-delete"
                    title="Eliminar empleado"
                    @click="confirmarEliminar(emp)"
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
      <div v-if="empleadosFiltrados.length > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ empleadosFiltrados.length }}</strong> de <strong>{{ empleados.length }}</strong> empleados
          <span v-if="empleadosFiltrados.length < empleados.length">(filtrados)</span>
        </span>
        <div class="footer-actions">
          <button
            v-if="empleadosFiltrados.length < empleados.length || search || activeFilter !== 'all'"
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
          ¿Estás seguro de que deseas eliminar al empleado <strong>{{ employeeToDelete?.nombre_completo }}</strong>?
          <br>
          <span style="color: var(--ink-soft); font-size: 0.875rem">
            Esta acción no se puede deshacer y eliminará todos los datos asociados.
          </span>
        </p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-danger" @click="deleteEmployee">
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

interface Empleado {
  id: string
  dni: string
  nombre_completo: string
  email?: string
  cargo_laboral: string | null
  modalidad: string | null
  is_active: boolean
  fecha_ingreso: string | null
  antiguedad: string | null
}

const { api } = useApi()
const route = useRoute()

const tenantId = computed(() => route.query.tenant as string || '')
const empleados = ref<Empleado[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const activeFilter = ref('all')
const showDeleteModal = ref(false)
const employeeToDelete = ref<Empleado | null>(null)

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: empleados.value.length },
  { label: 'Activos', value: 'active', count: activeEmployees.value },
  { label: 'Inactivos', value: 'inactive', count: inactiveEmployees.value },
])

const activeEmployees = computed(() => empleados.value.filter(e => e.is_active).length)
const inactiveEmployees = computed(() => empleados.value.filter(e => !e.is_active).length)

const avgSeniority = computed(() => {
  const active = empleados.value.filter(e => e.is_active && e.antiguedad)
  if (!active.length) return '—'
  
  // Parse seniority strings to get average years
  let totalYears = 0
  let count = 0
  active.forEach(e => {
    if (e.antiguedad) {
      const match = e.antiguedad.match(/(\d+)\s*año/)
      if (match) {
        totalYears += parseInt(match[1])
        count++
      }
    }
  })
  if (count === 0) return '—'
  const avg = Math.round(totalYears / count)
  return `${avg} año${avg > 1 ? 's' : ''}`
})

const empleadosFiltrados = computed(() => {
  let result = empleados.value

  // Filter by status
  if (activeFilter.value === 'active') {
    result = result.filter(e => e.is_active)
  } else if (activeFilter.value === 'inactive') {
    result = result.filter(e => !e.is_active)
  }

  // Filter by search
  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    result = result.filter(e =>
      e.nombre_completo.toLowerCase().includes(q) ||
      e.dni.includes(q) ||
      (e.cargo_laboral && e.cargo_laboral.toLowerCase().includes(q))
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

const getModalityClass = (modality: string | null) => {
  if (!modality) return 'modality-default'
  const map: Record<string, string> = {
    'Nombrado': 'modality-nombrado',
    'Contratado': 'modality-contratado',
    'CAS': 'modality-cas',
    'Locación': 'modality-locacion',
    'Practicante': 'modality-practicante',
  }
  return map[modality] || 'modality-default'
}

const clearFilters = () => {
  search.value = ''
  activeFilter.value = 'all'
}

const confirmarEliminar = (emp: Empleado) => {
  employeeToDelete.value = emp
  showDeleteModal.value = true
}

const deleteEmployee = async () => {
  if (!employeeToDelete.value) return
  try {
    await api(`/sigarh/rrhh/empleados/${employeeToDelete.value.id}`, { method: 'DELETE' })
    empleados.value = empleados.value.filter(e => e.id !== employeeToDelete.value?.id)
    showDeleteModal.value = false
    employeeToDelete.value = null
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo eliminar'
  }
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    empleados.value = await api<Empleado[]>('/sigarh/rrhh/empleados')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.empleados-container {
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

.empleados-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.empleados-table thead {
  background: var(--mist);
}

.empleados-table th {
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

.empleados-table td {
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
.col-dni { width: 10%; }
.col-position { width: 16%; }
.col-modality { width: 13%; }
.col-seniority { width: 12%; }
.col-status { width: 12%; }
.col-actions { width: 15%; text-align: right; }

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

.employee-email {
  font-size: 0.6875rem;
  color: var(--ink-soft);
}

/* DNI */
.dni-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Position */
.position-text {
  color: var(--ink);
}

/* Modality Badge */
.modality-badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
}

.modality-nombrado {
  background: var(--green-soft);
  color: var(--green);
}

.modality-contratado {
  background: var(--teal-soft);
  color: var(--teal);
}

.modality-cas {
  background: var(--amber-soft);
  color: var(--amber);
}

.modality-locacion {
  background: var(--purple-soft);
  color: var(--purple);
}

.modality-practicante {
  background: var(--blue-soft);
  color: var(--blue);
}

.modality-default {
  background: var(--mist);
  color: var(--ink-soft);
}

/* Seniority */
.seniority-text {
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
  .empleados-container {
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
  .empleados-container {
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

  .empleados-table td,
  .empleados-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }

  .col-dni {
    min-width: 90px;
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
}
</style>