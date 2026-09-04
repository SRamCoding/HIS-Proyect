<template>
  <div class="perfil-edit-container">
    <div class="perfil-edit-grid">
      <!-- Main Content -->
      <div class="perfil-edit-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-user-group" class="w-3.5 h-3.5" />
              Perfiles de Usuario
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Editar Perfil</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" :style="{ background: form.is_active ? 'var(--purple-soft)' : 'var(--mist)' }">
              <UIcon
                name="i-heroicons-user-group"
                class="w-6 h-6"
                :style="{ color: form.is_active ? 'var(--purple)' : 'var(--ink-soft)' }"
              />
            </div>
            <div>
              <h1 class="page-title">{{ form.nombre || 'Editar Perfil' }}</h1>
              <p class="page-subtitle">
                <span class="role-display">{{ form.rol_sistema_id ? rolesSistema.find(r => r.id === form.rol_sistema_id)?.nombre : 'Sin rol' }}</span>
                <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
                <span class="status-text-mini" :class="form.is_active ? 'text-active' : 'text-inactive'">
                  {{ form.is_active ? 'Activo' : 'Inactivo' }}
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
          <p style="color: var(--ink-soft)">Cargando información del perfil...</p>
        </div>

        <template v-else>
          <!-- Form Card -->
          <section class="form-card">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--purple-soft)">
                <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4" style="color: var(--purple)" />
              </div>
              <div>
                <h3 class="card-title">Configuración del Perfil</h3>
                <p class="card-subtitle">Actualiza los datos del perfil de usuario</p>
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
                  <UIcon name="i-heroicons-user-group" class="input-icon" />
                  <input
                    v-model="form.nombre"
                    type="text"
                    class="input-clinical"
                    placeholder="Ej: Administrador, Supervisor, Consultor"
                    :class="{ 'input-error': errors.nombre }"
                    @focus="errors.nombre = ''"
                  />
                </div>
                <span v-if="errors.nombre" class="error-message">{{ errors.nombre }}</span>
                <p class="field-hint">Nombre descriptivo del perfil</p>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Rol del Sistema</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-shield-check" class="input-icon" />
                  <select v-model="form.rol_sistema_id" class="input-clinical">
                    <option value="">Sin rol</option>
                    <option v-for="r in rolesSistema" :key="r.id" :value="r.id">{{ r.nombre }}</option>
                  </select>
                </div>
                <p class="field-hint">Rol base para el perfil</p>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Descripción</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea
                    v-model="form.descripcion"
                    class="input-clinical"
                    rows="2"
                    placeholder="Descripción del perfil y sus responsabilidades..."
                  />
                </div>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Módulos con acceso</label>
                <div class="modules-grid" style="border: 1px solid var(--line); border-radius: var(--radius); padding: 0.75rem;">
                  <div v-if="!todosModulos.length" class="text-sm" style="color: var(--ink-soft)">
                    No hay módulos disponibles
                  </div>
                  <label
                    v-for="mod in todosModulos"
                    :key="mod"
                    class="module-check"
                    :class="{ 'module-check--active': form.modulos_acceso.includes(mod) }"
                  >
                    <input
                      type="checkbox"
                      :value="mod"
                      v-model="form.modulos_acceso"
                      class="module-check-input"
                    />
                    <span class="module-check-label">{{ formatModulo(mod) }}</span>
                  </label>
                </div>
                <p class="field-hint">Selecciona los módulos a los que tendrá acceso este perfil</p>
              </div>

              <div class="form-group full-width">
                <div class="status-toggle">
                  <span class="toggle-label">Perfil Activo</span>
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
                <p class="field-hint">Los perfiles inactivos no estarán disponibles</p>
              </div>
            </div>

            <!-- Preview Section -->
            <div class="preview-section">
              <h4 class="preview-title">Vista Previa</h4>
              <div class="preview-card">
                <div class="preview-icon" :style="{ background: form.is_active ? 'var(--purple-soft)' : 'var(--mist)' }">
                  <UIcon name="i-heroicons-user-group" class="w-5 h-5" :style="{ color: form.is_active ? 'var(--purple)' : 'var(--ink-soft)' }" />
                </div>
                <div class="preview-info">
                  <span class="preview-name">{{ form.nombre || 'Nombre del perfil' }}</span>
                  <span class="preview-detail">
                    <span class="preview-role">{{ form.rol_sistema_id ? rolesSistema.find(r => r.id === form.rol_sistema_id)?.nombre : 'Sin rol' }}</span>
                    <span class="preview-modules">{{ form.modulos_acceso.length }} módulo(s) seleccionado(s)</span>
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
                  @click="handleSave"
                >
                  <UIcon v-if="saving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                  {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
                </button>
                <NuxtLink
                  :to="`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId}`"
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
      <div class="perfil-edit-sidebar">
        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--purple)" />
            <h4 class="widget-title">Resumen</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Nombre</span>
              <span class="summary-value">{{ form.nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Rol</span>
              <span class="summary-value">{{ form.rol_sistema_id ? rolesSistema.find(r => r.id === form.rol_sistema_id)?.nombre : 'Sin rol' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Módulos</span>
              <span class="summary-value">{{ form.modulos_acceso.length }}</span>
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
                <span>Los perfiles definen los permisos de usuario</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Pueden estar asociados a un rol del sistema</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los módulos seleccionados determinan el acceso</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los perfiles inactivos no se pueden asignar</span>
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
                  Al editar un perfil, revisa los módulos asignados para asegurar 
                  que los permisos sigan siendo adecuados.
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
                {{ form.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Módulos seleccionados</span>
              <span class="stat-number">{{ form.modulos_acceso.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Campos completos</span>
              <span class="stat-number">{{ filledFields }}/4</span>
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
const authStore = useAuthStore()

const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const rolesSistema = ref<any[]>([])

const todosModulos = computed(() => 
  authStore.user?.active_modules?.filter((m: string) => m.startsWith('sigarh_')) || []
)

const formatModulo = (code: string) => 
  code.replace('sigarh_', '').replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())

const errors = reactive({
  nombre: ''
})

const form = reactive({
  nombre: '',
  rol_sistema_id: '',
  descripcion: '',
  modulos_acceso: [] as string[],
  is_active: true,
})

const filledFields = computed(() => {
  let count = 0
  if (form.nombre) count++
  if (form.rol_sistema_id) count++
  if (form.descripcion) count++
  if (form.modulos_acceso.length) count++
  return count
})

const validateForm = (): boolean => {
  let valid = true
  if (!form.nombre.trim()) {
    errors.nombre = 'El nombre del perfil es requerido'
    valid = false
  }
  return valid
}

const handleSave = async () => {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/perfiles-usuario/${id.value}`, {
      method: 'PATCH',
      body: {
        nombre: form.nombre,
        rol_sistema_id: form.rol_sistema_id || null,
        descripcion: form.descripcion || null,
        modulos_acceso: form.modulos_acceso,
        is_active: form.is_active,
      }
    })
    router.push(`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId.value}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo guardar el perfil'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [data, roles] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/perfiles-usuario/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/roles-sistema'),
    ])
    form.nombre = data.nombre
    form.rol_sistema_id = data.rol_sistema_id || ''
    form.descripcion = data.descripcion || ''
    form.modulos_acceso = data.modulos_acceso || []
    form.is_active = data.is_active
    rolesSistema.value = roles
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar el perfil'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.perfil-edit-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.perfil-edit-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.perfil-edit-main {
  min-width: 0;
}

.perfil-edit-sidebar {
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

.role-display {
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

/* Modules Grid */
.modules-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.375rem;
  max-height: 200px;
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
  background: var(--purple-soft);
  border-color: var(--purple);
}

.module-check-input {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  accent-color: var(--purple);
  cursor: pointer;
  flex-shrink: 0;
}

.module-check-label {
  font-size: 0.8125rem;
  color: var(--ink);
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

.preview-role {
  font-weight: 500;
  color: var(--purple);
}

.preview-modules {
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
  .perfil-edit-grid {
    grid-template-columns: 1fr;
  }

  .perfil-edit-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .perfil-edit-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .perfil-edit-sidebar {
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

  .modules-grid {
    grid-template-columns: 1fr;
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

  .modules-grid {
    grid-template-columns: 1fr;
  }
}
</style>