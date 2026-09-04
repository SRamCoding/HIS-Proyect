<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Tramitar Papeleta' })

const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string

const form = reactive({
  empleado_id: '',
  motivo_id: '',
  fecha_tramite: new Date().toISOString().split('T')[0],
  detalle: '',
  estado: 'pendiente',
  mes_actual: true,
})

const empleados = ref<any[]>([])
const motivos = ref<any[]>([])
const saving = ref(false)
const error = ref('')

const errors = reactive({
  empleado_id: '',
  motivo_id: '',
  fecha_tramite: '',
  detalle: '',
})

const filledFields = computed(() => {
  let count = 0
  if (form.empleado_id) count++
  if (form.motivo_id) count++
  if (form.fecha_tramite) count++
  if (form.detalle) count++
  return count
})

const empleadoSeleccionado = computed(() =>
  empleados.value.find(e => e.id === form.empleado_id)
)

const motivoSeleccionado = computed(() =>
  motivos.value.find(m => m.id === form.motivo_id)
)

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

const getInitials = (name: string) => {
  if (!name || name === '—') return '?'
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const validateForm = (): boolean => {
  let valid = true
  if (!form.empleado_id) {
    errors.empleado_id = 'El empleado es requerido'
    valid = false
  }
  if (!form.motivo_id) {
    errors.motivo_id = 'El motivo es requerido'
    valid = false
  }
  if (!form.fecha_tramite) {
    errors.fecha_tramite = 'La fecha de trámite es requerida'
    valid = false
  }
  if (!form.detalle.trim()) {
    errors.detalle = 'El detalle es requerido'
    valid = false
  }
  return valid
}

async function guardar() {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    await $api('/sigarh/movimientos/papeletas', {
      method: 'POST',
      tenant,
      body: form
    })
    router.push(`/sigarh/movimientos/papeletas/estado?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    [empleados.value, motivos.value] = await Promise.all([
      $api('/sigarh/rrhh/empleados', { tenant }),
      $api('/sigarh/rrhh/motivos-justificacion', { tenant }),
    ])
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar datos'
  }
})
</script>

<template>
  <div class="papeleta-tramitar-container">
    <div class="papeleta-tramitar-grid">
      <!-- Main Content -->
      <div class="papeleta-tramitar-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/movimientos/papeletas/estado?tenant=${tenant}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-document-text" class="w-3.5 h-3.5" />
              Papeletas
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Tramitar</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--orange-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--orange)" />
            </div>
            <div>
              <h1 class="page-title">Tramitar Papeleta</h1>
              <p class="page-subtitle">Registra una nueva papeleta para un empleado</p>
            </div>
          </div>
        </div>

        <!-- Form Card -->
        <section class="form-card">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--orange-soft)">
              <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4" style="color: var(--orange)" />
            </div>
            <div>
              <h3 class="card-title">Datos de la Papeleta</h3>
              <p class="card-subtitle">Ingresa la información de la papeleta del empleado</p>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="error-banner">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ error }}
          </div>

          <div class="form-grid">
            <div class="form-group full-width">
              <label class="form-label">Empleado <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-user" class="input-icon" />
                <select v-model="form.empleado_id" class="input-clinical" :class="{ 'input-error': errors.empleado_id }" @change="errors.empleado_id = ''">
                  <option value="">Seleccione un empleado</option>
                  <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombres }} {{ e.apellidos }}</option>
                </select>
              </div>
              <span v-if="errors.empleado_id" class="error-message">{{ errors.empleado_id }}</span>
              <p class="field-hint">Empleado al que se le tramita la papeleta</p>
            </div>

            <div class="form-group full-width">
              <label class="form-label">Motivo <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-flag" class="input-icon" />
                <select v-model="form.motivo_id" class="input-clinical" :class="{ 'input-error': errors.motivo_id }" @change="errors.motivo_id = ''">
                  <option value="">Seleccione un motivo</option>
                  <option v-for="m in motivos" :key="m.id" :value="m.id">{{ m.nombre }}</option>
                </select>
              </div>
              <span v-if="errors.motivo_id" class="error-message">{{ errors.motivo_id }}</span>
              <p class="field-hint">Motivo de la papeleta</p>
            </div>

            <div class="form-group">
              <label class="form-label">Fecha de Trámite <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-calendar" class="input-icon" />
                <input 
                  v-model="form.fecha_tramite" 
                  type="date" 
                  class="input-clinical"
                  :class="{ 'input-error': errors.fecha_tramite }"
                  @change="errors.fecha_tramite = ''"
                />
              </div>
              <span v-if="errors.fecha_tramite" class="error-message">{{ errors.fecha_tramite }}</span>
              <p class="field-hint">Fecha en que se tramita la papeleta</p>
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
              <p class="field-hint">Estado inicial de la papeleta</p>
            </div>

            <div class="form-group full-width">
              <div class="checkbox-wrapper">
                <input v-model="form.mes_actual" type="checkbox" id="mes_actual" class="checkbox-custom" />
                <label for="mes_actual" class="checkbox-label">Mes actual</label>
              </div>
              <p class="field-hint">Indica si la papeleta corresponde al mes actual</p>
            </div>

            <div class="form-group full-width">
              <label class="form-label">Detalle <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                <textarea 
                  v-model="form.detalle" 
                  class="input-clinical" 
                  rows="3" 
                  placeholder="Descripción detallada de la papeleta..."
                  :class="{ 'input-error': errors.detalle }"
                  @focus="errors.detalle = ''"
                />
              </div>
              <span v-if="errors.detalle" class="error-message">{{ errors.detalle }}</span>
              <p class="field-hint">Información detallada sobre la papeleta</p>
            </div>
          </div>

          <!-- Preview Section -->
          <div v-if="form.empleado_id || form.motivo_id" class="preview-section">
            <h4 class="preview-title">Vista Previa</h4>
            <div class="preview-card">
              <div class="preview-icon" :style="{ background: getEstadoBgColor(form.estado) }">
                <UIcon :name="getEstadoIcon(form.estado)" class="w-5 h-5" :style="{ color: getEstadoColor(form.estado) }" />
              </div>
              <div class="preview-info">
                <span class="preview-empleado">
                  <strong>Empleado:</strong> {{ empleadoSeleccionado?.nombres || '—' }} {{ empleadoSeleccionado?.apellidos || '' }}
                </span>
                <span class="preview-motivo">
                  <strong>Motivo:</strong> {{ motivoSeleccionado?.nombre || '—' }}
                </span>
                <span class="preview-detalle">{{ form.detalle || 'Sin detalle' }}</span>
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
                {{ saving ? 'Guardando...' : 'Tramitar Papeleta' }}
              </button>
              <NuxtLink 
                :to="`/sigarh/movimientos/papeletas/estado?tenant=${tenant}`"
                class="btn-cancel"
              >
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Widgets -->
      <div class="papeleta-tramitar-sidebar">
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
                <span>Las papeletas registran trámites administrativos</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El motivo clasifica el tipo de papeleta</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El detalle debe ser claro y específico</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Las papeletas quedan registradas con estado pendiente</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--orange)" />
            <h4 class="widget-title">Resumen</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Empleado</span>
              <span class="summary-value">{{ empleadoSeleccionado?.nombres || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Motivo</span>
              <span class="summary-value">{{ motivoSeleccionado?.nombre || '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Fecha</span>
              <span class="summary-value font-mono-data">{{ formatDate(form.fecha_tramite) }}</span>
            </div>
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
                  Verifica que todos los datos sean correctos antes de tramitar 
                  la papeleta para evitar errores en el registro.
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
            <div class="stat-item">
              <span class="stat-label">Mes actual</span>
              <span class="stat-number" :style="{ color: form.mes_actual ? 'var(--green)' : 'var(--ink-soft)' }">
                {{ form.mes_actual ? '✓ Sí' : 'No' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.papeleta-tramitar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.papeleta-tramitar-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.papeleta-tramitar-main {
  min-width: 0;
}

.papeleta-tramitar-sidebar {
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
  gap: 0.25rem;
  min-width: 120px;
}

.preview-empleado,
.preview-motivo {
  font-size: 0.8125rem;
  color: var(--ink);
}

.preview-detalle {
  font-size: 0.75rem;
  color: var(--ink-soft);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
  .papeleta-tramitar-grid {
    grid-template-columns: 1fr;
  }

  .papeleta-tramitar-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .papeleta-tramitar-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .papeleta-tramitar-sidebar {
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