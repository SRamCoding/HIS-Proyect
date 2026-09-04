<!-- frontend/pages/admin/modulos/dependencias.vue -->
<template>
  <div>
    <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
      <span>Módulos</span><span>/</span><span>Dependencias</span>
    </div>
    <h1 class="text-lg font-semibold mb-1" style="color: var(--ink)">Dependencias de Módulos</h1>
    <p class="text-sm mb-4" style="color: var(--ink-soft)">
      Define qué módulos requieren que otro módulo esté activo primero (ej. laboratorio requiere admisión).
    </p>

    <!-- Formulario de nueva dependencia -->
    <div class="mb-6 p-4" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <h2 class="text-sm font-semibold mb-3" style="color: var(--ink)">Nueva dependencia</h2>
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
    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Módulo</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Requiere</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Obligatorio</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Creado</th>
            <th class="text-right font-medium px-5 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="dep in dependencias" :key="dep.id" style="border-bottom: 1px solid var(--line)">
            <td class="px-5 py-3 font-medium" style="color: var(--ink)">
              {{ moduleName(dep.module_code) }}
              <span class="text-xs block" style="color: var(--ink-soft)">{{ dep.module_code }}</span>
            </td>
            <td class="px-5 py-3" style="color: var(--ink)">
              {{ moduleName(dep.depends_on_code) }}
              <span class="text-xs block" style="color: var(--ink-soft)">{{ dep.depends_on_code }}</span>
            </td>
            <td class="px-5 py-3">
              <span class="badge" :class="dep.is_required ? 'badge--alert' : 'badge--neutral'">
                {{ dep.is_required ? 'Sí' : 'No' }}
              </span>
            </td>
            <td class="px-5 py-3 text-xs" style="color: var(--ink-soft)">{{ formatDate(dep.created_at) }}</td>
              <td class="px-5 py-3 text-right">
                <button class="text-sm font-medium" style="color: var(--alert)" @click="abrirConfirmacion(dep)">Eliminar</button>
              </td>
          </tr>
          <tr v-if="!dependencias.length">
            <td colspan="4" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">
              Sin dependencias registradas.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
      <!-- Modal de confirmación -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="showConfirmModal = false">
      <div class="modal-box">
        <h3 class="text-base font-semibold mb-2" style="color: var(--ink)">¿Eliminar dependencia?</h3>
        <p class="text-sm mb-4" style="color: var(--ink-soft)">
          "{{ depToDelete ? moduleName(depToDelete.module_code) : '' }}" ya no requerirá que
          "{{ depToDelete ? moduleName(depToDelete.depends_on_code) : '' }}" esté activo.
        </p>
        <div class="flex justify-end gap-2">
          <button class="btn-secondary" @click="showConfirmModal = false">Cancelar</button>
          <button class="btn-danger" :disabled="deleting" @click="ejecutarEliminar">
            {{ deleting ? 'Eliminando...' : 'Eliminar' }}
          </button>
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
    formError.value = e?.data?.detail || 'No se pudo crear la dependencia'
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
    error.value = e?.data?.detail || 'No se pudo eliminar'
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
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: var(--paper);
  border-radius: var(--radius);
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
}
</style>