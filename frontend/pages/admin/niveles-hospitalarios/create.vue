<!-- pages/admin/niveles-hospitalarios/create.vue -->
<template>
  <div class="create-level-container">
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

    <div class="onboarding-grid">
      <!-- Main Content -->
      <div class="onboarding-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink to="/admin/niveles-hospitalarios" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-building-library" class="w-3.5 h-3.5" />
              Niveles Hospitalarios
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Nuevo Nivel</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-building-office-2" class="w-6 h-6" style="color: var(--teal)" />
            </div>
            <div>
              <h1 class="text-2xl font-bold leading-tight" style="color: var(--ink)">Configurar Nivel Hospitalario</h1>
              <p class="text-sm" style="color: var(--ink-soft)">Define la estructura y módulos disponibles para este nivel</p>
            </div>
          </div>
        </div>

        <!-- Step 1: Basic Information -->
        <section class="onboarding-card" v-show="currentStep === 0">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-identification" class="w-4 h-4" style="color: var(--teal)" />
            </div>
            <div>
              <h3 class="card-title">Información Básica</h3>
              <p class="card-subtitle">Datos generales del nivel hospitalario</p>
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
        <section class="onboarding-card" v-show="currentStep === 1">
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
        <section class="onboarding-card" v-show="currentStep === 2">
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
        <div v-if="error" class="error-banner">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
          {{ error }}
        </div>

        <!-- Navigation Actions -->
        <div class="onboarding-actions">
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
            <button class="btn-primary" :disabled="saving" @click="handleCreate(false)">
              <UIcon v-if="saving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
              {{ saving ? 'Creando...' : 'Crear Nivel' }}
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
              to="/admin/niveles-hospitalarios"
              class="btn-cancel"
            >
              Cancelar
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Sidebar Widgets -->
      <div class="onboarding-sidebar">
        <!-- Onboarding Guide Widget -->
        <div class="widget widget-guide">
          <div class="widget-header">
            <UIcon name="i-heroicons-light-bulb" class="widget-icon" style="color: var(--amber)" />
            <h4 class="widget-title">Guía Rápida</h4>
          </div>
          <div class="widget-content">
            <div class="guide-item" :class="{ 'guide-active': currentStep === 0 }">
              <span class="guide-number">1</span>
              <div>
                <p class="guide-title">Información Básica</p>
                <p class="guide-desc">Define el código, nombre y color del nivel</p>
              </div>
            </div>
            <div class="guide-item" :class="{ 'guide-active': currentStep === 1 }">
              <span class="guide-number">2</span>
              <div>
                <p class="guide-title">Módulos App</p>
                <p class="guide-desc">Selecciona los módulos administrativos</p>
              </div>
            </div>
            <div class="guide-item" :class="{ 'guide-active': currentStep === 2 }">
              <span class="guide-number">3</span>
              <div>
                <p class="guide-title">Módulos SIGARH</p>
                <p class="guide-desc">Selecciona los módulos de RRHH</p>
              </div>
            </div>
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
              <span class="summary-label">Código</span>
              <span class="summary-value">{{ form.code || 'No definido' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Nombre</span>
              <span class="summary-value">{{ form.name || 'No definido' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Color</span>
              <div class="summary-color">
                <div class="color-dot" :style="{ background: form.color }"></div>
                <span>{{ form.color }}</span>
              </div>
            </div>
            <div class="summary-item">
              <span class="summary-label">Estado</span>
              <span class="summary-badge" :class="{ 'badge-active': form.is_active, 'badge-inactive': !form.is_active }">
                {{ form.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Módulos App</span>
              <span class="summary-value">{{ seleccionadosApp.length }} seleccionados</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Módulos SIGARH</span>
              <span class="summary-value">{{ seleccionadosSigarh.length }} seleccionados</span>
            </div>
            <div class="summary-total">
              <span>Total Módulos</span>
              <span class="total-number">{{ modulosSeleccionados.length }}</span>
            </div>
          </div>
        </div>

        <!-- Tips Widget -->
        <div class="widget widget-tips">
          <div class="widget-header">
            <UIcon name="i-heroicons-sparkles" class="widget-icon" style="color: var(--purple)" />
            <h4 class="widget-title">Consejos</h4>
          </div>
          <div class="widget-content">
            <ul class="tips-list">
              <li class="tip-item">
                <UIcon name="i-heroicons-check-circle" class="tip-icon" style="color: var(--teal)" />
                <span>Usa códigos MINSA estándar para facilitar la identificación</span>
              </li>
              <li class="tip-item">
                <UIcon name="i-heroicons-check-circle" class="tip-icon" style="color: var(--teal)" />
                <span>Los colores ayudan a distinguir niveles en el dashboard</span>
              </li>
              <li class="tip-item">
                <UIcon name="i-heroicons-check-circle" class="tip-icon" style="color: var(--teal)" />
                <span>Selecciona solo los módulos necesarios para cada nivel</span>
              </li>
              <li class="tip-item">
                <UIcon name="i-heroicons-check-circle" class="tip-icon" style="color: var(--teal)" />
                <span>Puedes ajustar la configuración más tarde</span>
              </li>
            </ul>
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

const { api } = useApi()
const router = useRouter()

const currentStep = ref(0)
const steps = ['Información Básica', 'Módulos App', 'Módulos SIGARH']

const saving = ref(false)
const loadingModulos = ref(true)
const error = ref('')
const modulosSeleccionados = ref<string[]>([])
const todosModulos = ref<Modulo[]>([])
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
  sort_order: 99,
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

const handleCreate = async (createAnother: boolean) => {
  if (!validateStep1()) {
    currentStep.value = 0
    return
  }

  saving.value = true
  error.value = ''
  try {
    await api('/admin/niveles-hospitalarios', {
      method: 'POST',
      body: {
        code: form.code,
        name: form.name,
        description: form.description || null,
        color: form.color,
        sort_order: form.sort_order,
        default_modules: { app: seleccionadosApp.value, sigarh: seleccionadosSigarh.value },
        default_roles: [],
      },
    })

    if (createAnother) {
      Object.assign(form, { code: '', name: '', description: '', color: '#6b7280', sort_order: 99, is_active: true })
      modulosSeleccionados.value = []
      currentStep.value = 0
    } else {
      router.push('/admin/niveles-hospitalarios')
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo crear el nivel'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    todosModulos.value = await api<Modulo[]>('/admin/modulos/catalogo')
  } finally {
    loadingModulos.value = false
  }
})
</script>

<style scoped>
/* Container */
.create-level-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid Layout */
.onboarding-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.onboarding-main {
  min-width: 0;
}

.onboarding-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Cards */
.onboarding-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  animation: slideIn 0.3s ease;
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

/* Navigation Actions */
.onboarding-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

/* Guide Widget */
.guide-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.625rem 0;
  border-bottom: 1px solid var(--line);
  opacity: 0.5;
  transition: all 0.3s ease;
}

.guide-item:last-child {
  border-bottom: none;
}

.guide-item.guide-active {
  opacity: 1;
}

.guide-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  background: var(--mist);
  color: var(--ink-soft);
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.guide-item.guide-active .guide-number {
  background: var(--teal);
  color: white;
}

.guide-title {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  margin: 0;
}

.guide-desc {
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
}

/* Summary Widget */
.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0;
}

.summary-color {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.color-dot {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid var(--line);
}

.summary-badge {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
}

.badge-active {
  background: var(--teal-soft);
  color: var(--teal);
}

.badge-inactive {
  background: var(--mist);
  color: var(--ink-soft);
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  border-top: 2px solid var(--line);
}

.total-number {
  background: var(--teal);
  color: white;
  padding: 0.125rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8125rem;
}

/* Tips Widget */
.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  padding: 0.375rem 0;
  font-size: 0.8125rem;
  color: var(--ink);
}

.tip-icon {
  width: 1rem;
  height: 1rem;
  margin-top: 0.125rem;
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .onboarding-grid {
    grid-template-columns: 1fr;
  }
  
  .onboarding-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .create-level-container {
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
  
  .onboarding-sidebar {
    grid-template-columns: 1fr;
  }
  
  .onboarding-actions {
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