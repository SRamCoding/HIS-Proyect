<template>
  <div class="rol-sistema-create-container">
    <div class="rol-sistema-create-grid">
      <!-- Main Content -->
      <div class="rol-sistema-create-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-shield-check" class="w-3.5 h-3.5" />
              Roles del Sistema
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Nuevo Rol</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--navy-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--navy)" />
            </div>
            <div>
              <h1 class="page-title">Crear Rol del Sistema</h1>
              <p class="page-subtitle">Roles disponibles para asignar a Perfiles de Usuario en este hospital</p>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="error-banner">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
          {{ error }}
        </div>

        <!-- Form Card -->
        <section class="form-card">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--navy-soft)">
              <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4" style="color: var(--navy)" />
            </div>
            <div>
              <h3 class="card-title">Configuración del Rol</h3>
              <p class="card-subtitle">Define un nuevo rol del sistema con sus permisos y restricciones</p>
            </div>
          </div>

          <!-- Datos del Rol -->
          <div class="section-block">
            <h4 class="section-title">Datos del Rol</h4>
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Código Interno <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-barcode" class="input-icon" />
                  <input
                    v-model="form.codigo"
                    type="text"
                    class="input-clinical font-mono-data"
                    placeholder="medico"
                    :class="{ 'input-error': errors.codigo }"
                    @focus="errors.codigo = ''"
                  />
                </div>
                <span v-if="errors.codigo" class="error-message">{{ errors.codigo }}</span>
                <p class="field-hint">Minúsculas y guión bajo. No se puede cambiar fácilmente después.</p>
              </div>

              <div class="form-group">
                <label class="form-label">Nombre Visible <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-tag" class="input-icon" />
                  <input
                    v-model="form.nombre"
                    type="text"
                    class="input-clinical"
                    placeholder="Médico"
                    :class="{ 'input-error': errors.nombre }"
                    @focus="errors.nombre = ''"
                  />
                </div>
                <span v-if="errors.nombre" class="error-message">{{ errors.nombre }}</span>
                <p class="field-hint">Nombre que verán los usuarios en la interfaz</p>
              </div>

              <div class="form-group">
                <label class="form-label">Panel Asociado <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-squares-2x2" class="input-icon" />
                  <select v-model="form.panel" class="input-clinical">
                    <option value="app">Panel Hospital (app)</option>
                    <option value="sigarh">Panel SIGARH</option>
                    <option value="portal">Portal</option>
                  </select>
                </div>
                <p class="field-hint">A qué panel entra un usuario con este rol</p>
              </div>

              <div class="form-group">
                <label class="form-label">Módulo Requerido</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-cube" class="input-icon" />
                  <select v-model="form.modulo_requerido" class="input-clinical">
                    <option value="">— Ninguno (rol siempre disponible) —</option>
                    <option v-for="m in todosModulos" :key="m.code" :value="m.code">{{ m.name }}</option>
                  </select>
                </div>
                <p class="field-hint">Si el hospital no tiene este módulo activo, el rol no aparecerá</p>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Descripción</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea
                    v-model="form.descripcion"
                    class="input-clinical"
                    rows="3"
                    placeholder="Descripción del rol y sus responsabilidades..."
                  />
                </div>
              </div>

              <div class="form-group full-width">
                <div class="status-toggle">
                  <span class="toggle-label">Rol Activo</span>
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
                <p class="field-hint">Los roles inactivos no estarán disponibles para asignar</p>
              </div>
            </div>
          </div>

          <!-- Módulos Permitidos -->
          <div class="section-block">
            <h4 class="section-title">Módulos Permitidos</h4>
            <p class="section-desc">
              Solo estos módulos podrán marcarse en "Perfiles de Usuario" cuando se elija este rol.
              Deja vacío para no restringir — se mostrarán todos los módulos del hospital.
            </p>
            <div class="flex items-center gap-2 mb-3">
              <button class="btn-sm btn-outline" @click="toggleTodosModulos">
                {{ form.modulos_permitidos.length === todosModulos.length ? 'Deseleccionar todos' : 'Seleccionar todos' }}
              </button>
              <span class="text-xs" style="color: var(--ink-soft)">
                {{ form.modulos_permitidos.length }} de {{ todosModulos.length }} seleccionados
              </span>
            </div>
            <div class="modules-grid">
              <div v-if="!todosModulos.length" class="text-sm" style="color: var(--ink-soft)">
                No hay módulos disponibles
              </div>
              <label
                v-for="m in modulosApp"
                :key="m.code"
                class="module-check"
                :class="{ 'module-check--active': form.modulos_permitidos.includes(m.code) }"
              >
                <input
                  type="checkbox"
                  :value="m.code"
                  v-model="form.modulos_permitidos"
                  class="module-check-input"
                />
                <span class="module-check-label">
                  <span class="module-badge badge-app">App</span>
                  {{ m.name }}
                </span>
              </label>
              <label
                v-for="m in modulosSigarh"
                :key="m.code"
                class="module-check"
                :class="{ 'module-check--active': form.modulos_permitidos.includes(m.code) }"
              >
                <input
                  type="checkbox"
                  :value="m.code"
                  v-model="form.modulos_permitidos"
                  class="module-check-input"
                />
                <span class="module-check-label">
                  <span class="module-badge badge-sigarh">SIGARH</span>
                  {{ m.name }}
                </span>
              </label>
            </div>
          </div>

          <!-- Grupos Ocupacionales Permitidos -->
          <div class="section-block">
            <h4 class="section-title">Grupos Ocupacionales Permitidos</h4>
            <p class="section-desc">
              Solo empleados de estos grupos ocupacionales podrán vincularse a un usuario con este rol.
              Deja vacío para no restringir.
            </p>
            <div class="flex items-center gap-2 mb-3">
              <button class="btn-sm btn-outline" @click="toggleTodosGrupos">
                {{ form.grupos_ocupacionales_permitidos.length === gruposOcupacionales.length ? 'Deseleccionar todos' : 'Seleccionar todos' }}
              </button>
              <span class="text-xs" style="color: var(--ink-soft)">
                {{ form.grupos_ocupacionales_permitidos.length }} de {{ gruposOcupacionales.length }} seleccionados
              </span>
            </div>
            <div class="groups-grid">
              <div v-if="!gruposOcupacionales.length" class="text-sm" style="color: var(--ink-soft)">
                No hay grupos ocupacionales registrados
              </div>
              <label
                v-for="g in gruposOcupacionales"
                :key="g.id"
                class="group-check"
                :class="{ 'group-check--active': form.grupos_ocupacionales_permitidos.includes(g.id) }"
              >
                <input
                  type="checkbox"
                  :value="g.id"
                  v-model="form.grupos_ocupacionales_permitidos"
                  class="group-check-input"
                />
                <span class="group-check-label">{{ g.nombre }}</span>
              </label>
            </div>
          </div>

          <!-- Preview Section -->
          <div v-if="form.nombre || form.codigo" class="preview-section">
            <h4 class="preview-title">Vista Previa</h4>
            <div class="preview-card">
              <div class="preview-icon" :style="{ background: form.is_active ? 'var(--navy-soft)' : 'var(--mist)' }">
                <UIcon name="i-heroicons-shield-check" class="w-5 h-5" :style="{ color: form.is_active ? 'var(--navy)' : 'var(--ink-soft)' }" />
              </div>
              <div class="preview-info">
                <span class="preview-name">{{ form.nombre || 'Nombre del rol' }}</span>
                <span class="preview-detail">
                  <span class="preview-code">{{ form.codigo || 'Sin código' }}</span>
                  <span class="preview-panel">{{ form.panel }}</span>
                </span>
                <span class="preview-stats">
                  <span>{{ form.modulos_permitidos.length }} módulos</span>
                  <span>{{ form.grupos_ocupacionales_permitidos.length }} grupos</span>
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
                @click="handleCreate(false)"
              >
                <UIcon v-if="saving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                {{ saving ? 'Creando...' : 'Crear Rol' }}
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
                :to="`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId}`"
                class="btn-cancel"
              >
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Widgets -->
      <div class="rol-sistema-create-sidebar">
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
                <span>Los roles definen permisos a nivel de sistema</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Pueden restringir módulos y grupos ocupacionales</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El código interno no debe cambiar después de creado</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los roles inactivos no se pueden asignar</span>
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
              <span class="summary-label">Código</span>
              <span class="summary-value font-mono-data">{{ form.codigo || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Nombre</span>
              <span class="summary-value">{{ form.nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Panel</span>
              <span class="summary-value">{{ form.panel || '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Módulos</span>
              <span class="summary-value">{{ form.modulos_permitidos.length }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Grupos</span>
              <span class="summary-value">{{ form.grupos_ocupacionales_permitidos.length }}</span>
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
                  Define roles con códigos claros y consistentes. El código no debe 
                  cambiar después de creado, ya que se usa como identificador en el sistema.
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
              <span class="stat-label">Módulos</span>
              <span class="stat-number">{{ form.modulos_permitidos.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Grupos</span>
              <span class="stat-number">{{ form.grupos_ocupacionales_permitidos.length }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

interface Modulo {
  id: string
  code: string
  name: string
  category: string
  is_active: boolean
}

interface GrupoOcupacional {
  id: string
  nombre: string
}

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')

const todosModulos = ref<Modulo[]>([])
const gruposOcupacionales = ref<GrupoOcupacional[]>([])

const modulosApp = computed(() => todosModulos.value.filter(m => m.category === 'app'))
const modulosSigarh = computed(() => todosModulos.value.filter(m => m.category === 'sigarh'))

const errors = reactive({
  codigo: '',
  nombre: '',
})

const form = reactive({
  codigo: '',
  nombre: '',
  panel: 'app',
  modulo_requerido: '',
  descripcion: '',
  is_active: true,
  modulos_permitidos: [] as string[],
  grupos_ocupacionales_permitidos: [] as string[],
})

const filledFields = computed(() => {
  let count = 0
  if (form.codigo) count++
  if (form.nombre) count++
  if (form.panel) count++
  if (form.modulo_requerido) count++
  if (form.descripcion) count++
  if (form.modulos_permitidos.length) count++
  if (form.grupos_ocupacionales_permitidos.length) count++
  return count
})

const toggleTodosModulos = () => {
  if (form.modulos_permitidos.length === todosModulos.value.length) {
    form.modulos_permitidos = []
  } else {
    form.modulos_permitidos = todosModulos.value.map(m => m.code)
  }
}

const toggleTodosGrupos = () => {
  if (form.grupos_ocupacionales_permitidos.length === gruposOcupacionales.value.length) {
    form.grupos_ocupacionales_permitidos = []
  } else {
    form.grupos_ocupacionales_permitidos = gruposOcupacionales.value.map(g => g.id)
  }
}

const resetForm = () => {
  Object.assign(form, {
    codigo: '',
    nombre: '',
    panel: 'app',
    modulo_requerido: '',
    descripcion: '',
    is_active: true,
    modulos_permitidos: [],
    grupos_ocupacionales_permitidos: [],
  })
  errors.codigo = ''
  errors.nombre = ''
}

const validateForm = (): boolean => {
  let valid = true
  if (!form.codigo.trim()) {
    errors.codigo = 'El código interno es requerido'
    valid = false
  }
  if (!form.nombre.trim()) {
    errors.nombre = 'El nombre visible es requerido'
    valid = false
  }
  return valid
}

const handleCreate = async (createAnother: boolean) => {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/roles-sistema', {
      method: 'POST',
      body: {
        codigo: form.codigo.trim(),
        nombre: form.nombre.trim(),
        panel: form.panel,
        modulo_requerido: form.modulo_requerido || null,
        descripcion: form.descripcion || null,
        is_active: form.is_active,
        modulos_permitidos: form.modulos_permitidos,
        grupos_ocupacionales_permitidos: form.grupos_ocupacionales_permitidos,
      },
    })

    if (createAnother) {
      resetForm()
    } else {
      router.push(`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId.value}`)
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo crear el rol'
  } finally {
    saving.value = false
  }
}

const cargarCatalogos = async () => {
  try {
    const [modulos, grupos] = await Promise.all([
      api<Modulo[]>('/sigarh/mantenimiento/modulos-catalogo'),
      api<GrupoOcupacional[]>('/sigarh/mantenimiento/grupos-ocupacionales'),
    ])
    todosModulos.value = modulos
    gruposOcupacionales.value = grupos
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudieron cargar los catálogos'
  }
}

onMounted(cargarCatalogos)
</script>

<style scoped>
.rol-sistema-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.rol-sistema-create-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.rol-sistema-create-main {
  min-width: 0;
}

.rol-sistema-create-sidebar {
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

/* Section Block */
.section-block {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.section-block:first-of-type {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.5rem 0;
}

.section-desc {
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin: 0 0 1rem 0;
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

/* Modules Grid */
.modules-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.375rem;
  max-height: 250px;
  overflow-y: auto;
}

.module-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.625rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--paper);
  border: 1px solid transparent;
}

.module-check:hover {
  background: var(--mist);
}

.module-check--active {
  background: var(--navy-soft);
  border-color: var(--navy);
}

.module-check-input {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  accent-color: var(--navy);
  cursor: pointer;
  flex-shrink: 0;
}

.module-check-label {
  font-size: 0.8125rem;
  color: var(--ink);
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.module-badge {
  font-size: 0.5625rem;
  font-weight: 700;
  padding: 0.0625rem 0.375rem;
  border-radius: 3px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-app {
  background: var(--teal-soft);
  color: var(--teal);
}

.badge-sigarh {
  background: var(--purple-soft);
  color: var(--purple);
}

/* Groups Grid */
.groups-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.375rem;
  max-height: 200px;
  overflow-y: auto;
}

.group-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.625rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--paper);
  border: 1px solid transparent;
}

.group-check:hover {
  background: var(--mist);
}

.group-check--active {
  background: var(--navy-soft);
  border-color: var(--navy);
}

.group-check-input {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  accent-color: var(--navy);
  cursor: pointer;
  flex-shrink: 0;
}

.group-check-label {
  font-size: 0.8125rem;
  color: var(--ink);
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

.preview-panel {
  background: var(--mist);
  padding: 0.0625rem 0.375rem;
  border-radius: 4px;
}

.preview-stats {
  display: flex;
  gap: 0.75rem;
  font-size: 0.6875rem;
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

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
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
  .rol-sistema-create-grid {
    grid-template-columns: 1fr;
  }

  .rol-sistema-create-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .rol-sistema-create-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .rol-sistema-create-sidebar {
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

  .modules-grid,
  .groups-grid {
    grid-template-columns: 1fr;
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

  .modules-grid,
  .groups-grid {
    grid-template-columns: 1fr;
  }
}
</style>