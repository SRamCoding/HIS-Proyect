<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Medicamentos e Insumos' })
const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string
const lista = ref<any[]>([])
const loading = ref(true)
const busqueda = ref('')
onMounted(async () => { lista.value = await $api('/sigarh/config-farmacia/medicamentos', { tenant }); loading.value = false })
const listaFiltrada = computed(() => busqueda.value
  ? lista.value.filter(m => m.nombre.toLowerCase().includes(busqueda.value.toLowerCase()) || m.codigo_digemid?.includes(busqueda.value))
  : lista.value)
</script>
<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div><h1 class="text-xl font-semibold text-gray-800">Medicamentos e Insumos</h1><p class="text-sm text-gray-500 mt-0.5">Catálogo de medicamentos e insumos médicos</p></div>
      <NuxtLink :to="`/sigarh/config-farmacia/medicamentos/create?tenant=${tenant}`">
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:#1e3a5f"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Medicamento</button>
      </NuxtLink>
    </div>
    <input v-model="busqueda" placeholder="Buscar por nombre o código DIGEMID..." class="w-full max-w-sm px-3 py-2 border border-gray-200 rounded-lg text-sm" />
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-400">Cargando...</div>
      <div v-else-if="!listaFiltrada.length" class="p-8 text-center text-gray-400">No hay medicamentos registrados</div>
      <table v-else class="w-full text-sm">
        <thead><tr class="border-b border-gray-100 bg-gray-50">
          <th class="text-left px-4 py-3 font-medium text-gray-600">Nombre</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Código DIGEMID</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Concentración</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Forma Farmacéutica</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Tipo</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Activo</th>
          <th class="px-4 py-3"></th>
        </tr></thead>
        <tbody>
          <tr v-for="m in listaFiltrada" :key="m.id" class="border-b border-gray-50 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium">{{ m.nombre }}</td>
            <td class="px-4 py-3 font-mono text-xs text-gray-600">{{ m.codigo_digemid || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ m.concentracion || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ m.forma_farmaceutica || '—' }}</td>
            <td class="px-4 py-3"><span class="px-2 py-0.5 rounded text-xs" :class="m.tipo === 'MEDICAMENTO' ? 'bg-blue-50 text-blue-700' : 'bg-purple-50 text-purple-700'">{{ m.tipo }}</span></td>
            <td class="px-4 py-3"><UIcon :name="m.is_active ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" :class="m.is_active ? 'text-green-500' : 'text-gray-300'" class="w-4 h-4" /></td>
            <td class="px-4 py-3"><NuxtLink :to="`/sigarh/config-farmacia/medicamentos/${m.id}?tenant=${tenant}`" class="text-blue-600 hover:underline text-xs">Editar</NuxtLink></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>