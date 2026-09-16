<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Registro de Raciones' })
const { api } = useApi()
const route = useRoute()
const tenant = route.query.tenant as string
const lista = ref<any[]>([])
const loading = ref(true)
const fechaFiltro = ref(new Date().toISOString().split('T')[0])

async function cargar() {
  loading.value = true
  try { lista.value = await api(`/sigarh/nutricion/raciones?fecha=${fechaFiltro.value}`, { tenant }) }
  finally { loading.value = false }
}
onMounted(cargar)
watch(fechaFiltro, cargar)

async function entregar(id: string) {
  await api(`/sigarh/nutricion/raciones/${id}/entregar`, { method: 'POST', tenant })
  cargar()
}
</script>
<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div><h1 class="text-xl font-semibold text-gray-800">Registro de Raciones</h1><p class="text-sm text-gray-500 mt-0.5">Control de raciones alimentarias del personal</p></div>
      <NuxtLink :to="`/sigarh/nutricion/raciones/create?tenant=${tenant}`">
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:#1e3a5f"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva Ración</button>
      </NuxtLink>
    </div>
    <div class="flex items-center gap-3">
      <label class="text-sm text-gray-600">Fecha:</label>
      <input v-model="fechaFiltro" type="date" class="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
      <span class="text-sm text-gray-500">{{ lista.length }} raciones — {{ lista.filter(r=>r.entregado).length }} entregadas</span>
    </div>
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-400">Cargando...</div>
      <div v-else-if="!lista.length" class="p-8 text-center text-gray-400">No hay raciones para esta fecha</div>
      <table v-else class="w-full text-sm">
        <thead><tr class="border-b border-gray-100 bg-gray-50">
          <th class="text-left px-4 py-3 font-medium text-gray-600">DNI</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Nombre</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Dependencia</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Tipo Ración</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Estado</th>
          <th class="px-4 py-3"></th>
        </tr></thead>
        <tbody>
          <tr v-for="r in lista" :key="r.id" class="border-b border-gray-50 hover:bg-gray-50">
            <td class="px-4 py-3 font-mono text-xs">{{ r.dni }}</td>
            <td class="px-4 py-3 font-medium">{{ r.nombre_completo }}</td>
            <td class="px-4 py-3 text-gray-600">{{ r.dependencia }}</td>
            <td class="px-4 py-3"><span class="px-2 py-0.5 bg-orange-50 text-orange-700 rounded text-xs">{{ r.tipo_racion }}</span></td>
            <td class="px-4 py-3">
              <span v-if="r.entregado" class="flex items-center gap-1 text-green-600 text-xs"><UIcon name="i-heroicons-check-circle" class="w-4 h-4" /> Entregado</span>
              <span v-else class="text-yellow-600 text-xs">Pendiente</span>
            </td>
            <td class="px-4 py-3">
              <button v-if="!r.entregado" @click="entregar(r.id)"
                class="px-2 py-1 rounded text-xs text-white" style="background:#1e3a5f">
                Entregar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>