<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/mantenimiento/tipos-guardia?tenant=${tenantId}`" style="color: var(--ink-soft)">Tipos de Guardia</NuxtLink>
        <span>/</span><span>Editar</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Editar Tipo de Guardia</h1>
    </div>

    <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>

    <template v-else>
      <div class="p-6" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Nombre*</label>
            <input v-model="form.nombre" class="input-clinical" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Codigo</label>
            <input v-model="form.codigo" class="input-clinical" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Horas</label>
            <input v-model.number="form.horas" type="number" class="input-clinical" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Descripcion</label>
            <textarea v-model="form.descripcion" class="input-clinical" rows="3" />
          </div>
          <div class="flex items-center gap-2">
            <input type="checkbox" v-model="form.is_active" id="activo" />
            <label for="activo" class="text-sm" style="color: var(--ink)">Activo</label>
          </div>
        </div>
        <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>
        <div class="flex gap-3 mt-6">
          <button class="btn-primary" :disabled="saving" @click="handleSave">{{ saving ? 'Guardando...' : 'Guardar cambios' }}</button>
          <NuxtLink :to="`/sigarh/mantenimiento/tipos-guardia?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Cancelar</NuxtLink>
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
const form = reactive({ nombre: '', codigo: '', horas: null as number | null, descripcion: '', is_active: true })
const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/tipos-guardia/${id.value}`, { method: 'PATCH', body: { ...form } })
    router.push(`/sigarh/mantenimiento/tipos-guardia?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const data = await api<any>(`/sigarh/mantenimiento/tipos-guardia/${id.value}`)
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.horas = data.horas || null
    form.descripcion = data.descripcion || ''
    form.is_active = data.is_active
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>