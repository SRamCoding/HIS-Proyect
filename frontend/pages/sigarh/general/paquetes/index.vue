<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Paquetes' })
const { api: $api } = useApi()
const route = useRoute()
const tenant = route.query.tenant as string
const lista = ref<any[]>([])
const loading = ref(true)
onMounted(async () => { lista.value = await $api('/sigarh/general/paquetes', { tenant }); loading.value = false })
</script>
<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div><h1 class="text-xl font-semibold text-gray-800">Paquetes</h1><p class="text-sm text-gray-500 mt-0.5">Paquetes de procedimientos y servicios</p></div>
      <NuxtLink :to="`/sigarh/general/paquetes/create?tenant=${tenant}`">
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:#1e3a5f"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Paquete</button>
      </NuxtLink>
    </div>
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-400">Cargando...</div>
      <div v-else-if="!lista.length" class="p-8 text-center text-gray-400">No hay paquetes registrados</div>
      <table v-else class="w-full text-sm">
        <thead><tr class="border-b border-gray-100 bg-gray-50">
          <th class="text-left px-4 py-3 font-medium text-gray-600">Nombre</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Código</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Precio Total (S/.)</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Activo</th>
          <th class="px-4 py-3"></th>
        </tr></thead>
        <tbody>
          <tr v-for="p in lista" :key="p.id" class="border-b border-gray-50 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium">{{ p.nombre }}</td>
            <td class="px-4 py-3 font-mono text-xs text-gray-600">{{ p.codigo || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ p.precio_total != null ? p.precio_total.toFixed(2) : '—' }}</td>
            <td class="px-4 py-3"><UIcon :name="p.is_active ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" :class="p.is_active ? 'text-green-500' : 'text-gray-300'" class="w-4 h-4" /></td>
            <td class="px-4 py-3"><NuxtLink :to="`/sigarh/general/paquetes/${p.id}?tenant=${tenant}`" class="text-blue-600 hover:underline text-xs">Editar</NuxtLink></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>