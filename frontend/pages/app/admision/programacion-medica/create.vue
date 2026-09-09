<template>
  <div class="programacion-create-container">
    <div class="programacion-create-grid">
      <!-- Main Content -->
      <div class="programacion-create-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="link('/app/admision/programacion-medica')" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-calendar-days" class="w-3.5 h-3.5" />
              Programación Médica
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Nueva Programación</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--teal)" />
            </div>
            <div>
              <h1 class="page-title">Agregar Programación</h1>
              <p class="page-subtitle">Registra una nueva programación médica</p>
            </div>
          </div>
        </div>

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
              <p class="card-subtitle">Ingresa la información de la programación médica</p>
            </div>
          </div>

          <div class="form-grid">
            <!-- Servicio Field - NUEVO -->
            <div class="form-group">
              <label class="form-label">Servicio <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-building-office" class="input-icon" />
                <select v-model="form.servicio_id" class="input-clinical" :class="{ 'input-error': errors.servicio_id }">
                  <option value="">Seleccionar...</option>
                  <option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                </select>
              </div>
              <span v-if="errors.servicio_id" class="error-message">{{ errors.servicio_id }}</span>
              <p class="field-hint">Servicio al que pertenece la programación</p>
            </div>

            <div class="form-group">
              <label class="form-label">Especialidad <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-star" class="input-icon" />
                <select v-model="form.especialidad_id" class="input-clinical" :class="{ 'input-error': errors.especialidad_id }" @change="onEspecialidadChange">
                  <option value="">Seleccionar...</option>
                  <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
                </select>
              </div>
              <span v-if="errors.especialidad_id" class="error-message">{{ errors.especialidad_id }}</span>
              <p class="field-hint">Especialidad médica de la programación</p>
            </div>

            <div class="form-group">
              <label class="form-label">Médico <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-user" class="input-icon" />
                <select v-model="form.medico_id" class="input-clinical" :class="{ 'input-error': errors.medico_id }" :disabled="!medicos.length">
                  <option value="">{{ form.especialidad_id ? 'Seleccionar...' : 'Selecciona una especialidad primero' }}</option>
                  <option v-for="m in medicos" :key="m.id" :value="m.id">{{ m.nombre_completo }}</option>
                </select>
              </div>
              <span v-if="errors.medico_id" class="error-message">{{ errors.medico_id }}</span>
              <p v-if="form.especialidad_id && !medicos.length && !cargandoMedicos" class="field-hint-warning">
                <UIcon name="i-heroicons-exclamation-triangle" class="w-3.5 h-3.5" />
                No hay médicos con esta especialidad asignada en SIGARH.
              </p>
              <p v-else class="field-hint">Médico asignado a la programación</p>
            </div>

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
                  <option value="">Seleccionar...</option>
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
          <div v-if="form.servicio_id || form.especialidad_id || form.medico_id" class="preview-section">
            <h4 class="preview-title">Vista Previa</h4>
            <div class="preview-card">
              <div class="preview-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--teal)" />
              </div>
              <div class="preview-info">
                <span class="preview-title-text">{{ servicioSeleccionado?.nombre || 'Servicio' }}</span>
                <span class="preview-detail">
                  <span class="preview-especialidad">{{ especialidadSeleccionada?.nombre || 'Especialidad' }}</span>
                  <span class="preview-medico">{{ medicoSeleccionado?.nombre_completo || 'Médico no seleccionado' }}</span>
                  <span class="preview-date">{{ form.fecha ? formatFecha(form.fecha) : 'Sin fecha' }}</span>
                </span>
                <span class="preview-schedule">
                  <span class="preview-turno">{{ form.turno || 'Sin turno' }}</span>
                  <span class="preview-hours">{{ form.hora_inicio || '--:--' }} - {{ form.hora_fin || '--:--' }}</span>
                </span>
              </div>
              <span class="preview-status preview-active">
                <span class="preview-dot dot-active" />
                Nueva programación
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
                {{ guardando ? 'Guardando...' : 'Guardar Programación' }}
              </button>
              <NuxtLink
                :to="link('/app/admision/programacion-medica')"
                class="btn-cancel"
              >
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Widgets -->
      <div class="programacion-create-sidebar">
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
                <span>El servicio y la especialidad determinan los médicos disponibles</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El tiempo de atención se usa para calcular citas</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Las programaciones activas aparecen en consultorio</span>
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
              <span class="summary-label">Servicio</span>
              <span class="summary-value">{{ servicioSeleccionado?.nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Especialidad</span>
              <span class="summary-value">{{ especialidadSeleccionada?.nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Médico</span>
              <span class="summary-value">{{ medicoSeleccionado?.nombre_completo || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Fecha</span>
              <span class="summary-value font-mono-data">{{ form.fecha || '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Turno</span>
              <span class="summary-value">{{ form.turno || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Horario</span>
              <span class="summary-value font-mono-data">{{ form.hora_inicio || '--:--' }} - {{ form.hora_fin || '--:--' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Tiempo atención</span>
              <span class="summary-value">{{ form.tiempo_promedio_atencion || 0 }} min</span>
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
                  Selecciona primero el servicio y la especialidad para ver los médicos disponibles. 
                  El tiempo de atención ayuda a gestionar la agenda de citas.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats Widget -->
        <div class="widget widget-stats">
          <div class="widget-header">
            <UIcon name="i-heroicons-chart-bar" class="widget-icon" style="color: var(--purple)" />
            <h4 class="widget-title">Estado del Formulario</h4>
          </div>
          <div class="widget-content">
            <div class="stat-item">
              <span class="stat-label">Campos completos</span>
              <span class="stat-number">{{ filledFields }}/{{ totalFields }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Turno</span>
              <span class="stat-number" :style="{ color: form.turno ? 'var(--teal)' : 'var(--ink-soft)' }">
                {{ form.turno || '—' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth', 'programacion-sigarh'] })

const { api } = useApi()
const { link } = useHospitalNav()

const servicios = ref<any[]>([])
const especialidades = ref<any[]>([])
const medicos = ref<any[]>([])
const cargandoMedicos = ref(false)
const guardando = ref(false)
const error = ref('')
const exito = ref('')

const errors = reactive({
  servicio_id: '',
  especialidad_id: '',
  medico_id: '',
  fecha: '',
  turno: '',
  hora_inicio: '',
  hora_fin: '',
})

const form = reactive({
  servicio_id: '',
  especialidad_id: '',
  medico_id: '',
  fecha: '',
  turno: '',
  hora_inicio: '',
  hora_fin: '',
  tiempo_promedio_atencion: 15,
  mostrar_en_consultorio: false,
  descripcion: '',
})

const servicioSeleccionado = computed(() =>
  servicios.value.find(s => s.id === form.servicio_id)
)

const especialidadSeleccionada = computed(() =>
  especialidades.value.find(e => e.id === form.especialidad_id)
)

const medicoSeleccionado = computed(() =>
  medicos.value.find(m => m.id === form.medico_id)
)

const filledFields = computed(() => {
  let count = 0
  if (form.servicio_id) count++
  if (form.especialidad_id) count++
  if (form.medico_id) count++
  if (form.fecha) count++
  if (form.turno) count++
  if (form.hora_inicio) count++
  if (form.hora_fin) count++
  if (form.tiempo_promedio_atencion) count++
  if (form.descripcion) count++
  return count
})

const totalFields = 9

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
    servicios.value = await api('/app/consulta-externa/programacion-medica/servicios')
    especialidades.value = await api('/app/consulta-externa/programacion-medica/especialidades')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar catálogos'
  }
})

async function onEspecialidadChange() {
  form.medico_id = ''
  medicos.value = []
  errors.medico_id = ''
  if (!form.especialidad_id) return
  cargandoMedicos.value = true
  try {
    medicos.value = await api(`/app/consulta-externa/programacion-medica/medicos/${form.especialidad_id}`)
    if (!medicos.value.length) {
      error.value = 'No hay médicos disponibles para esta especialidad'
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar médicos'
  } finally {
    cargandoMedicos.value = false
  }
}

function validar(): boolean {
  let valid = true

  if (!form.servicio_id) {
    errors.servicio_id = 'El servicio es requerido'
    valid = false
  } else {
    errors.servicio_id = ''
  }

  if (!form.especialidad_id) {
    errors.especialidad_id = 'La especialidad es requerida'
    valid = false
  } else {
    errors.especialidad_id = ''
  }

  if (!form.medico_id) {
    errors.medico_id = 'El médico es requerido'
    valid = false
  } else {
    errors.medico_id = ''
  }

  if (!form.fecha) {
    errors.fecha = 'La fecha es requerida'
    valid = false
  } else {
    errors.fecha = ''
  }

  if (!form.turno) {
    errors.turno = 'El turno es requerido'
    valid = false
  } else {
    errors.turno = ''
  }

  if (!form.hora_inicio) {
    errors.hora_inicio = 'La hora de inicio es requerida'
    valid = false
  } else {
    errors.hora_inicio = ''
  }

  if (!form.hora_fin) {
    errors.hora_fin = 'La hora de fin es requerida'
    valid = false
  } else {
    errors.hora_fin = ''
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
    await api('/app/consulta-externa/programacion-medica', {
      method: 'POST',
      body: {
        ...form,
        tiempo_promedio_atencion: form.tiempo_promedio_atencion || 15,
      }
    })
    exito.value = 'Programación registrada correctamente'
    setTimeout(() => navigateTo(link('/app/admision/programacion-medica')), 1500)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar la programación'
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
.programacion-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.programacion-create-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.programacion-create-main {
  min-width: 0;
}

.programacion-create-sidebar {
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

.input-clinical:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.field-hint-warning {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--amber);
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
  flex-wrap: wrap;
}

.preview-especialidad {
  font-weight: 500;
  color: var(--teal);
}

.preview-medico {
  font-weight: 500;
  color: var(--teal-dark);
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

.preview-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  display: inline-block;
}

.dot-active {
  background: var(--green);
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
  .programacion-create-grid {
    grid-template-columns: 1fr;
  }

  .programacion-create-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .programacion-create-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .programacion-create-sidebar {
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
