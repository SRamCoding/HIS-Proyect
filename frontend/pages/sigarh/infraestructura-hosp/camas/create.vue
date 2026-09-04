<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Nueva Cama' })
const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string
const form = reactive({
  codigo: '', nombre: '', sala_id: '', piso_id: '', servicio_id: '',
  sala_texto: '', piso_texto: '', servicio_texto: '',
  tipo_cama: '', estado: 'DISPONIBLE', is_active: true,
})
const pisos = ref<any[]>([])
const salas = ref<any[]>([])
const servicios = ref<any[]>([])
const saving = ref(false)
const error = ref('')

onMounted(async () => {
  [pisos.value, salas.value, servicios.value] = await Promise.all([
    $api('/sigarh/infraestructura-hosp/pisos', { tenant }),
    $api('/sigarh/infraestructura-hosp/salas', { tenant }),
    $api('/sigarh/mantenimiento/servicios', { tenant }),
  ])
})

watch(() => form.piso_id, (val) => {
  form.piso_texto = pisos.value.find(p => p.id === val)?.nombre || ''
})
watch(() => form.sala_id, (val) => {
  form.sala_texto = salas.value.find(s => s.id === val)?.nombre || ''
})
watch(() => form.servicio_id, (val) => {
  form.servicio_texto = servicios.value.find(s => s.id === val)?.nombre || ''
})

async function guardar() {
  saving.value = true; error.value = ''
  try {
    await $api('/sigarh/infraestructura-hosp/camas', { method: 'POST', tenant, body: form })
    router.push(`/sigarh/infraestructura-hosp/camas?tenant=${tenant}`)
  } catch (e: any) { error.value = e?.data?.detail || 'Error al guardar' } finally { saving.value = false }
}
</script>
<template>
  <div class="p-6 max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink :to="`/sigarh/infraestructura-hosp/camas?tenant=${tenant}`" class="text-gray-400 hover:text-gray-600"><UIcon name="i-heroicons-arrow-left" class="w-5 h-5" /></NuxtLink>
      <h1 class="text-xl font-semibold text-gray-800">Nueva Cama</h1>
    </div>
    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">{{ error }}</div>
      <div class="grid grid-cols-2 gap-4">
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Código</label><input v-model="form.codigo" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label><input v-model="form.nombre" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Piso</label>
          <select v-model="form.piso_id" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Sin piso</option>
            <option v-for="p in pisos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
          </select>
        </div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Sala</label>
          <select v-model="form.sala_id" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Sin sala</option>
            <option v-for="s in salas" :key="s.id" :value="s.id">{{ s.nombre }}</option>
          </select>
        </div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Servicio</label>
          <select v-model="form.servicio_id" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Sin servicio</option>
            <option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
          </select>
        </div>
        <div><label class="block text-sm font-medium text-gray-700 mb-1">Tipo de Cama</label>
          <select v-model="form.tipo_cama" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Sin tipo</option>
            <option>ADULTO</option><option>PEDIÁTRICO</option><option>UCI</option>
            <option>NEONATAL</option><option>MATERNIDAD</option><option>OBSERVACIÓN</option>
          </select>
        </div>
        <div class="col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <select v-model="form.estado" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option>DISPONIBLE</option><option>OCUPADA</option><option>MANTENIMIENTO</option><option>RESERVADA</option>
          </select>
        </div>
        <div class="col-span-2 flex items-center gap-2"><input v-model="form.is_active" type="checkbox" id="activo" class="rounded" /><label for="activo" class="text-sm text-gray-700">Activo</label></div>
      </div>
      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink :to="`/sigarh/infraestructura-hosp/camas?tenant=${tenant}`"><button class="px-4 py-2 rounded-lg text-sm border border-gray-200 text-gray-600">Cancelar</button></NuxtLink>
        <button @click="guardar" :disabled="saving" class="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50" style="background:#1e3a5f">{{ saving ? 'Guardando...' : 'Guardar' }}</button>
      </div>
    </div>
  </div>
</template>