<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Cambios de Turno - Nutrición' })
const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string
const lista = ref<any[]>([])
const loading = ref(true)
onMounted(async () => { lista.value = await $api('/sigarh/nutricion/cambio-turno', { tenant }); loading.value = false })
</script>
<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div><h1 class="text-xl font-semibold text-gray-800">Cambios de Turno - Nutrición</h1><p class="text-sm text-gray-500 mt-0.5">Registro de cambios de turno del personal de nutrición</p></div>
      <NuxtLink :to="`/sigarh/nutricion/cambio-turno/create?tenant=${tenant}`">
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:#1e3a5f"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Cambio</button>
      </NuxtLink>
    </div>
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-400">Cargando...</div>
      <div v-else-if="!lista.length" class="p-8 text-center text-gray-400">No hay cambios de turno registrados</div>
      <table v-else class="w-full text-sm">
        <thead><tr class="border-b border-gray-100 bg-gray-50">
          <th class="text-left px-4 py-3 font-medium text-gray-600">Fecha</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Turno Saliente</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Turno Entrante</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Raciones Entregadas</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Observaciones</th>
        </tr></thead>
        <tbody>
          <tr v-for="c in lista" :key="c.id" class="border-b border-gray-50 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium">{{ c.fecha }}</td>
            <td class="px-4 py-3 text-gray-600">{{ c.turno_saliente }}</td>
            <td class="px-4 py-3 text-gray-600">{{ c.turno_entrante }}</td>
            <td class="px-4 py-3 text-center font-medium">{{ c.raciones_entregadas ?? '—' }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ c.observaciones || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>