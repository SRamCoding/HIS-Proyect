<template>
  <div class="panel-camas-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft, #ccfbf1)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--teal, #0d9488)" />
        </div>
        <div>
          <h1 class="page-title">Panel de Camas</h1>
          <p class="page-subtitle">Hospitalización · Gestión de camas disponibles y ocupadas</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="cargar">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
          Refrescar
        </button>
      </div>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Camas -->
      <div class="stat-widget" style="background: var(--paper, #ffffff); border-left: 4px solid var(--teal, #0d9488)">
        <div class="stat-icon" style="background: var(--teal-soft, #ccfbf1)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--teal, #0d9488)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ camas.length }}</span>
          <span class="stat-label">Total Camas</span>
        </div>
      </div>

      <!-- Disponibles -->
      <div class="stat-widget" style="background: var(--paper, #ffffff); border-left: 4px solid var(--green, #16a34a)">
        <div class="stat-icon" style="background: var(--green-soft, #dcfce7)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green, #16a34a)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ disponibles }}</span>
          <span class="stat-label">Disponibles</span>
        </div>
      </div>

      <!-- Ocupadas -->
      <div class="stat-widget" style="background: var(--paper, #ffffff); border-left: 4px solid var(--alert, #dc2626)">
        <div class="stat-icon" style="background: var(--alert-soft, #fee2e2)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--alert, #dc2626)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ ocupadas }}</span>
          <span class="stat-label">Ocupadas</span>
        </div>
      </div>

      <!-- Mantenimiento -->
      <div class="stat-widget" style="background: var(--paper, #ffffff); border-left: 4px solid var(--blue, #2563eb)">
        <div class="stat-icon" style="background: var(--blue-soft, #dbeafe)">
          <UIcon name="i-heroicons-wrench-screwdriver" class="w-5 h-5" style="color: var(--blue, #2563eb)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ mantenimiento }}</span>
          <span class="stat-label">Mantenimiento</span>
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
              <label class="filter-label">Piso</label>
              <div class="input-wrapper-small">
                <UIcon name="i-heroicons-building-office" class="input-icon-small" />
                <select v-model="pisoSeleccionado" class="input-clinical-small" @change="cargar">
                  <option value="">Todos los pisos</option>
                  <option v-for="p in pisos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                </select>
              </div>
            </div>
          </div>
          <div class="filter-result">
            <span class="result-count">{{ camas.length }} camas</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Leyenda de Estados -->
    <div class="legend-section">
      <div class="legend-card">
        <span class="legend-title">Estado de Camas</span>
        <div class="legend-items">
          <span class="legend-item">
            <span class="legend-dot legend-disponible"></span>
            Disponible
          </span>
          <span class="legend-item">
            <span class="legend-dot legend-ocupada"></span>
            Ocupada
          </span>
          <span class="legend-item">
            <span class="legend-dot legend-mantenimiento"></span>
            Mantenimiento
          </span>
          <span class="legend-item">
            <span class="legend-dot legend-reservada"></span>
            Reservada
          </span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="cargando" class="loading-state">
      <div class="loading-spinner">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal, #0d9488)" />
      </div>
      <p style="color: var(--ink-soft, #64748b)">Cargando panel de camas...</p>
    </div>

    <!-- Error Message -->
    <div v-else-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Grid de Camas -->
    <div v-else-if="camas.length" class="camas-grid">
      <div
        v-for="c in camas"
        :key="c.id"
        class="cama-card"
        :class="{
          'cama-disponible': c.estado === 'DISPONIBLE',
          'cama-ocupada': c.estado === 'OCUPADA',
          'cama-mantenimiento': c.estado === 'MANTENIMIENTO',
          'cama-reservada': c.estado === 'RESERVADA',
        }"
        @click="verDetalle(c)"
      >
        <div class="cama-header">
          <span class="cama-codigo">{{ c.codigo }}</span>
          <span class="cama-estado-badge" :class="{
            'badge-disponible': c.estado === 'DISPONIBLE',
            'badge-ocupada': c.estado === 'OCUPADA',
            'badge-mantenimiento': c.estado === 'MANTENIMIENTO',
            'badge-reservada': c.estado === 'RESERVADA',
          }">
            {{ c.estado }}
          </span>
        </div>
        <div class="cama-body">
          <div class="cama-info">
            <UIcon name="i-heroicons-building-office" class="cama-icon" />
            <span class="cama-sala">{{ c.sala_nombre || '—' }}</span>
          </div>
          <div v-if="c.tipo_cama" class="cama-info">
            <UIcon name="i-heroicons-tag" class="cama-icon" />
            <span class="cama-tipo">{{ c.tipo_cama }}</span>
          </div>
          <div v-if="c.estado === 'OCUPADA' && c.paciente_nombre" class="cama-paciente">
            <UIcon name="i-heroicons-user" class="cama-icon" />
            <span class="cama-paciente-nombre">{{ c.paciente_nombre }}</span>
          </div>
        </div>
        <div class="cama-footer">
          <span class="cama-hint">Click para ver detalle</span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!cargando" class="empty-state">
      <div class="empty-icon" style="background: var(--mist, #f1f5f9)">
        <UIcon name="i-heroicons-building-office-2" class="w-12 h-12" style="color: var(--ink-soft, #64748b)" />
      </div>
      <h3 style="color: var(--ink, #1e293b)">No hay camas registradas</h3>
      <p style="color: var(--ink-soft, #64748b)">No se encontraron camas para los filtros seleccionados</p>
      <button class="btn-secondary" @click="pisoSeleccionado = ''; cargar()">
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
        Limpiar filtros
      </button>
    </div>

    <!-- Modal Detalle -->
    <div v-if="camaDetalle" class="modal-overlay" @click.self="camaDetalle = null">
      <div class="modal-container modal-detalle">
        <!-- Modal Header -->
        <div class="modal-header" :style="{ background: getEstadoColor(camaDetalle.estado) }">
          <div class="modal-header-left">
            <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: white" />
            <span class="modal-title">Cama {{ camaDetalle.codigo }}</span>
          </div>
          <button class="modal-close" @click="camaDetalle = null">
            <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
          </button>
        </div>

        <!-- Modal Body -->
        <div class="modal-body">
          <div class="detalle-grid">
            <div class="detalle-item">
              <span class="detalle-label">Sala</span>
              <span class="detalle-value">{{ camaDetalle.sala_nombre || '—' }}</span>
            </div>
            <div class="detalle-item">
              <span class="detalle-label">Tipo</span>
              <span class="detalle-value">{{ camaDetalle.tipo_cama || '—' }}</span>
            </div>
            <div class="detalle-item">
              <span class="detalle-label">Estado</span>
              <span class="detalle-value">
                <span class="estado-badge-modal" :class="{
                  'badge-disponible': camaDetalle.estado === 'DISPONIBLE',
                  'badge-ocupada': camaDetalle.estado === 'OCUPADA',
                  'badge-mantenimiento': camaDetalle.estado === 'MANTENIMIENTO',
                  'badge-reservada': camaDetalle.estado === 'RESERVADA',
                }">
                  {{ camaDetalle.estado }}
                </span>
              </span>
            </div>
            <div v-if="camaDetalle.piso_nombre" class="detalle-item">
              <span class="detalle-label">Piso</span>
              <span class="detalle-value">{{ camaDetalle.piso_nombre }}</span>
            </div>
          </div>

          <!-- Información de paciente si está ocupada -->
          <div v-if="camaDetalle.estado === 'OCUPADA'" class="paciente-info-modal">
            <div class="paciente-info-header">
              <UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--teal, #0d9488)" />
              <span class="paciente-info-title">Información del Paciente</span>
            </div>
            <div class="paciente-info-grid">
              <div class="paciente-info-item">
                <span class="paciente-info-label">Paciente</span>
                <span class="paciente-info-value">{{ camaDetalle.paciente_nombre || '—' }}</span>
              </div>
              <div class="paciente-info-item">
                <span class="paciente-info-label">DNI</span>
                <span class="paciente-info-value font-mono-data">{{ camaDetalle.paciente_dni || 'NN' }}</span>
              </div>
              <div class="paciente-info-item">
                <span class="paciente-info-label">N° Hospitalización</span>
                <span class="paciente-info-value">{{ camaDetalle.numero_hospitalizacion || '—' }}</span>
              </div>
              <div class="paciente-info-item">
                <span class="paciente-info-label">Ingreso</span>
                <span class="paciente-info-value">{{ camaDetalle.fecha_ingreso ? formatFechaHora(camaDetalle.fecha_ingreso) : '—' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <button class="btn-modal-secondary" @click="camaDetalle = null">
            Cerrar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const { api } = useApi()

// Estado
const pisos = ref<any[]>([])
const camas = ref<any[]>([])
const pisoSeleccionado = ref('')
const cargando = ref(false)
const error = ref('')
const camaDetalle = ref<any>(null)

// Computed
const disponibles = computed(() => camas.value.filter(c => c.estado === 'DISPONIBLE').length)
const ocupadas = computed(() => camas.value.filter(c => c.estado === 'OCUPADA').length)
const mantenimiento = computed(() => camas.value.filter(c => c.estado === 'MANTENIMIENTO').length)

// Helpers
const formatFechaHora = (fecha: string) => {
  if (!fecha) return '—'
  return new Date(fecha).toLocaleString('es-PE')
}

const getEstadoColor = (estado: string) => {
  const map: Record<string, string> = {
    'DISPONIBLE': '#16a34a',
    'OCUPADA': '#dc2626',
    'MANTENIMIENTO': '#2563eb',
    'RESERVADA': '#d97706'
  }
  return map[estado] || '#1e293b'
}

// Funciones
async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const params = pisoSeleccionado.value ? `?piso_id=${pisoSeleccionado.value}` : ''
    camas.value = await api(`/app/hospitalizacion/panel-camas${params}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar el panel de camas'
  } finally {
    cargando.value = false
  }
}

function verDetalle(c: any) {
  camaDetalle.value = c
}

// Lifecycle
onMounted(async () => {
  try {
    pisos.value = await api('/app/hospitalizacion/pisos')
  } catch (e: any) { /* silencioso */ }
  await cargar()
})
</script>

<style scoped>
/* ============================================
   Estilos principales - Panel de Camas
   ============================================ */
.panel-camas-container {
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
  color: var(--ink, #1e293b);
  margin: 0;
  line-height: 1.2;
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--ink-soft, #64748b);
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
  border: 1px solid var(--line, #e2e8f0);
  background: var(--paper, #ffffff);
  color: var(--ink, #1e293b);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-secondary:hover {
  background: var(--mist, #f1f5f9);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
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
  border-radius: var(--radius, 10px);
  border: 1px solid var(--line, #e2e8f0);
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
  transition: all 0.2s ease;
}

.stat-widget:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md, 0 4px 6px rgba(0,0,0,0.07));
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
  color: var(--ink, #1e293b);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--ink-soft, #64748b);
}

/* Filter Section */
.filter-section {
  margin-bottom: 1rem;
}

.filter-card {
  background: var(--paper, #ffffff);
  border-radius: var(--radius-lg, 14px);
  border: 1px solid var(--line, #e2e8f0);
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
  overflow: hidden;
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1.25rem;
  background: var(--mist, #f1f5f9);
  border-bottom: 1px solid var(--line, #e2e8f0);
}

.filter-header-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--ink-soft, #64748b);
}

.filter-header-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink, #1e293b);
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
  color: var(--ink, #1e293b);
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
  color: var(--ink-soft, #64748b);
}

.input-clinical-small {
  width: 100%;
  padding: 0.375rem 0.625rem 0.375rem 2rem;
  border-radius: 6px;
  border: 1px solid var(--line, #e2e8f0);
  background: var(--paper, #ffffff);
  color: var(--ink, #1e293b);
  font-size: 0.8125rem;
  transition: all 0.2s ease;
}

.input-clinical-small:focus {
  outline: none;
  border-color: var(--teal, #0d9488);
  box-shadow: 0 0 0 3px var(--teal-soft, #ccfbf1);
}

.filter-result {
  display: flex;
  align-items: center;
}

.result-count {
  font-size: 0.8125rem;
  color: var(--ink-soft, #64748b);
}

/* Legend Section */
.legend-section {
  margin-bottom: 1.5rem;
}

.legend-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.625rem 1.25rem;
  background: var(--paper, #ffffff);
  border-radius: var(--radius, 10px);
  border: 1px solid var(--line, #e2e8f0);
  flex-wrap: wrap;
}

.legend-title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft, #64748b);
}

.legend-items {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--ink, #1e293b);
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.legend-disponible {
  background: var(--green, #16a34a);
}

.legend-ocupada {
  background: var(--alert, #dc2626);
}

.legend-mantenimiento {
  background: var(--blue, #2563eb);
}

.legend-reservada {
  background: var(--amber, #d97706);
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
  background: var(--alert-soft, #fee2e2);
  color: var(--alert, #dc2626);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

/* Grid de Camas */
.camas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.cama-card {
  background: var(--paper, #ffffff);
  border-radius: var(--radius, 10px);
  border: 2px solid var(--line, #e2e8f0);
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cama-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md, 0 4px 6px rgba(0,0,0,0.07));
}

.cama-card.cama-disponible {
  border-color: var(--green, #16a34a);
  background: var(--green-soft, #dcfce7);
}

.cama-card.cama-ocupada {
  border-color: var(--alert, #dc2626);
  background: var(--alert-soft, #fee2e2);
}

.cama-card.cama-mantenimiento {
  border-color: var(--blue, #2563eb);
  background: var(--blue-soft, #dbeafe);
}

.cama-card.cama-reservada {
  border-color: var(--amber, #d97706);
  background: var(--amber-soft, #fef3c7);
}

.cama-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cama-codigo {
  font-size: 1rem;
  font-weight: 700;
  color: var(--ink, #1e293b);
}

.cama-estado-badge {
  font-size: 0.625rem;
  font-weight: 600;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  text-transform: uppercase;
}

.badge-disponible {
  background: var(--green, #16a34a);
  color: white;
}

.badge-ocupada {
  background: var(--alert, #dc2626);
  color: white;
}

.badge-mantenimiento {
  background: var(--blue, #2563eb);
  color: white;
}

.badge-reservada {
  background: var(--amber, #d97706);
  color: white;
}

.cama-body {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.cama-info {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--ink-soft, #64748b);
}

.cama-icon {
  width: 0.875rem;
  height: 0.875rem;
  flex-shrink: 0;
}

.cama-sala {
  font-weight: 500;
  color: var(--ink, #1e293b);
}

.cama-tipo {
  color: var(--ink-soft, #64748b);
}

.cama-paciente {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding-top: 0.25rem;
  border-top: 1px solid var(--line, #e2e8f0);
  margin-top: 0.25rem;
}

.cama-paciente-nombre {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink, #1e293b);
}

.cama-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.25rem;
  border-top: 1px solid var(--line, #e2e8f0);
}

.cama-hint {
  font-size: 0.625rem;
  color: var(--ink-soft, #64748b);
  opacity: 0.7;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
  background: var(--paper, #ffffff);
  border-radius: var(--radius-lg, 14px);
  border: 1px solid var(--line, #e2e8f0);
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

/* ============================================
   Modal Styles
   ============================================ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.modal-container {
  background: var(--paper, #ffffff);
  border-radius: var(--radius-lg, 14px);
  box-shadow: var(--shadow-lg, 0 10px 25px rgba(0,0,0,0.15));
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: modalSlideIn 0.2s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-radius: var(--radius-lg, 14px) var(--radius-lg, 14px) 0 0;
  flex-shrink: 0;
}

.modal-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.modal-title {
  font-size: 1rem;
  font-weight: 600;
  color: white;
}

.modal-close {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 6px;
  transition: background 0.2s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.15);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.detalle-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.detalle-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.detalle-label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft, #64748b);
}

.detalle-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink, #1e293b);
}

.estado-badge-modal {
  display: inline-block;
  padding: 0.125rem 0.625rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Paciente Info Modal */
.paciente-info-modal {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line, #e2e8f0);
}

.paciente-info-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.paciente-info-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--ink, #1e293b);
}

.paciente-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.paciente-info-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  padding: 0.375rem;
  border-radius: var(--radius, 10px);
  background: var(--mist, #f1f5f9);
}

.paciente-info-label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft, #64748b);
}

.paciente-info-value {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink, #1e293b);
}

/* Modal Footer */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--line, #e2e8f0);
  flex-shrink: 0;
}

.btn-modal-secondary {
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line, #e2e8f0);
  background: var(--paper, #ffffff);
  color: var(--ink, #1e293b);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-modal-secondary:hover {
  background: var(--mist, #f1f5f9);
}

/* Responsive */
@media (max-width: 1200px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .camas-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }
}

@media (max-width: 1024px) {
  .panel-camas-container {
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
  .panel-camas-container {
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

  .camas-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }

  .legend-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .legend-items {
    gap: 0.75rem;
  }

  .detalle-grid {
    grid-template-columns: 1fr;
  }

  .paciente-info-grid {
    grid-template-columns: 1fr;
  }

  .modal-container {
    max-width: 100%;
    margin: 0.5rem;
  }
}

@media (max-width: 480px) {
  .widgets-grid {
    grid-template-columns: 1fr;
  }

  .camas-grid {
    grid-template-columns: 1fr;
  }

  .cama-card {
    padding: 0.75rem;
  }

  .filter-body {
    padding: 0.75rem;
  }
}
</style>