<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Nuevo Tiempo de Procedimiento' })
const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string
const form = reactive({ nombre: '', codigo: '', especialidad_id: '', duracion_minutos: 30, is_active: true })
const especialidades = ref<any[]>([])
const saving = ref(false)
const error = ref('')
onMounted(async () => { especialidades.value = await $api('/sigarh/rrhh/especialidades', { tenant }) })
async function guardar() {
  saving.value = true; error.value = ''
  try {
    await $api('/sigarh/general/tiempos', { method: 'POST', tenant, body: form })
    router.push(`/sigarh/general/tiempos?tenant=${tenant}`)
  } catch (e: any) { error.value = e?.data?.detail || 'Error al guardar' } finally { saving.value = false }
}
</script>
<template>
  <div class="p-6 max-w-lg">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink :to="`/sigarh/general/tiempos?tenant=${tenant}`" class="text-gray-400 hover:text-gray-600"><UIcon name="i-heroicons-arrow-left" class="w-5 h-5" /></NuxtLink>
      <h1 class="text-xl font-semibold text-gray-800">Nuevo Tiempo de Procedimiento</h1>
    </div>
    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">{{ error }}</div>
      <div class="grid grid-cols-2 gap-4">
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Nombre del Procedimiento</label><input v-model="form.nombre" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Código</label><input v-model="form.codigo" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Duración (minutos)</label><input v-model="form.duracion_minutos" type="number" min="5" step="5" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Especialidad</label>
          <select v-model="form.especialidad_id" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Sin especialidad específica</option>
            <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
          </select>
        </div>
        <div class="col-span-2 flex items-center gap-2"><input v-model="form.is_active" type="checkbox" id="activo" class="rounded" /><label for="activo" class="text-sm text-gray-700">Activo</label></div>
      </div>
      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink :to="`/sigarh/general/tiempos?tenant=${tenant}`"><button class="px-4 py-2 rounded-lg text-sm border border-gray-200 text-gray-600">Cancelar</button></NuxtLink>
        <button @click="guardar" :disabled="saving" class="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50" style="background:#1e3a5f">{{ saving ? 'Guardando...' : 'Guardar' }}</button>
      </div>
    </div>
  </div>
</template>