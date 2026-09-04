<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Editar Sala' })

const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string
const id = route.params.id as string

const form = reactive({
  nombre: '',
  codigo: '',
  piso_id: '',
  servicio_id: '',
  capacidad: 1,
  is_active: true,
})

const pisos = ref<any[]>([])
const servicios = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const errors = reactive({
  nombre: '',
  codigo: '',
  capacidad: '',
})

const filledFields = computed(() => {
  let count = 0
  if (form.nombre) count++
  if (form.codigo) count++
  if (form.piso_id) count++
  if (form.servicio_id) count++
  if (form.capacidad > 0) count++
  return count
})

const pisoSeleccionado = computed(() =>
  pisos.value.find(p => p.id === form.piso_id)
)

const servicioSeleccionado = computed(() =>
  servicios.value.find(s => s.id === form.servicio_id)
)

const validateForm = (): boolean => {
  let valid = true
  if (!form.nombre.trim()) {
    errors.nombre = 'El nombre de la sala es requerido'
    valid = false
  }
  if (!form.codigo.trim()) {
    errors.codigo = 'El código de la sala es requerido'
    valid = false
  }
  if (!form.capacidad || form.capacidad < 1) {
    errors.capacidad = 'La capacidad debe ser al menos 1'
    valid = false
  }
  return valid
}

