<template>
  <div class="hospital-edit-container">
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
            <NuxtLink to="/admin/hospitales" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-building-office-2" class="w-3.5 h-3.5" />
              Hospitales
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Editar</span>
          </div>
          <div class="flex items-center justify-between gap-4">
            <div class="flex items-center gap-4">
              <div class="header-icon" :style="{ background: form.is_active ? 'var(--teal-soft)' : 'var(--mist)' }">
                <UIcon 
                  name="i-heroicons-building-office-2" 
                  class="w-6 h-6" 
                  :style="{ color: form.is_active ? 'var(--teal)' : 'var(--ink-soft)' }" 
                />
              </div>
              <div>
                <h1 class="page-title">{{ form.name || 'Editar Hospital' }}</h1>
                <p class="page-subtitle">
                  <span class="domain-display font-mono-data">{{ subdomain ? `${subdomain}.erp.local` : '—' }}</span>
                  <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
                  <span class="status-text-mini" :class="form.is_active ? 'text-active' : 'text-inactive'">
                    {{ form.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </p>
              </div>
            </div>
            <button
              class="btn-danger"
              @click="confirmDelete"
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
          <p style="color: var(--ink-soft)">Cargando información del hospital...</p>
        </div>

        <template v-else>
          <!-- Step 1: Identidad -->
          <section class="edit-card" v-show="currentStep === 0">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-identification" class="w-4 h-4" style="color: var(--teal)" />
              </div>
              <div>
                <h3 class="card-title">Identidad del Hospital</h3>
                <p class="card-subtitle">Datos principales del establecimiento</p>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group full-width">
                <label class="form-label">Nombre Oficial <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-building-office-2" class="input-icon" />
                  <input 
                    v-model="form.name" 
                    class="input-clinical" 
                    placeholder="Ej: Hospital Túmán"
                    :class="{ 'input-error': errors.name }"
                  />
                </div>
                <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Subdominio</label>
                <div class="subdomain-display-field">
                  <UIcon name="i-heroicons-globe-alt" class="input-icon" />
                  <span class="subdomain-text font-mono-data">{{ subdomain || '—' }}</span>
                  <span class="subdomain-suffix">.erp.local</span>
                </div>
                <p class="field-hint">El subdominio no puede modificarse después de la creación</p>
              </div>

              <div class="form-group">
                <label class="form-label">Nivel del Establecimiento</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-building-library" class="input-icon" />
                  <input 
                    v-model="form.hospital_level" 
                    class="input-clinical" 
                    placeholder="Ej: III-1"
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">RUC</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document" class="input-icon" />
                  <input 
                    v-model="form.ruc" 
                    class="input-clinical font-mono-data" 
                    placeholder="20123456789"
                    maxlength="11"
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Teléfono</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-phone" class="input-icon" />
                  <input 
                    v-model="form.phone" 
                    class="input-clinical" 
                    placeholder="(01) 234-5678"
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Email</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-envelope" class="input-icon" />
                  <input 
                    v-model="form.email" 
                    type="email" 
                    class="input-clinical" 
                    placeholder="contacto@hospital.pe"
                  />
                </div>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Dirección</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-map-pin" class="input-icon" />
                  <input 
                    v-model="form.address" 
                    class="input-clinical" 
                    placeholder="Av. Principal 123, Lima"
                  />
                </div>
              </div>

              <div class="form-group full-width">
                <div class="status-toggle">
                  <span class="toggle-label">Hospital Activo</span>
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
              </div>
            </div>
          </section>

          <!-- Step 2: Misión, Visión y Valores -->
          <section class="edit-card" v-show="currentStep === 1">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--purple-soft)">
                <UIcon name="i-heroicons-flag" class="w-4 h-4" style="color: var(--purple)" />
              </div>
              <div>
                <h3 class="card-title">Misión, Visión y Valores</h3>
                <p class="card-subtitle">Identidad institucional del hospital</p>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group full-width">
                <label class="form-label">Misión</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-target" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea 
                    v-model="form.mission" 
                    class="input-clinical" 
                    rows="3" 
                    placeholder="Describir la misión del hospital..."
                  />
                </div>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Visión</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-eye" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea 
                    v-model="form.vision" 
                    class="input-clinical" 
                    rows="3" 
                    placeholder="Describir la visión del hospital..."
                  />
                </div>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Valores</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-heart" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea 
                    v-model="form.values" 
                    class="input-clinical" 
                    rows="3" 
                    placeholder="Listar los valores del hospital..."
                  />
                </div>
              </div>
            </div>
          </section>

          <!-- Step 3: Módulos App -->
          <section class="edit-card" v-show="currentStep === 2">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--green-soft)">
                <UIcon name="i-heroicons-squares-plus" class="w-4 h-4" style="color: var(--green)" />
              </div>
              <div>
                <h3 class="card-title">Módulos App</h3>
                <p class="card-subtitle">Módulos clínicos y administrativos del panel principal</p>
              </div>
            </div>

            <div class="module-controls">
              <div class="module-actions">
                <div class="search-wrapper-small">
                  <UIcon name="i-heroicons-magnifying-glass" class="search-icon-small" />
                  <input
                    v-model="searchModApp"
                    type="text"
                    placeholder="Buscar módulo..."
                    class="search-input-small"
                    style="border: 1px solid var(--line); background: var(--paper)"
                  />
                </div>
                <button class="action-btn action-clear" @click="deseleccionarTodos('app')">
                  <UIcon name="i-heroicons-x-circle" class="w-4 h-4" />
                  Deseleccionar todos
                </button>
              </div>
              <span class="module-counter">
                {{ activosApp }}/{{ modulosApp.length }}
              </span>
            </div>

            <div class="module-grid">
              <label
                v-for="mod in modulosFiltradosApp"
                :key="mod.code"
                class="module-check"
                :class="{ 'module-check--active': modulosActivos.includes(mod.code) }"
                style="border: 1px solid var(--line)"
              >
                <input
                  type="checkbox"
                  :value="mod.code"
                  v-model="modulosActivos"
                  class="module-check-input"
                />
                <span class="module-check-label">{{ mod.name }}</span>
              </label>
            </div>
          </section>

          <!-- Step 4: Módulos SIGARH -->
          <section class="edit-card" v-show="currentStep === 3">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--navy-soft)">
                <UIcon name="i-heroicons-folder-open" class="w-4 h-4" style="color: var(--navy)" />
              </div>
              <div>
                <h3 class="card-title">Módulos SIGARH</h3>
                <p class="card-subtitle">Módulos de configuración y recursos humanos</p>
              </div>
            </div>

            <div class="module-controls">
              <div class="module-actions">
                <div class="search-wrapper-small">
                  <UIcon name="i-heroicons-magnifying-glass" class="search-icon-small" />
                  <input
                    v-model="searchModSigarh"
                    type="text"
                    placeholder="Buscar módulo..."
                    class="search-input-small"
                    style="border: 1px solid var(--line); background: var(--paper)"
                  />
                </div>
                <button class="action-btn action-clear" @click="deseleccionarTodos('sigarh')">
                  <UIcon name="i-heroicons-x-circle" class="w-4 h-4" />
                  Deseleccionar todos
                </button>
              </div>
              <span class="module-counter">
                {{ activosSigarh }}/{{ modulosSigarh.length }}
              </span>
            </div>

            <div class="module-grid">
              <label
                v-for="mod in modulosFiltradosSigarh"
                :key="mod.code"
                class="module-check"
                :class="{ 'module-check--active': modulosActivos.includes(mod.code) }"
                style="border: 1px solid var(--line)"
              >
                <input
                  type="checkbox"
                  :value="mod.code"
                  v-model="modulosActivos"
                  class="module-check-input"
                />
                <span class="module-check-label">{{ mod.name }}</span>
              </label>
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
              v-if="currentStep < 3"
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
                to="/admin/hospitales"
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
        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Resumen</h4>
          </div>
          <div class="widget-content">
            <div class="widget-progress">
              <span class="widget-progress-label">Módulos</span>
              <div class="widget-progress-bar">
                <div 
                  class="widget-progress-fill" 
                  :style="{ width: moduleProgress + '%' }"
                />
              </div>
              <span class="widget-progress-value">{{ modulosActivos.length }}/{{ todosModulos.length }}</span>
            </div>

            <div class="summary-item">
              <span class="summary-label">Hospital</span>
              <span class="summary-value">{{ form.name || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Dominio</span>
              <span class="summary-value font-mono-data">{{ subdomain ? `${subdomain}.erp.local` : '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Nivel</span>
              <span class="summary-value">{{ form.hospital_level || '—' }}</span>
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
            <div class="summary-divider"></div>
            <div class="distribution-summary">
              <div class="distribution-bar">
                <div 
                  class="distribution-fill app" 
                  :style="{ width: appPercentage + '%' }"
                />
                <div 
                  class="distribution-fill sigarh" 
                  :style="{ width: sigarhPercentage + '%' }"
                />
              </div>
              <div class="distribution-labels">
                <span class="distribution-label">
                  <span class="distribution-dot" style="background: var(--green)"></span>
                  App {{ activosApp }}
                </span>
                <span class="distribution-label">
                  <span class="distribution-dot" style="background: var(--navy)"></span>
                  SIGARH {{ activosSigarh }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Access Widget -->
        <div class="widget widget-quick">
          <div class="widget-header">
            <UIcon name="i-heroicons-rocket-launch" class="widget-icon" style="color: var(--amber)" />
            <h4 class="widget-title">Accesos Rápidos</h4>
          </div>
          <div class="widget-content">
            <button class="quick-action" @click="irA('')">
              <UIcon name="i-heroicons-globe-alt" class="w-4 h-4" style="color: var(--teal)" />
              <span>Ver Landing</span>
              <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3.5 h-3.5 ml-auto" style="color: var(--ink-soft)" />
            </button>
              <button class="quick-action" @click="irA('/app')">
                <UIcon name="i-heroicons-squares-2x2" class="w-4 h-4" style="color: var(--green)" />
                <span>Panel Hospitalario</span>
                <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3.5 h-3.5 ml-auto" style="color: var(--ink-soft)" />
              </button>
            <button class="quick-action" @click="irA('/sigarh')">
              <UIcon name="i-heroicons-folder-open" class="w-4 h-4" style="color: var(--navy)" />
              <span>Panel SIGARH</span>
              <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3.5 h-3.5 ml-auto" style="color: var(--ink-soft)" />
            </button>
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
                  Los cambios en módulos se aplican de inmediato al guardar. Desactivar un módulo no elimina los datos ya registrados.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats Widget -->
        <div class="widget widget-stats">
          <div class="widget-header">
            <UIcon name="i-heroicons-chart-bar" class="widget-icon" style="color: var(--purple)" />
            <h4 class="widget-title">Estadísticas</h4>
          </div>
          <div class="widget-content">
            <div class="stat-item">
              <span class="stat-label">Total Módulos</span>
              <span class="stat-number">{{ todosModulos.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Módulos Activos</span>
              <span class="stat-number">{{ modulosActivos.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Tasa Activación</span>
              <span class="stat-number">{{ moduleProgress }}%</span>
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
          ¿Estás seguro de que deseas eliminar el hospital <strong>{{ form.name }}</strong>?
          <br>
          <span style="color: var(--ink-soft); font-size: 0.875rem">
            Esta acción no se puede deshacer y eliminará todos los datos asociados.
          </span>
        </p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-danger" @click="handleDelete">
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            Eliminar Permanentemente
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Modulo {
  id: string
  code: string
  name: string
  category: 'app' | 'sigarh'
}

interface Hospital {
  id: string
  name: string
  domain: string
  hospital_level: string
  ruc: string
  phone: string
  email: string
  address: string
  mission: string
  vision: string
  values: string
  is_active: boolean
  active_modules: string[]
}

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const id = computed(() => route.params.id as string)
const steps = ['Identidad', 'Misión y Visión', 'Módulos App', 'Módulos SIGARH']

const currentStep = ref(0)
const loading = ref(true)
const saving = ref(false)
const saveError = ref('')
const showDeleteModal = ref(false)

const searchModApp = ref('')
const searchModSigarh = ref('')
const modulosActivos = ref<string[]>([])
const todosModulos = ref<Modulo[]>([])
const subdomain = ref('')

const errors = reactive({
  name: ''
})

const form = reactive({
  name: '',
  hospital_level: '',
  ruc: '',
  phone: '',
  email: '',
  address: '',
  mission: '',
  vision: '',
  values: '',
  is_active: true,
})

const modulosApp = computed(() => todosModulos.value.filter(m => m.category === 'app'))
const modulosSigarh = computed(() => todosModulos.value.filter(m => m.category === 'sigarh'))

const modulosFiltradosApp = computed(() =>
  modulosApp.value.filter(m => 
    !searchModApp.value || m.name.toLowerCase().includes(searchModApp.value.toLowerCase())
  )
)

const modulosFiltradosSigarh = computed(() =>
  modulosSigarh.value.filter(m => 
    !searchModSigarh.value || m.name.toLowerCase().includes(searchModSigarh.value.toLowerCase())
  )
)

const activosApp = computed(() =>
  modulosActivos.value.filter(code => modulosApp.value.some(m => m.code === code)).length
)

const activosSigarh = computed(() =>
  modulosActivos.value.filter(code => modulosSigarh.value.some(m => m.code === code)).length
)

const moduleProgress = computed(() => {
  if (!todosModulos.value.length) return 0
  return Math.round((modulosActivos.value.length / todosModulos.value.length) * 100)
})

const appPercentage = computed(() => {
  const total = modulosActivos.value.length
  if (total === 0) return 0
  return Math.round((activosApp.value / total) * 100)
})

const sigarhPercentage = computed(() => {
  const total = modulosActivos.value.length
  if (total === 0) return 0
  return Math.round((activosSigarh.value / total) * 100)
})

const nextStep = () => {
  if (currentStep.value === 0 && !validateStep1()) return
  if (currentStep.value < 3) currentStep.value++
}

const validateStep1 = (): boolean => {
  let valid = true
  errors.name = !form.name ? 'El nombre es requerido' : ''
  if (errors.name) valid = false
  return valid
}

const deseleccionarTodos = (category: 'app' | 'sigarh') => {
  const codes = category === 'app' 
    ? modulosApp.value.map(m => m.code)
    : modulosSigarh.value.map(m => m.code)
  modulosActivos.value = modulosActivos.value.filter(c => !codes.includes(c))
}

const irA = (path: string) => {
  const baseUrl = window.location.origin
  const tenantId = id.value
  if (path === '') {
    window.open(`${baseUrl}?tenant=${tenantId}`, '_blank')
  } else if (path === '/sigarh') {
    window.open(`${baseUrl}/sigarh/login?tenant=${tenantId}`, '_blank')
  } else if (path === '/app') {
    window.open(`${baseUrl}/app/login?tenant=${tenantId}`, '_blank')
  } else {
    window.open(`${baseUrl}${path}?tenant=${tenantId}`, '_blank')
  }
}

const confirmDelete = () => {
  showDeleteModal.value = true
}

const handleDelete = async () => {
  try {
    await api(`/admin/hospitales/${id.value}`, { method: 'DELETE' })
    router.push('/admin/hospitales')
  } catch (e: any) {
    saveError.value = e?.data?.detail || 'No se pudo eliminar el hospital'
  } finally {
    showDeleteModal.value = false
  }
}

const handleSave = async () => {
  if (!validateStep1()) {
    currentStep.value = 0
    return
  }

  saving.value = true
  saveError.value = ''
  try {
    await api(`/admin/hospitales/${id.value}`, {
      method: 'PATCH',
      body: {
        name: form.name,
        hospital_level: form.hospital_level || null,
        ruc: form.ruc || null,
        phone: form.phone || null,
        email: form.email || null,
        address: form.address || null,
        mission: form.mission || null,
        vision: form.vision || null,
        values: form.values || null,
        is_active: form.is_active,
      },
    })

    await api('/admin/hospitales/modulos', {
      method: 'PUT',
      body: {
        tenant_id: id.value,
        module_codes: modulosActivos.value,
      },
    })

    router.push('/admin/hospitales')
  } catch (e: any) {
    saveError.value = e?.data?.detail || 'No se pudo guardar el hospital'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [hospital, modulos] = await Promise.all([
      api<Hospital>(`/admin/hospitales/${id.value}`),
      api<Modulo[]>('/admin/modulos/catalogo'),
    ])

    form.name = hospital.name
    form.hospital_level = hospital.hospital_level || ''
    form.ruc = hospital.ruc || ''
    form.phone = hospital.phone || ''
    form.email = hospital.email || ''
    form.address = hospital.address || ''
    form.mission = hospital.mission || ''
    form.vision = hospital.vision || ''
    form.values = hospital.values || ''
    form.is_active = hospital.is_active
    subdomain.value = hospital.domain?.split('.')[0] || ''
    modulosActivos.value = hospital.active_modules || []
    todosModulos.value = modulos
  } catch (e: any) {
    saveError.value = e?.data?.detail || 'No se pudo cargar el hospital'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.hospital-edit-container {
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
.edit-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.edit-main {
  min-width: 0;
}

.edit-sidebar {
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

.domain-display {
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

.error-message {
  display: block;
  font-size: 0.75rem;
  color: var(--alert);
  margin-top: 0.25rem;
}

.field-hint {
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin-top: 0.375rem;
}

/* Subdomain Display */
.subdomain-display-field {
  display: flex;
  align-items: center;
  padding: 0.625rem 0.875rem;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--mist);
  color: var(--ink-soft);
  font-size: 0.875rem;
  position: relative;
}

.subdomain-display-field .input-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--ink-soft);
}

.subdomain-text {
  padding-left: 1.75rem;
  color: var(--ink);
}

.subdomain-suffix {
  margin-left: auto;
  color: var(--ink-soft);
}

/* Status Toggle */
.status-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-radius: 12px;
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

/* Module Controls */
.module-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.module-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-wrapper-small {
  position: relative;
  min-width: 180px;
}

.search-icon-small {
  position: absolute;
  left: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  width: 0.875rem;
  height: 0.875rem;
  color: var(--ink-soft);
}

.search-input-small {
  width: 100%;
  padding: 0.375rem 0.625rem 0.375rem 2rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  transition: all 0.2s ease;
}

.search-input-small:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-clear {
  color: var(--ink-soft);
}

.action-clear:hover {
  background: var(--mist);
}

.module-counter {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink-soft);
  background: var(--mist);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
}

/* Module Grid */
.module-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.625rem;
}

.module-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--paper);
}

.module-check:hover {
  background: var(--mist);
}

.module-check--active {
  background: var(--teal-soft);
  border-color: var(--teal) !important;
}

.module-check-input {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  accent-color: var(--teal);
  cursor: pointer;
  flex-shrink: 0;
}

.module-check-label {
  font-size: 0.8125rem;
  color: var(--ink);
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

/* Actions */
.edit-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1.5rem;
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
}

.summary-divider {
  height: 1px;
  background: var(--line);
  margin: 0.5rem 0;
}

.distribution-summary {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.distribution-bar {
  display: flex;
  height: 6px;
  border-radius: 3px;
  overflow: hidden;
  background: var(--mist);
}

.distribution-fill {
  height: 100%;
  transition: width 0.6s ease;
}

.distribution-fill.app {
  background: var(--green);
}

.distribution-fill.sigarh {
  background: var(--navy);
}

.distribution-labels {
  display: flex;
  justify-content: space-between;
}

.distribution-label {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.distribution-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

/* Quick Access Widget */
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

.quick-action:hover {
  background: var(--mist);
}

.quick-action + .quick-action {
  margin-top: 0.25rem;
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
  .hospital-edit-container {
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
  
  .page-subtitle {
    flex-wrap: wrap;
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
  
  .subdomain-display-field {
    flex-wrap: wrap;
  }
  
  .subdomain-suffix {
    margin-left: 0;
    width: 100%;
    padding-top: 0.25rem;
  }
  
  .module-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .module-actions {
    flex-direction: column;
  }
  
  .search-wrapper-small {
    width: 100%;
  }
}
</style>