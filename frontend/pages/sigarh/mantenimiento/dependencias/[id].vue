<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/mantenimiento/dependencias?tenant=${tenantId}`" style="color: var(--ink-soft)">Dependencias</NuxtLink>
        <span>/</span><span>Editar</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Editar Dependencia</h1>
    </div>
    <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
    <template v-else>
      <div class="p-6" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Nombre *</label>
            <input v-model="form.nombre" class="input-clinical" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Codigo</label>
            <input v-model="form.codigo" class="input-clinical" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Clasificacion</label>
            <select v-model="form.clasificacion" class="input-clinical">
              <option value="administrativa">Administrativa</option>
              <option value="asistencial">Asistencial</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Departamento</label>
            <select v-model="form.departamento_id" class="input-clinical" @change="form.servicio_id = ''">
              <option value="">Sin departamento</option>
              <option v-for="d in departamentos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Servicio</label>
            <select v-model="form.servicio_id" class="input-clinical" :disabled="!form.departamento_id">
              <option value="">Sin servicio</option>
              <option v-for="s in serviciosFiltrados" :key="s.id" :value="s.id">{{ s.nombre }}</option>
            </select>
            <p class="text-xs mt-1" style="color: var(--ink-soft)">Selecciona un departamento primero</p>
          </div>
          <div class="flex items-center gap-2">
            <input type="checkbox" v-model="form.is_active" id="activo" />
            <label for="activo" class="text-sm" style="color: var(--ink)">Activo</label>
          </div>
        </div>
        <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>
        <div class="flex gap-3 mt-6">
          <button class="btn-primary" :disabled="saving" @click="handleSave">{{ saving ? 'Guardando...' : 'Guardar cambios' }}</button>
          <NuxtLink :to="`/sigarh/mantenimiento/dependencias?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Cancelar</NuxtLink>
        </div>
      </div>
    </template>
  </div>
</template>
<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const departamentos = ref<any[]>([])
const servicios = ref<any[]>([])

const form = reactive({
  nombre: '',
  codigo: '',
  clasificacion: 'administrativa',
  departamento_id: '',
  servicio_id: '',
  is_active: true
})

const serviciosFiltrados = computed(() =>
  servicios.value.filter(s => s.departamento_id === form.departamento_id)
)

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/dependencias/${id.value}`, {
      method: 'PATCH',
      body: {
        nombre: form.nombre,
        codigo: form.codigo || null,
        clasificacion: form.clasificacion,
        departamento_id: form.departamento_id || null,
        servicio_id: form.servicio_id || null,
        is_active: form.is_active
      }
    })
    router.push(`/sigarh/mantenimiento/dependencias?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, deps, servs] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/dependencias/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/departamentos'),
      api<any[]>('/sigarh/mantenimiento/servicios'),
    ])
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.clasificacion = data.clasificacion || 'administrativa'
    form.departamento_id = data.departamento_id || ''
    form.servicio_id = data.servicio_id || ''
    form.is_active = data.is_active
    departamentos.value = deps
    servicios.value = servs
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>
