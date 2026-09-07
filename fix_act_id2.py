content = """<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/mantenimiento/actividades?tenant=${tenantId}`" style="color: var(--ink-soft)">Actividades</NuxtLink>
        <span>/</span><span>Editar</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Editar Actividad</h1>
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
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Tipo de Actividad</label>
            <select v-model="form.tipo_actividad_id" class="input-clinical">
              <option value="">Sin tipo</option>
              <option v-for="t in tiposActividad" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div>
            <div class="flex items-center gap-2 mb-1">
              <input type="checkbox" v-model="form.requiere_consultorio" id="consultorio" />
              <label for="consultorio" class="text-sm font-medium" style="color: var(--ink)">Requiere Consultorio</label>
            </div>
            <p class="text-xs" style="color: var(--ink-soft)">Actívelo si esta actividad se atiende en un consultorio (ej. Consulta Externa). Los días de atención se configurarán en el módulo de Consultorios, no en el Rol. Déjelo desactivado para actividades como Guardia, Retén o Sin Actividad, donde los días se definen directamente en el Rol.</p>
          </div>
          <div class="flex items-center gap-2">
            <input type="checkbox" v-model="form.is_active" id="activo" />
            <label for="activo" class="text-sm" style="color: var(--ink)">Activo</label>
          </div>
        </div>
        <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>
        <div class="flex gap-3 mt-6">
          <button class="btn-primary" :disabled="saving" @click="handleSave">{{ saving ? 'Guardando...' : 'Guardar cambios' }}</button>
          <NuxtLink :to="`/sigarh/mantenimiento/actividades?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Cancelar</NuxtLink>
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
const tiposActividad = ref<any[]>([])
const form = reactive({
  nombre: '',
  codigo: '',
  tipo_actividad_id: '',
  requiere_consultorio: false,
  is_active: true
})
const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/actividades/${id.value}`, {
      method: 'PATCH',
      body: {
        nombre: form.nombre,
        codigo: form.codigo || null,
        tipo_actividad_id: form.tipo_actividad_id || null,
        requiere_consultorio: form.requiere_consultorio,
        is_active: form.is_active
      }
    })
    router.push(`/sigarh/mantenimiento/actividades?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const [data, tipos] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/actividades/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/tipos-actividad'),
    ])
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.tipo_actividad_id = data.tipo_actividad_id || ''
    form.requiere_consultorio = data.requiere_consultorio ?? false
    form.is_active = data.is_active
    tiposActividad.value = tipos
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>
"""

with open('[id].vue', 'w', encoding='utf-8') as f:
    f.write(content)
print('Listo')
