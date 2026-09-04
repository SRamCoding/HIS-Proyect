<template>
  <div class="catalogo-edit-container">
    <!-- Progress Indicator (solo 1 paso) -->
    <div class="onboarding-progress">
      <div class="progress-steps">
        <div 
          class="step-item active completed"
        >
          <div class="step-circle">
            <span class="step-check">✓</span>
          </div>
          <span class="step-label">Editar Catálogo</span>
        </div>
      </div>
    </div>

    <div class="catalogo-edit-grid">
      <!-- Main Content -->
      <div class="catalogo-edit-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/infraestructura/catalogos?tenant=${tenant}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-list-bullet" class="w-3.5 h-3.5" />
              Catálogos
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Editar</span>
          </div>
          <div class="flex items-center justify-between gap-4">
            <div class="flex items-center gap-4">
              <div class="header-icon" :style="{ background: form.is_active ? 'var(--teal-soft)' : 'var(--mist)' }">
                <UIcon 
                  name="i-heroicons-tag" 
                  class="w-6 h-6" 
                  :style="{ color: form.is_active ? 'var(--teal)' : 'var(--ink-soft)' }" 
                />
              </div>
              <div>
                <h1 class="page-title">{{ form.nombre || 'Editar Catálogo' }}</h1>
                <p class="page-subtitle">
                  <span class="dni-display font-mono-data">Código: {{ form.codigo || '—' }}</span>
                  <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
                  <span class="status-text-mini" :class="form.is_active ? 'text-active' : 'text-inactive'">
                    {{ form.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </p>
              </div>
            </div>
            <button
              class="btn-danger"
              @click="confirmarEliminar"
            >
              <UIcon name="i-heroicons-trash" class="w-4 h-4" />
              Eliminar
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando información del catálogo...</p>
        </div>

        <template v-else>
          <!-- Form Card -->
          <section class="catalogo-edit-card">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-document-text" class="w-4 h-4" style="color: var(--teal)" />
              </div>
              <div>
                <h3 class="card-title">Datos del Catálogo</h3>
                <p class="card-subtitle">Edita la información del elemento del catálogo</p>
              </div>
            </div>

            <!-- Código Section (No modificable) -->
            <div class="codigo-section">
              <div class="codigo-header">
                <div class="codigo-header-left">
                  <UIcon name="i-heroicons-identification" class="w-4 h-4" style="color: var(--navy)" />
                  <span class="codigo-title">Código del Elemento</span>
                </div>
                <div class="codigo-display-field">
                  <span class="codigo-value font-mono-data">{{ form.codigo || '—' }}</span>
                  <span class="codigo-hint">No modificable</span>
                </div>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group full-width">
                <label class="form-label">Categoría <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-tag" class="input-icon" />
                  <select 
                    v-model="form.categoria" 
                    class="input-clinical"
                    :class="{ 'input-error': errors.categoria }"
                    @change="errors.categoria = ''"
                  >
                    <option value="">Seleccione una categoría</option>
                    <option v-for="c in CATEGORIAS" :key="c" :value="c">{{ formatCategoria(c) }}</option>
                  </select>
                </div>
                <span v-if="errors.categoria" class="error-message">{{ errors.categoria }}</span>
                <p class="field-hint">Selecciona la categoría a la que pertenece el elemento</p>
              </div>

              <div class="form-group">
                <label class="form-label">Código <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-identification" class="input-icon" />
                  <input 
                    v-model="form.codigo" 
                    type="text" 
                    class="input-clinical font-mono-data input-readonly"
                    :class="{ 'input-error': errors.codigo }"
                    placeholder="Ej: DOC-001"
                    disabled
                  />
                </div>
                <span v-if="errors.codigo" class="error-message">{{ errors.codigo }}</span>
                <p class="field-hint">El código no puede modificarse</p>
              </div>

              <div class="form-group">
                <label class="form-label">Orden</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-numbered-list" class="input-icon" />
                  <input 
                    v-model="form.orden" 
                    type="number" 
                    class="input-clinical"
                    placeholder="0"
                  />
                </div>
                <p class="field-hint">Orden de visualización (opcional)</p>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Nombre <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" />
                  <input 
                    v-model="form.nombre" 
                    type="text" 
                    class="input-clinical"
                    :class="{ 'input-error': errors.nombre }"
                    placeholder="Ej: Documento de Identidad"
                    @input="errors.nombre = ''"
                  />
                </div>
                <span v-if="errors.nombre" class="error-message">{{ errors.nombre }}</span>
                <p class="field-hint">Nombre descriptivo del elemento</p>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Descripción</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea 
                    v-model="form.descripcion" 
                    class="input-clinical" 
                    rows="2"
                    placeholder="Descripción detallada del elemento..."
                  />
                </div>
              </div>

              <div class="form-group full-width">
                <div class="status-toggle">
                  <span class="toggle-label">Elemento Activo</span>
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
                <p class="field-hint" style="margin-top: 0.5rem;">Los elementos inactivos no se muestran en los listados</p>
              </div>
            </div>

            <!-- Preview Section -->
            <div v-if="form.categoria || form.nombre" class="preview-section">
              <h4 class="preview-title">Vista Previa</h4>
              <div class="preview-card">
                <div class="preview-icon" :style="{ background: form.is_active ? 'var(--teal-soft)' : 'var(--mist)' }">
                  <UIcon name="i-heroicons-tag" class="w-5 h-5" :style="{ color: form.is_active ? 'var(--teal)' : 'var(--ink-soft)' }" />
                </div>
                <div class="preview-info">
                  <span class="preview-name">{{ form.nombre || 'Nombre no definido' }}</span>
                  <span class="preview-dates">
                    <span class="preview-category">{{ form.categoria ? formatCategoria(form.categoria) : 'Sin categoría' }}</span>
                    <span v-if="form.codigo" class="preview-code">• {{ form.codigo }}</span>
                  </span>
                </div>
                <span class="preview-status" :class="form.is_active ? 'status-active' : 'status-inactive'">
                  <UIcon :name="form.is_active ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" />
                  {{ form.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="error" class="error-banner">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
              {{ error }}
            </div>

            <!-- Actions -->
            <div class="catalogo-edit-actions">
              <div class="action-spacer"></div>
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
                  :to="`/sigarh/infraestructura/catalogos?tenant=${tenant}`"
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
      <div class="catalogo-edit-sidebar">
        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Resumen</h4>
          </div>
          <div class="widget-content">
            <div class="widget-progress">
              <span class="widget-progress-label">Progreso</span>
              <div class="widget-progress-bar">
                <div 
                  class="widget-progress-fill" 
                  :style="{ width: progressPercentage + '%' }"
                />
              </div>
              <span class="widget-progress-value">{{ progressPercentage }}%</span>
            </div>

            <div class="summary-item">
              <span class="summary-label">Categoría</span>
              <span class="summary-value">{{ form.categoria ? formatCategoria(form.categoria) : '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Código</span>
              <span class="summary-value font-mono-data">{{ form.codigo || '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Nombre</span>
              <span class="summary-value">{{ form.nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Orden</span>
              <span class="summary-value">{{ form.orden || '0' }}</span>
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
                <p class="tip-title">Tip</p>
                <p class="tip-text">
                  El código no puede modificarse. Actualiza el nombre y descripción 
                  según sea necesario para mantener la información actualizada.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats Widget -->
        <div class="widget widget-quick-stats">
          <div class="widget-header">
            <UIcon name="i-heroicons-chart-bar" class="widget-icon" style="color: var(--navy)" />
            <h4 class="widget-title">Estadísticas</h4>
          </div>
          <div class="widget-content">
            <div class="stat-item">
              <span class="stat-label">Campos Completos</span>
              <span class="stat-number">{{ filledFields }}/{{ totalFields }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Estado</span>
              <span class="stat-number" :style="{ color: form.is_active ? 'var(--green)' : 'var(--ink-soft)' }">
                {{ form.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Categoría</span>
              <span class="stat-number" :style="{ color: form.categoria ? 'var(--teal)' : 'var(--ink-soft)' }">
                {{ form.categoria ? '✓' : '—' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-content" style="background: var(--paper); border-radius: var(--radius-lg)">
        <div class="modal-header">
          <div class="modal-icon" style="background: var(--alert-soft)">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6" style="color: var(--alert)" />
          </div>
          <h3 class="modal-title">Confirmar Eliminación</h3>
        </div>
        <p class="modal-body">
          ¿Estás seguro de que deseas eliminar el catálogo <strong>{{ form.nombre }}</strong>?
          <br>
          <span style="color: var(--ink-soft); font-size: 0.875rem">
            Esta acción no se puede deshacer y eliminará todos los datos asociados.
          </span>
        </p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-danger" @click="deleteItem">
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            Eliminar Permanentemente
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Editar Catálogo' })

const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()

const tenant = route.query.tenant as string
const id = route.params.id as string

const CATEGORIAS = [
  'tipos_documento', 'tipos_servicio', 'modalidades_atencion',
  'estados_cita', 'tipos_diagnostico', 'tipos_alta',
  'procedencia_emergencia', 'tipos_grupo_ocupacional', 'metodos_pago',
  'tipos_producto', 'estados_emergencia', 'destino_atencion',
  'tipos_comprobante', 'estados_comprobante',
]

const form = reactive({
  categoria: '',
  codigo: '',
  nombre: '',
  descripcion: '',
  orden: 0,
  is_active: true,
})

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const showDeleteModal = ref(false)

const errors = reactive({
  categoria: '',
  codigo: '',
  nombre: '',
})

const filledFields = computed(() => {
  let count = 0
  if (form.categoria) count++
  if (form.codigo) count++
  if (form.nombre) count++
  if (form.descripcion) count++
  return count
})

const totalFields = 4

const progressPercentage = computed(() => {
  let progress = 0
  if (form.categoria) progress += 25
  if (form.codigo) progress += 25
  if (form.nombre) progress += 25
  if (form.descripcion) progress += 25
  return progress
})

const formatCategoria = (categoria: string) => {
  return categoria
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (l) => l.toUpperCase())
}

const validateForm = (): boolean => {
  let valid = true
  if (!form.categoria) {
    errors.categoria = 'La categoría es requerida'
    valid = false
  }
  if (!form.codigo) {
    errors.codigo = 'El código es requerido'
    valid = false
  }
  if (!form.nombre) {
    errors.nombre = 'El nombre es requerido'
    valid = false
  }
  return valid
}

const confirmarEliminar = () => {
  showDeleteModal.value = true
}

const deleteItem = async () => {
  try {
    await $api(`/sigarh/infraestructura/catalogos/${id}`, {
      method: 'DELETE',
      tenant
    })
    router.push(`/sigarh/infraestructura/catalogos?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo eliminar el catálogo'
  } finally {
    showDeleteModal.value = false
  }
}

async function guardar() {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    await $api(`/sigarh/infraestructura/catalogos/${id}`, {
      method: 'PATCH',
      tenant,
      body: {
        categoria: form.categoria,
        nombre: form.nombre,
        descripcion: form.descripcion || null,
        orden: form.orden || 0,
        is_active: form.is_active,
      }
    })
    router.push(`/sigarh/infraestructura/catalogos?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar los cambios'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const data = await $api(`/sigarh/infraestructura/catalogos/${id}`, { tenant })
    Object.assign(form, data)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar el catálogo'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.catalogo-edit-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Progress Steps */
.onboarding-progress {
  margin-bottom: 2rem;
}

.progress-steps {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  background: var(--paper);
  border: 1px solid var(--line);
  opacity: 0.5;
  transition: all 0.3s ease;
}

.step-item.active {
  opacity: 1;
  border-color: var(--teal);
  background: var(--teal-soft);
}

.step-item.completed {
  opacity: 1;
  border-color: var(--teal);
  background: rgba(8, 145, 178, 0.08);
}

.step-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  background: var(--mist);
  color: var(--ink-soft);
  transition: all 0.3s ease;
}

.step-item.active .step-circle {
  background: var(--teal);
  color: white;
}

.step-item.completed .step-circle {
  background: var(--teal);
  color: white;
}

.step-check {
  font-size: 0.875rem;
}

.step-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
}

/* Grid */
.catalogo-edit-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.catalogo-edit-main {
  min-width: 0;
}

.catalogo-edit-sidebar {
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

.dni-display {
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

.btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--alert);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background: var(--alert-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Cards */
.catalogo-edit-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
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

/* Código Section */
.codigo-section {
  background: var(--mist);
  border-radius: var(--radius);
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.codigo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.codigo-header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.codigo-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.codigo-display-field {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.codigo-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.codigo-hint {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  background: var(--line);
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

.input-clinical.input-readonly {
  background: var(--mist);
  color: var(--ink-soft);
  cursor: not-allowed;
}

.input-clinical.input-readonly:focus {
  box-shadow: none;
  border-color: var(--line);
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

.preview-dates {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.preview-category {
  font-weight: 500;
}

.preview-code {
  font-family: monospace;
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

.status-active {
  background: var(--green-soft);
  color: var(--green);
}

.status-inactive {
  background: var(--mist);
  color: var(--ink-soft);
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

/* Actions */
.catalogo-edit-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1.5rem;
  margin-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.action-spacer {
  flex: 1;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
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

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--mist);
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
.widget-progress {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.widget-progress-label {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.widget-progress-bar {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: var(--mist);
  overflow: hidden;
}

.widget-progress-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--teal);
  transition: width 0.6s ease;
}

.widget-progress-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--teal);
}

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

/* Quick Stats Widget */
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

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  max-width: 420px;
  width: 100%;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.modal-body {
  color: var(--ink);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Animations */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Responsive */
@media (max-width: 1024px) {
  .catalogo-edit-grid {
    grid-template-columns: 1fr;
  }

  .catalogo-edit-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .catalogo-edit-container {
    padding: 1rem;
  }

  .progress-steps {
    flex-wrap: wrap;
  }

  .step-item {
    flex: 1;
    min-width: 120px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .catalogo-edit-sidebar {
    grid-template-columns: 1fr;
  }

  .catalogo-edit-actions {
    flex-wrap: wrap;
  }

  .action-group {
    flex-wrap: wrap;
    width: 100%;
  }

  .action-group > * {
    flex: 1;
    justify-content: center;
  }

  .page-subtitle {
    flex-wrap: wrap;
  }

  .codigo-header {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .codigo-display-field {
    flex-wrap: wrap;
  }

  .status-toggle {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .modal-content {
    margin: 1rem;
  }
}
</style>