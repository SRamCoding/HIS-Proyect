<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Tramitar Cambio de Turno' })

const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string

const form = reactive({
  solicitante_id: '',
  aceptante_id: '',
  fecha_original: '',
  fecha_reemplazo: '',
  modalidad_solicitante: 'MAÑANA',
  modalidad_aceptante: 'MAÑANA',
  estado: 'pendiente',
})

const empleados = ref<any[]>([])
const saving = ref(false)
const error = ref('')
const errors = reactive({
  solicitante_id: '',
  aceptante_id: '',
  fecha_original: '',
  fecha_reemplazo: '',
})

const empleadoSeleccionado = computed(() => 
  empleados.value.find(e => e.id === form.solicitante_id)
)

const empleadoAceptante = computed(() => 
  empleados.value.find(e => e.id === form.aceptante_id)
)

const filledFields = computed(() => {
  let count = 0
  if (form.solicitante_id) count++
  if (form.aceptante_id) count++
  if (form.fecha_original) count++
  if (form.fecha_reemplazo) count++
  return count
})

const modalidades = ['MAÑANA', 'TARDE', 'NOCHE', 'GUARDIA']

const formatDate = (date: string) => {
  if (!date) return '—'
  const d = new Date(date)
  return d.toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const getEstadoColor = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'var(--amber)',
    aprobado: 'var(--green)',
    rechazado: 'var(--alert)'
  }
  return map[estado] || 'var(--ink-soft)'
}

const getEstadoBgColor = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'var(--amber-soft)',
    aprobado: 'var(--green-soft)',
    rechazado: 'var(--alert-soft)'
  }
  return map[estado] || 'var(--mist)'
}

const getEstadoIcon = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'i-heroicons-clock',
    aprobado: 'i-heroicons-check-circle',
    rechazado: 'i-heroicons-x-circle'
  }
  return map[estado] || 'i-heroicons-circle'
}

const formatEstado = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'Pendiente',
    aprobado: 'Aprobado',
    rechazado: 'Rechazado'
  }
  return map[estado] || estado
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

const validateForm = (): boolean => {
  let valid = true
  if (!form.solicitante_id) {
    errors.solicitante_id = 'El empleado solicitante es requerido'
    valid = false
  }
  if (!form.aceptante_id) {
    errors.aceptante_id = 'El empleado aceptante es requerido'
    valid = false
  }
  if (form.solicitante_id && form.solicitante_id === form.aceptante_id) {
    errors.aceptante_id = 'El aceptante debe ser diferente al solicitante'
    valid = false
  }
  if (!form.fecha_original) {
    errors.fecha_original = 'La fecha original es requerida'
    valid = false
  }
  if (!form.fecha_reemplazo) {
    errors.fecha_reemplazo = 'La fecha de reemplazo es requerida'
    valid = false
  }
  return valid
}

