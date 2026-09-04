<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Nueva Ración' })
const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string
const form = reactive({ dni: '', nombre_completo: '', dependencia: '', tipo_racion: 'DESAYUNO', fecha: new Date().toISOString().split('T')[0], observacion: '' })
const saving = ref(false)
const error = ref('')
async function guardar() {
  saving.value = true; error.value = ''
  try {
    await $api('/sigarh/nutricion/raciones', { method: 'POST', tenant, body: form })
    router.push(`/sigarh/nutricion/raciones?tenant=${tenant}`)
  } catch (e: any) { error.value = e?.data?.detail || 'Error al guardar' } finally { saving.value = false }
}
</script>
<template>
  <div class="p-6 max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink :to="`/sigarh/nutricion/raciones?tenant=${tenant}`" class="text-gray-400 hover:text-gray-600"><UIcon name="i-heroicons-arrow-left" class="w-5 h-5" /></NuxtLink>
      <h1 class="text-xl font-semibold text-gray-800">Nueva Ración</h1>
    </div>
    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">{{ error }}</div>
      <div class="grid grid-cols-2 gap-4">
        <div><label class="block text-sm font-medium text-gray-700 mb-1">DNI</label><input v-model="form.dni" type="text" maxlength="8" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Tipo de Ración</label>
          <select v-model="form.tipo_racion" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option>DESAYUNO</option><option>ALMUERZO</option><option>CENA</option><option>REFRIGERIO</option>
          </select>
        </div>
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Nombre Completo</label><input v-model="form.nombre_completo" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Dependencia / Servicio</label><input v-model="form.dependencia" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Fecha</label><input v-model="form.fecha" type="date" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Observación</label><textarea v-model="form.observacion" rows="2" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
      </div>
      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink :to="`/sigarh/nutricion/raciones?tenant=${tenant}`"><button class="px-4 py-2 rounded-lg text-sm border border-gray-200 text-gray-600">Cancelar</button></NuxtLink>
        <button @click="guardar" :disabled="saving" class="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50" style="background:#1e3a5f">{{ saving ? 'Guardando...' : 'Guardar' }}</button>
      </div>
    </div>
  </div>
</template>