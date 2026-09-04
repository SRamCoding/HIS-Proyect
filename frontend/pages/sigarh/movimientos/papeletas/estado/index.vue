<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Estado de Papeletas' })
const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string

const lista = ref<any[]>([])
const loading = ref(true)
const filtroEstado = ref('')

async function cargar() {
  loading.value = true
  try {
    const q = filtroEstado.value ? `?estado=${filtroEstado.value}` : ''
    lista.value = await $api(`/sigarh/movimientos/papeletas${q}`, { tenant })
  } finally { loading.value = false }
}
onMounted(cargar)

const colorEstado: Record<string,string> = { pendiente:'#f59e0b', aprobado:'#10b981', rechazado:'#ef4444' }
</script>

<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-gray-800">Estado de Papeletas</h1>
        <p class="text-sm text-gray-500 mt-0.5">Seguimiento de papeletas tramitadas</p>
      </div>
      <NuxtLink :to="`/sigarh/movimientos/papeletas/tramitar?tenant=${tenant}`">
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:#1e3a5f">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Tramitar Papeleta
        </button>
      </NuxtLink>
    </div>

    <select v-model="filtroEstado" @change="cargar" class="px-3 py-2 rounded-lg border border-gray-200 text-sm bg-white">
      <option value="">Todos</option>
      <option value="pendiente">Pendiente</option>
      <option value="aprobado">Aprobado</option>
      <option value="rechazado">Rechazado</option>
    </select>

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-400">Cargando...</div>
      <div v-else-if="!lista.length" class="p-8 text-center text-gray-400">No hay papeletas registradas</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-100 bg-gray-50">
            <th class="text-left px-4 py-3 font-medium text-gray-600">Empleado</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Cargo</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Motivo</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Fecha Trámite</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in lista" :key="p.id" class="border-b border-gray-50 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium">{{ p.empleado_nombre }}</td>
            <td class="px-4 py-3 text-gray-600">{{ p.cargo_laboral }}</td>
            <td class="px-4 py-3 text-gray-600">{{ p.motivo_nombre }}</td>
            <td class="px-4 py-3 text-gray-600">{{ p.fecha_tramite }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-1 rounded-full text-xs font-medium text-white"
                :style="`background:${colorEstado[p.estado] || '#6b7280'}`">{{ p.estado }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>