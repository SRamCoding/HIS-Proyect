<!-- frontend/pages/admin/modulos/dependencias.vue -->
<template>
  <div class="auditoria-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-link" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <h1 class="page-title">Dependencias de Módulos</h1>
          <p class="page-subtitle">
            Define qué módulos requieren que otro módulo esté activo primero (ej. laboratorio requiere admisión).
          </p>
        </div>
      </div>
    </div>

    <!-- Formulario de nueva dependencia -->
    <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1.25rem 1.5rem; margin-bottom: 1.5rem;">
      <h2 class="detail-label" style="font-size: 0.875rem; font-weight: 600; color: var(--ink); margin-bottom: 0.75rem;">Nueva dependencia</h2>
      <div v-if="formError" class="mb-3 text-sm" style="color: var(--alert)">{{ formError }}</div>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
        <div>
          <label class="text-xs block mb-1" style="color: var(--ink-soft)">Módulo (el que depende)</label>
          <select v-model="form.module_code" class="input-clinical w-full">
            <option value="" disabled>Selecciona un módulo...</option>
            <option v-for="m in modulos" :key="m.code" :value="m.code">{{ m.name }} ({{ m.code }})</option>
          </select>
        </div>
        <div>
          <label class="text-xs block mb-1" style="color: var(--ink-soft)">Requiere que esté activo</label>
          <select v-model="form.depends_on_code" class="input-clinical w-full">
            <option value="" disabled>Selecciona un módulo...</option>
            <option v-for="m in modulos" :key="m.code" :value="m.code">{{ m.name }} ({{ m.code }})</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <label class="flex items-center gap-2 text-sm" style="color: var(--ink)">
            <input type="checkbox" v-model="form.is_required" />
            Obligatorio
          </label>
          <button class="btn-primary ml-auto" :disabled="saving" @click="crearDependencia">
            {{ saving ? 'Guardando...' : 'Agregar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Tabla de dependencias -->
    <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
      <div v-if="loading" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando dependencias...</p>
      </div>
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
      </div>
      <div v-else-if="!dependencias.length" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-link" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">Sin dependencias registradas</h3>
        <p style="color: var(--ink-soft)">Las dependencias entre módulos aparecerán aquí</p>
      </div>
      <div v-else class="table-responsive">
        <table class="auditoria-table">
          <thead>
            <tr>
              <th><span class="th-content">Módulo</span></th>
              <th><span class="th-content">Requiere</span></th>
              <th><span class="th-content">Obligatorio</span></th>
              <th><span class="th-content">Creado</span></th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="dep in dependencias" :key="dep.id">
              <td>
                <span class="model-text" style="color: var(--ink); font-weight: 500;">{{ moduleName(dep.module_code) }}</span>
                <span class="ip-text" style="display: block;">{{ dep.module_code }}</span>
              </td>
              <td>
                <span class="model-text" style="color: var(--ink);">{{ moduleName(dep.depends_on_code) }}</span>
                <span class="ip-text" style="display: block;">{{ dep.depends_on_code }}</span>
              </td>
              <td>
                <span class="badge" :class="dep.is_required ? 'badge--alert' : 'badge--neutral'">
                  {{ dep.is_required ? 'Sí' : 'No' }}
                </span>
              </td>
              <td class="ip-text">{{ formatDate(dep.created_at) }}</td>
              <td style="text-align: right">
                <button class="action-clear" style="color: var(--alert)" @click="abrirConfirmacion(dep)">Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal de confirmación -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="showConfirmModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <div class="modal-icon" style="background: var(--alert-soft)">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5" style="color: var(--alert)" />
          </div>
          <h3 class="modal-title">¿Eliminar dependencia?</h3>
        </div>
        <p class="modal-body" style="color: var(--ink-soft); font-size: 0.875rem;">
          "{{ depToDelete ? moduleName(depToDelete.module_code) : '' }}" ya no requerirá que
          "{{ depToDelete ? moduleName(depToDelete.depends_on_code) : '' }}" esté activo.
        </p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showConfirmModal = false">Cancelar</button>
          <button class="btn-danger" :disabled="deleting" @click="ejecutarEliminar">
            {{ deleting ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface ModuleDependency {
  id: string
  module_code: string
  depends_on_code: string
  is_required: boolean
  created_at: string
}

interface Modulo {
  id: string
  code: string
  name: string
  category: string
  is_active: boolean
}

const { api } = useApi()

const dependencias = ref<ModuleDependency[]>([])
const modulos = ref<Modulo[]>([])
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const formError = ref('')

const form = reactive({
  module_code: '',
  depends_on_code: '',
  is_required: true,
})

const moduleName = (code: string) => {
  const m = modulos.value.find(m => m.code === code)
  return m ? m.name : code
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const crearDependencia = async () => {
  formError.value = ''
  if (!form.module_code || !form.depends_on_code) {
    formError.value = 'Selecciona ambos módulos.'
    return
  }
  if (form.module_code === form.depends_on_code) {
    formError.value = 'Un módulo no puede depender de sí mismo.'
    return
  }
  saving.value = true
  try {
    const nueva = await api<ModuleDependency>('/admin/modulos/dependencias', {
      method: 'POST',
      body: {
        module_code: form.module_code,
        depends_on_code: form.depends_on_code,
        is_required: form.is_required,
      },
    })
    dependencias.value.unshift(nueva)
    form.module_code = ''
    form.depends_on_code = ''
    form.is_required = true
  } catch (e: any) {
    formError.value = apiErr(e, 'No se pudo crear la dependencia')
  } finally {
    saving.value = false
  }
}

const showConfirmModal = ref(false)
const depToDelete = ref<ModuleDependency | null>(null)
const deleting = ref(false)

const abrirConfirmacion = (dep: ModuleDependency) => {
  depToDelete.value = dep
  showConfirmModal.value = true
}

const ejecutarEliminar = async () => {
  if (!depToDelete.value) return
  deleting.value = true
  try {
    await api(`/admin/modulos/dependencias/${depToDelete.value.id}`, { method: 'DELETE' })
    dependencias.value = dependencias.value.filter(d => d.id !== depToDelete.value!.id)
    showConfirmModal.value = false
  } catch (e: any) {
    error.value = apiErr(e, 'No se pudo eliminar')
  } finally {
    deleting.value = false
  }
}


const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    const [deps, mods] = await Promise.all([
      api<ModuleDependency[]>('/admin/modulos/dependencias'),
      api<Modulo[]>('/admin/modulos/catalogo'),
    ])
    dependencias.value = deps
    modulos.value = mods
  } catch (e: any) {
    error.value = apiErr(e, 'Error de conexión')
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
<style scoped>
.modal-content {
  max-width: 420px;
  width: 100%;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
}
.btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--alert);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-danger:hover:not(:disabled) { background: var(--alert-dark); }
.btn-danger:disabled { opacity: 0.6; cursor: not-allowed; }
</style>