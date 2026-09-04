<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Tramitar Licencia' })
const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string

const form = reactive({
  nombre_empleado: '', dni: '', dependencia: '', cargo: '',
  tipo_licencia: 'CON GOCE DE HABER', fecha_inicio: '', fecha_fin: '',
  dias_solicitados: 0, motivo: '', estado: 'pendiente',
})
const saving = ref(false)
const error = ref('')

watch([() => form.fecha_inicio, () => form.fecha_fin], () => {
  if (form.fecha_inicio && form.fecha_fin) {
    const diff = new Date(form.fecha_fin).getTime() - new Date(form.fecha_inicio).getTime()
    form.dias_solicitados = Math.max(0, Math.ceil(diff / 86400000) + 1)
  }
})

async function guardar() {
  saving.value = true; error.value = ''
  try {
    await $api('/sigarh/movimientos/licencias', { method: 'POST', tenant, body: form })
    router.push(`/sigarh/movimientos/licencias?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar'
  } finally { saving.value = false }
}
</script>

<template>
  <div class="p-6 max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink :to="`/sigarh/movimientos/licencias?tenant=${tenant}`"
        class="text-gray-400 hover:text-gray-600">
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
      </NuxtLink>
      <h1 class="text-xl font-semibold text-gray-800">Tramitar Licencia</h1>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">{{ error }}</div>

      <div class="grid grid-cols-2 gap-4">
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Nombre del Empleado</label>
          <input v-model="form.nombre_empleado" type="text"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">DNI</label>
          <input v-model="form.dni" type="text" maxlength="8"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de Licencia</label>
          <select v-model="form.tipo_licencia"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option>CON GOCE DE HABER</option>
            <option>SIN GOCE DE HABER</option>
            <option>POR ENFERMEDAD</option>
            <option>POR MATERNIDAD</option>
            <option>POR PATERNIDAD</option>
            <option>POR FALLECIMIENTO</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Dependencia</label>
          <input v-model="form.dependencia" type="text"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Cargo</label>
          <input v-model="form.cargo" type="text"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fecha Inicio</label>
          <input v-model="form.fecha_inicio" type="date"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fecha Fin</label>
          <input v-model="form.fecha_fin" type="date"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Días</label>
          <input v-model="form.dias_solicitados" type="number" readonly
            class="w-full px-3 py-2 border border-gray-100 bg-gray-50 rounded-lg text-sm" />
        </div>
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Motivo</label>
          <textarea v-model="form.motivo" rows="3"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
      </div>

      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink :to="`/sigarh/movimientos/licencias?tenant=${tenant}`">
          <button class="px-4 py-2 rounded-lg text-sm border border-gray-200 text-gray-600">Cancelar</button>
        </NuxtLink>
        <button @click="guardar" :disabled="saving"
          class="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50"
          style="background:#1e3a5f">
          {{ saving ? 'Guardando...' : 'Tramitar Licencia' }}
        </button>
      </div>
    </div>
  </div>
</template>