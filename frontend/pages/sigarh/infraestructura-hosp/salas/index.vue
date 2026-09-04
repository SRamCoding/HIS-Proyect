<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Salas' })
const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string
const lista = ref<any[]>([])
const loading = ref(true)
const filtroPiso = ref('')
const pisos = ref<any[]>([])
onMounted(async () => {
  [lista.value, pisos.value] = await Promise.all([
    $api('/sigarh/infraestructura-hosp/salas', { tenant }),
    $api('/sigarh/infraestructura-hosp/pisos', { tenant }),
  ])
  loading.value = false
})
const listaFiltrada = computed(() => filtroPiso.value ? lista.value.filter(s => s.piso_id === filtroPiso.value) : lista.value)
</script>
<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div><h1 class="text-xl font-semibold text-gray-800">Salas</h1><p class="text-sm text-gray-500 mt-0.5">Salas del hospital por piso</p></div>
      <NuxtLink :to="`/sigarh/infraestructura-hosp/salas/create?tenant=${tenant}`">
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:#1e3a5f"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva Sala</button>
      </NuxtLink>
    </div>
    <select v-model="filtroPiso" class="px-3 py-2 rounded-lg border border-gray-200 text-sm bg-white">
      <option value="">Todos los pisos</option>
      <option v-for="p in pisos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
    </select>
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-400">Cargando...</div>
      <div v-else-if="!listaFiltrada.length" class="p-8 text-center text-gray-400">No hay salas registradas</div>
      <table v-else class="w-full text-sm">
        <thead><tr class="border-b border-gray-100 bg-gray-50">
          <th class="text-left px-4 py-3 font-medium text-gray-600">Nombre</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Código</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Piso</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Capacidad</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Activo</th>
          <th class="px-4 py-3"></th>
        </tr></thead>
        <tbody>
          <tr v-for="s in listaFiltrada" :key="s.id" class="border-b border-gray-50 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium">{{ s.nombre }}</td>
            <td class="px-4 py-3 font-mono text-xs text-gray-600">{{ s.codigo || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ pisos.find(p => p.id === s.piso_id)?.nombre || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ s.capacidad }}</td>
            <td class="px-4 py-3"><UIcon :name="s.is_active ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" :class="s.is_active ? 'text-green-500' : 'text-gray-300'" class="w-4 h-4" /></td>
            <td class="px-4 py-3"><NuxtLink :to="`/sigarh/infraestructura-hosp/salas/${s.id}?tenant=${tenant}`" class="text-blue-600 hover:underline text-xs">Editar</NuxtLink></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>