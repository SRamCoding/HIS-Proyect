<template>
  <div class="atenciones-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-clipboard-document-list" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Atenciones Médicas</h1>
          <p class="page-subtitle">Consulta Externa · Gestión de atenciones médicas</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="limpiarFiltros">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
          Refrescar
        </button>
        <NuxtLink :to="link('/app/consulta-externa/atenciones-medicas/historial')" class="btn-secondary">
  <UIcon name="i-heroicons-clock" class="w-4 h-4" />
  Ver Historial
</NuxtLink>
      </div>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Citas -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--teal)">
        <div class="stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ items.length }}</span>
          <span class="stat-label">Total Citas</span>
        </div>
      </div>

      <!-- Pendientes de Atención -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ pendientesAtencion }}</span>
          <span class="stat-label">Pendientes de Atención</span>
        </div>
      </div>

      <!-- Con Triaje -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ conTriaje }}</span>
          <span class="stat-label">Con Triaje</span>
        </div>
      </div>

      <!-- Sin Triaje -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--alert)">
        <div class="stat-icon" style="background: var(--alert-soft)">
          <UIcon name="i-heroicons-exclamation-circle" class="w-5 h-5" style="color: var(--alert)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ sinTriaje }}</span>
          <span class="stat-label">Sin Triaje</span>
        </div>
      </div>
    </div>

    <!-- Filter Section -->
    <div class="filter-section">
      <div class="filter-card">
        <div class="filter-header">
          <UIcon name="i-heroicons-funnel" class="filter-header-icon" />
          <span class="filter-header-title">Filtros</span>
        </div>
        <div class="filter-body">
          <div class="filter-group">
            <div class="filter-item">
              <label class="filter-label">Fecha</label>
              <div class="input-wrapper-small">
                <UIcon name="i-heroicons-calendar" class="input-icon-small" />
                <input 
                  v-model="filtros.fecha" 
                  type="date" 
                  class="input-clinical-small" 
                  @change="cargar"
                />
              </div>
            </div>
            <div class="filter-item">
              <label class="filter-label">Especialidad</label>
              <div class="input-wrapper-small">
                <UIcon name="i-heroicons-star" class="input-icon-small" />
                <select v-model="filtros.especialidad_id" class="input-clinical-small" @change="cargar">
                  <option value="">Todas</option>
                  <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
                </select>
              </div>
            </div>
          </div>
          <div class="filter-result">
            <span class="result-count">{{ items.length }} resultados</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="cargando" class="loading-state">
      <div class="loading-spinner">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>
      <p style="color: var(--ink-soft)">Cargando citas para atención médica...</p>
    </div>

    <!-- Error Message -->
    <div v-else-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Table -->
    <div v-else-if="items.length" class="table-card">
      <div class="table-header">
        <div class="table-header-left">
          <span class="table-title">Citas para Atención</span>
          <span class="table-count">{{ items.length }} citas</span>
        </div>
      </div>
      <div class="table-responsive">
        <table class="atenciones-table">
          <thead>
            <tr>
              <th class="col-hc">
                <span class="th-content">HC</span>
              </th>
              <th class="col-paciente">
                <span class="th-content">Paciente</span>
              </th>
              <th class="col-especialidad">
                <span class="th-content">Especialidad</span>
              </th>
              <th class="col-medico">
                <span class="th-content">Médico</span>
              </th>
              <th class="col-hora">
                <span class="th-content">Hora</span>
              </th>
              <th class="col-triaje">
                <span class="th-content">Triaje</span>
              </th>
              <th class="col-actions">
                <span class="th-content">Acción</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="it in items" :key="it.cita_id" class="table-row">
              <td class="col-hc">
                <span class="hc-text font-mono-data">{{ it.paciente_hc || '—' }}</span>
              </td>
              <td class="col-paciente">
                <div class="paciente-cell">
                  <div class="paciente-avatar" :style="{ background: getPacienteColor(it.paciente_nombre) }">
                    <span>{{ getInitials(it.paciente_nombre) }}</span>
                  </div>
                  <span class="paciente-name">{{ it.paciente_nombre }}</span>
                </div>
              </td>
              <td class="col-especialidad">
                <span class="especialidad-badge" :style="{ background: getEspecialidadColor(it.especialidad_nombre || it.servicio_nombre || '') + '22', color: getEspecialidadColor(it.especialidad_nombre || it.servicio_nombre || '') }">
                  {{ it.especialidad_nombre || it.servicio_nombre || '—' }}
                </span>
              </td>
              <td class="col-medico">
                <span class="medico-name">{{ it.medico_nombre }}</span>
              </td>
              <td class="col-hora">
                <span class="hora-text font-mono-data">{{ it.hora_inicio }}</span>
              </td>
              <td class="col-triaje">
                <span class="status-badge" :class="it.paso_triaje ? 'status-completado' : 'status-pendiente'">
                  <span class="status-dot" :class="it.paso_triaje ? 'dot-completado' : 'dot-pendiente'" />
                  {{ it.paso_triaje ? 'Completado' : 'Pendiente' }}
                </span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <button 
                    class="action-btn action-atender" 
                    title="Atender paciente"
                    @click="atender(it.cita_id)"
                  >
                    <UIcon name="i-heroicons-play" class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!cargando" class="empty-state">
      <div class="empty-icon" style="background: var(--mist)">
        <UIcon name="i-heroicons-clipboard-document-list" class="w-12 h-12" style="color: var(--ink-soft)" />
      </div>
      <h3 style="color: var(--ink)">No hay citas pendientes</h3>
      <p style="color: var(--ink-soft)">Todas las citas han sido atendidas para esta fecha</p>
      <button class="btn-secondary" @click="limpiarFiltros">
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
        Refrescar
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const { api } = useApi()
const { link } = useHospitalNav()

