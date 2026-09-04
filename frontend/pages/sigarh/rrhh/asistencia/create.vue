<template>
  <div class="asistencia-create-container">
    <div class="asistencia-create-grid">
      <!-- Main Content -->
      <div class="asistencia-create-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/rrhh/asistencia?tenant=${tenantId}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-clipboard-document-check" class="w-3.5 h-3.5" />
              Registro de Asistencia
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Registrar</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--green-soft)">
              <UIcon name="i-heroicons-check-circle" class="w-6 h-6" style="color: var(--green)" />
            </div>
            <div>
              <h1 class="page-title">Registrar Asistencia</h1>
              <p class="page-subtitle">Registra la asistencia diaria de los empleados</p>
            </div>
          </div>
        </div>

        <!-- Form Card -->
        <section class="form-card">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--green-soft)">
              <UIcon name="i-heroicons-clipboard-document-check" class="w-4 h-4" style="color: var(--green)" />
            </div>
            <div>
              <h3 class="card-title">Registro de Asistencia</h3>
              <p class="card-subtitle">Ingresa los datos de asistencia del empleado</p>
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group full-width">
              <label class="form-label">Empleado <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-user" class="input-icon" />
                <select v-model="form.empleado_id" class="input-clinical" :class="{ 'input-error': errors.empleado_id }" @change="errors.empleado_id = ''">
                  <option value="">Seleccione un empleado</option>
                  <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombre_completo }}</option>
                </select>
              </div>
              <span v-if="errors.empleado_id" class="error-message">{{ errors.empleado_id }}</span>
              <p class="field-hint">Selecciona el empleado al que se registrará la asistencia</p>
            </div>

            <div class="form-group">
              <label class="form-label">Fecha <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-calendar-days" class="input-icon" />
                <input 
                  v-model="form.fecha" 
                  type="date" 
                  class="input-clinical"
                  :class="{ 'input-error': errors.fecha }"
                  @change="errors.fecha = ''"
                />
              </div>
              <span v-if="errors.fecha" class="error-message">{{ errors.fecha }}</span>
              <p class="field-hint">Fecha del registro de asistencia</p>
            </div>

            <div class="form-group">
              <label class="form-label">Estado</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-flag" class="input-icon" />
                <select v-model="form.estado" class="input-clinical">
                  <option value="presente">Presente</option>
                  <option value="ausente">Ausente</option>
                  <option value="tardanza">Tardanza</option>
                  <option value="justificado">Justificado</option>
                </select>
              </div>
              <p class="field-hint">Estado de asistencia del empleado</p>
            </div>

            <div class="form-group">
              <label class="form-label">Hora de Entrada</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-clock" class="input-icon" />
                <input v-model="form.hora_entrada" type="time" class="input-clinical" />
              </div>
              <p class="field-hint">Hora de ingreso del empleado</p>
            </div>

            <div class="form-group">
              <label class="form-label">Hora de Salida</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-clock" class="input-icon" />
                <input v-model="form.hora_salida" type="time" class="input-clinical" />
              </div>
              <p class="field-hint">Hora de salida del empleado</p>
            </div>

            <div class="form-group full-width">
              <label class="form-label">Observación</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                <textarea 
                  v-model="form.observacion" 
                  class="input-clinical" 
                  rows="2" 
                  placeholder="Observaciones adicionales sobre la asistencia..."
                />
              </div>
            </div>
          </div>

          <!-- Preview Section -->
          <div v-if="form.empleado_id || form.fecha" class="preview-section">
            <h4 class="preview-title">Vista Previa</h4>
            <div class="preview-card">
              <div class="preview-icon" :style="{ background: getEstadoColor(form.estado) + '22' }">
                <UIcon :name="getEstadoIcon(form.estado)" class="w-5 h-5" :style="{ color: getEstadoColor(form.estado) }" />
              </div>
              <div class="preview-info">
                <span class="preview-name">{{ empleadoSeleccionado?.nombre_completo || 'Empleado no seleccionado' }}</span>
                <span class="preview-date">{{ form.fecha ? formatDate(form.fecha) : 'Fecha no seleccionada' }}</span>
              </div>
              <span class="preview-status" :style="{ background: getEstadoColor(form.estado) + '22', color: getEstadoColor(form.estado) }">
                <UIcon :name="getEstadoIcon(form.estado)" class="w-3.5 h-3.5" />
                {{ formatEstado(form.estado) }}
              </span>
              <span v-if="form.hora_entrada" class="preview-time">
                <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
                {{ form.hora_entrada }}{{ form.hora_salida ? ` - ${form.hora_salida}` : '' }}
              </span>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="error-banner">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ error }}
          </div>

          <!-- Actions -->
          <div class="form-actions">
            <div class="action-group">
              <button 
                class="btn-primary" 
                :disabled="saving" 
                @click="handleCreate(false)"
              >
                <UIcon v-if="saving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                {{ saving ? 'Registrando...' : 'Registrar Asistencia' }}
              </button>
              <button 
                class="btn-outline" 
                :disabled="saving" 
                @click="handleCreate(true)"
              >
                <UIcon name="i-heroicons-plus" class="w-4 h-4" />
                Registrar otro
              </button>
              <NuxtLink 
                :to="`/sigarh/rrhh/asistencia?tenant=${tenantId}`"
                class="btn-cancel"
              >
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Widgets -->
      <div class="asistencia-create-sidebar">
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
                <span>Registra la asistencia diaria de los empleados</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los estados disponibles son: Presente, Ausente, Tardanza, Justificado</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Las horas de entrada y salida son opcionales</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Las observaciones ayudan a documentar incidencias</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--green)" />
            <h4 class="widget-title">Resumen</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Empleado</span>
              <span class="summary-value">{{ empleadoSeleccionado?.nombre_completo || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Fecha</span>
              <span class="summary-value font-mono-data">{{ form.fecha ? formatDate(form.fecha) : '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Estado</span>
              <span class="summary-value">
                <span class="status-badge-mini" :style="{ background: getEstadoColor(form.estado) + '22', color: getEstadoColor(form.estado) }">
                  <UIcon :name="getEstadoIcon(form.estado)" class="w-3 h-3" />
                  {{ formatEstado(form.estado) }}
                </span>
              </span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Horario</span>
              <span class="summary-value font-mono-data">{{ form.hora_entrada || '—' }}{{ form.hora_salida ? ` - ${form.hora_salida}` : '' }}</span>
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
                  Registra la asistencia diariamente para mantener un control preciso 
                  de la puntualidad y presencia del personal.
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
              <span class="stat-number">{{ filledFields }}/4</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Estado actual</span>
              <span class="stat-number" :style="{ color: getEstadoColor(form.estado) }">
                {{ formatEstado(form.estado) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Horario</span>
              <span class="stat-number" :style="{ color: form.hora_entrada ? 'var(--teal)' : 'var(--ink-soft)' }">
                {{ form.hora_entrada ? '✓ Registrado' : '—' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const empleados = ref<any[]>([])

const errors = reactive({
  empleado_id: '',
  fecha: ''
})

const form = reactive({
  empleado_id: '',
  fecha: new Date().toISOString().split('T')[0],
  hora_entrada: '',
  hora_salida: '',
  estado: 'presente',
  observacion: '',
})

const empleadoSeleccionado = computed(() => 
  empleados.value.find(e => e.id === form.empleado_id)
)

const filledFields = computed(() => {
  let count = 0
  if (form.empleado_id) count++
  if (form.fecha) count++
  if (form.estado) count++
  if (form.hora_entrada || form.hora_salida) count++
  return count
})

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

const getEstadoIcon = (estado: string) => {
  const map: Record<string, string> = {
    presente: 'i-heroicons-check-circle',
    ausente: 'i-heroicons-x-circle',
    tardanza: 'i-heroicons-clock',
    justificado: 'i-heroicons-document-text'
  }
  return map[estado] || 'i-heroicons-circle'
}

const getEstadoColor = (estado: string) => {
  const map: Record<string, string> = {
    presente: 'var(--green)',
    ausente: 'var(--alert)',
    tardanza: 'var(--amber)',
    justificado: 'var(--teal)'
  }
  return map[estado] || 'var(--ink-soft)'
}

const validateForm = (): boolean => {
  let valid = true
  if (!form.empleado_id) {
    errors.empleado_id = 'El empleado es requerido'
    valid = false
  }
  if (!form.fecha) {
    errors.fecha = 'La fecha es requerida'
    valid = false
  }
  return valid
}

const handleCreate = async (createAnother: boolean) => {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/rrhh/asistencia', {
      method: 'POST',
      body: {
        empleado_id: form.empleado_id,
        fecha: form.fecha,
        hora_entrada: form.hora_entrada || null,
        hora_salida: form.hora_salida || null,
        estado: form.estado,
        observacion: form.observacion || null,
      }
    })

    if (createAnother) {
      Object.assign(form, { 
        empleado_id: '', 
        hora_entrada: '', 
        hora_salida: '', 
        estado: 'presente', 
        observacion: '' 
      })
      errors.empleado_id = ''
      errors.fecha = ''
    } else {
      router.push(`/sigarh/rrhh/asistencia?tenant=${tenantId.value}`)
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo registrar la asistencia'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    empleados.value = await api<any[]>('/sigarh/rrhh/empleados')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar empleados'
  }
})
</script>

<style scoped>
.asistencia-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.asistencia-create-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.asistencia-create-main {
  min-width: 0;
}

.asistencia-create-sidebar {
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

.input-clinical::placeholder {
  color: var(--ink-soft);
  opacity: 0.6;
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

.preview-date {
  font-size: 0.75rem;
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

.preview-time {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
  background: var(--mist);
  color: var(--ink-soft);
  flex-shrink: 0;
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
  margin-top: 1.5rem;
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

.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid var(--teal);
  background: transparent;
  color: var(--teal);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-outline:hover:not(:disabled) {
  background: var(--teal-soft);
}

.btn-outline:disabled {
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

/* Status Badge Mini */
.status-badge-mini {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  font-size: 0.6875rem;
  font-weight: 500;
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
  .asistencia-create-grid {
    grid-template-columns: 1fr;
  }

  .asistencia-create-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .asistencia-create-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .asistencia-create-sidebar {
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

  .preview-status,
  .preview-time {
    align-self: flex-start;
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
}
</style>