async function guardar() {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    await $api(`/sigarh/infraestructura-hosp/salas/${id}`, {
      method: 'PATCH',
      tenant,
      body: {
        nombre: form.nombre,
        codigo: form.codigo,
        piso_id: form.piso_id || null,
        servicio_id: form.servicio_id || null,
        capacidad: form.capacidad,
        is_active: form.is_active,
      }
    })
    router.push(`/sigarh/infraestructura-hosp/salas?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [data, pss, svs] = await Promise.all([
      $api(`/sigarh/infraestructura-hosp/salas/${id}`, { tenant }),
      $api('/sigarh/infraestructura-hosp/pisos', { tenant }),
      $api('/sigarh/mantenimiento/servicios', { tenant }),
    ])
    Object.assign(form, data)
    pisos.value = pss
    servicios.value = svs
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar datos'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="sala-edit-container">
    <div class="sala-edit-grid">
      <!-- Main Content -->
      <div class="sala-edit-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/infraestructura-hosp/salas?tenant=${tenant}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-building-office-2" class="w-3.5 h-3.5" />
              Salas
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Editar Sala</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" :style="{ background: form.is_active ? 'var(--teal-soft)' : 'var(--mist)' }">
              <UIcon
                name="i-heroicons-building-office-2"
                class="w-6 h-6"
                :style="{ color: form.is_active ? 'var(--teal)' : 'var(--ink-soft)' }"
              />
            </div>
            <div>
              <h1 class="page-title">{{ form.nombre || 'Editar Sala' }}</h1>
              <p class="page-subtitle">
                <span class="code-display font-mono-data">{{ form.codigo ? `Código: ${form.codigo}` : 'Sin código' }}</span>
                <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
                <span class="status-text-mini" :class="form.is_active ? 'text-active' : 'text-inactive'">
                  {{ form.is_active ? 'Activa' : 'Inactiva' }}
                </span>
              </p>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando información de la sala...</p>
        </div>

        <template v-else>
          <!-- Form Card -->
          <section class="form-card">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4" style="color: var(--teal)" />
              </div>
              <div>
                <h3 class="card-title">Configuración de la Sala</h3>
                <p class="card-subtitle">Actualiza los datos de la sala</p>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="error" class="error-banner">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
              {{ error }}
            </div>

            <div class="form-grid">
              <div class="form-group full-width">
                <label class="form-label">Nombre de la Sala <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-building-office-2" class="input-icon" />
                  <input
                    v-model="form.nombre"
                    type="text"
                    class="input-clinical"
                    placeholder="Ej: Sala de Emergencias, Sala de Operaciones"
                    :class="{ 'input-error': errors.nombre }"
                    @focus="errors.nombre = ''"
                  />
                </div>
                <span v-if="errors.nombre" class="error-message">{{ errors.nombre }}</span>
                <p class="field-hint">Nombre descriptivo de la sala</p>
              </div>

              <div class="form-group">
                <label class="form-label">Código <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-barcode" class="input-icon" />
                  <input
                    v-model="form.codigo"
                    type="text"
                    class="input-clinical font-mono-data"
                    placeholder="Ej: SAL-001"
                    :class="{ 'input-error': errors.codigo }"
                    @focus="errors.codigo = ''"
                  />
                </div>
                <span v-if="errors.codigo" class="error-message">{{ errors.codigo }}</span>
                <p class="field-hint">Código identificador único de la sala</p>
              </div>

              <div class="form-group">
                <label class="form-label">Capacidad <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-users" class="input-icon" />
                  <input
                    v-model.number="form.capacidad"
                    type="number"
                    min="1"
                    class="input-clinical font-mono-data"
                    placeholder="Ej: 10"
                    :class="{ 'input-error': errors.capacidad }"
                    @focus="errors.capacidad = ''"
                  />
                </div>
                <span v-if="errors.capacidad" class="error-message">{{ errors.capacidad }}</span>
                <p class="field-hint">Número máximo de personas que puede albergar</p>
              </div>

              <div class="form-group">
                <label class="form-label">Piso</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-arrow-up" class="input-icon" />
                  <select v-model="form.piso_id" class="input-clinical">
                    <option value="">Sin piso</option>
                    <option v-for="p in pisos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                  </select>
                </div>
                <p class="field-hint">Ubicación en el edificio</p>
              </div>

              <div class="form-group">
                <label class="form-label">Servicio</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-folder" class="input-icon" />
                  <select v-model="form.servicio_id" class="input-clinical">
                    <option value="">Sin servicio</option>
                    <option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                  </select>
                </div>
                <p class="field-hint">Servicio al que pertenece la sala</p>
              </div>

              <div class="form-group full-width">
                <div class="status-toggle">
                  <span class="toggle-label">Sala Activa</span>
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
                <p class="field-hint">Las salas inactivas no estarán disponibles</p>
              </div>
            </div>

            <!-- Preview Section -->
            <div class="preview-section">
              <h4 class="preview-title">Vista Previa</h4>
              <div class="preview-card">
                <div class="preview-icon" :style="{ background: form.is_active ? 'var(--teal-soft)' : 'var(--mist)' }">
                  <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" :style="{ color: form.is_active ? 'var(--teal)' : 'var(--ink-soft)' }" />
                </div>
                <div class="preview-info">
                  <span class="preview-name">{{ form.nombre || 'Nombre de la sala' }}</span>
                  <span class="preview-detail">
                    <span class="preview-code">{{ form.codigo || 'Sin código' }}</span>
                    <span class="preview-capacity">Capacidad: {{ form.capacidad || 0 }} personas</span>
                  </span>
                </div>
                <span class="preview-status" :class="form.is_active ? 'preview-active' : 'preview-inactive'">
                  <span class="preview-dot" :class="form.is_active ? 'dot-active' : 'dot-inactive'" />
                  {{ form.is_active ? 'Activa' : 'Inactiva' }}
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
                  {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
                </button>
                <NuxtLink
                  :to="`/sigarh/infraestructura-hosp/salas?tenant=${tenant}`"
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
      <div class="sala-edit-sidebar">
        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Resumen</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Nombre</span>
              <span class="summary-value">{{ form.nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Código</span>
              <span class="summary-value font-mono-data">{{ form.codigo || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Capacidad</span>
              <span class="summary-value">{{ form.capacidad || 0 }} personas</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Piso</span>
              <span class="summary-value">{{ pisoSeleccionado?.nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Servicio</span>
              <span class="summary-value">{{ servicioSeleccionado?.nombre || '—' }}</span>
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

        <!-- Info Widget -->
        <div class="widget widget-info">
          <div class="widget-header">
            <UIcon name="i-heroicons-information-circle" class="widget-icon" style="color: var(--navy)" />
            <h4 class="widget-title">Información</h4>
          </div>
          <div class="widget-content">
            <ul class="info-list">
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Las salas son espacios físicos dentro del hospital</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Pueden estar asociadas a un piso y un servicio</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>La capacidad define el aforo máximo de la sala</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Las salas inactivas no se pueden asignar</span>
              </li>
            </ul>
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
                  Al editar una sala, verifica que el código y nombre sean consistentes 
                  con la nomenclatura del hospital.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Status Widget -->
        <div class="widget widget-stats">
          <div class="widget-header">
            <UIcon name="i-heroicons-chart-bar" class="widget-icon" style="color: var(--purple)" />
            <h4 class="widget-title">Estado</h4>
          </div>
          <div class="widget-content">
            <div class="stat-item">
              <span class="stat-label">Estado actual</span>
              <span class="stat-number" :style="{ color: form.is_active ? 'var(--green)' : 'var(--ink-soft)' }">
                {{ form.is_active ? 'Activa' : 'Inactiva' }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Capacidad</span>
              <span class="stat-number">{{ form.capacidad || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Campos completos</span>
              <span class="stat-number">{{ filledFields }}/5</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sala-edit-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.sala-edit-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.sala-edit-main {
  min-width: 0;
}

.sala-edit-sidebar {
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
}

.code-display {
  font-size: 0.8125rem;
}

.status-dot-mini {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.dot-active-mini {
  background: var(--green);
}

.dot-inactive-mini {
  background: var(--ink-soft);
}

.status-text-mini {
  font-size: 0.75rem;
  font-weight: 500;
}

.text-active {
  color: var(--green);
}

.text-inactive {
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

.preview-code {
  font-family: monospace;
}

.preview-capacity {
  color: var(--teal);
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
  .sala-edit-grid {
    grid-template-columns: 1fr;
  }

  .sala-edit-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .sala-edit-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .sala-edit-sidebar {
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
    flex-wrap: wrap;
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