// Estado
const especialidades = ref<any[]>([])
const items = ref<any[]>([])
const cargando = ref(false)
const error = ref('')

// Filtros
const filtros = reactive({
  fecha: new Date().toISOString().slice(0, 10),
  especialidad_id: '',
})

// Computed
const pendientesAtencion = computed(() => items.value.length)
const conTriaje = computed(() => items.value.filter(i => i.paso_triaje).length)
const sinTriaje = computed(() => items.value.filter(i => !i.paso_triaje).length)

// Helpers
const getInitials = (name: string) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map((word: string) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getPacienteColor = (name: string) => {
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

const getEspecialidadColor = (name: string) => {
  const colors = [
    'var(--teal)',
    'var(--purple)',
    'var(--navy)',
    'var(--amber)',
    'var(--green)',
    'var(--pink)',
    'var(--blue)',
    'var(--orange)'
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

// Funciones
function limpiarFiltros() {
  filtros.fecha = new Date().toISOString().slice(0, 10)
  filtros.especialidad_id = ''
  cargar()
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (filtros.fecha) params.set('fecha', filtros.fecha)
    if (filtros.especialidad_id) params.set('especialidad_id', filtros.especialidad_id)
    items.value = await api(`/app/consulta-externa/triaje/pendientes?${params}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar citas'
  } finally {
    cargando.value = false
  }
}

function atender(citaId: string) {
  navigateTo(link(`/app/consulta-externa/atenciones-medicas/${citaId}`))
}

// Lifecycle
onMounted(async () => {
  try {
    especialidades.value = await api('/app/consulta-externa/programacion-medica/especialidades')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar catálogos'
  }
  await cargar()
})
</script>

<style scoped>
/* ============================================
   Mismos estilos que Programación Médica
   ============================================ */
.atenciones-container {
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

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-secondary:hover {
  background: var(--mist);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
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

/* Filter Section */
.filter-section {
  margin-bottom: 1.5rem;
}

.filter-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1.25rem;
  background: var(--mist);
  border-bottom: 1px solid var(--line);
}

.filter-header-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--ink-soft);
}

.filter-header-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.filter-body {
  padding: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  flex: 1;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  white-space: nowrap;
}

.input-wrapper-small {
  position: relative;
  min-width: 150px;
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
  width: 100%;
  padding: 0.375rem 0.625rem 0.375rem 2rem;
  border-radius: 6px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  font-size: 0.8125rem;
  transition: all 0.2s ease;
}

.input-clinical-small:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.filter-result {
  display: flex;
  align-items: center;
}

.result-count {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Loading State */
.loading-state {
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

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--alert-soft);
  color: var(--alert);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

/* Table Card */
.table-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--line);
}

.table-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.table-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.table-count {
  font-size: 0.75rem;
  color: var(--ink-soft);
  background: var(--mist);
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
}

.table-responsive {
  overflow-x: auto;
}

.atenciones-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.atenciones-table thead {
  background: var(--mist);
}

.atenciones-table th {
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

.atenciones-table td {
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

.col-hc { width: 8%; }
.col-paciente { width: 22%; }
.col-especialidad { width: 18%; }
.col-medico { width: 16%; }
.col-hora { width: 12%; }
.col-triaje { width: 12%; }
.col-actions { width: 12%; text-align: right; }

/* Paciente Cell */
.paciente-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.paciente-avatar {
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

.paciente-name {
  font-weight: 500;
  color: var(--ink);
}

/* HC Text */
.hc-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Especialidad Badge */
.especialidad-badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Medico */
.medico-name {
  font-weight: 500;
  color: var(--ink);
}

/* Hora */
.hora-text {
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

.status-completado {
  background: var(--green-soft);
  color: var(--green);
}

.status-pendiente {
  background: var(--amber-soft);
  color: var(--amber);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.dot-completado {
  background: var(--green);
}

.dot-pendiente {
  background: var(--amber);
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

.action-atender:hover {
  color: var(--teal);
  border-color: var(--teal-soft);
  background: var(--teal-soft);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state h3 {
  font-size: 1.125rem;
  margin: 0;
}

.empty-state p {
  margin: 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .atenciones-container {
    padding: 1rem 1.5rem;
  }

  .filter-body {
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

  .input-wrapper-small {
    min-width: auto;
  }

  .filter-result {
    justify-content: flex-end;
  }
}

@media (max-width: 768px) {
  .atenciones-container {
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

  .col-actions {
    min-width: 60px;
  }

  .col-paciente {
    min-width: 130px;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .widgets-grid {
    grid-template-columns: 1fr;
  }

  .col-actions {
    min-width: 50px;
  }

  .action-btn {
    width: 28px;
    height: 28px;
  }

  .action-buttons {
    gap: 0.125rem;
  }

  .filter-body {
    padding: 0.75rem;
  }
}
</style>