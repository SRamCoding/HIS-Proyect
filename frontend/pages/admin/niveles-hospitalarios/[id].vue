<template>
  <div class="edit-level-container">
    <!-- Progress Indicator -->
    <div class="onboarding-progress">
      <div class="progress-steps">
        <div 
          v-for="(step, index) in steps" 
          :key="index"
          class="step-item"
          :class="{ 
            active: currentStep >= index, 
            completed: currentStep > index 
          }"
        >
          <div class="step-circle">
            <span v-if="currentStep > index" class="step-check">✓</span>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <span class="step-label">{{ step }}</span>
        </div>
      </div>
    </div>

    <div class="edit-grid">
      <!-- Main Content -->
      <div class="edit-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink to="/admin/niveles-hospitalarios" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-building-library" class="w-3.5 h-3.5" />
              Niveles Hospitalarios
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Editar</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" :style="{ background: form.color + '33' }">
              <UIcon name="i-heroicons-pencil-square" class="w-6 h-6" :style="{ color: form.color }" />
            </div>
            <div>
              <h1 class="page-title">Editar Nivel Hospitalario</h1>
              <p class="page-subtitle">
                <span class="level-badge" :style="{ background: form.color, color: getContrastColor(form.color) }">
                  {{ form.code || 'Código' }}
                </span>
                {{ form.name || 'Sin nombre' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando nivel hospitalario...</p>
        </div>

        <template v-else>
          <!-- Step 1: Basic Information -->
          <section class="edit-card" v-show="currentStep === 0">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-identification" class="w-4 h-4" style="color: var(--teal)" />
              </div>
              <div>
                <h3 class="card-title">Información Básica</h3>
                <p class="card-subtitle">Actualiza los datos generales del nivel</p>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Código MINSA <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-barcode" class="input-icon" />
                  <input 
                    v-model="form.code" 
                    class="input-clinical font-mono-data" 
                    placeholder="Ej: III-1"
                    :class="{ 'input-error': errors.code }"
                  />
                </div>
                <span v-if="errors.code" class="error-message">{{ errors.code }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Nombre <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-pencil" class="input-icon" />
                  <input 
                    v-model="form.name" 
                    class="input-clinical" 
                    placeholder="Ej: Hospital Nacional"
                    :class="{ 'input-error': errors.name }"
                  />
                </div>
                <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Descripción</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" />
                  <textarea 
                    v-model="form.description" 
                    class="input-clinical" 
                    rows="2" 
                    placeholder="Descripción opcional del nivel"
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Color Identificador <span class="required">*</span></label>
                <div class="color-picker-wrapper">
                  <input
                    type="color"
                    v-model="form.color"
                    class="color-picker-input"
                  />
                  <input 
                    v-model="form.color" 
                    class="input-clinical font-mono-data flex-1" 
                    placeholder="#6b7280"
                    :class="{ 'input-error': errors.color }"
                  />
                  <div class="color-preview" :style="{ background: form.color }"></div>
                </div>
                <span v-if="errors.color" class="error-message">{{ errors.color }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Orden de Visualización</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-arrows-up-down" class="input-icon" />
                  <input 
                    v-model.number="form.sort_order" 
                    type="number" 
                    class="input-clinical font-mono-data" 
                    min="0"
                  />
                </div>
              </div>

              <div class="form-group full-width">
                <div class="status-toggle">
                  <div class="status-preview">
                    <div
                      class="status-badge"
                      :style="{ 
                        background: form.color + '22', 
                        color: form.color,
                        borderColor: form.color + '44'
                      }"
                    >
                      <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" />
                      <span>{{ form.code || 'Código' }} — {{ form.name || 'Nombre del nivel' }}</span>
                    </div>
                    <span class="preview-label">Vista previa de la etiqueta</span>
                  </div>
                  <label class="toggle-container">
                    <span class="toggle-label">Activo</span>
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
                  </label>
                </div>
              </div>
            </div>
          </section>

          <!-- Step 2: App Modules -->
          <section class="edit-card" v-show="currentStep === 1">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--purple-soft)">
                <UIcon name="i-heroicons-squares-plus" class="w-4 h-4" style="color: var(--purple)" />
              </div>
              <div>
                <h3 class="card-title">Módulos App</h3>
                <p class="card-subtitle">Selecciona los módulos disponibles en el panel administrativo</p>
              </div>
            </div>

            <div class="module-controls">
              <div class="module-actions">
                <button class="action-btn action-select" @click="seleccionarTodos('app')">
                  <UIcon name="i-heroicons-check-circle" class="w-4 h-4" />
                  Seleccionar todos
                </button>
                <button class="action-btn action-clear" @click="limpiarCategoria('app')">
                  <UIcon name="i-heroicons-x-circle" class="w-4 h-4" />
                  Limpiar
                </button>
              </div>
              <span class="module-counter">
                {{ seleccionadosApp.length }}/{{ modulosApp.length }}
              </span>
            </div>

            <div v-if="loadingModulos" class="module-skeleton">
              <div v-for="i in 6" :key="i" class="skeleton-chip" />
            </div>
            <div v-else class="module-grid">
              <button
                v-for="mod in modulosApp"
                :key="mod.code"
                type="button"
                class="module-chip"
                :class="{ 'module-chip--active': modulosSeleccionados.includes(mod.code) }"
                @click="toggleModulo(mod.code)"
              >
                <UIcon
                  :name="modulosSeleccionados.includes(mod.code) ? 'i-heroicons-check-circle-solid' : 'i-heroicons-plus-circle'"
                  class="w-4 h-4 shrink-0"
                />
                <span class="truncate">{{ mod.name }}</span>
                <span v-if="modulosSeleccionados.includes(mod.code)" class="chip-badge">✓</span>
              </button>
            </div>
          </section>

          <!-- Step 3: SIGARH Modules -->
          <section class="edit-card" v-show="currentStep === 2">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--navy-soft)">
                <UIcon name="i-heroicons-rectangle-stack" class="w-4 h-4" style="color: var(--navy)" />
              </div>
              <div>
                <h3 class="card-title">Módulos SIGARH</h3>
                <p class="card-subtitle">Selecciona los módulos disponibles en el panel de RRHH</p>
              </div>
            </div>

            <div class="module-controls">
              <div class="module-actions">
                <button class="action-btn action-select" @click="seleccionarTodos('sigarh')">
                  <UIcon name="i-heroicons-check-circle" class="w-4 h-4" />
                  Seleccionar todos
                </button>
                <button class="action-btn action-clear" @click="limpiarCategoria('sigarh')">
                  <UIcon name="i-heroicons-x-circle" class="w-4 h-4" />
                  Limpiar
                </button>
              </div>
              <span class="module-counter">
                {{ seleccionadosSigarh.length }}/{{ modulosSigarh.length }}
              </span>
            </div>

            <div v-if="loadingModulos" class="module-skeleton">
              <div v-for="i in 6" :key="i" class="skeleton-chip" />
            </div>
            <div v-else class="module-grid">
              <button
                v-for="mod in modulosSigarh"
                :key="mod.code"
                type="button"
                class="module-chip"
                :class="{ 'module-chip--active': modulosSeleccionados.includes(mod.code) }"
                @click="toggleModulo(mod.code)"
              >
                <UIcon
                  :name="modulosSeleccionados.includes(mod.code) ? 'i-heroicons-check-circle-solid' : 'i-heroicons-plus-circle'"
                  class="w-4 h-4 shrink-0"
                />
                <span class="truncate">{{ mod.name }}</span>
                <span v-if="modulosSeleccionados.includes(mod.code)" class="chip-badge">✓</span>
              </button>
            </div>
          </section>

          <!-- Error Message -->
          <div v-if="saveError" class="error-banner">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ saveError }}
          </div>

          <!-- Navigation Actions -->
          <div class="edit-actions">
            <button 
              v-if="currentStep > 0"
              class="btn-secondary"
              @click="currentStep--"
            >
              <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
              Anterior
            </button>
            
            <div class="action-spacer"></div>

            <button 
              v-if="currentStep < 2"
              class="btn-primary"
              @click="nextStep"
            >
              Siguiente
              <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
            </button>

            <div v-else class="action-group">
              <button class="btn-primary" :disabled="saving" @click="handleSave">
                <UIcon v-if="saving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
              </button>
              <NuxtLink
                to="/admin/niveles-hospitalarios"
                class="btn-cancel"
              >
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </template>
      </div>

      <!-- Sidebar Widgets -->
      <div class="edit-sidebar">
        <!-- Info Widget -->
        <div class="widget widget-info">
          <div class="widget-header">
            <UIcon name="i-heroicons-information-circle" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Información del Nivel</h4>
          </div>
          <div class="widget-content">
            <div class="info-item">
              <span class="info-label">ID</span>
              <span class="info-value font-mono-data">#{{ id }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Código</span>
              <span class="info-value">
                <span class="mini-badge" :style="{ background: form.color, color: getContrastColor(form.color) }">
                  {{ form.code || '—' }}
                </span>
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">Nombre</span>
              <span class="info-value">{{ form.name || '—' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Estado</span>
              <span class="info-value">
                <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
                  <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
                  {{ form.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </span>
            </div>
          </div>
        </div>

        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--amber)" />
            <h4 class="widget-title">Resumen de Configuración</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Módulos App</span>
              <span class="summary-value">{{ seleccionadosApp.length }} seleccionados</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Módulos SIGARH</span>
              <span class="summary-value">{{ seleccionadosSigarh.length }} seleccionados</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-total">
              <span>Total Módulos</span>
              <span class="total-number">{{ modulosSeleccionados.length }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-actions">
              <button class="summary-btn" @click="resetToOriginal">
                <UIcon name="i-heroicons-arrow-uturn-left" class="w-4 h-4" />
                Restaurar original
              </button>
            </div>
          </div>
        </div>

        <!-- Module Distribution Widget -->
        <div class="widget widget-distribution">
          <div class="widget-header">
            <UIcon name="i-heroicons-chart-pie" class="widget-icon" style="color: var(--purple)" />
            <h4 class="widget-title">Distribución</h4>
          </div>
          <div class="widget-content">
            <div class="distribution-item">
              <div class="distribution-label">
                <span class="distribution-dot" style="background: var(--teal)"></span>
                <span>App</span>
              </div>
              <div class="distribution-bar">
                <div 
                  class="distribution-fill" 
                  :style="{ 
                    width: getDistributionPercentage('app') + '%',
                    background: 'var(--teal)'
                  }"
                />
              </div>
              <span class="distribution-value">{{ seleccionadosApp.length }}</span>
            </div>
            <div class="distribution-item">
              <div class="distribution-label">
                <span class="distribution-dot" style="background: var(--navy)"></span>
                <span>SIGARH</span>
              </div>
              <div class="distribution-bar">
                <div 
                  class="distribution-fill" 
                  :style="{ 
                    width: getDistributionPercentage('sigarh') + '%',
                    background: 'var(--navy)'
                  }"
                />
              </div>
              <span class="distribution-value">{{ seleccionadosSigarh.length }}</span>
            </div>
            <div class="distribution-total">
              <span>Total: {{ modulosSeleccionados.length }}</span>
            </div>
          </div>
        </div>

        <!-- Quick Actions Widget -->
        <div class="widget widget-actions">
          <div class="widget-header">
            <UIcon name="i-heroicons-bolt" class="widget-icon" style="color: var(--green)" />
            <h4 class="widget-title">Acciones Rápidas</h4>
          </div>
          <div class="widget-content">
            <button class="quick-action" @click="currentStep = 0">
              <UIcon name="i-heroicons-identification" class="w-4 h-4" />
              Información Básica
            </button>
            <button class="quick-action" @click="currentStep = 1">
              <UIcon name="i-heroicons-squares-plus" class="w-4 h-4" />
              Módulos App
            </button>
            <button class="quick-action" @click="currentStep = 2">
              <UIcon name="i-heroicons-rectangle-stack" class="w-4 h-4" />
              Módulos SIGARH
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Modulo {
  code: string
  name: string
  category: 'app' | 'sigarh'
}

interface Nivel {
  id: number
  code: string
  name: string
  description: string
  color: string
  sort_order: number
  is_active: boolean
  default_modules: {
    app: string[]
    sigarh: string[]
  }
}

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const id = computed(() => route.params.id as string)
const currentStep = ref(0)
const steps = ['Información Básica', 'Módulos App', 'Módulos SIGARH']

const loading = ref(true)
const loadingModulos = ref(true)
const saving = ref(false)
const saveError = ref('')
const modulosSeleccionados = ref<string[]>([])
const todosModulos = ref<Modulo[]>([])
const originalModules = ref<string[]>([])
const errors = reactive({
  code: '',
  name: '',
  color: ''
})

const form = reactive({
  code: '',
  name: '',
  description: '',
  color: '#6b7280',
  sort_order: 0,
  is_active: true,
})

const modulosApp = computed(() => todosModulos.value.filter(m => m.category === 'app'))
const modulosSigarh = computed(() => todosModulos.value.filter(m => m.category === 'sigarh'))
const seleccionadosApp = computed(() => modulosSeleccionados.value.filter(c => modulosApp.value.some(m => m.code === c)))
const seleccionadosSigarh = computed(() => modulosSeleccionados.value.filter(c => modulosSigarh.value.some(m => m.code === c)))

const toggleModulo = (code: string) => {
  const i = modulosSeleccionados.value.indexOf(code)
  if (i === -1) modulosSeleccionados.value.push(code)
  else modulosSeleccionados.value.splice(i, 1)
}

const seleccionarTodos = (category: 'app' | 'sigarh') => {
  const lista = category === 'app' ? modulosApp.value : modulosSigarh.value
  lista.forEach(m => {
    if (!modulosSeleccionados.value.includes(m.code)) modulosSeleccionados.value.push(m.code)
  })
}

const limpiarCategoria = (category: 'app' | 'sigarh') => {
  const lista = category === 'app' ? modulosApp.value : modulosSigarh.value
  const codes = new Set(lista.map(m => m.code))
  modulosSeleccionados.value = modulosSeleccionados.value.filter(c => !codes.has(c))
}

const nextStep = () => {
  if (currentStep.value === 0 && !validateStep1()) return
  if (currentStep.value < 2) currentStep.value++
}

const validateStep1 = (): boolean => {
  let valid = true
  errors.code = !form.code ? 'El código es requerido' : ''
  errors.name = !form.name ? 'El nombre es requerido' : ''
  errors.color = !form.color ? 'El color es requerido' : ''
  if (errors.code || errors.name || errors.color) valid = false
  return valid
}

const getContrastColor = (hex: string) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.5 ? '#000000' : '#FFFFFF'
}

const getDistributionPercentage = (category: 'app' | 'sigarh') => {
  const total = modulosSeleccionados.value.length
  if (total === 0) return 0
  const count = category === 'app' ? seleccionadosApp.value.length : seleccionadosSigarh.value.length
  return Math.round((count / total) * 100)
}

const resetToOriginal = () => {
  modulosSeleccionados.value = [...originalModules.value]
}

const handleSave = async () => {
  if (!validateStep1()) {
    currentStep.value = 0
    return
  }

  saving.value = true
  saveError.value = ''
  try {
    const appMods = modulosSeleccionados.value.filter(c => modulosApp.value.some(m => m.code === c))
    const sigarhMods = modulosSeleccionados.value.filter(c => modulosSigarh.value.some(m => m.code === c))

    await api(`/admin/niveles-hospitalarios/${id.value}`, {
      method: 'PATCH',
      body: {
        code: form.code,
        name: form.name,
        description: form.description || null,
        color: form.color,
        sort_order: form.sort_order,
        is_active: form.is_active,
        default_modules: { app: appMods, sigarh: sigarhMods },
      },
    })
    router.push('/admin/niveles-hospitalarios')
  } catch (e: any) {
    saveError.value = e?.data?.detail || 'No se pudo guardar el nivel'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [nivel, modulos] = await Promise.all([
      api<Nivel>(`/admin/niveles-hospitalarios/${id.value}`),
      api<Modulo[]>('/admin/modulos/catalogo'),
    ])

    form.code = nivel.code
    form.name = nivel.name
    form.description = nivel.description || ''
    form.color = nivel.color || '#6b7280'
    form.sort_order = nivel.sort_order || 0
    form.is_active = nivel.is_active !== undefined ? nivel.is_active : true

    todosModulos.value = modulos
    const selected = [
      ...(nivel.default_modules?.app || []),
      ...(nivel.default_modules?.sigarh || []),
    ]
    modulosSeleccionados.value = selected
    originalModules.value = selected
  } catch (e: any) {
    saveError.value = 'No se pudo cargar el nivel'
  } finally {
    loading.value = false
    loadingModulos.value = false
  }
})
</script>

