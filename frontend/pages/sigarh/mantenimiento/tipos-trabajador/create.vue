<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/mantenimiento/tipos-trabajador?tenant=${tenantId}`" style="color: var(--ink-soft)">Tipos de Trabajador</NuxtLink>
        <span>/</span><span>Crear</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Nuevo Tipo de Trabajador</h1>
    </div>

    <div class="p-6" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Nombre*</label>
          <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Nombrado, Contratado, CAS" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Codigo</label>
          <input v-model="form.codigo" class="input-clinical" />
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
        <button class="btn-primary" :disabled="saving" @click="handleCreate(false)">{{ saving ? 'Guardando...' : 'Crear' }}</button>
        <button class="px-4 py-2 rounded text-sm font-medium" style="border: 1px solid var(--line); color: var(--ink)" :disabled="saving" @click="handleCreate(true)">Crear y crear otro</button>
        <NuxtLink :to="`/sigarh/mantenimiento/tipos-trabajador?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Cancelar</NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const form = reactive({ nombre: '', codigo: '', descripcion: '', is_active: true })
const handleCreate = async (createAnother: boolean) => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/tipos-trabajador', { method: 'POST', body: { ...form } })
    if (createAnother) { Object.assign(form, { nombre: '', codigo: '', descripcion: '', is_active: true }) }
    else { router.push(`/sigarh/mantenimiento/tipos-trabajador?tenant=${tenantId.value}`) }
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear' }
  finally { saving.value = false }
}
</script>