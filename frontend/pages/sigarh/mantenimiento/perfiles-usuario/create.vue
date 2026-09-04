<template>
  <div class="perfil-create-container">
    <div class="perfil-create-grid">
      <!-- Main Content -->
      <div class="perfil-create-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-user-group" class="w-3.5 h-3.5" />
              Perfiles de Usuario
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Nuevo Perfil</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--purple-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--purple)" />
            </div>
            <div>
              <h1 class="page-title">Crear Perfil de Usuario</h1>
              <p class="page-subtitle">Define un nuevo perfil con permisos específicos</p>
            </div>
          </div>
        </div>

        <!-- Form Card -->
        <section class="form-card">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--purple-soft)">
              <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4" style="color: var(--purple)" />
            </div>
            <div>
              <h3 class="card-title">Configuración del Perfil</h3>
              <p class="card-subtitle">Ingresa los datos del nuevo perfil de usuario</p>
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
                    <option v-for="r in rolesDisponibles" :key="r.id" :value="r.id">{{ r.nombre }}</option>
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
                <div v-if="!modulosDisponibles.length" class="text-sm" style="color: var(--ink-soft)">
                  No hay Módulos disponibles
                </div>
                <label
                  v-for="mod in modulosDisponibles"
                  :key="mod.code"
                  class="module-check"
                  :class="{ 'module-check--active': form.modulos_acceso.includes(mod.code) }"
                >
                  <input
                    type="checkbox"
                    :value="mod.code"
                    v-model="form.modulos_acceso"
                    class="module-check-input"
                  />
                  <span class="module-check-label">{{ mod.name }}</span>
                </label>
              </div>
              <p class="field-hint">Selecciona los Módulos a los que tendrá acceso este perfil</p>
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
          <div v-if="form.nombre || form.modulos_acceso.length" class="preview-section">
            <h4 class="preview-title">Vista Previa</h4>
            <div class="preview-card">
              <div class="preview-icon" :style="{ background: form.is_active ? 'var(--purple-soft)' : 'var(--mist)' }">
                <UIcon name="i-heroicons-user-group" class="w-5 h-5" :style="{ color: form.is_active ? 'var(--purple)' : 'var(--ink-soft)' }" />
              </div>
              <div class="preview-info">
                <span class="preview-name">{{ form.nombre || 'Nombre del perfil' }}</span>
                <span class="preview-detail">
                  <span class="preview-role">{{ form.rol_sistema_id ? rolesSistema.find(r => r.id === form.rol_sistema_id)?.nombre : 'Sin rol' }}</span>
                  <span class="preview-modules">{{ form.modulos_acceso.length }} Módulo(s) seleccionado(s)</span>
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
                {{ saving ? 'Creando...' : 'Crear Perfil' }}
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
                :to="`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId}`"
                class="btn-cancel"
              >
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Widgets -->
      <div class="perfil-create-sidebar">
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
                <span>Los perfiles definen los permisos de usuario</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Pueden estar asociados a un rol del sistema</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los Módulos seleccionados determinan el acceso</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los perfiles inactivos no se pueden asignar</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--purple)" />
            <h4 class="widget-title">Resumen</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Nombre</span>
              <span class="summary-value">{{ form.nombre || 'â€”' }}</span>
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

        <!-- Tip Widget -->
        <div class="widget widget-tip">
          <div class="widget-content">
            <div class="tip-content">
              <UIcon name="i-heroicons-light-bulb" class="tip-icon" style="color: var(--amber)" />
              <div>
                <p class="tip-title">Consejo</p>
                <p class="tip-text">
                  Asigna solo los Módulos necesarios para cada perfil, siguiendo 
                  el principio de mínimo privilegio.
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
              <span class="stat-label">Módulos seleccionados</span>
              <span class="stat-number">{{ form.modulos_acceso.length }}</span>
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

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const tenant = computed(() => route.query.tenant as string || '')

const saving = ref(false)
const error = ref('')
const rolesSistema = ref<any[]>([])
const todosModulos = ref<any[]>([])

const rolesDisponibles = computed(() =>
  rolesSistema.value.filter(r =>
    r.is_active && (!r.modulo_requerido || authStore.user?.active_modules?.includes(r.modulo_requerido))
  )
)

const modulosDisponibles = computed(() => {
  let base = todosModulos.value.filter(m => authStore.user?.active_modules?.includes(m.code))
  const rol = rolesSistema.value.find(r => r.id === form.rol_sistema_id)
  if (rol && rol.modulos_permitidos?.length) {
    base = base.filter(m => rol.modulos_permitidos.includes(m.code))
  }
  return base
})

const errors = reactive({ nombre: '' })

const form = reactive({
  nombre: '',
  rol_sistema_id: '',
  descripcion: '',
  modulos_acceso: [] as string[],
  is_active: true,
})

watch(() => form.rol_sistema_id, () => {
  const codigosValidos = modulosDisponibles.value.map(m => m.code)
  form.modulos_acceso = form.modulos_acceso.filter(m => codigosValidos.includes(m))
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

const handleCreate = async (createAnother: boolean) => {
  if (!validateForm()) return
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/perfiles-usuario', {
      method: 'POST',
      tenant: tenant.value,
      body: {
        nombre: form.nombre,
        rol_sistema_id: form.rol_sistema_id || null,
        descripcion: form.descripcion || null,
        modulos_acceso: form.modulos_acceso,
        is_active: form.is_active,
      }
    })
    if (createAnother) {
      Object.assign(form, { nombre: '', rol_sistema_id: '', descripcion: '', modulos_acceso: [], is_active: true })
      errors.nombre = ''
    } else {
      router.push('/sigarh/mantenimiento/perfiles-usuario?tenant=' + tenant.value)
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo crear el perfil'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [roles, modulos] = await Promise.all([
      api('/sigarh/mantenimiento/roles-sistema'),
      api('/sigarh/mantenimiento/modulos-catalogo'),
    ])
    rolesSistema.value = roles
    todosModulos.value = modulos
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar catalogos'
  }
})
</script>

