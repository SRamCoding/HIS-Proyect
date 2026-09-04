<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Tramitar Cambio de Turno' })
const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string

const form = reactive({
  solicitante_id: '', aceptante_id: '',
  fecha_original: '', fecha_reemplazo: '',
  modalidad_solicitante: 'MAÑANA', modalidad_aceptante: 'MAÑANA',
  estado: 'pendiente',
})
const empleados = ref<any[]>([])
const saving = ref(false)
const error = ref('')

onMounted(async () => {
  empleados.value = await $api('/sigarh/rrhh/empleados', { tenant })
})

async function guardar() {
  saving.value = true; error.value = ''
  try {
    await $api('/sigarh/movimientos/cambio-turno', { method: 'POST', tenant, body: form })
    router.push(`/sigarh/movimientos/cambio-turno/estado?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar'
  } finally { saving.value = false }
}
</script>

<template>
  <div class="p-6 max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink :to="`/sigarh/movimientos/cambio-turno/estado?tenant=${tenant}`" class="text-gray-400 hover:text-gray-600">
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
      </NuxtLink>
      <h1 class="text-xl font-semibold text-gray-800">Tramitar Cambio de Turno</h1>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">{{ error }}</div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Empleado Solicitante</label>
          <select v-model="form.solicitante_id" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Seleccione</option>
            <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombres }} {{ e.apellidos }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Turno Solicitante</label>
          <select v-model="form.modalidad_solicitante" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option>MAÑANA</option><option>TARDE</option><option>NOCHE</option><option>GUARDIA</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Empleado Aceptante</label>
          <select v-model="form.aceptante_id" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Seleccione</option>
            <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombres }} {{ e.apellidos }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Turno Aceptante</label>
          <select v-model="form.modalidad_aceptante" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option>MAÑANA</option><option>TARDE</option><option>NOCHE</option><option>GUARDIA</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fecha Original</label>
          <input v-model="form.fecha_original" type="date" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de Reemplazo</label>
          <input v-model="form.fecha_reemplazo" type="date" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <select v-model="form.estado" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="pendiente">Pendiente</option>
            <option value="aprobado">Aprobado</option>
            <option value="rechazado">Rechazado</option>
          </select>
        </div>
      </div>

      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink :to="`/sigarh/movimientos/cambio-turno/estado?tenant=${tenant}`">
          <button class="px-4 py-2 rounded-lg text-sm border border-gray-200 text-gray-600">Cancelar</button>
        </NuxtLink>
        <button @click="guardar" :disabled="saving"
          class="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50" style="background:#1e3a5f">
          {{ saving ? 'Guardando...' : 'Tramitar Cambio' }}
        </button>
      </div>
    </div>
  </div>
</template>