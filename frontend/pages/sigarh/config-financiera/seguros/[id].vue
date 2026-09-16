<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Editar Seguro' })
const { api: $api } = useApi()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string
const id = route.params.id as string
const form = reactive({ nombre: '', ruc: '', tipo: '', porcentaje_cobertura: 100, contacto: '', telefono: '', direccion: '', is_active: true })
const saving = ref(false)
const error = ref('')
onMounted(async () => { Object.assign(form, await $api(`/sigarh/config-financiera/seguros/${id}`, { tenant })) })
async function guardar() {
  saving.value = true; error.value = ''
  try {
    await $api(`/sigarh/config-financiera/seguros/${id}`, { method: 'PATCH', tenant, body: form })
    router.push(`/sigarh/config-financiera/seguros?tenant=${tenant}`)
  } catch (e: any) { error.value = e?.data?.detail || 'Error al guardar' } finally { saving.value = false }
}
</script>
<template>
  <div class="p-6 max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink :to="`/sigarh/config-financiera/seguros?tenant=${tenant}`" class="text-gray-400 hover:text-gray-600"><UIcon name="i-heroicons-arrow-left" class="w-5 h-5" /></NuxtLink>
      <h1 class="text-xl font-semibold text-gray-800">Editar Seguro</h1>
    </div>
    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">{{ error }}</div>
      <div class="grid grid-cols-2 gap-4">
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Nombre del Seguro</label><input v-model="form.nombre" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">RUC</label><input v-model="form.ruc" type="text" maxlength="11" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
          <select v-model="form.tipo" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option>SIS</option><option>ESSALUD</option><option>SOAT</option><option>PRIVADO</option><option>CONVENIO</option><option>PARTICULAR</option>
          </select>
        </div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Cobertura (%)</label><input v-model="form.porcentaje_cobertura" type="number" min="0" max="100" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Contacto</label><input v-model="form.contacto" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Teléfono</label><input v-model="form.telefono" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Dirección</label><input v-model="form.direccion" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div class="col-span-2 flex items-center gap-2"><input v-model="form.is_active" type="checkbox" id="activo" class="rounded" /><label for="activo" class="text-sm text-gray-700">Activo</label></div>
      </div>
      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink :to="`/sigarh/config-financiera/seguros?tenant=${tenant}`"><button class="px-4 py-2 rounded-lg text-sm border border-gray-200 text-gray-600">Cancelar</button></NuxtLink>
        <button @click="guardar" :disabled="saving" class="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50" style="background:#1e3a5f">{{ saving ? 'Guardando...' : 'Guardar cambios' }}</button>
      </div>
    </div>
  </div>
</template>