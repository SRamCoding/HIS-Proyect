<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Tramitar Papeleta' })
const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()
const tenant = route.query.tenant as string

const form = reactive({
  empleado_id: '', motivo_id: '',
  fecha_tramite: new Date().toISOString().split('T')[0],
  detalle: '', estado: 'pendiente', mes_actual: true,
})
const empleados = ref<any[]>([])
const motivos = ref<any[]>([])
const saving = ref(false)
const error = ref('')

onMounted(async () => {
  [empleados.value, motivos.value] = await Promise.all([
    $api('/sigarh/rrhh/empleados', { tenant }),
    $api('/sigarh/rrhh/motivos-justificacion', { tenant }),
  ])
})

async function guardar() {
  saving.value = true; error.value = ''
  try {
    await $api('/sigarh/movimientos/papeletas', { method: 'POST', tenant, body: form })
    router.push(`/sigarh/movimientos/papeletas/estado?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar'
  } finally { saving.value = false }
}
</script>

<template>
  <div class="p-6 max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink :to="`/sigarh/movimientos/papeletas/estado?tenant=${tenant}`" class="text-gray-400 hover:text-gray-600">
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
      </NuxtLink>
      <h1 class="text-xl font-semibold text-gray-800">Tramitar Papeleta</h1>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">{{ error }}</div>

      <div class="grid grid-cols-2 gap-4">
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Empleado</label>
          <select v-model="form.empleado_id" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Seleccione un empleado</option>
            <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombres }} {{ e.apellidos }}</option>
          </select>
        </div>
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Motivo</label>
          <select v-model="form.motivo_id" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Seleccione un motivo</option>
            <option v-for="m in motivos" :key="m.id" :value="m.id">{{ m.nombre }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de Trámite</label>
          <input v-model="form.fecha_tramite" type="date" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <select v-model="form.estado" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="pendiente">Pendiente</option>
            <option value="aprobado">Aprobado</option>
            <option value="rechazado">Rechazado</option>
          </select>
        </div>
        <div class="col-span-2 flex items-center gap-2">
          <input v-model="form.mes_actual" type="checkbox" id="mes_actual" class="rounded" />
          <label for="mes_actual" class="text-sm text-gray-700">Mes actual</label>
        </div>
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Detalle</label>
          <textarea v-model="form.detalle" rows="3" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
      </div>

      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink :to="`/sigarh/movimientos/papeletas/estado?tenant=${tenant}`">
          <button class="px-4 py-2 rounded-lg text-sm border border-gray-200 text-gray-600">Cancelar</button>
        </NuxtLink>
        <button @click="guardar" :disabled="saving"
          class="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50" style="background:#1e3a5f">
          {{ saving ? 'Guardando...' : 'Tramitar Papeleta' }}
        </button>
      </div>
    </div>
  </div>
</template>