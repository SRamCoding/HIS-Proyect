<template>
  <div class="programacion-edit-container">
    <div class="programacion-edit-grid">
      <!-- Main Content -->
      <div class="programacion-edit-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="link('/app/consulta-externa/programacion-medica')" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-calendar-days" class="w-3.5 h-3.5" />
              Programación Médica
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Editar Programación</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" :style="{ background: form.estado === 'activo' ? 'var(--teal-soft)' : 'var(--mist)' }">
              <UIcon
                name="i-heroicons-calendar-days"
                class="w-6 h-6"
                :style="{ color: form.estado === 'activo' ? 'var(--teal)' : 'var(--ink-soft)' }"
              />
            </div>
            <div>
              <h1 class="page-title">{{ programacion.medico_nombre || 'Editar Programación' }}</h1>
              <p class="page-subtitle">
                <span class="especialidad-display">{{ programacion.especialidad_nombre || 'Sin especialidad' }}</span>
                <span class="separator">·</span>
                <span class="estado-display" :class="form.estado === 'activo' ? 'estado-activo' : form.estado === 'cancelado' ? 'estado-cancelado' : 'estado-completado'">
                  {{ form.estado === 'activo' ? 'Activa' : form.estado === 'cancelado' ? 'Cancelada' : 'Completada' }}
                </span>
              </p>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="cargando" class="loading-state">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando información de la programación...</p>
        </div>

        <template v-else>
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
                <h3 class="card-title">Datos de la Programación</h3>
                <p class="card-subtitle">Actualiza la información de la programación médica</p>
              </div>
            </div>

            <div class="info-fields">
              <div class="info-field">
                <span class="info-field-label">Especialidad</span>
                <span class="info-field-value">{{ programacion.especialidad_nombre || '—' }}</span>
              </div>
              <div class="info-field">
                <span class="info-field-label">Médico</span>
                <span class="info-field-value">{{ programacion.medico_nombre || '—' }}</span>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Fecha <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-calendar" class="input-icon" />
                  <input
                    v-model="form.fecha"
                    type="date"
                    class="input-clinical"
                    :class="{ 'input-error': errors.fecha }"
                    @change="errors.fecha = ''"
                  />
                </div>
                <span v-if="errors.fecha" class="error-message">{{ errors.fecha }}</span>
                <p class="field-hint">Fecha de la programación</p>
              </div>

              <div class="form-group">
                <label class="form-label">Turno <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-clock" class="input-icon" />
                  <select v-model="form.turno" class="input-clinical" :class="{ 'input-error': errors.turno }" @change="errors.turno = ''">
                    <option value="MAÑANA">☀️ Mañana</option>
                    <option value="TARDE">⛅ Tarde</option>
                    <option value="NOCHE">🌙 Noche</option>
                  </select>
                </div>
                <span v-if="errors.turno" class="error-message">{{ errors.turno }}</span>
                <p class="field-hint">Turno de la programación</p>
              </div>

              <div class="form-group">
                <label class="form-label">Hora de Inicio <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-clock" class="input-icon" />
                  <input
                    v-model="form.hora_inicio"
                    type="time"
                    class="input-clinical"
                    :class="{ 'input-error': errors.hora_inicio }"
                    @change="errors.hora_inicio = ''"
                  />
                </div>
                <span v-if="errors.hora_inicio" class="error-message">{{ errors.hora_inicio }}</span>
                <p class="field-hint">Hora de inicio de la atención</p>
              </div>

              <div class="form-group">
                <label class="form-label">Hora de Fin <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-clock" class="input-icon" />
                  <input
                    v-model="form.hora_fin"
                    type="time"
                    class="input-clinical"
                    :class="{ 'input-error': errors.hora_fin }"
                    @change="errors.hora_fin = ''"
                  />
                </div>
                <span v-if="errors.hora_fin" class="error-message">{{ errors.hora_fin }}</span>
                <p class="field-hint">Hora de fin de la atención</p>
              </div>

              <div class="form-group">
                <label class="form-label">Tiempo Promedio de Atención (min)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-chart-bar" class="input-icon" />
                  <input
                    v-model.number="form.tiempo_promedio_atencion"
                    type="number"
                    min="1"
                    class="input-clinical font-mono-data"
                    placeholder="15"
                  />
                </div>
                <p class="field-hint">Duración estimada por paciente</p>
              </div>

              <div class="form-group">
                <label class="form-label">Estado</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-flag" class="input-icon" />
                  <select v-model="form.estado" class="input-clinical">
                    <option value="activo">Activo</option>
                    <option value="cancelado">Cancelado</option>
                    <option value="completado">Completado</option>
                  </select>
                </div>
                <p class="field-hint">Estado actual de la programación</p>
              </div>

              <div class="form-group">
                <div class="checkbox-wrapper">
                  <input type="checkbox" v-model="form.mostrar_en_consultorio" id="mostrarConsultorio" class="checkbox-custom" />
                  <label for="mostrarConsultorio" class="checkbox-label">Mostrar en Consultorio</label>
                </div>
                <p class="field-hint">Visible en el módulo de consultorio</p>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Descripción</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea
                    v-model="form.descripcion"
                    class="input-clinical"
                    rows="3"
                    placeholder="Descripción de la programación..."
                  />
                </div>
              </div>
            </div>

            <!-- Preview Section -->
            <div class="preview-section">
              <h4 class="preview-title">Vista Previa</h4>
              <div class="preview-card">
                <div class="preview-icon" :style="{ background: form.estado === 'activo' ? 'var(--teal-soft)' : 'var(--mist)' }">
                  <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" :style="{ color: form.estado === 'activo' ? 'var(--teal)' : 'var(--ink-soft)' }" />
                </div>
                <div class="preview-info">
                  <span class="preview-title-text">{{ programacion.medico_nombre || 'Médico' }}</span>
                  <span class="preview-detail">
                    <span class="preview-especialidad">{{ programacion.especialidad_nombre || 'Especialidad' }}</span>
                    <span class="preview-date">{{ form.fecha ? formatFecha(form.fecha) : 'Sin fecha' }}</span>
                  </span>
                  <span class="preview-schedule">
                    <span class="preview-turno">{{ form.turno || 'Sin turno' }}</span>
                    <span class="preview-hours">{{ form.hora_inicio || '--:--' }} - {{ form.hora_fin || '--:--' }}</span>
                  </span>
                </div>
                <span class="preview-status" :class="form.estado === 'activo' ? 'preview-active' : form.estado === 'cancelado' ? 'preview-cancelado' : 'preview-completado'">
                  <span class="preview-dot" :class="form.estado === 'activo' ? 'dot-active' : form.estado === 'cancelado' ? 'dot-cancelado' : 'dot-completado'" />
                  {{ form.estado === 'activo' ? 'Activa' : form.estado === 'cancelado' ? 'Cancelada' : 'Completada' }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="form-actions">
              <div class="action-group">
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
                  :to="link('/app/consulta-externa/programacion-medica')"
                  class="btn-cancel"
                >
                  Cancelar
                </NuxtLink>
              </div>
            </div>
          </section>
        </template>
      </div>

      <!-- Sidebar Widgets -->
      <div class="programacion-edit-sidebar">
        <!-- Info Widget -->
        <div class="widget widget-info">
          <div class="widget-header">
            <UIcon name="i-heroicons-information-circle" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Información</h4>
          </div>
          <div class="widget-content">
            <ul class="info-list">
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los campos con * son obligatorios</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Especialidad y médico no se pueden modificar</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El estado permite controlar la programación</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Las programaciones canceladas no aparecen en consultorio</span>
              </li>
            </ul>
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
              <span class="summary-label">Especialidad</span>
              <span class="summary-value">{{ programacion.especialidad_nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Médico</span>
              <span class="summary-value">{{ programacion.medico_nombre || '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Fecha</span>
              <span class="summary-value font-mono-data">{{ form.fecha || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Turno</span>
              <span class="summary-value">{{ form.turno || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Horario</span>
              <span class="summary-value font-mono-data">{{ form.hora_inicio || '--:--' }} - {{ form.hora_fin || '--:--' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Estado</span>
              <span class="summary-value">
                <span class="status-badge-mini" :class="form.estado === 'activo' ? 'status-active-mini' : form.estado === 'cancelado' ? 'status-cancelado-mini' : 'status-completado-mini'">
                  {{ form.estado === 'activo' ? 'Activa' : form.estado === 'cancelado' ? 'Cancelada' : 'Completada' }}
                </span>
              </span>
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
                  Cambia el estado a "Cancelado" si la programación no se llevará a cabo, 
                  o a "Completado" una vez finalizada la atención.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats Widget -->
        <div class="widget widget-stats">
          <div class="widget-header">
            <UIcon name="i-heroicons-chart-bar" class="widget-icon" style="color: var(--purple)" />
            <h4 class="widget-title">Estado</h4>
          </div>
          <div class="widget-content">
            <div class="stat-item">
              <span class="stat-label">Estado actual</span>
              <span class="stat-number" :style="{ color: form.estado === 'activo' ? 'var(--green)' : form.estado === 'cancelado' ? 'var(--alert)' : 'var(--teal)' }">
                {{ form.estado === 'activo' ? 'Activa' : form.estado === 'cancelado' ? 'Cancelada' : 'Completada' }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Turno</span>
              <span class="stat-number">{{ form.turno || '—' }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Campos completos</span>
              <span class="stat-number">{{ filledFields }}/{{ totalFields }}</span>
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

const progId = route.params.id as string

const cargando = ref(true)
const guardando = ref(false)
const error = ref('')
const exito = ref('')
const programacion = ref<any>({})

const errors = reactive({
  fecha: '',
  turno: '',
  hora_inicio: '',
  hora_fin: '',
})

const form = reactive({
  fecha: '',
  turno: '',
  hora_inicio: '',
  hora_fin: '',
  tiempo_promedio_atencion: 15,
  mostrar_en_consultorio: false,
  descripcion: '',
  estado: 'activo',
})

const filledFields = computed(() => {
  let count = 0
  if (form.fecha) count++
  if (form.turno) count++
  if (form.hora_inicio) count++
  if (form.hora_fin) count++
  if (form.tiempo_promedio_atencion) count++
  if (form.descripcion) count++
  return count
})

const totalFields = 6

const formatFecha = (fecha: string) => {
  if (!fecha) return '—'
  const d = new Date(fecha)
  return d.toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

onMounted(async () => {
  try {
    const data = await api(`/app/consulta-externa/programacion-medica/${progId}`)
    programacion.value = data
    form.fecha = data.fecha
    form.turno = data.turno
    form.hora_inicio = data.hora_inicio
    form.hora_fin = data.hora_fin
    form.tiempo_promedio_atencion = data.tiempo_promedio_atencion || 15
    form.mostrar_en_consultorio = data.mostrar_en_consultorio
    form.descripcion = data.descripcion || ''
    form.estado = data.estado || 'activo'
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar la programación'
  } finally {
    cargando.value = false
  }
})

function validar(): boolean {
  let valid = true
  if (!form.fecha) {
    errors.fecha = 'La fecha es requerida'
    valid = false
  }
  if (!form.turno) {
    errors.turno = 'El turno es requerido'
    valid = false
  }
  if (!form.hora_inicio) {
    errors.hora_inicio = 'La hora de inicio es requerida'
    valid = false
  }
  if (!form.hora_fin) {
    errors.hora_fin = 'La hora de fin es requerida'
    valid = false
  }
  if (form.hora_inicio && form.hora_fin && form.hora_inicio >= form.hora_fin) {
    errors.hora_fin = 'La hora de fin debe ser posterior a la de inicio'
    valid = false
  }
  return valid
}

async function guardar() {
  if (!validar()) return

  error.value = ''
  exito.value = ''
  guardando.value = true
  try {
    await api(`/app/consulta-externa/programacion-medica/${progId}`, {
      method: 'PATCH',
      body: {
        fecha: form.fecha,
        turno: form.turno,
        hora_inicio: form.hora_inicio,
        hora_fin: form.hora_fin,
        tiempo_promedio_atencion: form.tiempo_promedio_atencion || 15,
        mostrar_en_consultorio: form.mostrar_en_consultorio,
        descripcion: form.descripcion || null,
        estado: form.estado,
      }
    })
    exito.value = ' Cambios guardados correctamente'
    setTimeout(() => {
      navigateTo(link('/app/consulta-externa/programacion-medica'))
    }, 1500)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar cambios'
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
.programacion-edit-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.programacion-edit-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.programacion-edit-main {
  min-width: 0;
}

.programacion-edit-sidebar {
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

.especialidad-display {
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

.estado-activo {
  background: var(--green-soft);
  color: var(--green);
}

.estado-cancelado {
  background: var(--alert-soft);
  color: var(--alert);
}

.estado-completado {
  background: var(--teal-soft);
  color: var(--teal);
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

/* Info Fields */
.info-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  padding: 1rem;
  border-radius: var(--radius);
  background: var(--mist);
  margin-bottom: 1.5rem;
}

.info-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-field-label {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft);
}

.info-field-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
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

.required {
  color: var(--alert);
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

.input-clinical.input-error {
  border-color: var(--alert);
}

.input-clinical.input-error:focus {
  box-shadow: 0 0 0 3px var(--alert-soft);
}

.input-clinical[type="date"],
.input-clinical[type="time"] {
  color-scheme: light;
}

.error-message {
  display: block;
  font-size: 0.75rem;
  color: var(--alert);
  margin-top: 0.25rem;
}

.field-hint {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  margin-top: 0.25rem;
}

/* Checkbox */
.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0;
}

.checkbox-custom {
  accent-color: var(--teal);
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.checkbox-label {
  font-size: 0.8125rem;
  color: var(--ink);
  cursor: pointer;
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

.preview-title-text {
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

.preview-especialidad {
  font-weight: 500;
  color: var(--teal);
}

.preview-date {
  color: var(--ink-soft);
}

.preview-schedule {
  display: flex;
  gap: 0.75rem;
  font-size: 0.75rem;
}

.preview-turno {
  font-weight: 500;
  color: var(--amber);
}

.preview-hours {
  font-family: monospace;
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

.preview-active {
  background: var(--green-soft);
  color: var(--green);
}

.preview-cancelado {
  background: var(--alert-soft);
  color: var(--alert);
}

.preview-completado {
  background: var(--teal-soft);
  color: var(--teal);
}

.preview-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  display: inline-block;
}

.dot-active {
  background: var(--green);
}

.dot-cancelado {
  background: var(--alert);
}

.dot-completado {
  background: var(--teal);
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

/* Info Widget */
.info-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  padding: 0.375rem 0;
  font-size: 0.8125rem;
  color: var(--ink);
}

.info-item-icon {
  width: 1rem;
  height: 1rem;
  margin-top: 0.125rem;
  flex-shrink: 0;
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

/* Status Badge Mini */
.status-badge-mini {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  font-size: 0.6875rem;
  font-weight: 500;
}

.status-active-mini {
  background: var(--green-soft);
  color: var(--green);
}

.status-cancelado-mini {
  background: var(--alert-soft);
  color: var(--alert);
}

.status-completado-mini {
  background: var(--teal-soft);
  color: var(--teal);
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
  font-size: 1rem;
  font-weight: 700;
  color: var(--ink);
}

/* Responsive */
@media (max-width: 1024px) {
  .programacion-edit-grid {
    grid-template-columns: 1fr;
  }

  .programacion-edit-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .programacion-edit-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .info-fields {
    grid-template-columns: 1fr;
  }

  .programacion-edit-sidebar {
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

  .page-subtitle {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .preview-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .preview-info {
    min-width: auto;
    width: 100%;
  }

  .preview-detail {
    flex-wrap: wrap;
  }

  .preview-schedule {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .preview-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .summary-value {
    max-width: 100%;
    text-align: left;
  }

  .checkbox-wrapper {
    flex-wrap: wrap;
  }
}
</style>