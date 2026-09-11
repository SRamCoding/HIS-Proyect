<!-- frontend/pages/admin/reportes/hospitales-modulos.vue -->
<template>
  <div>
    <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
      <span>Reportes</span><span>/</span><span>Hospitales y Módulos</span>
    </div>
    <h1 class="text-lg font-semibold mb-1" style="color: var(--ink)">Reporte de Hospitales y Módulos</h1>
    <p class="text-sm mb-4" style="color: var(--ink-soft)">
      Módulos activos por cada hospital habilitado en el sistema.
    </p>

    <div class="mb-4 flex flex-wrap items-center gap-3">
      <input v-model="search" class="input-clinical max-w-xs" placeholder="Buscar hospital..." />
      <button class="btn-secondary" @click="exportCsv">Exportar CSV</button>
    </div>

    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm" style="min-width: 640px">
          <thead>
            <tr style="border-bottom: 1px solid var(--line)">
              <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Hospital</th>
              <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Dominio</th>
              <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Módulos Activos</th>
              <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in filtrados" :key="row.domain" style="border-bottom: 1px solid var(--line)">
              <td class="px-5 py-3 font-medium" style="color: var(--ink)">{{ row.hospital_name }}</td>
              <td class="px-5 py-3 text-xs" style="color: var(--ink-soft)">{{ row.domain }}</td>
              <td class="px-5 py-3">
                <div class="flex flex-wrap gap-1" style="max-width: 320px">
                  <span v-for="mod in row.active_modules" :key="mod" class="badge badge--neutral">{{ mod }}</span>
                </div>
              </td>
              <td class="px-5 py-3 font-medium" style="color: var(--ink)">{{ row.total_modules }}</td>
            </tr>
            <tr v-if="!filtrados.length">
              <td colspan="4" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">
                {{ search ? 'Sin resultados.' : 'Sin hospitales activos.' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface HospitalModuleReport {
  hospital_name: string
  domain: string
  active_modules: string[]
  total_modules: number
}

const { api } = useApi()

const rows = ref<HospitalModuleReport[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')

const filtrados = computed(() => {
  if (!search.value.trim()) return rows.value
  const q = search.value.toLowerCase()
  return rows.value.filter(r =>
    r.hospital_name.toLowerCase().includes(q) ||
    r.domain.toLowerCase().includes(q)
  )
})

const exportCsv = () => {
  const headers = ['Hospital', 'Dominio', 'Módulos Activos', 'Total']
  const rowsCsv = filtrados.value.map(r => [
    r.hospital_name,
    r.domain,
    r.active_modules.join(' | '),
    String(r.total_modules),
  ])
  const csv = [headers.join(','), ...rowsCsv.map(r => r.map(v => `"${v}"`).join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `hospitales_modulos_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    rows.value = await api<HospitalModuleReport[]>('/admin/reportes/hospitales-modulos')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>