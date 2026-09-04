<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Editar Consultorio' })
const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string
const id = route.params.id as string

const form = reactive({ nombre: '', especialidad_id: '', piso_id: '', capacidad: 1, equipamiento: '', is_active: true })
const especialidades = ref<any[]>([])
const pisos = ref<any[]>([])
const saving = ref(false)
const error = ref('')

onMounted(async () => {
  const [data, esps, pss] = await Promise.all([
    $api(`/sigarh/infraestructura/consultorios/${id}`, { tenant }),
    $api('/sigarh/rrhh/especialidades', { tenant }),
    $api('/sigarh/infraestructura-hosp/pisos', { tenant }),
  ])
  Object.assign(form, data)
  especialidades.value = esps
  pisos.value = pss
})

async function guardar() {
  saving.value = true; error.value = ''
  try {
    await $api(`/sigarh/infraestructura/consultorios/${id}`, { method: 'PATCH', tenant, body: form })
    router.push(`/sigarh/infraestructura/consultorios?tenant=${tenant}`)
  } catch (e: any) { error.value = e?.data?.detail || 'Error al guardar' } finally { saving.value = false }
}
</script>

<template>
  <div class="p-6 max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink :to="`/sigarh/infraestructura/consultorios?tenant=${tenant}`" class="text-gray-400 hover:text-gray-600">
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
      </NuxtLink>
      <h1 class="text-xl font-semibold text-gray-800">Editar Consultorio</h1>
    </div>
    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">{{ error }}</div>
      <div class="grid grid-cols-2 gap-4">
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Nombre del Consultorio</label>
          <input v-model="form.nombre" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Especialidad</label>
          <select v-model="form.especialidad_id" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Sin especialidad fija</option>
            <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Piso</label>
          <select v-model="form.piso_id" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Sin piso asignado</option>
            <option v-for="p in pisos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Capacidad de Sala</label>
          <input v-model="form.capacidad" type="number" min="1" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Equipamiento</label>
          <textarea v-model="form.equipamiento" rows="3" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div class="col-span-2 flex items-center gap-2">
          <input v-model="form.is_active" type="checkbox" id="activo" class="rounded" />
          <label for="activo" class="text-sm text-gray-700">Activo</label>
        </div>
      </div>
      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink :to="`/sigarh/infraestructura/consultorios?tenant=${tenant}`">
          <button class="px-4 py-2 rounded-lg text-sm border border-gray-200 text-gray-600">Cancelar</button>
        </NuxtLink>
        <button @click="guardar" :disabled="saving"
          class="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50" style="background:#1e3a5f">
          {{ saving ? 'Guardando...' : 'Guardar cambios' }}
        </button>
      </div>
    </div>
  </div>
</template>