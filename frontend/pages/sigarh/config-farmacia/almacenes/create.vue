<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Nuevo Almacén' })

const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string

const form = reactive({
  nombre: '',
  codigo: '',
  tipo: 'FARMACIA',
  responsable: '',
  ubicacion: '',
  descripcion: '',
  is_active: true,
})

const saving = ref(false)
const error = ref('')

const errors = reactive({
  nombre: '',
  codigo: '',
  responsable: '',
})

const filledFields = computed(() => {
  let count = 0
  if (form.nombre) count++
  if (form.codigo) count++
  if (form.tipo) count++
  if (form.responsable) count++
  if (form.ubicacion) count++
  if (form.descripcion) count++
  return count
})

const tiposAlmacen = [
  { value: 'FARMACIA', label: 'Farmacia' },
  { value: 'ALMACÉN CENTRAL', label: 'Almacén Central' },
  { value: 'ALMACÉN SECUNDARIO', label: 'Almacén Secundario' },
  { value: 'BOTIQUÍN', label: 'Botiquín' },
]

const getTipoColor = (tipo: string) => {
  const map: Record<string, string> = {
    farmacia: 'var(--teal)',
    'almacén central': 'var(--navy)',
    'almacén secundario': 'var(--amber)',
    botiquín: 'var(--purple)',
  }
  return map[tipo?.toLowerCase()] || 'var(--ink-soft)'
}

const getTipoBgColor = (tipo: string) => {
  const map: Record<string, string> = {
    farmacia: 'var(--teal-soft)',
    'almacén central': 'var(--navy-soft)',
    'almacén secundario': 'var(--amber-soft)',
    botiquín: 'var(--purple-soft)',
  }
  return map[tipo?.toLowerCase()] || 'var(--mist)'
}

const getTipoIcon = (tipo: string) => {
  const map: Record<string, string> = {
    farmacia: 'i-heroicons-prescription',
    'almacén central': 'i-heroicons-building-storefront',
    'almacén secundario': 'i-heroicons-building-office-2',
    botiquín: 'i-heroicons-squares-2x2',
  }
  return map[tipo?.toLowerCase()] || 'i-heroicons-building-storefront'
}

const formatTipo = (tipo: string) => {
  if (!tipo) return '—'
  return tipo.charAt(0).toUpperCase() + tipo.slice(1).toLowerCase()
}

const validateForm = (): boolean => {
  let valid = true
  if (!form.nombre.trim()) {
    errors.nombre = 'El nombre del almacén es requerido'
    valid = false
  }
  if (!form.codigo.trim()) {
    errors.codigo = 'El código del almacén es requerido'
    valid = false
  }
  if (!form.responsable.trim()) {
    errors.responsable = 'El responsable es requerido'
    valid = false
  }
  return valid
}

