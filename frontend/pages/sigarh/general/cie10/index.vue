<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Diagnósticos CIE-10' })
const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string
const lista = ref<any[]>([])
const loading = ref(true)
const busqueda = ref('')

async function cargar() {
  loading.value = true
  try {
    const q = busqueda.value ? `?q=${encodeURIComponent(busqueda.value)}` : ''
    lista.value = await $api(`/sigarh/general/cie10${q}`, { tenant })
  } finally { loading.value = false }
}
onMounted(cargar)

let timeout: any
watch(busqueda, () => { clearTimeout(timeout); timeout = setTimeout(cargar, 400) })
</script>
<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div><h1 class="text-xl font-semibold text-gray-800">Diagnósticos CIE-10</h1><p class="text-sm text-gray-500 mt-0.5">Clasificación Internacional de Enfermedades</p></div>
      <NuxtLink :to="`/sigarh/general/cie10/create?tenant=${tenant}`">
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:#1e3a5f"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Diagnóstico</button>
      </NuxtLink>
    </div>
    <input v-model="busqueda" placeholder="Buscar por código o descripción..." class="w-full max-w-sm px-3 py-2 border border-gray-200 rounded-lg text-sm" />
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-400">Cargando...</div>
      <div v-else-if="!lista.length" class="p-8 text-center text-gray-400">No se encontraron diagnósticos</div>
      <table v-else class="w-full text-sm">
        <thead><tr class="border-b border-gray-100 bg-gray-50">
          <th class="text-left px-4 py-3 font-medium text-gray-600">Código</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Descripción</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Categoría</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Activo</th>
          <th class="px-4 py-3"></th>
        </tr></thead>
        <tbody>
          <tr v-for="d in lista" :key="d.id" class="border-b border-gray-50 hover:bg-gray-50">
            <td class="px-4 py-3 font-mono text-sm font-bold text-blue-700">{{ d.codigo_cie10 || d.codigo }}</td>
            <td class="px-4 py-3 font-medium">{{ d.descripcion || d.nombre }}</td>
            <td class="px-4 py-3 text-gray-600">{{ d.categoria || '—' }}</td>
            <td class="px-4 py-3"><UIcon :name="d.is_active ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" :class="d.is_active ? 'text-green-500' : 'text-gray-300'" class="w-4 h-4" /></td>
            <td class="px-4 py-3"><NuxtLink :to="`/sigarh/general/cie10/${d.id}?tenant=${tenant}`" class="text-blue-600 hover:underline text-xs">Editar</NuxtLink></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>