<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Tramitar Licencia' })

const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string

const form = reactive({
  nombre_empleado: '',
  dni: '',
  dependencia: '',
  cargo: '',
  tipo_licencia: 'CON GOCE DE HABER',
  fecha_inicio: '',
  fecha_fin: '',
  dias_solicitados: 0,
  motivo: '',
  estado: 'pendiente',
})

const saving = ref(false)
const error = ref('')

const errors = reactive({
  nombre_empleado: '',
  dni: '',
  fecha_inicio: '',
  fecha_fin: '',
  motivo: '',
})

const filledFields = computed(() => {
  let count = 0
  if (form.nombre_empleado) count++
  if (form.dni) count++
  if (form.fecha_inicio) count++
  if (form.fecha_fin) count++
  if (form.motivo) count++
  return count
})

const tiposLicencia = [
  'CON GOCE DE HABER',
  'SIN GOCE DE HABER',
  'POR ENFERMEDAD',
  'POR MATERNIDAD',
  'POR PATERNIDAD',
  'POR FALLECIMIENTO'
]

const formatDate = (date: string) => {
  if (!date) return '—'
  const d = new Date(date)
  return d.toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const getTipoColor = (tipo: string) => {
  const map: Record<string, string> = {
    'CON GOCE DE HABER': 'var(--green)',
    'SIN GOCE DE HABER': 'var(--alert)',
    'POR ENFERMEDAD': 'var(--amber)',
    'POR MATERNIDAD': 'var(--purple)',
    'POR PATERNIDAD': 'var(--teal)',
    'POR FALLECIMIENTO': 'var(--navy)'
  }
  return map[tipo] || 'var(--ink-soft)'
}

const getTipoBgColor = (tipo: string) => {
  const map: Record<string, string> = {
    'CON GOCE DE HABER': 'var(--green-soft)',
    'SIN GOCE DE HABER': 'var(--alert-soft)',
    'POR ENFERMEDAD': 'var(--amber-soft)',
    'POR MATERNIDAD': 'var(--purple-soft)',
    'POR PATERNIDAD': 'var(--teal-soft)',
    'POR FALLECIMIENTO': 'var(--navy-soft)'
  }
  return map[tipo] || 'var(--mist)'
}

watch([() => form.fecha_inicio, () => form.fecha_fin], () => {
  if (form.fecha_inicio && form.fecha_fin) {
    const diff = new Date(form.fecha_fin).getTime() - new Date(form.fecha_inicio).getTime()
    form.dias_solicitados = Math.max(0, Math.ceil(diff / 86400000) + 1)
  } else {
    form.dias_solicitados = 0
  }
})

const validateForm = (): boolean => {
  let valid = true
  if (!form.nombre_empleado.trim()) {
    errors.nombre_empleado = 'El nombre del empleado es requerido'
    valid = false
  }
  if (!form.dni.trim()) {
    errors.dni = 'El DNI es requerido'
    valid = false
  } else if (form.dni.length !== 8) {
    errors.dni = 'El DNI debe tener 8 dígitos'
    valid = false
  }
  if (!form.fecha_inicio) {
    errors.fecha_inicio = 'La fecha de inicio es requerida'
    valid = false
  }
  if (!form.fecha_fin) {
    errors.fecha_fin = 'La fecha de fin es requerida'
    valid = false
  }
  if (form.fecha_inicio && form.fecha_fin && new Date(form.fecha_inicio) > new Date(form.fecha_fin)) {
    errors.fecha_fin = 'La fecha de fin debe ser posterior a la fecha de inicio'
    valid = false
  }
  if (!form.motivo.trim()) {
    errors.motivo = 'El motivo es requerido'
    valid = false
  }
  return valid
}

async function guardar() {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    await $api('/sigarh/movimientos/licencias', {
      method: 'POST',
      tenant,
      body: form
    })
    router.push(`/sigarh/movimientos/licencias?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="licencia-tramitar-container">
    <div class="licencia-tramitar-grid">
      <!-- Main Content -->
      <div class="licencia-tramitar-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/movimientos/licencias?tenant=${tenant}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-document-text" class="w-3.5 h-3.5" />
              Licencias
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Tramitar</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--teal)" />
            </div>
            <div>
              <h1 class="page-title">Tramitar Licencia</h1>
              <p class="page-subtitle">Registra una nueva licencia para un empleado</p>
            </div>
          </div>
        </div>

        <!-- Form Card -->
        <section class="form-card">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4" style="color: var(--teal)" />
            </div>
            <div>
              <h3 class="card-title">Datos de la Licencia</h3>
              <p class="card-subtitle">Ingresa la información de la licencia del empleado</p>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="error-banner">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ error }}
          </div>

          <div class="form-grid">
            <div class="form-group full-width">
              <label class="form-label">Nombre del Empleado <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-user" class="input-icon" />
                <input 
                  v-model="form.nombre_empleado" 
                  type="text" 
                  class="input-clinical" 
                  placeholder="Ej: Juan Pérez Gutiérrez"
                  :class="{ 'input-error': errors.nombre_empleado }"
                  @focus="errors.nombre_empleado = ''"
                />
              </div>
              <span v-if="errors.nombre_empleado" class="error-message">{{ errors.nombre_empleado }}</span>
              <p class="field-hint">Nombre completo del empleado</p>
            </div>

            <div class="form-group">
              <label class="form-label">DNI <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-identification" class="input-icon" />
                <input 
                  v-model="form.dni" 
                  type="text" 
                  maxlength="8" 
                  class="input-clinical font-mono-data" 
                  placeholder="Ej: 76557726"
                  :class="{ 'input-error': errors.dni }"
                  @focus="errors.dni = ''"
                />
              </div>
              <span v-if="errors.dni" class="error-message">{{ errors.dni }}</span>
              <p class="field-hint">Documento Nacional de Identidad (8 dígitos)</p>
            </div>

            <div class="form-group">
              <label class="form-label">Tipo de Licencia</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document-text" class="input-icon" />
                <select v-model="form.tipo_licencia" class="input-clinical">
                  <option v-for="t in tiposLicencia" :key="t" :value="t">{{ t }}</option>
                </select>
              </div>
              <p class="field-hint">Clasificación de la licencia</p>
            </div>

            <div class="form-group">
              <label class="form-label">Dependencia</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-building-office" class="input-icon" />
                <input 
                  v-model="form.dependencia" 
                  type="text" 
                  class="input-clinical" 
                  placeholder="Ej: Área de Salud"
                />
              </div>
              <p class="field-hint">Dependencia del empleado</p>
            </div>

            <div class="form-group">
              <label class="form-label">Cargo</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-briefcase" class="input-icon" />
                <input 
                  v-model="form.cargo" 
                  type="text" 
                  class="input-clinical" 
                  placeholder="Ej: Médico Especialista"
                />
              </div>
              <p class="field-hint">Cargo laboral del empleado</p>
            </div>

            <div class="form-group">
              <label class="form-label">Días Solicitados</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-calendar-days" class="input-icon" />
                <input 
                  v-model.number="form.dias_solicitados" 
                  type="number" 
                  readonly 
                  class="input-clinical font-mono-data" 
                  style="background: var(--mist); cursor: not-allowed;"
                />
              </div>
              <p class="field-hint">Calculado automáticamente según fechas</p>
            </div>

            <div class="form-group">
              <label class="form-label">Fecha de Inicio <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-calendar" class="input-icon" />
                <input 
                  v-model="form.fecha_inicio" 
                  type="date" 
                  class="input-clinical"
                  :class="{ 'input-error': errors.fecha_inicio }"
                  @change="errors.fecha_inicio = ''"
                />
              </div>
              <span v-if="errors.fecha_inicio" class="error-message">{{ errors.fecha_inicio }}</span>
              <p class="field-hint">Fecha de inicio de la licencia</p>
            </div>

            <div class="form-group">
              <label class="form-label">Fecha de Fin <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-calendar" class="input-icon" />
                <input 
                  v-model="form.fecha_fin" 
                  type="date" 
                  class="input-clinical"
                  :class="{ 'input-error': errors.fecha_fin }"
                  @change="errors.fecha_fin = ''"
                />
              </div>
              <span v-if="errors.fecha_fin" class="error-message">{{ errors.fecha_fin }}</span>
              <p class="field-hint">Fecha de fin de la licencia</p>
            </div>

            <div class="form-group full-width">
              <label class="form-label">Motivo <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                <textarea 
                  v-model="form.motivo" 
                  class="input-clinical" 
                  rows="3" 
                  placeholder="Describa el motivo de la licencia..."
                  :class="{ 'input-error': errors.motivo }"
                  @focus="errors.motivo = ''"
                />
              </div>
              <span v-if="errors.motivo" class="error-message">{{ errors.motivo }}</span>
              <p class="field-hint">Descripción detallada del motivo</p>
            </div>
          </div>

          <!-- Preview Section -->
          <div v-if="form.nombre_empleado || form.fecha_inicio" class="preview-section">
            <h4 class="preview-title">Vista Previa</h4>
            <div class="preview-card">
              <div class="preview-icon" :style="{ background: getTipoBgColor(form.tipo_licencia) }">
                <UIcon name="i-heroicons-document-text" class="w-5 h-5" :style="{ color: getTipoColor(form.tipo_licencia) }" />
              </div>
              <div class="preview-info">
                <span class="preview-name">{{ form.nombre_empleado || 'Nombre del empleado' }}</span>
                <span class="preview-detail">
                  <span class="preview-type" :style="{ color: getTipoColor(form.tipo_licencia) }">{{ form.tipo_licencia }}</span>
                  <span class="preview-dates">
                    {{ form.fecha_inicio ? formatDate(form.fecha_inicio) : '—' }}
                    → 
                    {{ form.fecha_fin ? formatDate(form.fecha_fin) : '—' }}
                  </span>
                  <span class="preview-days">{{ form.dias_solicitados }} día(s)</span>
                </span>
              </div>
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
                {{ saving ? 'Guardando...' : 'Tramitar Licencia' }}
              </button>
              <NuxtLink 
                :to="`/sigarh/movimientos/licencias?tenant=${tenant}`"
                class="btn-cancel"
              >
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Widgets -->
      <div class="licencia-tramitar-sidebar">
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
                <span>Las licencias pueden ser con o sin goce de haber</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los días se calculan automáticamente</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El motivo debe ser claro y detallado</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Las licencias quedan registradas con estado pendiente</span>
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
              <span class="summary-label">Empleado</span>
              <span class="summary-value">{{ form.nombre_empleado || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Tipo</span>
              <span class="summary-value" :style="{ color: getTipoColor(form.tipo_licencia) }">{{ form.tipo_licencia }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Inicio</span>
              <span class="summary-value font-mono-data">{{ formatDate(form.fecha_inicio) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Fin</span>
              <span class="summary-value font-mono-data">{{ formatDate(form.fecha_fin) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Días</span>
              <span class="summary-value">{{ form.dias_solicitados }}</span>
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
                  Verifica que todos los datos del empleado sean correctos antes 
                  de tramitar la licencia para evitar errores en los registros.
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
              <span class="stat-number">{{ filledFields }}/5</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Días</span>
              <span class="stat-number">{{ form.dias_solicitados }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Tipo</span>
              <span class="stat-number" :style="{ color: getTipoColor(form.tipo_licencia) }">
                {{ form.tipo_licencia.slice(0, 15) }}{{ form.tipo_licencia.length > 15 ? '...' : '' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.licencia-tramitar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.licencia-tramitar-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.licencia-tramitar-main {
  min-width: 0;
}

.licencia-tramitar-sidebar {
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

.input-clinical[readonly] {
  background: var(--mist);
  cursor: not-allowed;
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

.preview-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.preview-detail {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  font-size: 0.75rem;
}

.preview-type {
  font-weight: 500;
  padding: 0.0625rem 0.5rem;
  border-radius: 10px;
  background: var(--mist);
}

.preview-dates {
  color: var(--ink-soft);
}

.preview-days {
  font-weight: 600;
  color: var(--teal);
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
  .licencia-tramitar-grid {
    grid-template-columns: 1fr;
  }

  .licencia-tramitar-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .licencia-tramitar-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .licencia-tramitar-sidebar {
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
    flex-direction: column;
    align-items: flex-start;
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