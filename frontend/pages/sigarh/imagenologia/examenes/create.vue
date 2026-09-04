<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Nuevo Examen de Imagenología' })
const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string
const form = reactive({ nombre: '', codigo: '', modalidad: '', region_anatomica: '', tiempo_resultado: '', precio: 0, descripcion: '', requiere_contraste: false, is_active: true })
const saving = ref(false)
const error = ref('')
async function guardar() {
  saving.value = true; error.value = ''
  try {
    await $api('/sigarh/imagenologia/examenes', { method: 'POST', tenant, body: form })
    router.push(`/sigarh/imagenologia/examenes?tenant=${tenant}`)
  } catch (e: any) { error.value = e?.data?.detail || 'Error al guardar' } finally { saving.value = false }
}
</script>
<template>
  <div class="p-6 max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink :to="`/sigarh/imagenologia/examenes?tenant=${tenant}`" class="text-gray-400 hover:text-gray-600"><UIcon name="i-heroicons-arrow-left" class="w-5 h-5" /></NuxtLink>
      <h1 class="text-xl font-semibold text-gray-800">Nuevo Examen de Imagenología</h1>
    </div>
    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">{{ error }}</div>
      <div class="grid grid-cols-2 gap-4">
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Nombre del Examen</label><input v-model="form.nombre" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Código</label><input v-model="form.codigo" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Modalidad</label>
          <select v-model="form.modalidad" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Seleccione</option>
            <option>RADIOGRAFÍA</option><option>ECOGRAFÍA</option><option>TOMOGRAFÍA</option>
            <option>RESONANCIA MAGNÉTICA</option><option>MAMOGRAFÍA</option><option>DENSITOMETRÍA</option>
            <option>FLUOROSCOPÍA</option><option>OTROS</option>
          </select>
        </div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Región Anatómica</label><input v-model="form.region_anatomica" type="text" placeholder="Ej: Tórax, Abdomen, Cráneo" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Tiempo de Resultado</label><input v-model="form.tiempo_resultado" type="text" placeholder="Ej: 2 horas" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Precio (S/.)</label><input v-model="form.precio" type="number" step="0.01" min="0" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Descripción / Preparación</label><textarea v-model="form.descripcion" rows="2" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div class="col-span-2 flex gap-6">
          <div class="flex items-center gap-2"><input v-model="form.requiere_contraste" type="checkbox" id="contraste" class="rounded" /><label for="contraste" class="text-sm text-gray-700">Requiere contraste</label></div>
          <div class="flex items-center gap-2"><input v-model="form.is_active" type="checkbox" id="activo" class="rounded" /><label for="activo" class="text-sm text-gray-700">Activo</label></div>
        </div>
      </div>
      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink :to="`/sigarh/imagenologia/examenes?tenant=${tenant}`"><button class="px-4 py-2 rounded-lg text-sm border border-gray-200 text-gray-600">Cancelar</button></NuxtLink>
        <button @click="guardar" :disabled="saving" class="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50" style="background:#1e3a5f">{{ saving ? 'Guardando...' : 'Guardar' }}</button>
      </div>
    </div>
  </div>
</template>