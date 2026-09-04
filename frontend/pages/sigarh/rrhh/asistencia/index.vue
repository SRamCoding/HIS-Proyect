<template>
  <div class="asistencia-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-clipboard-document-check" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <h1 class="page-title">Registro de Asistencia</h1>
          <p class="page-subtitle">Control de asistencia diaria del personal</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/rrhh/asistencia/create?tenant=${tenantId}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Registrar Asistencia
      </NuxtLink>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Registros -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--navy)">
        <div class="stat-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-clipboard-document-list" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ items.length }}</span>
          <span class="stat-label">Total Registros</span>
        </div>
      </div>

      <!-- Presentes -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ presentes }}</span>
          <span class="stat-label">Presentes</span>
        </div>
      </div>

      <!-- Ausentes -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--alert)">
        <div class="stat-icon" style="background: var(--alert-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--alert)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ ausentes }}</span>
          <span class="stat-label">Ausentes</span>
        </div>
      </div>

      <!-- Tardanzas -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ tardanzas }}</span>
          <span class="stat-label">Tardanzas</span>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <div class="filter-left">
        <div class="filter-group">
          <div class="filter-item">
            <label class="filter-label">Fecha</label>
            <div class="input-wrapper-small">
              <UIcon name="i-heroicons-calendar-days" class="input-icon-small" />
              <input 
                v-model="filtroFecha" 
                type="date" 
                class="input-clinical-small" 
                @change="cargar"
                style="border: 1px solid var(--line); background: var(--paper)"
              />
            </div>
          </div>
          <div class="filter-item">
            <label class="filter-label">Empleado</label>
            <div class="input-wrapper-small">
              <UIcon name="i-heroicons-user" class="input-icon-small" />
              <select v-model="filtroEmpleado" class="input-clinical-small" @change="cargar" style="border: 1px solid var(--line); background: var(--paper)">
                <option value="">Todos los empleados</option>
                <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombre_completo }}</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      <div class="filter-right">
        <span class="result-count">{{ items.length }} registros</span>
        <button class="btn-secondary btn-sm" @click="resetFilters">
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
        <p style="color: var(--ink-soft)">Cargando registros de asistencia...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button class="btn-secondary" @click="cargar">Reintentar</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="items.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-clipboard-document-check" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay registros de asistencia</h3>
        <p style="color: var(--ink-soft)">Comienza registrando la asistencia del personal</p>
        <NuxtLink :to="`/sigarh/rrhh/asistencia/create?tenant=${tenantId}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Registrar Asistencia
        </NuxtLink>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="asistencia-table">
          <thead>
            <tr>
              <th class="col-employee">
                <span class="th-content">Empleado</span>
              </th>
              <th class="col-date">
                <span class="th-content">Fecha</span>
              </th>
              <th class="col-time-in">
                <span class="th-content">Entrada</span>
              </th>
              <th class="col-time-out">
                <span class="th-content">Salida</span>
              </th>
              <th class="col-status">
                <span class="th-content">Estado</span>
              </th>
              <th class="col-observation">
                <span class="th-content">Observación</span>
              </th>
              <th class="col-actions">
                <span class="th-content">Acciones</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in items"
              :key="item.id"
              class="table-row"
            >
              <td class="col-employee">
                <div class="employee-cell">
                  <div class="employee-avatar" :style="{ background: getEmployeeColor(item.empleado_nombre || '') }">
                    <span>{{ getInitials(item.empleado_nombre || '—') }}</span>
                  </div>
                  <span class="employee-name">{{ item.empleado_nombre || '—' }}</span>
                </div>
              </td>
              <td class="col-date">
                <span class="date-text font-mono-data">{{ formatDate(item.fecha) }}</span>
              </td>
              <td class="col-time-in">
                <span class="time-text font-mono-data">{{ item.hora_entrada || '—' }}</span>
              </td>
              <td class="col-time-out">
                <span class="time-text font-mono-data">{{ item.hora_salida || '—' }}</span>
              </td>
              <td class="col-status">
                <span class="status-badge" :class="getStatusClass(item.estado)">
                  <UIcon :name="getStatusIcon(item.estado)" class="w-3.5 h-3.5" />
                  {{ formatEstado(item.estado) }}
                </span>
              </td>
              <td class="col-observation">
                <span class="observation-text">{{ item.observacion || '—' }}</span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <NuxtLink
                    :to="`/sigarh/rrhh/asistencia/${item.id}?tenant=${tenantId}`"
                    class="action-btn action-edit"
                    title="Editar registro"
                  >
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
                  </NuxtLink>
                  <button
                    class="action-btn action-delete"
                    title="Eliminar registro"
                    @click="confirmarEliminar(item)"
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
      <div v-if="items.length > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ items.length }}</strong> registros
          <span v-if="filtroFecha || filtroEmpleado">(filtrados)</span>
        </span>
        <span class="footer-summary">
          <span class="summary-dot" style="background: var(--green)" />
          {{ presentes }} presentes
          <span class="summary-dot" style="background: var(--alert)" />
          {{ ausentes }} ausentes
          <span class="summary-dot" style="background: var(--amber)" />
          {{ tardanzas }} tardanzas
        </span>
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
          ¿Estás seguro de que deseas eliminar este registro de asistencia?
          <br>
          <span style="color: var(--ink-soft); font-size: 0.875rem">
            Esta acción no se puede deshacer.
          </span>
        </p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-danger" @click="deleteItem">
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

