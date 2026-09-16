<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Exámenes de Laboratorio' })
const { api: $api } = useApi()
const route = useRoute()
const tenant = route.query.tenant as string
const lista = ref<any[]>([])
const loading = ref(true)
const busqueda = ref('')
const filtroCategoria = ref('')

onMounted(async () => { lista.value = await $api('/sigarh/laboratorio/examenes', { tenant }); loading.value = false })

const listaFiltrada = computed(() => lista.value.filter(e => {
  const matchBusqueda = !busqueda.value || e.nombre.toLowerCase().includes(busqueda.value.toLowerCase()) || e.codigo?.includes(busqueda.value)
  const matchCategoria = !filtroCategoria.value || e.categoria === filtroCategoria.value
  return matchBusqueda && matchCategoria
}))

const categorias = computed(() => [...new Set(lista.value.map(e => e.categoria).filter(Boolean))])
</script>
<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div><h1 class="text-xl font-semibold text-gray-800">Exámenes de Laboratorio</h1><p class="text-sm text-gray-500 mt-0.5">Catálogo de exámenes de laboratorio clínico</p></div>
      <NuxtLink :to="`/sigarh/laboratorio/examenes/create?tenant=${tenant}`">
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:#1e3a5f"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Examen</button>
      </NuxtLink>
    </div>
    <div class="flex gap-3">
      <input v-model="busqueda" placeholder="Buscar por nombre o código..." class="px-3 py-2 border border-gray-200 rounded-lg text-sm w-64" />
      <select v-model="filtroCategoria" class="px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white">
        <option value="">Todas las categorías</option>
        <option v-for="c in categorias" :key="c" :value="c">{{ c }}</option>
      </select>
    </div>
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-400">Cargando...</div>
      <div v-else-if="!listaFiltrada.length" class="p-8 text-center text-gray-400">No hay exámenes registrados</div>
      <table v-else class="w-full text-sm">
        <thead><tr class="border-b border-gray-100 bg-gray-50">
          <th class="text-left px-4 py-3 font-medium text-gray-600">Nombre</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Código</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Categoría</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Muestra</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Precio (S/.)</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Activo</th>
          <th class="px-4 py-3"></th>
        </tr></thead>
        <tbody>
          <tr v-for="e in listaFiltrada" :key="e.id" class="border-b border-gray-50 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium">{{ e.nombre }}</td>
            <td class="px-4 py-3 font-mono text-xs text-gray-600">{{ e.codigo || '—' }}</td>
            <td class="px-4 py-3"><span class="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">{{ e.categoria || '—' }}</span></td>
            <td class="px-4 py-3 text-gray-600">{{ e.muestra || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ e.precio != null ? e.precio.toFixed(2) : '—' }}</td>
            <td class="px-4 py-3"><UIcon :name="e.is_active ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" :class="e.is_active ? 'text-green-500' : 'text-gray-300'" class="w-4 h-4" /></td>
            <td class="px-4 py-3"><NuxtLink :to="`/sigarh/laboratorio/examenes/${e.id}?tenant=${tenant}`" class="text-blue-600 hover:underline text-xs">Editar</NuxtLink></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>