async function guardar() {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    await $api('/sigarh/config-farmacia/almacenes', {
      method: 'POST',
      tenant,
      body: {
        nombre: form.nombre,
        codigo: form.codigo,
        tipo: form.tipo,
        responsable: form.responsable,
        ubicacion: form.ubicacion || null,
        descripcion: form.descripcion || null,
        is_active: form.is_active,
      }
    })
    router.push(`/sigarh/config-farmacia/almacenes?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="almacen-create-container">
    <div class="almacen-create-grid">
      <!-- Main Content -->
      <div class="almacen-create-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/config-farmacia/almacenes?tenant=${tenant}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-building-storefront" class="w-3.5 h-3.5" />
              Almacenes
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Nuevo Almacén</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--teal)" />
            </div>
            <div>
              <h1 class="page-title">Crear Almacén</h1>
              <p class="page-subtitle">Registra un nuevo almacén o farmacia en el hospital</p>
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
              <h3 class="card-title">Configuración del Almacén</h3>
              <p class="card-subtitle">Ingresa los datos del nuevo almacén o farmacia</p>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="error-banner">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ error }}
          </div>

          <div class="form-grid">
            <div class="form-group full-width">
              <label class="form-label">Nombre <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-building-storefront" class="input-icon" />
                <input
                  v-model="form.nombre"
                  type="text"
                  class="input-clinical"
                  placeholder="Ej: Farmacia Central, Almacén de Medicamentos"
                  :class="{ 'input-error': errors.nombre }"
                  @focus="errors.nombre = ''"
                />
              </div>
              <span v-if="errors.nombre" class="error-message">{{ errors.nombre }}</span>
              <p class="field-hint">Nombre descriptivo del almacén o farmacia</p>
            </div>

            <div class="form-group">
              <label class="form-label">Código <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-barcode" class="input-icon" />
                <input
                  v-model="form.codigo"
                  type="text"
                  class="input-clinical font-mono-data"
                  placeholder="Ej: ALM-001"
                  :class="{ 'input-error': errors.codigo }"
                  @focus="errors.codigo = ''"
                />
              </div>
              <span v-if="errors.codigo" class="error-message">{{ errors.codigo }}</span>
              <p class="field-hint">Código identificador único del almacén</p>
            </div>

            <div class="form-group">
              <label class="form-label">Tipo</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-list-bullet" class="input-icon" />
                <select v-model="form.tipo" class="input-clinical">
                  <option v-for="t in tiposAlmacen" :key="t.value" :value="t.value">{{ t.label }}</option>
                </select>
              </div>
              <p class="field-hint">Clasificación del almacén según su función</p>
            </div>

            <div class="form-group">
              <label class="form-label">Responsable <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-user" class="input-icon" />
                <input
                  v-model="form.responsable"
                  type="text"
                  class="input-clinical"
                  placeholder="Ej: Dr. Juan Pérez"
                  :class="{ 'input-error': errors.responsable }"
                  @focus="errors.responsable = ''"
                />
              </div>
              <span v-if="errors.responsable" class="error-message">{{ errors.responsable }}</span>
              <p class="field-hint">Persona responsable del almacén</p>
            </div>

            <div class="form-group">
              <label class="form-label">Ubicación</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-map-pin" class="input-icon" />
                <input
                  v-model="form.ubicacion"
                  type="text"
                  class="input-clinical"
                  placeholder="Ej: Piso 1, Ala Norte"
                />
              </div>
              <p class="field-hint">Ubicación física del almacén</p>
            </div>

            <div class="form-group full-width">
              <label class="form-label">Descripción</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                <textarea
                  v-model="form.descripcion"
                  class="input-clinical"
                  rows="2"
                  placeholder="Descripción adicional del almacén..."
                />
              </div>
            </div>

            <div class="form-group full-width">
              <div class="status-toggle">
                <span class="toggle-label">Almacén Activo</span>
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
              <p class="field-hint">Los almacenes inactivos no estarán disponibles</p>
            </div>
          </div>

          <!-- Preview Section -->
          <div v-if="form.nombre || form.codigo" class="preview-section">
            <h4 class="preview-title">Vista Previa</h4>
            <div class="preview-card">
              <div class="preview-icon" :style="{ background: form.is_active ? getTipoBgColor(form.tipo) : 'var(--mist)' }">
                <UIcon :name="getTipoIcon(form.tipo)" class="w-5 h-5" :style="{ color: form.is_active ? getTipoColor(form.tipo) : 'var(--ink-soft)' }" />
              </div>
              <div class="preview-info">
                <span class="preview-name">{{ form.nombre || 'Nombre del almacén' }}</span>
                <span class="preview-detail">
                  <span class="preview-code">{{ form.codigo || 'Sin código' }}</span>
                  <span class="preview-tipo" :style="{ color: getTipoColor(form.tipo) }">{{ formatTipo(form.tipo) }}</span>
                </span>
              </div>
              <span class="preview-status" :class="form.is_active ? 'preview-active' : 'preview-inactive'">
                <span class="preview-dot" :class="form.is_active ? 'dot-active' : 'dot-inactive'" />
                {{ form.is_active ? 'Activo' : 'Inactivo' }}
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
                {{ saving ? 'Guardando...' : 'Crear Almacén' }}
              </button>
              <NuxtLink
                :to="`/sigarh/config-farmacia/almacenes?tenant=${tenant}`"
                class="btn-cancel"
              >
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Widgets -->
      <div class="almacen-create-sidebar">
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
                <span>Los almacenes gestionan inventarios de medicamentos</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El tipo define la función del almacén</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El responsable debe ser una persona designada</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los almacenes inactivos no se pueden usar</span>
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
              <span class="summary-label">Nombre</span>
              <span class="summary-value">{{ form.nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Código</span>
              <span class="summary-value font-mono-data">{{ form.codigo || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Tipo</span>
              <span class="summary-value" :style="{ color: getTipoColor(form.tipo) }">{{ formatTipo(form.tipo) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Responsable</span>
              <span class="summary-value">{{ form.responsable || '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Estado</span>
              <span class="summary-value">
                <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
                  <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
                  {{ form.is_active ? 'Activo' : 'Inactivo' }}
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
                  Asigna un código único y descriptivo para facilitar la identificación 
                  del almacén en el sistema de inventario.
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
              <span class="stat-number">{{ filledFields }}/6</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Tipo</span>
              <span class="stat-number" :style="{ color: getTipoColor(form.tipo) }">{{ formatTipo(form.tipo) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Estado</span>
              <span class="stat-number" :style="{ color: form.is_active ? 'var(--green)' : 'var(--ink-soft)' }">
                {{ form.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.almacen-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.almacen-create-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.almacen-create-main {
  min-width: 0;
}

.almacen-create-sidebar {
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

.preview-tipo {
  font-weight: 500;
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
  .almacen-create-grid {
    grid-template-columns: 1fr;
  }

  .almacen-create-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .almacen-create-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .almacen-create-sidebar {
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