<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Editar Medicamento' })
const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string
const id = route.params.id as string
const form = reactive({
  nombre: '', codigo_digemid: '', concentracion: '', forma_farmaceutica: '',
  via_administracion: '', unidad_medida: '', tipo: 'MEDICAMENTO',
  precio_unitario: 0, requiere_receta: false, controlado: false, is_active: true,
})
const saving = ref(false)
const error = ref('')
onMounted(async () => { Object.assign(form, await $api(`/sigarh/config-farmacia/medicamentos/${id}`, { tenant })) })
async function guardar() {
  saving.value = true; error.value = ''
  try {
    await $api(`/sigarh/config-farmacia/medicamentos/${id}`, { method: 'PATCH', tenant, body: form })
    router.push(`/sigarh/config-farmacia/medicamentos?tenant=${tenant}`)
  } catch (e: any) { error.value = e?.data?.detail || 'Error al guardar' } finally { saving.value = false }
}
</script>
<template>
  <div class="p-6 max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink :to="`/sigarh/config-farmacia/medicamentos?tenant=${tenant}`" class="text-gray-400 hover:text-gray-600"><UIcon name="i-heroicons-arrow-left" class="w-5 h-5" /></NuxtLink>
      <h1 class="text-xl font-semibold text-gray-800">Editar Medicamento / Insumo</h1>
    </div>
    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">{{ error }}</div>
      <div class="grid grid-cols-2 gap-4">
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label><input v-model="form.nombre" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Código DIGEMID</label><input v-model="form.codigo_digemid" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
          <select v-model="form.tipo" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option>MEDICAMENTO</option><option>INSUMO</option><option>DISPOSITIVO MÉDICO</option>
          </select>
        </div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Concentración</label><input v-model="form.concentracion" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Forma Farmacéutica</label>
          <select v-model="form.forma_farmaceutica" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option>TABLETA</option><option>CÁPSULA</option><option>JARABE</option><option>AMPOLLA</option>
            <option>FRASCO</option><option>CREMA</option><option>ÓVULO</option><option>SUPOSITORIO</option><option>SOLUCIÓN</option>
          </select>
        </div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Vía de Administración</label>
          <select v-model="form.via_administracion" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option>ORAL</option><option>INTRAVENOSA</option><option>INTRAMUSCULAR</option>
            <option>SUBCUTÁNEA</option><option>TÓPICA</option><option>INHALATORIA</option>
          </select>
        </div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Unidad de Medida</label><input v-model="form.unidad_medida" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Precio Unitario (S/.)</label><input v-model="form.precio_unitario" type="number" step="0.01" min="0" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div class="col-span-2 flex gap-6">
          <div class="flex items-center gap-2"><input v-model="form.requiere_receta" type="checkbox" id="receta" class="rounded" /><label for="receta" class="text-sm text-gray-700">Requiere receta</label></div>
          <div class="flex items-center gap-2"><input v-model="form.controlado" type="checkbox" id="controlado" class="rounded" /><label for="controlado" class="text-sm text-gray-700">Medicamento controlado</label></div>
          <div class="flex items-center gap-2"><input v-model="form.is_active" type="checkbox" id="activo" class="rounded" /><label for="activo" class="text-sm text-gray-700">Activo</label></div>
        </div>
      </div>
      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink :to="`/sigarh/config-farmacia/medicamentos?tenant=${tenant}`"><button class="px-4 py-2 rounded-lg text-sm border border-gray-200 text-gray-600">Cancelar</button></NuxtLink>
        <button @click="guardar" :disabled="saving" class="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50" style="background:#1e3a5f">{{ saving ? 'Guardando...' : 'Guardar cambios' }}</button>
      </div>
    </div>
  </div>
</template>