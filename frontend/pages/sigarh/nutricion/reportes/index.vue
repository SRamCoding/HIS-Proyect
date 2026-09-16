<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Reportes de Nutrición' })
const { api: $api } = useApi()
const route = useRoute()
const tenant = route.query.tenant as string
const fecha = ref(new Date().toISOString().split('T')[0])
const reporte = ref<any>(null)
const loading = ref(false)

async function generarReporte() {
  loading.value = true
  try { reporte.value = await $api(`/sigarh/nutricion/reportes?fecha=${fecha.value}`, { tenant }) }
  finally { loading.value = false }
}
onMounted(generarReporte)
watch(fecha, generarReporte)
</script>
<template>
  <div class="p-6 space-y-4">
    <div><h1 class="text-xl font-semibold text-gray-800">Reporte de Raciones</h1><p class="text-sm text-gray-500 mt-0.5">Resumen diario de raciones entregadas</p></div>
    <div class="flex items-center gap-3">
      <label class="text-sm text-gray-600">Fecha:</label>
      <input v-model="fecha" type="date" class="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
    </div>
    <div v-if="loading" class="p-8 text-center text-gray-400">Generando reporte...</div>
    <div v-else-if="reporte" class="space-y-4">
      <!-- Resumen -->
      <div class="grid grid-cols-3 gap-4">
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-3xl font-bold text-gray-800">{{ reporte.total }}</p>
          <p class="text-sm text-gray-500 mt-1">Total Raciones</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-3xl font-bold text-green-600">{{ reporte.entregadas }}</p>
          <p class="text-sm text-gray-500 mt-1">Entregadas</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-3xl font-bold text-yellow-500">{{ reporte.pendientes }}</p>
          <p class="text-sm text-gray-500 mt-1">Pendientes</p>
        </div>
      </div>
      <!-- Por tipo -->
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">Distribución por Tipo</h2>
        <div class="space-y-2">
          <div v-for="(cantidad, tipo) in reporte.por_tipo" :key="tipo" class="flex items-center justify-between">
            <span class="text-sm text-gray-600">{{ tipo }}</span>
            <span class="px-3 py-0.5 bg-orange-50 text-orange-700 rounded-full text-sm font-medium">{{ cantidad }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>