<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Nuevo Cambio de Turno' })
const { api: $api } = useApi()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string
const form = reactive({ fecha: new Date().toISOString().split('T')[0], turno_saliente: 'MAÑANA', turno_entrante: 'TARDE', raciones_entregadas: 0, observaciones: '' })
const saving = ref(false)
const error = ref('')
async function guardar() {
  saving.value = true; error.value = ''
  try {
    await $api('/sigarh/nutricion/cambio-turno', { method: 'POST', tenant, body: form })
    router.push(`/sigarh/nutricion/cambio-turno?tenant=${tenant}`)
  } catch (e: any) { error.value = e?.data?.detail || 'Error al guardar' } finally { saving.value = false }
}
</script>
<template>
  <div class="p-6 max-w-lg">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink :to="`/sigarh/nutricion/cambio-turno?tenant=${tenant}`" class="text-gray-400 hover:text-gray-600"><UIcon name="i-heroicons-arrow-left" class="w-5 h-5" /></NuxtLink>
      <h1 class="text-xl font-semibold text-gray-800">Nuevo Cambio de Turno</h1>
    </div>
    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">{{ error }}</div>
      <div class="grid grid-cols-2 gap-4">
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Fecha</label><input v-model="form.fecha" type="date" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Turno Saliente</label>
          <select v-model="form.turno_saliente" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option>MAÑANA</option><option>TARDE</option><option>NOCHE</option>
          </select>
        </div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Turno Entrante</label>
          <select v-model="form.turno_entrante" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option>MAÑANA</option><option>TARDE</option><option>NOCHE</option>
          </select>
        </div>
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Raciones Entregadas</label><input v-model="form.raciones_entregadas" type="number" min="0" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label><textarea v-model="form.observaciones" rows="3" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
      </div>
      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink :to="`/sigarh/nutricion/cambio-turno?tenant=${tenant}`"><button class="px-4 py-2 rounded-lg text-sm border border-gray-200 text-gray-600">Cancelar</button></NuxtLink>
        <button @click="guardar" :disabled="saving" class="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50" style="background:#1e3a5f">{{ saving ? 'Guardando...' : 'Guardar' }}</button>
      </div>
    </div>
  </div>
</template>