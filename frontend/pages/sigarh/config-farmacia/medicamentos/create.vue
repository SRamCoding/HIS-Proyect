<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Nuevo Medicamento' })

const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string

const form = reactive({
  nombre: '',
  codigo_digemid: '',
  concentracion: '',
  forma_farmaceutica: '',
  via_administracion: '',
  unidad_medida: '',
  tipo: 'MEDICAMENTO',
  precio_unitario: 0,
  requiere_receta: false,
  controlado: false,
  is_active: true,
})

const saving = ref(false)
const error = ref('')

const errors = reactive({
  nombre: '',
  codigo_digemid: '',
  concentracion: '',
  precio_unitario: '',
})

const filledFields = computed(() => {
  let count = 0
  if (form.nombre) count++
  if (form.codigo_digemid) count++
  if (form.concentracion) count++
  if (form.forma_farmaceutica) count++
  if (form.via_administracion) count++
  if (form.unidad_medida) count++
  if (form.tipo) count++
  if (form.precio_unitario > 0) count++
  return count
})

const tipoOptions = [
  { value: 'MEDICAMENTO', label: 'Medicamento' },
  { value: 'INSUMO', label: 'Insumo' },
  { value: 'DISPOSITIVO MÉDICO', label: 'Dispositivo Médico' },
]

const formaFarmaceuticaOptions = [
  { value: 'TABLETA', label: 'Tableta' },
  { value: 'CÁPSULA', label: 'Cápsula' },
  { value: 'JARABE', label: 'Jarabe' },
  { value: 'AMPOLLA', label: 'Ampolla' },
  { value: 'FRASCO', label: 'Frasco' },
  { value: 'CREMA', label: 'Crema' },
  { value: 'ÓVULO', label: 'Óvulo' },
  { value: 'SUPOSITORIO', label: 'Supositorio' },
  { value: 'SOLUCIÓN', label: 'Solución' },
]

const viaAdministracionOptions = [
  { value: 'ORAL', label: 'Oral' },
  { value: 'INTRAVENOSA', label: 'Intravenosa' },
  { value: 'INTRAMUSCULAR', label: 'Intramuscular' },
  { value: 'SUBCUTÁNEA', label: 'Subcutánea' },
  { value: 'TÓPICA', label: 'Tópica' },
  { value: 'INHALATORIA', label: 'Inhalatoria' },
]

const getTipoColor = (tipo: string) => {
  const map: Record<string, string> = {
    medicamento: 'var(--teal)',
    insumo: 'var(--purple)',
    'dispositivo médico': 'var(--navy)',
  }
  return map[tipo?.toLowerCase()] || 'var(--ink-soft)'
}

const getTipoBgColor = (tipo: string) => {
  const map: Record<string, string> = {
    medicamento: 'var(--teal-soft)',
    insumo: 'var(--purple-soft)',
    'dispositivo médico': 'var(--navy-soft)',
  }
  return map[tipo?.toLowerCase()] || 'var(--mist)'
}

const getTipoIcon = (tipo: string) => {
  const map: Record<string, string> = {
    medicamento: 'i-heroicons-prescription',
    insumo: 'i-heroicons-beaker',
    'dispositivo médico': 'i-heroicons-cpu-chip',
  }
  return map[tipo?.toLowerCase()] || 'i-heroicons-prescription'
}

const formatTipo = (tipo: string) => {
  if (!tipo) return '—'
  return tipo.charAt(0).toUpperCase() + tipo.slice(1).toLowerCase()
}

const validateForm = (): boolean => {
  let valid = true
  if (!form.nombre.trim()) {
    errors.nombre = 'El nombre del medicamento es requerido'
    valid = false
  }
  if (!form.codigo_digemid.trim()) {
    errors.codigo_digemid = 'El código DIGEMID es requerido'
    valid = false
  }
  if (!form.concentracion.trim()) {
    errors.concentracion = 'La concentración es requerida'
    valid = false
  }
  if (form.precio_unitario < 0) {
    errors.precio_unitario = 'El precio no puede ser negativo'
    valid = false
  }
  return valid
}

