<template>
  <div class="cita-detail-container">
    <div class="cita-detail-grid">
      <!-- Main Content -->
      <div class="cita-detail-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="link('/app/admision/agendamiento')" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-calendar" class="w-3.5 h-3.5" />
              Agendamiento de Citas
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Detalle de Cita</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" :style="{ background: getEstadoColor(cita?.estado || '') + '22' }">
              <UIcon
                name="i-heroicons-calendar-days"
                class="w-6 h-6"
                :style="{ color: getEstadoColor(cita?.estado || '') }"
              />
            </div>
            <div>
              <h1 class="page-title">{{ cita?.paciente_nombre || 'Detalle de Cita' }}</h1>
              <p class="page-subtitle">
                <span class="cita-id font-mono-data">#{{ citaId }}</span>
                <span class="separator">·</span>
                <span class="estado-display" :class="getEstadoClass(cita?.estado || '')">
                  {{ formatEstado(cita?.estado || '') }}
                </span>
                <span class="separator">·</span>
                <span class="fecha-display">{{ cita?.hora_inicio ? formatFecha(cita.hora_inicio) : '—' }}</span>
              </p>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="cargando" class="loading-state">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando información de la cita...</p>
        </div>

        <template v-else-if="cita">
          <!-- Success Message -->
          <div v-if="exito" class="success-banner">
            <UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />
            {{ exito }}
          </div>

          <!-- Error Message -->
          <div v-if="error" class="error-banner">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ error }}
          </div>

          <!-- Form Card -->
          <section class="form-card">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4" style="color: var(--teal)" />
              </div>
              <div>
                <h3 class="card-title">Información de la Cita</h3>
                <p class="card-subtitle">Detalles y gestión de la cita médica</p>
              </div>
            </div>

            <!-- Paciente Section -->
            <div class="section-block">
              <div class="section-header">
                <div class="section-header-icon" style="background: var(--purple-soft)">
                  <UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--purple)" />
                </div>
                <div>
                  <h4 class="section-title">Paciente</h4>
                  <p class="section-desc">Información del paciente</p>
                </div>
              </div>

              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">Nombre Completo</span>
                  <span class="info-value">{{ cita.paciente_nombre || '—' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">DNI</span>
                  <span class="info-value font-mono-data">{{ cita.paciente_dni || 'NN' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">N° Historia</span>
                  <span class="info-value font-mono-data">{{ cita.paciente_record || '—' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Seguro</span>
                  <span class="info-value">{{ cita.paciente_insurance || '—' }}</span>
                </div>
              </div>
            </div>

            <!-- Cita Section -->
            <div class="section-block">
              <div class="section-header">
                <div class="section-header-icon" style="background: var(--teal-soft)">
                  <UIcon name="i-heroicons-calendar-days" class="w-4 h-4" style="color: var(--teal)" />
                </div>
                <div>
                  <h4 class="section-title">Datos de la Cita</h4>
                  <p class="section-desc">Información de la programación</p>
                </div>
              </div>

              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">Fecha</span>
                  <span class="info-value font-mono-data">{{ cita.fecha ? formatFecha(cita.fecha) : '—' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Horario</span>
                  <span class="info-value font-mono-data">{{ cita.hora_inicio || '—' }} - {{ cita.hora_fin || '—' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Médico</span>
                  <span class="info-value">{{ cita.medico_nombre || '—' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Especialidad</span>
                  <span class="info-value">{{ cita.especialidad_nombre || '—' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Servicio</span>
                  <span class="info-value">{{ cita.servicio_nombre || '—' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Turno</span>
                  <span class="info-value">
                    <span class="turno-badge" :class="cita.turno === 'MAÑANA' ? 'turno-manana' : cita.turno === 'TARDE' ? 'turno-tarde' : 'turno-noche'">
                      <UIcon :name="getTurnoIcon(cita.turno)" class="w-3.5 h-3.5" />
                      {{ cita.turno || '—' }}
                    </span>
                  </span>
                </div>
              </div>
            </div>

            <!-- Edición Section -->
            <div class="section-block">
              <div class="section-header">
                <div class="section-header-icon" style="background: var(--amber-soft)">
                  <UIcon name="i-heroicons-pencil" class="w-4 h-4" style="color: var(--amber)" />
                </div>
                <div>
                  <h4 class="section-title">Editar Cita</h4>
                  <p class="section-desc">Actualiza la información de la cita</p>
                </div>
              </div>

              <div class="form-grid">
                <div class="form-group full-width">
                  <label class="form-label">Observación</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                    <textarea
                      v-model="form.observacion"
                      class="input-clinical"
                      rows="2"
                      placeholder="Observaciones adicionales..."
                    />
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Fuente Financiamiento</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-currency-dollar" class="input-icon" />
                    <input
                      v-model="form.fuente_financiamiento"
                      class="input-clinical"
                      placeholder="SIS, EsSalud, Particular..."
                    />
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Producto/Plan</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-document" class="input-icon" />
                    <input
                      v-model="form.producto_plan"
                      class="input-clinical"
                      placeholder="Plan de salud"
                    />
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Estado de la Cita</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-flag" class="input-icon" />
                    <select v-model="form.estado" class="input-clinical">
  <option value="separada">Separada</option>
  <option value="atendida">Atendida</option>
  <option value="cancelada">Cancelada</option>
  <option value="no_asistio">No Asistió</option>
</select>
                  </div>
                  <p class="field-hint">Cambia el estado de la cita según corresponda</p>
                </div>
              </div>
            </div>

            <!-- Preview Section -->
            <div class="preview-section">
              <h4 class="preview-title">Vista Previa</h4>
              <div class="preview-card">
                <div class="preview-icon" :style="{ background: getEstadoColor(form.estado) + '22' }">
                  <UIcon :name="getEstadoIcon(form.estado)" class="w-5 h-5" :style="{ color: getEstadoColor(form.estado) }" />
                </div>
                <div class="preview-info">
                  <span class="preview-name">{{ cita.paciente_nombre || 'Paciente' }}</span>
                  <span class="preview-detail">
                    <span class="preview-estado" :style="{ color: getEstadoColor(form.estado) }">
                      {{ formatEstado(form.estado) }}
                    </span>
                    <span class="preview-horario">{{ cita.hora_inicio || '--:--' }} - {{ cita.hora_fin || '--:--' }}</span>
                  </span>
                  <span class="preview-fuente">{{ form.fuente_financiamiento || 'Sin fuente' }}</span>
                </div>
                <span class="preview-status" :class="form.estado === 'atendida' ? 'preview-atendida' : form.estado === 'cancelada' ? 'preview-cancelada' : form.estado === 'no_asistio' ? 'preview-no-asistio' : form.estado === 'confirmada' ? 'preview-confirmada' : 'preview-separada'">
                  <span class="preview-dot" :class="form.estado === 'atendida' ? 'dot-atendida' : form.estado === 'cancelada' ? 'dot-cancelada' : form.estado === 'no_asistio' ? 'dot-no-asistio' : form.estado === 'confirmada' ? 'dot-confirmada' : 'dot-separada'" />
                  {{ formatEstado(form.estado) }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="form-actions">
              <div class="action-group">
                <button
                  v-if="cita.estado === 'separada'"
                  class="btn-primary"
                  style="background: var(--blue)"
                  :disabled="confirmando"
                  @click="confirmarCita"
                >
                  <UIcon v-if="confirmando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <UIcon v-else name="i-heroicons-check-badge" class="w-4 h-4" />
                  {{ confirmando ? 'Confirmando...' : 'Confirmar Cita' }}
                </button>
                <button
                  class="btn-primary"
                  :disabled="guardando"
                  @click="guardar"
                >
                  <UIcon v-if="guardando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                  {{ guardando ? 'Guardando...' : 'Guardar Cambios' }}
                </button>
                <NuxtLink
                  :to="link('/app/admision/agendamiento')"
                  class="btn-cancel"
                >
                  <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
                  Volver
                </NuxtLink>
              </div>
            </div>
          </section>
        </template>

        <div v-else class="empty-state">
          <div class="empty-icon" style="background: var(--mist)">
            <UIcon name="i-heroicons-calendar-days" class="w-12 h-12" style="color: var(--ink-soft)" />
          </div>
          <h3 style="color: var(--ink)">Cita no encontrada</h3>
          <p style="color: var(--ink-soft)">La cita que buscas no existe o fue eliminada</p>
          <NuxtLink :to="link('/app/admision/agendamiento')" class="btn-primary">
            <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
            Volver al listado
          </NuxtLink>
        </div>
      </div>

      <!-- Sidebar Widgets -->
      <div class="cita-detail-sidebar">
        <!-- Status Widget -->
        <div class="widget widget-status">
          <div class="widget-header">
            <UIcon name="i-heroicons-information-circle" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Estado de la Cita</h4>
          </div>
          <div class="widget-content">
            <div class="status-display">
              <div class="status-icon-large" :style="{ background: getEstadoColor(form.estado) + '22' }">
                <UIcon :name="getEstadoIcon(form.estado)" class="w-8 h-8" :style="{ color: getEstadoColor(form.estado) }" />
              </div>
              <div class="status-info">
                <span class="status-label">Estado actual</span>
                <span class="status-value-large" :style="{ color: getEstadoColor(form.estado) }">
                  {{ formatEstado(form.estado) }}
                </span>
              </div>
            </div>

            <div class="status-timeline">
              <div class="timeline-item" :class="{ 'timeline-active': form.estado === 'separada' }">
                <div class="timeline-dot" :class="{ 'dot-active': form.estado === 'separada' }" />
                <span class="timeline-label">Separada</span>
              </div>
              <div class="timeline-line" :class="{ 'line-active': form.estado === 'confirmada' || form.estado === 'atendida' || form.estado === 'cancelada' || form.estado === 'no_asistio' }" />
              <div class="timeline-item" :class="{ 'timeline-active': form.estado === 'confirmada' }">
                <div class="timeline-dot" :class="{ 'dot-active': form.estado === 'confirmada' }" />
                <span class="timeline-label">Confirmada</span>
              </div>
              <div class="timeline-line" :class="{ 'line-active': form.estado === 'atendida' || form.estado === 'cancelada' || form.estado === 'no_asistio' }" />
              <div class="timeline-item" :class="{ 'timeline-active': form.estado === 'atendida' }">
                <div class="timeline-dot" :class="{ 'dot-active': form.estado === 'atendida' }" />
                <span class="timeline-label">Atendida</span>
              </div>
              <div class="timeline-line" :class="{ 'line-active': form.estado === 'cancelada' || form.estado === 'no_asistio' }" />
              <div class="timeline-item" :class="{ 'timeline-active': form.estado === 'cancelada' || form.estado === 'no_asistio' }">
                <div class="timeline-dot" :class="{ 'dot-active': form.estado === 'cancelada' || form.estado === 'no_asistio' }" />
                <span class="timeline-label">{{ form.estado === 'no_asistio' ? 'No Asistió' : 'Cancelada' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Resumen</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Cita</span>
              <span class="summary-value font-mono-data">#{{ citaId }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Paciente</span>
              <span class="summary-value">{{ cita?.paciente_nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">DNI</span>
              <span class="summary-value font-mono-data">{{ cita?.paciente_dni || 'NN' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Fecha</span>
              <span class="summary-value font-mono-data">{{ cita?.fecha ? formatFecha(cita.fecha) : '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Horario</span>
              <span class="summary-value font-mono-data">{{ cita?.hora_inicio || '—' }} - {{ cita?.hora_fin || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Médico</span>
              <span class="summary-value">{{ cita?.medico_nombre || '—' }}</span>
            </div>
          </div>
        </div>

        <!-- Tip Widget -->
        <div class="widget widget-tip">
          <div class="widget-content">
            <div class="tip-content">
              <UIcon name="i-heroicons-light-bulb" class="tip-icon" style="color: var(--amber)" />
              <div>
                <p class="tip-title">Consejo</p>
                <p class="tip-text">
                  Actualiza el estado de la cita según el flujo de atención: 
                  "Separada" → "Confirmada" → "Atendida" o "No Asistió".
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats Widget -->
        <div class="widget widget-stats">
          <div class="widget-header">
            <UIcon name="i-heroicons-chart-bar" class="widget-icon" style="color: var(--purple)" />
            <h4 class="widget-title">Información Adicional</h4>
          </div>
          <div class="widget-content">
            <div class="stat-item">
              <span class="stat-label">Estado</span>
              <span class="stat-number" :style="{ color: getEstadoColor(form.estado) }">
                {{ formatEstado(form.estado) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Fuente Financiamiento</span>
              <span class="stat-number">{{ form.fuente_financiamiento || '—' }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Producto/Plan</span>
              <span class="stat-number">{{ form.producto_plan || '—' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const { api } = useApi()
const { link } = useHospitalNav()
const route = useRoute()

const citaId = route.params.id as string

const cargando = ref(true)
const guardando = ref(false)
const confirmando = ref(false)
const error = ref('')
const exito = ref('')
const cita = ref<any>(null)

const form = reactive({
  observacion: '',
  fuente_financiamiento: '',
  producto_plan: '',
  estado: 'separada',
})

const getEstadoColor = (estado: string) => {
  const map: Record<string, string> = {
    separada: 'var(--amber)',
    confirmada: 'var(--blue)',
    atendida: 'var(--green)',
    cancelada: 'var(--alert)',
    no_asistio: 'var(--ink-soft)',
  }
  return map[estado] || 'var(--ink-soft)'
}

const getEstadoClass = (estado: string) => {
  const map: Record<string, string> = {
    separada: 'estado-separada',
    confirmada: 'estado-confirmada',
    atendida: 'estado-atendida',
    cancelada: 'estado-cancelada',
    no_asistio: 'estado-no-asistio',
  }
  return map[estado] || ''
}

const getEstadoIcon = (estado: string) => {
  const map: Record<string, string> = {
    separada: 'i-heroicons-clock',
    confirmada: 'i-heroicons-check-badge',
    atendida: 'i-heroicons-check-circle',
    cancelada: 'i-heroicons-x-circle',
    no_asistio: 'i-heroicons-user-minus',
  }
  return map[estado] || 'i-heroicons-circle'
}

const formatEstado = (estado: string) => {
  const map: Record<string, string> = {
    separada: 'Separada',
    confirmada: 'Confirmada',
    atendida: 'Atendida',
    cancelada: 'Cancelada',
    no_asistio: 'No Asistió',
  }
  return map[estado] || estado
}

const formatFecha = (fecha: string) => {
  if (!fecha) return '—'
  const d = new Date(fecha)
  return d.toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const getTurnoIcon = (turno: string) => {
  const map: Record<string, string> = {
    'MAÑANA': 'i-heroicons-sun',
    'TARDE': 'i-heroicons-cloud',
    'NOCHE': 'i-heroicons-moon'
  }
  return map[turno] || 'i-heroicons-clock'
}

onMounted(async () => {
  try {
    cita.value = await api(`/app/consulta-externa/citas/${citaId}`)
    form.observacion = cita.value.observacion || ''
    form.fuente_financiamiento = cita.value.fuente_financiamiento || ''
    form.producto_plan = cita.value.producto_plan || ''
    form.estado = cita.value.estado || 'separada'
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar la cita'
  } finally {
    cargando.value = false
  }
})

async function guardar() {
  error.value = ''
  exito.value = ''
  guardando.value = true
  try {
    await api(`/app/consulta-externa/citas/${citaId}`, {
      method: 'PATCH',
      body: {
        observacion: form.observacion || null,
        fuente_financiamiento: form.fuente_financiamiento || null,
        producto_plan: form.producto_plan || null,
        estado: form.estado,
      }
    })
    exito.value = 'Cambios guardados correctamente'
    // Actualizar estado en cita local
    if (cita.value) {
      cita.value.estado = form.estado
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar cambios'
  } finally {
    guardando.value = false
  }
}

async function confirmarCita() {
  error.value = ''
  exito.value = ''
  confirmando.value = true
  try {
    cita.value = await api(`/app/consulta-externa/citas/${citaId}/confirmar`, { method: 'POST' })
    form.estado = cita.value.estado
    exito.value = 'Cita confirmada. Ya aparece en el módulo de Triaje.'
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al confirmar la cita'
  } finally {
    confirmando.value = false
  }
}
</script>

<style scoped>
.cita-detail-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.cita-detail-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.cita-detail-main {
  min-width: 0;
}

.cita-detail-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Header */
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.cita-id {
  font-size: 0.8125rem;
  font-weight: 500;
}

.separator {
  color: var(--line);
}

.estado-display {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
}

.estado-separada {
  background: var(--amber-soft);
  color: var(--amber);
}

.estado-confirmada {
  background: var(--blue-soft);
  color: var(--blue);
}

.estado-atendida {
  background: var(--green-soft);
  color: var(--green);
}

.estado-cancelada {
  background: var(--alert-soft);
  color: var(--alert);
}

.estado-no-asistio {
  background: var(--mist);
  color: var(--ink-soft);
}

.fecha-display {
  font-size: 0.8125rem;
}

/* Loading State */
.loading-state {
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

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Success Banner */
.success-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--green-soft);
  color: var(--green);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
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

/* Form Card */
.form-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 1.5rem;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.card-header-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.card-subtitle {
  font-size: 0.8125rem;
  color: var(--ink-soft);
  margin: 0;
}

/* Section Block */
.section-block {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.section-block:first-of-type {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.section-header-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.section-desc {
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius);
  background: var(--mist);
}

.info-label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft);
}

.info-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

/* Turno Badge */
.turno-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.turno-manana {
  background: var(--amber-soft);
  color: var(--amber);
}

.turno-tarde {
  background: var(--blue-soft);
  color: var(--blue);
}

.turno-noche {
  background: var(--navy-soft);
  color: var(--navy);
}

/* Form */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  margin-bottom: 0.5rem;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: var(--ink-soft);
}

.input-wrapper textarea + .input-icon {
  top: 0.75rem;
  transform: none;
}

.input-clinical {
  width: 100%;
  padding: 0.625rem 0.875rem;
  padding-left: 2.5rem;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.input-clinical:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.field-hint {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  margin-top: 0.25rem;
}

/* Preview Section */
.preview-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.preview-title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft);
  margin: 0 0 0.75rem 0;
}

.preview-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  background: var(--paper);
  flex-wrap: wrap;
}

.preview-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.preview-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 120px;
}

.preview-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.preview-detail {
  display: flex;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.preview-estado {
  font-weight: 500;
}

.preview-horario {
  font-family: monospace;
}

.preview-fuente {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.preview-status {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
  flex-shrink: 0;
}

.preview-separada {
  background: var(--amber-soft);
  color: var(--amber);
}

.preview-confirmada {
  background: var(--blue-soft);
  color: var(--blue);
}

.preview-atendida {
  background: var(--green-soft);
  color: var(--green);
}

.preview-cancelada {
  background: var(--alert-soft);
  color: var(--alert);
}

.preview-no-asistio {
  background: var(--mist);
  color: var(--ink-soft);
}

.preview-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  display: inline-block;
}

.dot-separada {
  background: var(--amber);
}

.dot-confirmada {
  background: var(--blue);
}

.dot-atendida {
  background: var(--green);
}

.dot-cancelada {
  background: var(--alert);
}

.dot-no-asistio {
  background: var(--ink-soft);
}

/* Form Actions */
.form-actions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.action-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  background: var(--teal);
  color: white;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: var(--teal-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ink-soft);
  text-decoration: none;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: var(--mist);
}

/* Empty state */
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

/* Widgets */
.widget {
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  border: 1px solid var(--line);
}

.widget-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--line);
}

.widget-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.widget-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.widget-content {
  padding: 1rem 1.25rem;
}

/* Status Widget */
.status-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.status-icon-large {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.status-info {
  display: flex;
  flex-direction: column;
}

.status-label {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.status-value-large {
  font-size: 1.125rem;
  font-weight: 700;
}

.status-timeline {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.timeline-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--mist);
  border: 2px solid var(--line);
}

.timeline-dot.dot-active {
  background: var(--teal);
  border-color: var(--teal);
}

.timeline-label {
  font-size: 0.625rem;
  color: var(--ink-soft);
  text-align: center;
}

.timeline-line {
  height: 2px;
  flex: 0.5;
  background: var(--line);
  margin-bottom: 1.25rem;
}

.timeline-line.line-active {
  background: var(--teal);
}

/* Summary Widget */
.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0;
  border-bottom: 1px solid var(--line);
}

.summary-item:last-of-type {
  border-bottom: none;
}

.summary-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.summary-value {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  max-width: 60%;
  text-align: right;
  word-break: break-word;
}

.summary-divider {
  height: 1px;
  background: var(--line);
  margin: 0.5rem 0;
}

/* Tip Widget */
.widget-tip {
  background: var(--amber-soft);
  border-color: var(--amber-soft);
}

.tip-content {
  display: flex;
  gap: 0.75rem;
}

.tip-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.tip-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.25rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tip-text {
  font-size: 0.8125rem;
  color: var(--ink);
  margin: 0;
  line-height: 1.5;
}

/* Stats Widget */
.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0;
}

.stat-item + .stat-item {
  border-top: 1px solid var(--line);
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.stat-number {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

/* Responsive */
@media (max-width: 1024px) {
  .cita-detail-grid {
    grid-template-columns: 1fr;
  }

  .cita-detail-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .cita-detail-container {
    padding: 1rem;
  }

  .info-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .cita-detail-sidebar {
    grid-template-columns: 1fr;
  }

  .action-group {
    flex-direction: column;
    width: 100%;
  }

  .action-group > * {
    width: 100%;
    justify-content: center;
  }
}
</style>