async function guardar() {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    await $api('/sigarh/movimientos/cambio-turno', {
      method: 'POST',
      tenant,
      body: form
    })
    router.push(`/sigarh/movimientos/cambio-turno/estado?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    empleados.value = await $api('/sigarh/rrhh/empleados', { tenant })
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar empleados'
  }
})
</script>

<template>
  <div class="cambio-turno-tramitar-container">
    <div class="cambio-turno-tramitar-grid">
      <!-- Main Content -->
      <div class="cambio-turno-tramitar-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/movimientos/cambio-turno/estado?tenant=${tenant}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-arrows-right-left" class="w-3.5 h-3.5" />
              Cambio de Turno
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Tramitar</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--navy-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--navy)" />
            </div>
            <div>
              <h1 class="page-title">Tramitar Cambio de Turno</h1>
              <p class="page-subtitle">Registra un nuevo cambio de turno entre empleados</p>
            </div>
          </div>
        </div>

        <!-- Form Card -->
        <section class="form-card">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--navy-soft)">
              <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4" style="color: var(--navy)" />
            </div>
            <div>
              <h3 class="card-title">Datos del Cambio de Turno</h3>
              <p class="card-subtitle">Ingresa la información del cambio de turno</p>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="error-banner">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ error }}
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Empleado Solicitante <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-user" class="input-icon" />
                <select v-model="form.solicitante_id" class="input-clinical" :class="{ 'input-error': errors.solicitante_id }" @change="errors.solicitante_id = ''">
                  <option value="">Seleccione</option>
                  <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombres }} {{ e.apellidos }}</option>
                </select>
              </div>
              <span v-if="errors.solicitante_id" class="error-message">{{ errors.solicitante_id }}</span>
              <p class="field-hint">Empleado que solicita el cambio</p>
            </div>

            <div class="form-group">
              <label class="form-label">Empleado Aceptante <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-user" class="input-icon" />
                <select v-model="form.aceptante_id" class="input-clinical" :class="{ 'input-error': errors.aceptante_id }" @change="errors.aceptante_id = ''">
                  <option value="">Seleccione</option>
                  <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombres }} {{ e.apellidos }}</option>
                </select>
              </div>
              <span v-if="errors.aceptante_id" class="error-message">{{ errors.aceptante_id }}</span>
              <p class="field-hint">Empleado que acepta el cambio</p>
            </div>

            <div class="form-group">
              <label class="form-label">Turno Solicitante</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-clock" class="input-icon" />
                <select v-model="form.modalidad_solicitante" class="input-clinical">
                  <option v-for="m in modalidades" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>
              <p class="field-hint">Turno que tiene el solicitante</p>
            </div>

            <div class="form-group">
              <label class="form-label">Turno Aceptante</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-clock" class="input-icon" />
                <select v-model="form.modalidad_aceptante" class="input-clinical">
                  <option v-for="m in modalidades" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>
              <p class="field-hint">Turno que tiene el aceptante</p>
            </div>

            <div class="form-group">
              <label class="form-label">Fecha Original <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-calendar" class="input-icon" />
                <input 
                  v-model="form.fecha_original" 
                  type="date" 
                  class="input-clinical"
                  :class="{ 'input-error': errors.fecha_original }"
                  @change="errors.fecha_original = ''"
                />
              </div>
              <span v-if="errors.fecha_original" class="error-message">{{ errors.fecha_original }}</span>
              <p class="field-hint">Fecha original del turno del solicitante</p>
            </div>

            <div class="form-group">
              <label class="form-label">Fecha de Reemplazo <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-calendar" class="input-icon" />
                <input 
                  v-model="form.fecha_reemplazo" 
                  type="date" 
                  class="input-clinical"
                  :class="{ 'input-error': errors.fecha_reemplazo }"
                  @change="errors.fecha_reemplazo = ''"
                />
              </div>
              <span v-if="errors.fecha_reemplazo" class="error-message">{{ errors.fecha_reemplazo }}</span>
              <p class="field-hint">Fecha en que el aceptante reemplazará</p>
            </div>

            <div class="form-group">
              <label class="form-label">Estado</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-flag" class="input-icon" />
                <select v-model="form.estado" class="input-clinical">
                  <option value="pendiente">⏳ Pendiente</option>
                  <option value="aprobado">✅ Aprobado</option>
                  <option value="rechazado">❌ Rechazado</option>
                </select>
              </div>
              <p class="field-hint">Estado inicial del cambio de turno</p>
            </div>
          </div>

          <!-- Preview Section -->
          <div v-if="form.solicitante_id || form.aceptante_id" class="preview-section">
            <h4 class="preview-title">Vista Previa</h4>
            <div class="preview-card">
              <div class="preview-icon" :style="{ background: getEstadoBgColor(form.estado) }">
                <UIcon :name="getEstadoIcon(form.estado)" class="w-5 h-5" :style="{ color: getEstadoColor(form.estado) }" />
              </div>
              <div class="preview-info">
                <span class="preview-solicitante">
                  <strong>Solicita:</strong> {{ empleadoSeleccionado?.nombres || '—' }} {{ empleadoSeleccionado?.apellidos || '' }}
                  <span class="preview-modalidad">({{ form.modalidad_solicitante }})</span>
                </span>
                <span class="preview-aceptante">
                  <strong>Acepta:</strong> {{ empleadoAceptante?.nombres || '—' }} {{ empleadoAceptante?.apellidos || '' }}
                  <span class="preview-modalidad">({{ form.modalidad_aceptante }})</span>
                </span>
                <span class="preview-fechas">
                  <span>Original: {{ formatDate(form.fecha_original) }}</span>
                  <span class="preview-arrow">→</span>
                  <span>Reemplazo: {{ formatDate(form.fecha_reemplazo) }}</span>
                </span>
              </div>
              <span class="preview-status" :style="{ background: getEstadoBgColor(form.estado), color: getEstadoColor(form.estado) }">
                <UIcon :name="getEstadoIcon(form.estado)" class="w-3.5 h-3.5" />
                {{ formatEstado(form.estado) }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="form-actions">
            <div class="action-group">
              <button 
                class="btn-primary" 
                :disabled="saving" 
                @click="guardar"
              >
                <UIcon v-if="saving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                {{ saving ? 'Guardando...' : 'Tramitar Cambio' }}
              </button>
              <NuxtLink 
                :to="`/sigarh/movimientos/cambio-turno/estado?tenant=${tenant}`"
                class="btn-cancel"
              >
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Widgets -->
      <div class="cambio-turno-tramitar-sidebar">
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
                <span>El solicitante y aceptante deben ser diferentes</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>La fecha de reemplazo debe ser la que cubrirá el aceptante</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El cambio quedará registrado con estado pendiente</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Puedes aprobar o rechazar el cambio posteriormente</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--navy)" />
            <h4 class="widget-title">Resumen</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Solicitante</span>
              <span class="summary-value">{{ empleadoSeleccionado?.nombres || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Aceptante</span>
              <span class="summary-value">{{ empleadoAceptante?.nombres || '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Fecha Original</span>
              <span class="summary-value font-mono-data">{{ formatDate(form.fecha_original) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Fecha Reemplazo</span>
              <span class="summary-value font-mono-data">{{ formatDate(form.fecha_reemplazo) }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Estado</span>
              <span class="summary-value">
                <span class="status-badge-mini" :style="{ background: getEstadoBgColor(form.estado), color: getEstadoColor(form.estado) }">
                  <UIcon :name="getEstadoIcon(form.estado)" class="w-3 h-3" />
                  {{ formatEstado(form.estado) }}
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
                  Verifica que ambos empleados estén de acuerdo antes de tramitar 
                  el cambio de turno para evitar inconvenientes.
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
              <span class="stat-label">Estado</span>
              <span class="stat-number" :style="{ color: getEstadoColor(form.estado) }">
                {{ formatEstado(form.estado) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cambio-turno-tramitar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.cambio-turno-tramitar-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.cambio-turno-tramitar-main {
  min-width: 0;
}

.cambio-turno-tramitar-sidebar {
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

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
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

.input-clinical[type="date"] {
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
  gap: 0.25rem;
  min-width: 120px;
}

.preview-solicitante,
.preview-aceptante {
  font-size: 0.8125rem;
  color: var(--ink);
}

.preview-modalidad {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  font-weight: 400;
}

.preview-fechas {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-family: monospace;
  color: var(--ink-soft);
}

.preview-arrow {
  color: var(--teal);
  font-weight: 600;
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
  .cambio-turno-tramitar-grid {
    grid-template-columns: 1fr;
  }

  .cambio-turno-tramitar-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .cambio-turno-tramitar-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .cambio-turno-tramitar-sidebar {
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

  .preview-status {
    align-self: flex-start;
  }

  .preview-fechas {
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

  .preview-fechas {
    flex-direction: column;
    align-items: flex-start;
  }

  .preview-arrow {
    transform: rotate(90deg);
  }
}
</style>