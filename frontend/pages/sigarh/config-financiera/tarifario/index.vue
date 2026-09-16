<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Tarifario' })
const { api } = useApi()
const route = useRoute()
const tenant = route.query.tenant as string
const lista = ref<any[]>([])
const loading = ref(true)
const busqueda = ref('')
onMounted(async () => { lista.value = await api('/sigarh/config-financiera/tarifario', { tenant }); loading.value = false })
const listaFiltrada = computed(() => busqueda.value ? lista.value.filter(t => t.nombre?.toLowerCase().includes(busqueda.value.toLowerCase())) : lista.value)
</script>
<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div><h1 class="text-xl font-semibold text-gray-800">Tarifario</h1><p class="text-sm text-gray-500 mt-0.5">Tarifas de procedimientos y servicios</p></div>
      <NuxtLink :to="`/sigarh/config-financiera/tarifario/create?tenant=${tenant}`">
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:#1e3a5f"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva Tarifa</button>
      </NuxtLink>
    </div>
    <input v-model="busqueda" placeholder="Buscar procedimiento..." class="w-full max-w-sm px-3 py-2 border border-gray-200 rounded-lg text-sm" />
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-400">Cargando...</div>
      <div v-else-if="!listaFiltrada.length" class="p-8 text-center text-gray-400">No hay tarifas registradas</div>
      <table v-else class="w-full text-sm">
        <thead><tr class="border-b border-gray-100 bg-gray-50">
          <th class="text-left px-4 py-3 font-medium text-gray-600">Nombre</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Código</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Categoría</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Precio SIS</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Precio Particular</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Activo</th>
          <th class="px-4 py-3"></th>
        </tr></thead>
        <tbody>
          <tr v-for="t in listaFiltrada" :key="t.id" class="border-b border-gray-50 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium">{{ t.nombre }}</td>
            <td class="px-4 py-3 font-mono text-xs text-gray-600">{{ t.codigo || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ t.categoria || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">S/. {{ t.precio_sis?.toFixed(2) || '0.00' }}</td>
            <td class="px-4 py-3 text-gray-600">S/. {{ t.precio_particular?.toFixed(2) || '0.00' }}</td>
            <td class="px-4 py-3"><UIcon :name="t.is_active ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" :class="t.is_active ? 'text-green-500' : 'text-gray-300'" class="w-4 h-4" /></td>
            <td class="px-4 py-3"><NuxtLink :to="`/sigarh/config-financiera/tarifario/${t.id}?tenant=${tenant}`" class="text-blue-600 hover:underline text-xs">Editar</NuxtLink></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>