interface Item {
  id: string
  empleado_nombre: string | null
  fecha: string
  hora_entrada: string | null
  hora_salida: string | null
  estado: string
  observacion: string | null
}

const { api } = useApi()
const route = useRoute()

const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const empleados = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const filtroFecha = ref('')
const filtroEmpleado = ref('')
const showDeleteModal = ref(false)
const itemToDelete = ref<Item | null>(null)

const presentes = computed(() => items.value.filter(i => i.estado === 'presente').length)
const ausentes = computed(() => items.value.filter(i => i.estado === 'ausente').length)
const tardanzas = computed(() => items.value.filter(i => i.estado === 'tardanza').length)

const getInitials = (name: string) => {
  if (!name || name === '—') return '?'
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

const formatDate = (date: string) => {
  if (!date) return '—'
  const d = new Date(date)
  return d.toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const formatEstado = (estado: string) => {
  const map: Record<string, string> = {
    presente: 'Presente',
    ausente: 'Ausente',
    tardanza: 'Tardanza',
    justificado: 'Justificado'
  }
  return map[estado] || estado
}

const getStatusClass = (estado: string) => {
  const map: Record<string, string> = {
    presente: 'status-presente',
    ausente: 'status-ausente',
    tardanza: 'status-tardanza',
    justificado: 'status-justificado'
  }
  return map[estado] || 'status-default'
}

const getStatusIcon = (estado: string) => {
  const map: Record<string, string> = {
    presente: 'i-heroicons-check-circle',
    ausente: 'i-heroicons-x-circle',
    tardanza: 'i-heroicons-clock',
    justificado: 'i-heroicons-document-text'
  }
  return map[estado] || 'i-heroicons-circle'
}

const resetFilters = () => {
  filtroFecha.value = new Date().toISOString().split('T')[0]
  filtroEmpleado.value = ''
  cargar()
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (filtroFecha.value) params.append('fecha', filtroFecha.value)
    if (filtroEmpleado.value) params.append('empleado_id', filtroEmpleado.value)
    const query = params.toString() ? `?${params.toString()}` : ''
    items.value = await api<Item[]>(`/sigarh/rrhh/asistencia${query}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }
}

const confirmarEliminar = (item: Item) => {
  itemToDelete.value = item
  showDeleteModal.value = true
}

const deleteItem = async () => {
  if (!itemToDelete.value) return
  try {
    await api(`/sigarh/rrhh/asistencia/${itemToDelete.value.id}`, { method: 'DELETE' })
    items.value = items.value.filter(i => i.id !== itemToDelete.value?.id)
    showDeleteModal.value = false
    itemToDelete.value = null
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo eliminar'
  }
}

onMounted(async () => {
  filtroFecha.value = new Date().toISOString().split('T')[0]
  try {
    const [_, emp] = await Promise.all([
      cargar(),
      api<any[]>('/sigarh/rrhh/empleados')
    ])
    empleados.value = emp
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar datos'
  }
})
</script>

<style scoped>
.asistencia-container {
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
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-soft);
}

.input-wrapper-small {
  position: relative;
}

.input-icon-small {
  position: absolute;
  left: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  width: 0.875rem;
  height: 0.875rem;
  color: var(--ink-soft);
}

.input-clinical-small {
  padding: 0.375rem 0.625rem 0.375rem 2rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  transition: all 0.2s ease;
  min-width: 150px;
}

.input-clinical-small:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.input-clinical-small[type="date"] {
  color-scheme: light;
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

.asistencia-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.asistencia-table thead {
  background: var(--mist);
}

.asistencia-table th {
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

.asistencia-table td {
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

.col-employee { width: 18%; }
.col-date { width: 12%; }
.col-time-in { width: 10%; }
.col-time-out { width: 10%; }
.col-status { width: 13%; }
.col-observation { width: 20%; }
.col-actions { width: 17%; text-align: right; }

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

/* Date & Time */
.date-text,
.time-text {
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

.status-presente {
  background: var(--green-soft);
  color: var(--green);
}

.status-ausente {
  background: var(--alert-soft);
  color: var(--alert);
}

.status-tardanza {
  background: var(--amber-soft);
  color: var(--amber);
}

.status-justificado {
  background: var(--teal-soft);
  color: var(--teal);
}

.status-default {
  background: var(--mist);
  color: var(--ink-soft);
}

/* Observation */
.observation-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
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
  .asistencia-container {
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

  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    flex-direction: column;
    align-items: stretch;
  }

  .input-clinical-small {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .asistencia-container {
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

  .col-actions {
    min-width: 70px;
  }

  .col-observation {
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

  .table-responsive {
    margin: 0 -0.5rem;
  }

  .asistencia-table td,
  .asistencia-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }

  .col-employee {
    min-width: 120px;
  }

  .col-actions {
    min-width: 60px;
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