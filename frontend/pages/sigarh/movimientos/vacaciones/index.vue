<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Justificaciones y Vacaciones' })
const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string

const vacaciones = ref<any[]>([])
const loading = ref(true)
const filtroEstado = ref('')

async function cargar() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filtroEstado.value) params.append('estado', filtroEstado.value)
    vacaciones.value = await $api(`/sigarh/movimientos/vacaciones?${params}`, { tenant })
  } finally {
    loading.value = false
  }
}

onMounted(cargar)

const estadoColor: Record<string, string> = {
  pendiente: '#f59e0b',
  aprobado: '#10b981',
  rechazado: '#ef4444',
}
</script>

<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-gray-800">Justificaciones y Vacaciones</h1>
        <p class="text-sm text-gray-500 mt-0.5">Gestión de solicitudes de vacaciones del personal</p>
      </div>
      <NuxtLink :to="`/sigarh/movimientos/vacaciones/create?tenant=${tenant}`">
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:#1e3a5f">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva Solicitud
        </button>
      </NuxtLink>
    </div>

    <!-- Filtros -->
    <div class="flex gap-3">
      <select v-model="filtroEstado" @change="cargar"
        class="px-3 py-2 rounded-lg border border-gray-200 text-sm bg-white">
        <option value="">Todos los estados</option>
        <option value="pendiente">Pendiente</option>
        <option value="aprobado">Aprobado</option>
        <option value="rechazado">Rechazado</option>
      </select>
    </div>

    <!-- Tabla -->
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-400">Cargando...</div>
      <div v-else-if="!vacaciones.length" class="p-8 text-center text-gray-400">
        No hay solicitudes registradas
      </div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-100 bg-gray-50">
            <th class="text-left px-4 py-3 font-medium text-gray-600">Empleado</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Tipo</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Desde</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Hasta</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Días</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Estado</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="v in vacaciones" :key="v.id" class="border-b border-gray-50 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium">{{ v.nombre_empleado }}</td>
            <td class="px-4 py-3 text-gray-600">{{ v.tipo }}</td>
            <td class="px-4 py-3 text-gray-600">{{ v.fecha_inicio }}</td>
            <td class="px-4 py-3 text-gray-600">{{ v.fecha_fin }}</td>
            <td class="px-4 py-3 text-gray-600">{{ v.dias_solicitados }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-1 rounded-full text-xs font-medium text-white"
                :style="`background:${estadoColor[v.estado] || '#6b7280'}`">
                {{ v.estado }}
              </span>
            </td>
            <td class="px-4 py-3">
              <NuxtLink :to="`/sigarh/movimientos/vacaciones/${v.id}?tenant=${tenant}`"
                class="text-blue-600 hover:underline text-xs">Ver</NuxtLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>