async function guardar() {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    await $api('/sigarh/config-farmacia/medicamentos', {
      method: 'POST',
      tenant,
      body: {
        nombre: form.nombre,
        codigo_digemid: form.codigo_digemid,
        concentracion: form.concentracion,
        forma_farmaceutica: form.forma_farmaceutica || null,
        via_administracion: form.via_administracion || null,
        unidad_medida: form.unidad_medida || null,
        tipo: form.tipo,
        precio_unitario: form.precio_unitario || 0,
        requiere_receta: form.requiere_receta,
        controlado: form.controlado,
        is_active: form.is_active,
      }
    })
    router.push(`/sigarh/config-farmacia/medicamentos?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="medicamento-create-container">
    <div class="medicamento-create-grid">
      <!-- Main Content -->
      <div class="medicamento-create-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/config-farmacia/medicamentos?tenant=${tenant}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-prescription" class="w-3.5 h-3.5" />
              Medicamentos
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Nuevo Medicamento</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--teal)" />
            </div>
            <div>
              <h1 class="page-title">Crear Medicamento / Insumo</h1>
              <p class="page-subtitle">Registra un nuevo producto en el catálogo farmacéutico</p>
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
              <h3 class="card-title">Configuración del Producto</h3>
              <p class="card-subtitle">Ingresa los datos del medicamento o insumo</p>
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
                <UIcon name="i-heroicons-prescription" class="input-icon" />
                <input
                  v-model="form.nombre"
                  type="text"
                  class="input-clinical"
                  placeholder="Ej: Paracetamol, Ibuprofeno"
                  :class="{ 'input-error': errors.nombre }"
                  @focus="errors.nombre = ''"
                />
              </div>
              <span v-if="errors.nombre" class="error-message">{{ errors.nombre }}</span>
              <p class="field-hint">Nombre comercial o genérico del producto</p>
            </div>

            <div class="form-group">
              <label class="form-label">Código DIGEMID <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-barcode" class="input-icon" />
                <input
                  v-model="form.codigo_digemid"
                  type="text"
                  class="input-clinical font-mono-data"
                  placeholder="Ej: DIG-001"
                  :class="{ 'input-error': errors.codigo_digemid }"
                  @focus="errors.codigo_digemid = ''"
                />
              </div>
              <span v-if="errors.codigo_digemid" class="error-message">{{ errors.codigo_digemid }}</span>
              <p class="field-hint">Código registrado en DIGEMID</p>
            </div>

            <div class="form-group">
              <label class="form-label">Tipo</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-list-bullet" class="input-icon" />
                <select v-model="form.tipo" class="input-clinical">
                  <option v-for="t in tipoOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
                </select>
              </div>
              <p class="field-hint">Clasificación del producto</p>
            </div>

            <div class="form-group">
              <label class="form-label">Concentración <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-beaker" class="input-icon" />
                <input
                  v-model="form.concentracion"
                  type="text"
                  class="input-clinical"
                  placeholder="Ej: 500mg, 10ml"
                  :class="{ 'input-error': errors.concentracion }"
                  @focus="errors.concentracion = ''"
                />
              </div>
              <span v-if="errors.concentracion" class="error-message">{{ errors.concentracion }}</span>
              <p class="field-hint">Concentración del principio activo</p>
            </div>

            <div class="form-group">
              <label class="form-label">Forma Farmacéutica</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document-text" class="input-icon" />
                <select v-model="form.forma_farmaceutica" class="input-clinical">
                  <option value="">Seleccione</option>
                  <option v-for="f in formaFarmaceuticaOptions" :key="f.value" :value="f.value">{{ f.label }}</option>
                </select>
              </div>
              <p class="field-hint">Presentación del producto</p>
            </div>

            <div class="form-group">
              <label class="form-label">Vía de Administración</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-arrows-right-left" class="input-icon" />
                <select v-model="form.via_administracion" class="input-clinical">
                  <option value="">Seleccione</option>
                  <option v-for="v in viaAdministracionOptions" :key="v.value" :value="v.value">{{ v.label }}</option>
                </select>
              </div>
              <p class="field-hint">Vía por la que se administra</p>
            </div>

            <div class="form-group">
              <label class="form-label">Unidad de Medida</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-ruler" class="input-icon" />
                <input
                  v-model="form.unidad_medida"
                  type="text"
                  class="input-clinical"
                  placeholder="Ej: unidad, caja, frasco"
                />
              </div>
              <p class="field-hint">Unidad de medida del producto</p>
            </div>

            <div class="form-group">
              <label class="form-label">Precio Unitario (S/)</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-currency-dollar" class="input-icon" />
                <input
                  v-model.number="form.precio_unitario"
                  type="number"
                  step="0.01"
                  min="0"
                  class="input-clinical font-mono-data"
                  placeholder="0.00"
                  :class="{ 'input-error': errors.precio_unitario }"
                  @focus="errors.precio_unitario = ''"
                />
              </div>
              <span v-if="errors.precio_unitario" class="error-message">{{ errors.precio_unitario }}</span>
              <p class="field-hint">Precio unitario en soles</p>
            </div>

            <div class="form-group full-width">
              <div class="checkbox-group">
                <div class="checkbox-item">
                  <input v-model="form.requiere_receta" type="checkbox" id="receta" class="checkbox-custom" />
                  <label for="receta" class="checkbox-label">Requiere receta médica</label>
                </div>
                <div class="checkbox-item">
                  <input v-model="form.controlado" type="checkbox" id="controlado" class="checkbox-custom" />
                  <label for="controlado" class="checkbox-label">Medicamento controlado</label>
                </div>
                <div class="checkbox-item">
                  <input v-model="form.is_active" type="checkbox" id="activo" class="checkbox-custom" />
                  <label for="activo" class="checkbox-label">Producto activo</label>
                </div>
              </div>
              <p class="field-hint">Características adicionales del producto</p>
            </div>
          </div>

          <!-- Preview Section -->
          <div v-if="form.nombre || form.codigo_digemid" class="preview-section">
            <h4 class="preview-title">Vista Previa</h4>
            <div class="preview-card">
              <div class="preview-icon" :style="{ background: form.is_active ? getTipoBgColor(form.tipo) : 'var(--mist)' }">
                <UIcon :name="getTipoIcon(form.tipo)" class="w-5 h-5" :style="{ color: form.is_active ? getTipoColor(form.tipo) : 'var(--ink-soft)' }" />
              </div>
              <div class="preview-info">
                <span class="preview-name">{{ form.nombre || 'Nombre del producto' }}</span>
                <span class="preview-detail">
                  <span class="preview-code">{{ form.codigo_digemid || 'Sin código' }}</span>
                  <span class="preview-type" :style="{ color: getTipoColor(form.tipo) }">{{ formatTipo(form.tipo) }}</span>
                </span>
                <span class="preview-concentration">{{ form.concentracion || 'Sin concentración' }}</span>
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
                {{ saving ? 'Guardando...' : 'Crear Producto' }}
              </button>
              <NuxtLink
                :to="`/sigarh/config-farmacia/medicamentos?tenant=${tenant}`"
                class="btn-cancel"
              >
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Widgets -->
      <div class="medicamento-create-sidebar">
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
                <span>El código DIGEMID es obligatorio</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>La concentración debe ser clara y precisa</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los medicamentos controlados requieren seguimiento especial</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El precio unitario es opcional</span>
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
              <span class="summary-label">Código DIGEMID</span>
              <span class="summary-value font-mono-data">{{ form.codigo_digemid || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Tipo</span>
              <span class="summary-value" :style="{ color: getTipoColor(form.tipo) }">{{ formatTipo(form.tipo) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Concentración</span>
              <span class="summary-value">{{ form.concentracion || '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Precio</span>
              <span class="summary-value font-mono-data">S/ {{ form.precio_unitario.toFixed(2) }}</span>
            </div>
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
                  Verifica que el código DIGEMID y la concentración sean correctos 
                  para evitar errores en el inventario y dispensación.
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
              <span class="stat-number">{{ filledFields }}/8</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Precio</span>
              <span class="stat-number font-mono-data">S/ {{ form.precio_unitario.toFixed(2) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Receta</span>
              <span class="stat-number" :style="{ color: form.requiere_receta ? 'var(--teal)' : 'var(--ink-soft)' }">
                {{ form.requiere_receta ? '✓ Requiere' : 'No requiere' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.medicamento-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.medicamento-create-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.medicamento-create-main {
  min-width: 0;
}

.medicamento-create-sidebar {
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

/* Checkbox Group */
.checkbox-group {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  padding: 0.5rem 0;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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

.preview-type {
  font-weight: 500;
}

.preview-concentration {
  font-size: 0.75rem;
  color: var(--teal);
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
  .medicamento-create-grid {
    grid-template-columns: 1fr;
  }

  .medicamento-create-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .medicamento-create-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .medicamento-create-sidebar {
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

  .checkbox-group {
    flex-direction: column;
    gap: 0.5rem;
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

  .checkbox-group {
    gap: 0.5rem;
  }
}
</style>