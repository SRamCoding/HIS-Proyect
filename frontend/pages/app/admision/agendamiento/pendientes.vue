<template>
  <div class="citas-confirmar-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <h1 class="page-title">Citas por Confirmar</h1>
          <p class="page-subtitle">Consulta Externa · Gestión de citas pendientes de confirmación</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="limpiarFiltros">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
          Refrescar
        </button>
      </div>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Pendientes -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ citas.length }}</span>
          <span class="stat-label">Total Pendientes</span>
        </div>
      </div>

      <!-- Por Confirmar Hoy -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--blue)">
        <div class="stat-icon" style="background: var(--blue-soft)">
          <UIcon name="i-heroicons-calendar" class="w-5 h-5" style="color: var(--blue)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ citasHoy }}</span>
          <span class="stat-label">Para hoy</span>
        </div>
      </div>

      <!-- Por Confirmar Mañana -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--purple)">
        <div class="stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ citasManana }}</span>
          <span class="stat-label">Para mañana</span>
        </div>
      </div>

      <!-- Próximas -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--teal)">
        <div class="stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-arrow-trending-up" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ citasProximas }}</span>
          <span class="stat-label">Próximas (2+ días)</span>
        </div>
      </div>
    </div>

    <!-- Filter Section -->
    <div v-if="exito" class="filter-card" role="status" style="padding: 16px; margin-bottom: 16px">
      <p>{{ exito }}</p>
      <NuxtLink :to="link('/app/consulta-externa/triaje')" class="btn-secondary">Ir a Registro de Triaje</NuxtLink>
    </div>
    <div class="filter-section">
      <div class="filter-card">
        <div class="filter-header">
          <UIcon name="i-heroicons-funnel" class="filter-header-icon" />
          <span class="filter-header-title">Filtros</span>
        </div>
        <div class="filter-body">
          <div class="filter-group">
            <div class="filter-item">
              <label class="filter-label">Fecha (vacía: todas)</label>
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
          </div>
          <div class="filter-result">
            <span class="result-count">{{ citas.length }} resultados</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="cargando" class="loading-state">
      <div class="loading-spinner">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--amber)" />
      </div>
      <p style="color: var(--ink-soft)">Cargando citas pendientes de confirmar...</p>
    </div>

    <!-- Error Message -->
    <div v-else-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Table -->
    <div v-else-if="citas.length" class="table-card">
      <div class="table-header">
        <div class="table-header-left">
          <span class="table-title">Citas Pendientes de Confirmación</span>
          <span class="table-count">{{ citas.length }} citas</span>
        </div>
      </div>
      <div class="table-responsive">
        <table class="citas-confirmar-table">
          <thead>
            <tr>
              <th class="col-paciente">
                <span class="th-content">Paciente</span>
              </th>
              <th class="col-dni">
                <span class="th-content">DNI</span>
              </th>
              <th class="col-fecha">
                <span class="th-content">Fecha</span>
              </th>
              <th class="col-hora">
                <span class="th-content">Hora</span>
              </th>
              <th class="col-tipo">
                <span class="th-content">Tipo Consulta</span>
              </th>
              <th class="col-especialidad">
                <span class="th-content">Especialidad</span>
              </th>
              <th class="col-actions">
                <span class="th-content">Acciones</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in citas" :key="c.id" class="table-row">
              <td class="col-paciente">
                <div class="paciente-cell">
                  <div class="paciente-avatar" :style="{ background: getPacienteColor(c.paciente_nombre) }">
                    <span>{{ getInitials(c.paciente_nombre) }}</span>
                  </div>
                  <span class="paciente-name">{{ c.paciente_nombre }}</span>
                </div>
              </td>
              <td class="col-dni">
                <span class="dni-text font-mono-data">{{ c.paciente_dni || '—' }}</span>
              </td>
              <td class="col-fecha">
                <span class="fecha-text font-mono-data">{{ formatFecha(c.fecha) }}</span>
              </td>
              <td class="col-hora">
                <span class="hora-text font-mono-data">{{ c.hora_inicio }} - {{ c.hora_fin }}</span>
              </td>
              <td class="col-tipo">
                <span class="tipo-badge" :style="{ background: getTipoColor(c.tipo_consulta) + '22', color: getTipoColor(c.tipo_consulta) }">
                  {{ c.tipo_consulta || '—' }}
                </span>
              </td>
              <td class="col-especialidad">
                <span class="especialidad-text">{{ c.especialidad_nombre || '—' }}</span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <button
                    class="action-btn action-view"
                    title="Imprimir comprobante"
                    :disabled="imprimiendoId === c.id"
                    @click="imprimir(c.id)"
                  >
                    <UIcon v-if="imprimiendoId === c.id" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                    <UIcon v-else name="i-heroicons-printer" class="w-4 h-4" />
                  </button>
                  <button 
                    class="action-btn action-confirm" 
                    title="Confirmar cita"
                    :disabled="!!confirmandoId"
                    @click="confirmar(c.id)"
                  >
                    <UIcon v-if="confirmandoId === c.id" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                    <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                  </button>
                  <NuxtLink 
                    :to="link(`/app/admision/agendamiento/${c.id}`)" 
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
    </div>

    <!-- Empty State -->
    <div v-else-if="!cargando" class="empty-state">
      <div class="empty-icon" style="background: var(--mist)">
        <UIcon name="i-heroicons-clock" class="w-12 h-12" style="color: var(--ink-soft)" />
      </div>
      <h3 style="color: var(--ink)">No hay citas pendientes</h3>
      <p style="color: var(--ink-soft)">No hay citas separadas {{ filtros.fecha ? 'para la fecha seleccionada' : 'con estos filtros' }}.</p>
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
const { abrirComprobante, imprimiendoId } = useCitaPdf()