<style scoped>
.perfil-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}
.perfil-create-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}
.perfil-create-main { min-width: 0; }
.perfil-create-sidebar { display: flex; flex-direction: column; gap: 1.25rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.page-subtitle { font-size: 0.875rem; color: var(--ink-soft); margin: 0.125rem 0 0 0; }
.form-card { background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1.5rem; animation: slideIn 0.3s ease; }
@keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.card-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
.card-header-icon { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.card-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.card-subtitle { font-size: 0.8125rem; color: var(--ink-soft); margin: 0; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
.form-group.full-width { grid-column: 1 / -1; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.5rem; }
.required { color: var(--alert); }
.input-wrapper { position: relative; }
.input-icon { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); width: 1rem; height: 1rem; color: var(--ink-soft); }
.input-wrapper textarea + .input-icon { top: 0.75rem; transform: none; }
.input-clinical { width: 100%; padding: 0.625rem 0.875rem; padding-left: 2.5rem; border-radius: 8px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; transition: all 0.2s ease; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.input-clinical.input-error { border-color: var(--alert); }
.input-clinical.input-error:focus { box-shadow: 0 0 0 3px var(--alert-soft); }
.input-clinical::placeholder { color: var(--ink-soft); opacity: 0.6; }
.error-message { display: block; font-size: 0.75rem; color: var(--alert); margin-top: 0.25rem; }
.field-hint { font-size: 0.6875rem; color: var(--ink-soft); margin-top: 0.25rem; }
.modules-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.375rem; max-height: 200px; overflow-y: auto; }
.module-check { display: flex; align-items: center; gap: 0.5rem; padding: 0.375rem 0.625rem; border-radius: 6px; cursor: pointer; }
.module-check:hover { background: var(--mist); }
.module-check input[type="checkbox"] { width: 14px; height: 14px; accent-color: var(--teal); cursor: pointer; }
.module-label { font-size: 0.75rem; color: var(--ink); cursor: pointer; }
.toggle-wrapper { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 1rem; background: var(--mist); border-radius: 8px; }
.toggle-info { display: flex; flex-direction: column; gap: 0.125rem; }
.toggle-label { font-size: 0.875rem; font-weight: 500; color: var(--ink); }
.toggle-desc { font-size: 0.75rem; color: var(--ink-soft); }
.toggle-switch { position: relative; width: 44px; height: 24px; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.toggle-slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: var(--line); border-radius: 24px; transition: 0.3s; }
.toggle-slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: 0.3s; }
input:checked + .toggle-slider { background: var(--teal); }
input:checked + .toggle-slider:before { transform: translateX(20px); }
.sidebar-card { background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1.25rem; }
.sidebar-title { font-size: 0.875rem; font-weight: 600; color: var(--ink); margin: 0 0 1rem 0; }
.progress-bar { height: 6px; background: var(--mist); border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--teal); border-radius: 3px; transition: width 0.3s ease; }
.summary-list { display: flex; flex-direction: column; gap: 0.625rem; }
.summary-item { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.summary-key { font-size: 0.8125rem; color: var(--ink-soft); }
.summary-value { font-size: 0.8125rem; font-weight: 500; color: var(--ink); text-align: right; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.action-buttons { display: flex; flex-direction: column; gap: 0.625rem; }
.btn { display: flex; align-items: center; justify-content: center; gap: 0.5rem; padding: 0.625rem 1rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; cursor: pointer; transition: all 0.2s ease; border: none; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--navy); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--teal); }
.btn-secondary { background: var(--mist); color: var(--ink); }
.btn-secondary:hover:not(:disabled) { background: var(--line); }
.btn-ghost { background: transparent; color: var(--ink-soft); border: 1px solid var(--line); }
.btn-ghost:hover:not(:disabled) { background: var(--mist); color: var(--ink); }
.btn-icon { width: 1rem; height: 1rem; }
.spinner { width: 1rem; height: 1rem; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.alert { display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.875rem 1rem; border-radius: 8px; margin-bottom: 1rem; }
.alert-error { background: var(--alert-soft); border: 1px solid var(--alert); }
.alert-icon { width: 1.125rem; height: 1.125rem; flex-shrink: 0; margin-top: 0.125rem; }
.alert-text { font-size: 0.875rem; color: var(--ink); }
@media (max-width: 1024px) {
  .perfil-create-grid { grid-template-columns: 1fr; }
  .perfil-create-sidebar { order: -1; }
}
@media (max-width: 640px) {
  .perfil-create-container { padding: 1rem; }
  .form-grid { grid-template-columns: 1fr; }
  .action-buttons { flex-direction: column; align-items: flex-start; }
  .summary-item { flex-direction: column; align-items: flex-start; gap: 0.25rem; }
  .summary-value { max-width: 100%; text-align: left; }
  .modules-grid { grid-template-columns: 1fr; }
}
</style>
