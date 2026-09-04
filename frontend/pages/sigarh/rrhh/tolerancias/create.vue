<template>
  <div class="tolerancia-create-container">
    <div class="tolerancia-create-grid">
      <!-- Main Content -->
      <div class="tolerancia-create-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/rrhh/tolerancias?tenant=${tenantId}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
              Tolerancias
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Nueva Tolerancia</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--navy-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--navy)" />
            </div>
            <div>
              <h1 class="page-title">Crear Tolerancia</h1>
              <p class="page-subtitle">Define los márgenes de tolerancia para el control de asistencia</p>
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
              <h3 class="card-title">Configuración de Tolerancia</h3>
              <p class="card-subtitle">Ingresa los datos de la nueva tolerancia</p>
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group full-width">
              <label class="form-label">Nombre <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-tag" class="input-icon" />
                <input 
                  v-model="form.nombre" 
                  class="input-clinical" 
                  placeholder="Ej: Tolerancia General, Tolerancia Especial"
                  :class="{ 'input-error': errors.nombre }"
                  @focus="errors.nombre = ''"
                />
              </div>
              <span v-if="errors.nombre" class="error-message">{{ errors.nombre }}</span>
              <p class="field-hint">Nombre descriptivo de la regla de tolerancia</p>
            </div>

            <div class="form-group">
              <label class="form-label">Minutos de Entrada</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-clock" class="input-icon" />
                <input 
                  v-model.number="form.minutos_entrada" 
                  type="number" 
                  min="0" 
                  class="input-clinical font-mono-data" 
                  placeholder="0"
                />
              </div>
              <p class="field-hint">Minutos de tolerancia al ingresar</p>
            </div>

            <div class="form-group">
              <label class="form-label">Minutos de Salida</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-clock" class="input-icon" />
                <input 
                  v-model.number="form.minutos_salida" 
                  type="number" 
                  min="0" 
                  class="input-clinical font-mono-data" 
                  placeholder="0"
                />
              </div>
              <p class="field-hint">Minutos de tolerancia al salir</p>
            </div>

            <div class="form-group full-width">
              <label class="form-label">Descripción</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                <textarea 
                  v-model="form.descripcion" 
                  class="input-clinical" 
                  rows="2" 
                  placeholder="Descripción adicional de la regla de tolerancia..."
                />
              </div>
            </div>

            <div class="form-group full-width">
              <div class="status-toggle">
                <span class="toggle-label">Tolerancia Activa</span>
                <button
                  type="button"
                  role="switch"
                  :aria-checked="form.is_active"
                  @click="form.is_active = !form.is_active"
                  class="toggle-switch"
                  :class="{ 'toggle-active': form.is_active }"
                >
                  <span class="toggle-slider" />
                </button>
              </div>
              <p class="field-hint">Las tolerancias inactivas no se aplicarán en el control de asistencia</p>
            </div>

            <!-- Preview Section -->
            <div v-if="form.nombre || form.minutos_entrada || form.minutos_salida" class="form-group full-width preview-section">
              <h4 class="preview-title">Vista Previa</h4>
              <div class="preview-card">
                <div class="preview-icon" :style="{ background: form.is_active ? 'var(--navy-soft)' : 'var(--mist)' }">
                  <UIcon name="i-heroicons-clock" class="w-5 h-5" :style="{ color: form.is_active ? 'var(--navy)' : 'var(--ink-soft)' }" />
                </div>
                <div class="preview-info">
                  <span class="preview-name">{{ form.nombre || 'Nombre de la tolerancia' }}</span>
                  <span class="preview-detail">
                    Entrada: {{ form.minutos_entrada || 0 }} min · Salida: {{ form.minutos_salida || 0 }} min
                  </span>
                </div>
                <span class="preview-status" :class="form.is_active ? 'preview-active' : 'preview-inactive'">
                  <span class="preview-dot" :class="form.is_active ? 'dot-active' : 'dot-inactive'" />
                  {{ form.is_active ? 'Activa' : 'Inactiva' }}
                </span>
              </div>
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
                {{ saving ? 'Creando...' : 'Crear Tolerancia' }}
              </button>
              <button 
                class="btn-outline" 
                :disabled="saving" 
                @click="handleCreate(true)"
              >
                <UIcon name="i-heroicons-plus" class="w-4 h-4" />
                Crear y otro
              </button>
              <NuxtLink 
                :to="`/sigarh/rrhh/tolerancias?tenant=${tenantId}`"
                class="btn-cancel"
              >
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Widgets -->
      <div class="tolerancia-create-sidebar">
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
                <span>Las tolerancias definen márgenes de tiempo para entrada y salida</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Se aplican automáticamente en el control de asistencia</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Puedes crear diferentes reglas para distintos grupos</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los valores se expresan en minutos</span>
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
              <span class="summary-label">Nombre</span>
              <span class="summary-value">{{ form.nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Entrada</span>
              <span class="summary-value font-mono-data">{{ form.minutos_entrada || 0 }} min</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Salida</span>
              <span class="summary-value font-mono-data">{{ form.minutos_salida || 0 }} min</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Estado</span>
              <span class="summary-value">
                <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
                  <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
                  {{ form.is_active ? 'Activa' : 'Inactiva' }}
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
                  Define tolerancias razonables según la política de la institución. 
                  Generalmente se usan entre 5 y 15 minutos para entrada y salida.
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
              <span class="stat-label">Tolerancia</span>
              <span class="stat-number" :style="{ color: (form.minutos_entrada || form.minutos_salida) ? 'var(--teal)' : 'var(--ink-soft)' }">
                {{ (form.minutos_entrada || form.minutos_salida) ? '✓ Configurada' : '—' }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Estado</span>
              <span class="stat-number" :style="{ color: form.is_active ? 'var(--green)' : 'var(--ink-soft)' }">
                {{ form.is_active ? 'Activa' : 'Inactiva' }}
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

const errors = reactive({
  nombre: ''
})

const form = reactive({
  nombre: '',
  minutos_entrada: 0,
  minutos_salida: 0,
  descripcion: '',
  is_active: true,
})

const filledFields = computed(() => {
  let count = 0
  if (form.nombre) count++
  if (form.minutos_entrada > 0) count++
  if (form.minutos_salida > 0) count++
  if (form.descripcion) count++
  return count
})

const validateForm = (): boolean => {
  let valid = true
  if (!form.nombre.trim()) {
    errors.nombre = 'El nombre de la tolerancia es requerido'
    valid = false
  }
  return valid
}

const handleCreate = async (createAnother: boolean) => {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/rrhh/tolerancias', {
      method: 'POST',
      body: {
        nombre: form.nombre,
        minutos_entrada: form.minutos_entrada || 0,
        minutos_salida: form.minutos_salida || 0,
        descripcion: form.descripcion || null,
        is_active: form.is_active,
      }
    })

    if (createAnother) {
      Object.assign(form, { 
        nombre: '', 
        minutos_entrada: 0, 
        minutos_salida: 0, 
        descripcion: '', 
        is_active: true 
      })
      errors.nombre = ''
    } else {
      router.push(`/sigarh/rrhh/tolerancias?tenant=${tenantId.value}`)
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo crear la tolerancia'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.tolerancia-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.tolerancia-create-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.tolerancia-create-main {
  min-width: 0;
}

.tolerancia-create-sidebar {
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

.input-clinical[type="number"] {
  -moz-appearance: textfield;
}

.input-clinical[type="number"]::-webkit-outer-spin-button,
.input-clinical[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
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

/* Status Toggle */
.status-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--mist);
}

.toggle-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.toggle-switch {
  position: relative;
  width: 44px;
  height: 24px;
  border-radius: 12px;
  background: var(--line);
  border: none;
  cursor: pointer;
  transition: background 0.3s ease;
  padding: 0;
}

.toggle-switch.toggle-active {
  background: var(--teal);
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  transition: transform 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle-active .toggle-slider {
  transform: translateX(20px);
}

/* Preview Section */
.preview-section {
  margin-top: 0.5rem;
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

.preview-active {
  background: var(--green-soft);
  color: var(--green);
}

.preview-inactive {
  background: var(--mist);
  color: var(--ink-soft);
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

.dot-inactive {
  background: var(--ink-soft);
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

.summary-divider {
  height: 1px;
  background: var(--line);
  margin: 0.5rem 0;
}

/* Status Badge Mini */
.status-badge-mini {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
}

.status-active-mini {
  background: var(--green-soft);
  color: var(--green);
}

.status-inactive-mini {
  background: var(--mist);
  color: var(--ink-soft);
}

.status-dot-mini {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  display: inline-block;
}

.dot-active-mini {
  background: var(--green);
}

.dot-inactive-mini {
  background: var(--ink-soft);
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
  .tolerancia-create-grid {
    grid-template-columns: 1fr;
  }

  .tolerancia-create-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .tolerancia-create-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .tolerancia-create-sidebar {
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
  .status-toggle {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

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