// Estado
const citas = ref<any[]>([])
const cargando = ref(false)
const error = ref('')
const confirmandoId = ref('')
const exito = ref('')

async function imprimir(citaId: string) {
  error.value = ''
  try {
    await abrirComprobante(citaId)
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo generar el comprobante de la cita'
  }
}

// Filtros
const filtros = reactive({
  fecha: '',
})

function fechaLocal(d: Date) { return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` }

// Computed
const citasHoy = computed(() => {
  const hoy = fechaLocal(new Date())
  return citas.value.filter(c => c.fecha === hoy).length
})

const citasManana = computed(() => {
  const manana = new Date()
  manana.setDate(manana.getDate() + 1)
  const mananaStr = fechaLocal(manana)
  return citas.value.filter(c => c.fecha === mananaStr).length
})

const citasProximas = computed(() => {
  const manana = new Date()
  manana.setDate(manana.getDate() + 1)
  const mananaStr = fechaLocal(manana)
  return citas.value.filter(c => c.fecha > mananaStr).length
})

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
    'var(--amber-soft)',
    'var(--blue-soft)',
    'var(--purple-soft)',
    'var(--teal-soft)',
    'var(--green-soft)',
    'var(--pink-soft)',
    'var(--navy-soft)',
    'var(--orange-soft)'
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const getTipoColor = (tipo: string) => {
  const map: Record<string, string> = {
    'CONSULTA EXTERNA': 'var(--blue)',
    'CONSULTA PEDIATRICA': 'var(--teal)',
    'CONSULTA GERIATRICA': 'var(--purple)',
    'CONSULTA OBSTETRICA': 'var(--pink)',
    'CONSULTA PSICOLOGICA': 'var(--green)',
    'CONSULTA NUTRICIONAL': 'var(--orange)',
    'CONSULTA ODONTOLOGICA': 'var(--navy)'
  }
  return map[tipo] || 'var(--ink-soft)'
}

const formatFecha = (fecha: string) => {
  if (!fecha) return '—'
  const d = new Date(`${fecha.slice(0, 10)}T00:00:00`)
  return d.toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

// Funciones
function limpiarFiltros() {
  filtros.fecha = ''
  cargar()
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const params = new URLSearchParams({ estado: 'separada' })
    if (filtros.fecha) params.set('fecha', filtros.fecha)
    citas.value = await api(`/app/consulta-externa/citas?${params}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar citas pendientes'
  } finally {
    cargando.value = false
  }
}

async function confirmar(citaId: string) {
  if (confirmandoId.value) return
  confirmandoId.value = citaId
  error.value = ''
  try {
    await api(`/app/consulta-externa/citas/${citaId}/confirmar`, { method: 'POST' })
    citas.value = citas.value.filter((c) => c.id !== citaId)
    exito.value = 'Cita confirmada. Continúa en Registro de Triaje seleccionando la fecha de la cita.'
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al confirmar la cita'
  } finally {
    confirmandoId.value = ''
  }
}

// Lifecycle
onMounted(cargar)
</script>

<style scoped>
/* ============================================
   Mismos estilos que Programación Médica
   ============================================ */
.citas-confirmar-container {
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
  min-width: 200px;
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
  border-color: var(--amber);
  box-shadow: 0 0 0 3px var(--amber-soft);
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

.citas-confirmar-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.citas-confirmar-table thead {
  background: var(--mist);
}

.citas-confirmar-table th {
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

.citas-confirmar-table td {
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

.col-paciente { width: 20%; }
.col-dni { width: 12%; }
.col-fecha { width: 12%; }
.col-hora { width: 16%; }
.col-tipo { width: 16%; }
.col-especialidad { width: 14%; }
.col-actions { width: 10%; text-align: right; }

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

.dni-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.fecha-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.hora-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.tipo-badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.especialidad-text {
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

.action-btn:hover:not(:disabled) {
  background: var(--mist);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-confirm:hover:not(:disabled) {
  color: var(--green);
  border-color: var(--green-soft);
  background: var(--green-soft);
}

.action-view:hover:not(:disabled) {
  color: var(--blue);
  border-color: var(--blue-soft);
  background: var(--blue-soft);
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
  .citas-confirmar-container {
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
  .citas-confirmar-container {
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
    min-width: 80px;
  }

  .col-paciente {
    min-width: 140px;
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
    min-width: 70px;
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