<style scoped>
.edit-level-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Progress Steps */
.onboarding-progress {
  margin-bottom: 2rem;
}

/* Grid Layout */
.edit-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
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

.level-badge {
  display: inline-block;
  padding: 0.125rem 0.625rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  font-family: monospace;
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

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Cards */
.edit-card {
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

/* Form */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

/* Color Picker */
.color-picker-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Status Toggle */
.status-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: var(--mist);
  border-radius: 12px;
}

/* Module Controls */
.module-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

/* Module Grid */
.module-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.625rem;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Navigation Actions */
.edit-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

/* Info Widget */
.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0;
  border-bottom: 1px solid var(--line);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.info-value {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
}

.mini-badge {
  display: inline-block;
  padding: 0.0625rem 0.5rem;
  border-radius: 3px;
  font-size: 0.6875rem;
  font-weight: 700;
  font-family: monospace;
}

.status-badge-mini {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
}

/* Summary Widget */
.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.total-number {
  background: var(--teal);
  color: white;
  padding: 0.0625rem 0.625rem;
  border-radius: 12px;
  font-size: 0.8125rem;
}

.summary-actions {
  padding-top: 0.5rem;
}

.summary-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: transparent;
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  justify-content: center;
}

.summary-btn:hover {
  background: var(--mist);
  color: var(--ink);
}

/* Distribution Widget */
.distribution-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.375rem 0;
}

.distribution-label {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: var(--ink);
  min-width: 70px;
}

.distribution-bar {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: var(--mist);
  overflow: hidden;
}

.distribution-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.distribution-value {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  min-width: 24px;
  text-align: right;
}

.distribution-total {
  text-align: center;
  font-size: 0.8125rem;
  color: var(--ink-soft);
  padding-top: 0.5rem;
  border-top: 1px solid var(--line);
  margin-top: 0.5rem;
}

/* Quick Actions Widget */
.quick-action {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--ink);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* Responsive */
@media (max-width: 1024px) {
  .edit-grid {
    grid-template-columns: 1fr;
  }
  
  .edit-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .edit-level-container {
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
  
  .module-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .edit-sidebar {
    grid-template-columns: 1fr;
  }
  
  .edit-actions {
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
}

@media (max-width: 480px) {
  .module-grid {
    grid-template-columns: 1fr;
  }
  
  .status-toggle {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .color-picker-wrapper {
    flex-wrap: wrap;
  }
}
</style>