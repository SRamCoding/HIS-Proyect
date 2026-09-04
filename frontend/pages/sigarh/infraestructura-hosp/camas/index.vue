<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Camas' })
const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string
const lista = ref<any[]>([])
const loading = ref(true)
const filtroEstado = ref('')

onMounted(async () => { lista.value = await $api('/sigarh/infraestructura-hosp/camas', { tenant }); loading.value = false })

const listaFiltrada = computed(() => filtroEstado.value ? lista.value.filter(c => c.estado === filtroEstado.value) : lista.value)

const estadoColor: Record<string,string> = {
  DISPONIBLE: '#10b981', OCUPADA: '#ef4444', MANTENIMIENTO: '#f59e0b', RESERVADA: '#6366f1'
}
</script>
<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div><h1 class="text-xl font-semibold text-gray-800">Camas</h1><p class="text-sm text-gray-500 mt-0.5">Panel de camas del hospital</p></div>
      <NuxtLink :to="`/sigarh/infraestructura-hosp/camas/create?tenant=${tenant}`">
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:#1e3a5f"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva Cama</button>
      </NuxtLink>
    </div>
    <select v-model="filtroEstado" class="px-3 py-2 rounded-lg border border-gray-200 text-sm bg-white">
      <option value="">Todos los estados</option>
      <option value="DISPONIBLE">Disponible</option>
      <option value="OCUPADA">Ocupada</option>
      <option value="MANTENIMIENTO">Mantenimiento</option>
      <option value="RESERVADA">Reservada</option>
    </select>
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-400">Cargando...</div>
      <div v-else-if="!listaFiltrada.length" class="p-8 text-center text-gray-400">No hay camas registradas</div>
      <table v-else class="w-full text-sm">
        <thead><tr class="border-b border-gray-100 bg-gray-50">
          <th class="text-left px-4 py-3 font-medium text-gray-600">Código</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Nombre</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Sala</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Piso</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Tipo</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Estado</th>
          <th class="px-4 py-3"></th>
        </tr></thead>
        <tbody>
          <tr v-for="c in listaFiltrada" :key="c.id" class="border-b border-gray-50 hover:bg-gray-50">
            <td class="px-4 py-3 font-mono text-xs font-medium">{{ c.codigo }}</td>
            <td class="px-4 py-3 font-medium">{{ c.nombre }}</td>
            <td class="px-4 py-3 text-gray-600">{{ c.sala_texto || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ c.piso_texto || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ c.tipo_cama || '—' }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-1 rounded-full text-xs font-medium text-white" :style="`background:${estadoColor[c.estado] || '#6b7280'}`">{{ c.estado }}</span>
            </td>
            <td class="px-4 py-3"><NuxtLink :to="`/sigarh/infraestructura-hosp/camas/${c.id}?tenant=${tenant}`" class="text-blue-600 hover:underline text-xs">Editar</NuxtLink></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>